from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

def test_groq_connection():
    try:
        groq_api_key = os.getenv("QROQ_API_KEY")
        if not groq_api_key:
            print("Error: GROQ_API_KEY not found in environment variables")
            return

        chat = ChatGroq(
            temperature=0.7,
            groq_api_key=groq_api_key,
            model_name="Llama-3.1-8B-Instant"
        )
        
        response = chat.invoke("Hello, can you hear me?")
        print("Groq connection successful!")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Error testing Groq: {e}")        
        print("Please make sure you have:")
        print("1. A valid GROQ_API_KEY in your .env file")
        print("2. The latest version of langchain-groq installed")
        print("3. Access to the gemma-7b-it model in your Groq account")


if __name__ == "__main__":
    test_groq_connection()