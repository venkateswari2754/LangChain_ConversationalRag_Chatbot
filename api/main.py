#from chroma_utils import index_document_to_chroma
from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from pydantic_models import QueryInput, QueryResponse, DeleteFileRequest, DocumentInfo
from mysql_util import insert_application_logs, get_chat_history, insert_document_record, delete_document_record, get_all_documents
from chroma_utils import index_document_to_chroma, delete_doc_from_chroma
from langchain_utils import get_rag_chain
from typing import List
import os
import shutil
import uuid
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(filename='app.log',level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)
logging.debug("Debugging information here")
app= FastAPI()


@app.post("/chat", response_model=QueryResponse)
def chat(query_input: QueryInput):
    session_id = query_input.session_id
    logging.info(f"Session ID: {session_id}, User Query: {query_input.question}, Model: {query_input.model.value}")
    
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Get the qroq API key from the .env file
    qroq_api_key = os.getenv("GROQ_API_KEY")
    if not qroq_api_key:
        raise HTTPException(status_code=500, detail="QROQ API key not found in environment variables")
    
    # Set the qroq API key dynamically
    os.environ["GROQ_API_KEY"] = qroq_api_key
    
    # Fetch chat history
    chat_history = get_chat_history(session_id) or []
    logging.debug(f"Chat history for session {session_id}: {chat_history}")
    
    # Ensure chat_history is in the correct format
    if not isinstance(chat_history, list):
        raise ValueError(f"Chat history should be a list, got {type(chat_history)}")
    
    rag_chain = get_rag_chain(query_input.model.value)
    answer = rag_chain.invoke({
        "input": query_input.question,
        "chat_history": chat_history,
    })['answer']
    
    insert_application_logs(session_id, query_input.question, answer, query_input.model.value)
    logging.info(f"Session ID: {session_id}, AI response: {answer}")
    return QueryResponse(answer=answer, session_id=session_id, model=query_input.model.value)
@app.post("/upload-doc")
def upload_and_index_document(file: UploadFile = File(...)):
    allowed_extenstions = ['.html', '.pdf', '.docx']
    file_extenstion = os.path.splitext(file.filename)[1].lower()
    if file_extenstion not in allowed_extenstions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed types: {allowed_extenstions}")
    temp_file_path=f"temp_{file.filename}"
    try:
        # Save the uploaded file to a temporary location
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_id=insert_document_record(file.filename)
        
        logging.info(f"File ID: {file_id}, Temp file path: {temp_file_path}")
        success=index_document_to_chroma(temp_file_path,file_id)
        if success:
            return {"message": "File {file.filename} indexed successfully" , "file_id": {file_id}}
        else:
            delete_document_record(file_id)
            raise HTTPException(status_code=500, detail="Failed to index File {file.filename}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
@app.get("/list-docs", response_model=List[DocumentInfo])
def list_documents():
    documents = get_all_documents()
    logging.info(f"Documents to return: {documents}")
    return documents

# @app.get("/list-docs", response_model=List[DocumentInfo])
# def list_documents():
#     logging.info(f"Executing list_documents endpoint")
#     # Fetch all documents from the database
#     documents = get_all_documents()
#     logging.info(f"Documents fetched: {documents}")
#     return documents

@app.delete("/delete-doc")
def delete_document(request: DeleteFileRequest):
    try:
        # Delete the document from ChromaDB
        chroma_delete_success = delete_doc_from_chroma(request.file_id)
        if chroma_delete_success:
            # Delete the record from our database
            db_delete_success=delete_document_record(request.file_id)
            if db_delete_success:
                return {"message": "Document deleted successfully"}
            else:
                raise HTTPException(status_code=500, detail="File deleted from chroma DB but failed to delete document record from database")
        else:
            raise HTTPException(status_code=404, detail="Document not found in ChromaDB")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {e}")
                            