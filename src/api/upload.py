import json
import base64
from src.core.chunking import extract_text_from_pdf, chunk_text
from src.core.llm import OllamaClient
from src.core.vector_db import PineconeManager

def handler(event, context):
    """
    AWS Lambda handler for document upload.
    Expects base64 encoded PDF in the event body.
    """
    try:
        body = json.loads(event.get("body", "{}"))
        file_content = body.get("file_content")
        file_name = body.get("file_name", "document.pdf")
        
        if not file_content:
            return {"statusCode": 400, "body": json.dumps({"error": "No file content provided"})}
            
        pdf_bytes = base64.b64decode(file_content)
        
        # 1. Extract text
        text = extract_text_from_pdf(pdf_bytes)
        
        # 2. Chunk text
        chunks = chunk_text(text)
        
        # 3. Generate embeddings and prepare for Pinecone
        llm = OllamaClient()
        db = PineconeManager()
        
        vectors = []
        for i, chunk in enumerate(chunks):
            embedding = llm.get_embeddings(chunk)
            vectors.append({
                "id": f"{file_name}_chunk_{i}",
                "values": embedding,
                "metadata": {
                    "text": chunk,
                    "source": file_name
                }
            })
            
        # 4. Upsert to Pinecone
        # Batch upsert in chunks of 100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            db.upsert_vectors(vectors[i:i + batch_size])
            
        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"Successfully processed and embedded {len(chunks)} chunks from {file_name}"})
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
