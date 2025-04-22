from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

# class ModelName(str, Enum):
#     GPT4_O = "gpt-4o"
#     GPT4_O_Mini= "gpt-4o-mini"
#     GPT3_5_Turbo = "gpt-3.5-turbo"
#     GPT4 = "gpt-4"
#     GPT4_O_Mini_16k = "gpt-4o-mini-16k"

class ModelName(str, Enum):    
    Llama8B = "Llama-3.1-8B-Instant",
    Llama70B="Llama-3.3-70B-Versatile",
    Gemma2="Gemma2-9B-IT"
    
class QueryInput(BaseModel):
    question: str = Field(..., description="User's question")
    session_id: str = Field(None, description="Session ID for tracking conversation")
    model: ModelName = Field(ModelName.Llama8B, description="Model to be used for the query")
    
class QueryResponse(BaseModel):
    answer: str 
    session_id: str 
    model: ModelName
    
class DocumentInfo(BaseModel):
    id: int
    filename: str 
    upload_timestamp: datetime 
    
class DeleteFileRequest(BaseModel):
    file_id: int