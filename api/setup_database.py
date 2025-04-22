import pymysql
from dotenv import load_dotenv
import os
from mysql_util import get_db_connection, insert_application_logs, get_chat_history

load_dotenv()

def setup_database():
    # First, connect without specifying a database to create it if it doesn't exist
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD"),
        port=int(os.getenv("MYSQL_PORT", 3306))
    )
    
    try:
        with conn.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('MYSQL_DB', 'rag_app')}")
            print(f"Database {os.getenv('MYSQL_DB', 'rag_app')} created or already exists")
            
            # Switch to the database
            cursor.execute(f"USE {os.getenv('MYSQL_DB', 'rag_app')}")
            
            # Create application_logs table
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
            print("application_logs table created or already exists")
            
            # Create document_store table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS document_store (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    filename VARCHAR(255),
                    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("document_store table created or already exists")
            
            conn.commit()
            print("Database setup completed successfully!")
            
    except pymysql.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    setup_database()

# Test connection
try:
    conn = get_db_connection()
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")

# Test inserting a log
try:
    insert_application_logs(
        session_id="test_session",
        user_query="test question",
        gpt_response="test response",
        model="gpt-4"
    )
    print("Log insertion successful!")
except Exception as e:
    print(f"Log insertion failed: {e}")

# Test retrieving chat history
try:
    history = get_chat_history("test_session")
    print("Chat history retrieval successful!")
    print(f"Retrieved {len(history)} messages")
except Exception as e:
    print(f"Chat history retrieval failed: {e}")