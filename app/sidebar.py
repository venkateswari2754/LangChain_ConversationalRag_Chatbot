import streamlit as st
from api_utils import upload_document, list_documents, delete_document

def display_sidebar():
    # Sidebar model selection
    model_options = [       
       
        "Llama-3.1-8B-Instant"
    ]
    st.sidebar.selectbox("Select Model",options= model_options,key="model")
    
    # Sidebar file upload
    st.sidebar.header("Upload Document")
    uploaded_file = st.sidebar.file_uploader("Upload a document", type=["pdf", "docx"])
    if(uploaded_file is not None):
        if st.sidebar.button("Upload"):
            with st.spinner("Uploading..."):
               upload_response=upload_document(uploaded_file)
               if upload_response:
                     st.sidebar.success(f"File {uploaded_file.name} uploaded with file id {uploaded_file.file_id} successfully")
                     st.session_state.documents=list_documents() # Refresh the document list
    
    # Sidebar document list
    st.sidebar.header("Uploaded Documents")
    if st.sidebar.button("Refresh"):
        st.session_state.documents = list_documents()
    # initialize document list if not present
    if "documents" not in st.session_state:
        st.session_state.documents = list_documents()
    
    documents=st.session_state.documents
    if documents:
        for doc in documents:
            st.sidebar.text(f"{doc['filename']} (ID: {doc['id']}, uploaded on: {doc['upload_timestamp']})")
        
        #Delete document
        selected_file_id = st.sidebar.selectbox("Select Document to delete", options=[doc['id'] for doc in documents],
                                                  format_func=lambda x: next((doc['filename'] for doc in documents if doc['id'] == x)))
        if st.sidebar.button("Delete Selected Document"):
            with st.spinner("Deleting..."):
                delete_response=delete_document(selected_file_id)
                if delete_response:
                    st.sidebar.success(f"File {selected_file_id} deleted successfully")
                    st.session_state.documents=list_documents()
                else:
                    st.sidebar.error(f"Error deleting file {selected_file_id}")