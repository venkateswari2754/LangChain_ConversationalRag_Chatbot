import streamlit as st
# from api_utils import  list_documents, delete_document
import requests


def upload_document(file):
    print("Uploading document...")
    try:
        files={"file": (file.name,file,file.type)}
        response=requests.post("http://localhost:8000/upload-doc", files=files)
        if response.status_code==200:
            return response.json()
        else:
            st.error(f"Error uploading document: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error uploading document: {str(e)}")
        return None

def list_documents():
    print("Listing documents...")
    try:
        response=requests.get("http://localhost:8000/list-docs")
        if response.status_code==200:
            return response.json()
        else:
            st.error(f"Error listing documents: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error listing documents: {str(e)}")
        return []

def delete_document(file_id):
    header={"accept":"application/json","Content-Type": "application/json"}
    data={"file_id": file_id}
    print("Deleting document...")
    try:
        response=requests.delete("http://localhost:8000/delete-doc", headers=header, json=data)
        if response.status_code==200:
            return response.json()
        else:
            st.error(f"Error deleting document: {response.text}")
            return None
    
    except Exception as e:
        st.error(f"Error deleting document: {str(e)}")
        return False
def get_api_response(question, session_id, model):
    header={"accept":"application/json","Content-Type": "application/json"}
    data={"question": question, "model": model}
    if session_id:
        data["session_id"]=session_id
        
    print("Getting API response...")
    try:
        response=requests.post("http://localhost:8000/chat", headers=header, json=data)
        if response.status_code==200:
            return response.json()
        else:
            st.error(f"Error getting API response: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error getting API response: {str(e)}")
        return None