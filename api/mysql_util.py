import pymysql
from dotenv import load_dotenv
import os

#Load environment variables from .env file
load_dotenv()

def get_db_connection():
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),  # Replace with your database name
        port=int(os.getenv("MYSQL_PORT"))
    )
    return conn

def create_application_logs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS application_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(255),
            user_query TEXT,
            get_response TEXT,
            model VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_application_logs(session_id, user_query, gpt_response, model):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        #Insert data into the application_logs table
        cursor.execute('''
            INSERT INTO application_logs (session_id, user_query, get_response, model)
            VALUES (%s, %s, %s, %s)
        ''', (session_id, user_query, gpt_response, model))
        conn.commit()
    except pymysql.Error as e:
        print(f"Error inserting application logs: {e}")
    finally:
        conn.close()

def get_chat_history(session_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)  # Use DictCursor for dictionary-like results
    try:
        #Execute the query to fetch chat history
        cursor.execute('''
            SELECT user_query, get_response 
            FROM application_logs 
            WHERE session_id = %s 
            ORDER BY created_at
        ''', (session_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.extend([
                {"role": "human", "content": row['user_query']},
                {"role": "ai", "content": row['get_response']}
            ])
    except pymysql.Error as e:
        print(f"Error fetching chat history: {e}")
        messages = []
    finally:
        conn.close()
    
    return messages

def create_document_store():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        #Create the document_store table if it doesn't exist
     cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_store (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255),
                upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
     conn.commit()
    except pymysql.Error as e:
        print(f"Error creating document_store table: {e}")
    finally:
        conn.close()

def insert_document_record(filename):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        #Insert the filename into the document_store table
        cursor.execute('INSERT INTO document_store (filename) VALUES (%s)', (filename,))
        conn.commit()
        file_id = cursor.lastrowid  # Get the ID of the inserted row
    except pymysql.Error as e:
        print(f"Error inserting document record: {e}")
        file_id = None
    finally:
        conn.close()
    return file_id


def delete_document_record(file_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        #Execute the DELETE query
       cursor.execute('DELETE FROM document_store WHERE id = %s', (file_id,))
       conn.commit()
       success = True
    except pymysql.Error as e:
        print(f"Error deleting document record: {e}")
        success = False
    finally:
        conn.close()
    return success

def get_all_documents():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)  # Use DictCursor for dictionary-like results
    try:
        #Execute the SELECT query
        cursor.execute("SELECT id, filename, upload_timestamp FROM document_store")
        rows = cursor.fetchall()  # Fetch all rows from the result
    except pymysql.Error as e:
        print(f"Error fetching documents: {e}")
        rows = []
    finally:
        conn.close()
    
    #Return the rows as a list of dictionaries
    return rows

#Initialize the database and create tables if they don't exist
create_application_logs()
create_document_store()