import urllib.parse
import boto3
import os
from src.core.chunking import extract_text_from_pdf, chunk_text
from src.core.llm import OllamaClient
from src.core.vector_db import PineconeManager

s3_client = boto3.client('s3')

def handler(event, context):
    """
    AWS Lambda handler for S3 object creation event.
    Triggered automatically when a PDF is uploaded to the S3 bucket.
    """
    try:
        # Get the bucket and object key from the Event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        
        if not key.endswith('.pdf'):
            print(f"Skipping non-PDF file: {key}")
            return {"statusCode": 200, "body": "Skipped non-PDF file"}

        print(f"Processing PDF from S3: {bucket}/{key}")
        
        # 1. Download file from S3
        response = s3_client.get_object(Bucket=bucket, Key=key)
        pdf_bytes = response['Body'].read()
        
        # 2. Extract text
        text = extract_text_from_pdf(pdf_bytes)
        
        # 3. Chunk text
        chunks = chunk_text(text)
        
        # 4. Generate embeddings and prepare for Pinecone
        llm = OllamaClient()
        db = PineconeManager()
        
        vectors = []
        for i, chunk in enumerate(chunks):
            embedding = llm.get_embeddings(chunk)
            vectors.append({
                "id": f"{key}_chunk_{i}",
                "values": embedding,
                "metadata": {
                    "text": chunk,
                    "source": key
                }
            })
            
        # 5. Upsert to Pinecone in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            db.upsert_vectors(vectors[i:i + batch_size])
            
        print(f"Successfully indexed {len(chunks)} chunks into Pinecone.")
        return {
            "statusCode": 200,
            "body": f"Successfully processed and embedded {len(chunks)} chunks from {key}"
        }
        
    except Exception as e:
        print(f"Error processing S3 event: {str(e)}")
        raise e
