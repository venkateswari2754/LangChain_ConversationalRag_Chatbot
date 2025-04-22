from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders  import PyPDFLoader, Docx2txtLoader
 # You'll need to import the appropriate Qroq embeddings
from typing import List, Dict, Any
from langchain_core.documents import Document        
from langchain_chroma import Chroma
from langchain_experimental.text_splitter import SemanticChunker
# from langchain_openai.embeddings import OpenAIEmbeddings 
import os
import logging
from dotenv import load_dotenv

import os
import logging
# from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_experimental.text_splitter import SemanticChunker

# Load environment variables from .env file
load_dotenv()

# Retrieve the OpenAI API key
qroq_api_key =os.getenv("QROQ_API_KEY") 
if not qroq_api_key:
    raise ValueError("Qroq API key not found in  environment variables")

logging.basicConfig(filename='app.log', level=logging.INFO)

# Initialize HuggingFace embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={'device': 'cpu'}
)

# Initialize the text splitter and vectorstore
text_splitter = SemanticChunker(embeddings)
collection_name = "documents"
vectorstore = Chroma(collection_name=collection_name, embedding_function=embeddings)
logging.info("vectorstore initialized with HuggingFace embeddings")

def index_document_to_chroma(file_path: str, file_id: int) -> bool:
    """
    Index the document to ChromaDB.
    """
    try:
        logging.info(f"File ID: {file_id}, file path: {file_path}")
        
        # Load and split the document
        splits = load_and_split_document(file_path)
        logging.info(f"Splits content: {splits}, Type: {type(splits)}")
        
        # Add metadata to each document and store in vectorstore
        for split in splits:
            if split.metadata is None:
                split.metadata = {}
            split.metadata['file_id'] = file_id
            
        
        vectorstore.add_documents(splits, embedding=embeddings)
        logging.info(f"Document added to vectorstore: {file_path}")     
             
        logging.info("Document indexed successfully")
        return True
    except Exception as e:
        logging.error(f"Error indexing document: {e}")
        return False

def load_and_split_document(file_path: str):
    """
    Load and split the document based on its type.
    """
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
        logging.info(f"PDF file loaded: {file_path}")
    elif file_path.endswith('.docx'):
        loader = Docx2txtLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")
    
    documents = loader.load()
    logging.info(f"documents info after: {documents}")
    return text_splitter.split_documents(documents) 
   
  
    
def delete_doc_from_chroma(file_id: int) -> bool:
    """
    Delete the document from ChromaDB.
    """
    try:
        # Assuming you have a method to delete documents by file_id
        docs=vectorstore.get(where={"file_id": file_id})
        print(f"Documents found {len(docs['ids'])} document chunks for file_id: {file_id}")
        if docs:
            vectorstore._collection.delete(where={"file_id": file_id}) 
            print(f"Deleted all documents with file_id: {file_id}")           
            return True
        else:
            print(f"No documents found with file_id: {file_id}")
            return False

    except Exception as e:
        print(f"Error deleting document: {e}")
        return False