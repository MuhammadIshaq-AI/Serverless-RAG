import os
import sys
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load variables from .env file so Pinecone and Ollama work locally
load_dotenv()

# Ensure we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.chunking import extract_text_from_pdf, chunk_text
from src.core.llm import OllamaClient
from src.core.vector_db import PineconeManager

app = FastAPI(title="Serverless RAG Interface (LOCAL MODE)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("app/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

class QueryRequest(BaseModel):
    query: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("app/static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/upload")
async def upload_pdf_local(file: UploadFile = File(...)):
    """Processes the PDF completely locally. No S3 or AWS Lambda needed."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        pdf_bytes = await file.read()
        
        # 1. Extract text
        text = extract_text_from_pdf(pdf_bytes)
        
        # 2. Chunk text
        chunks = chunk_text(text)
        
        # 3. Embed & Upsert
        llm = OllamaClient()
        db = PineconeManager()
        
        vectors = []
        for i, chunk in enumerate(chunks):
            embedding = llm.get_embeddings(chunk)
            vectors.append({
                "id": f"{file.filename}_chunk_{i}",
                "values": embedding,
                "metadata": {
                    "text": chunk,
                    "source": file.filename
                }
            })
            
        # Batch upsert
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            db.upsert_vectors(vectors[i:i + batch_size])
            
        return {
            "message": f"Successfully processed and embedded {len(chunks)} chunks locally.", 
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query")
async def query_rag_local(request: QueryRequest):
    """Answers queries locally by talking directly to Pinecone & EC2 Ollama."""
    try:
        llm = OllamaClient()
        db = PineconeManager()
        
        # 1. Generate embedding for the query
        query_embedding = llm.get_embeddings(request.query)
        
        # 2. Retrieve relevant context from Pinecone
        matches = db.query(query_embedding, top_k=5)
        
        context_texts = [match["metadata"]["text"] for match in matches if "metadata" in match]
        context_str = "\n---\n".join(context_texts)
        
        # 3. Generate response using Ollama
        response = llm.generate_response(request.query, context_str)
        
        return {
            "query": request.query,
            "response": response,
            "context_used": context_texts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying locally: {str(e)}")
