from dotenv import load_dotenv
from main import preprocess_text
from main import model
from supabase import create_client
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_note(file_name, text):
    clean = preprocess_text(text)
    embedding = model.encode(clean).tolist()
    supabase.table("notes").insert({
        "file_name": file_name,
        "content": clean,
        "embedding": embedding
    }).execute()

try:
    insert_note("example.txt", "this is an example")
    print("Insertion successful.")
except Exception as e:
    print("Error during insertion:", str(e))