from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
from supabase import create_client
from textblob import TextBlob
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import HTTPException
import os

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

app = FastAPI()

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("ENV URL:", os.getenv("SUPABASE_URL"))
print("ENV KEY loaded:", os.getenv("SUPABASE_KEY") is not None)

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL or Key not found in environment variables.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def preprocess_text(text: str) -> str:
    return str(TextBlob(text).correct())

def search_model(BaseModel):
    query:str
    top_k:int = 10

Threshold = 0.3

@app.post("/search")
def search(request: SearchRequest):
    try:
        query_embedding = model.encode(preprocess_text(request.query)).tolist()

        response = supabase.rpc(
            "match_notes",
            {
                "query_embedding": query_embedding,
                "match_count": request.top_k
            }
        ).execute()

        result = [rlt for rlt in response.data if rlt['similarity'] > Threshold]

        rslt = []

        if not result:
            return {"message": "match not found"}
        else:
            for row in result:
                rslt.append({
                    "file": row['file_name'],
                    "path": row['path'],
                    "similarity": round(row['similarity'], 3),
                    "content": row['content']
                })
    
        return {"results": rslt}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to the Semantic Search API"}