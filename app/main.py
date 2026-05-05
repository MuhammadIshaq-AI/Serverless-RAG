import os
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import boto3
import uuid

app = FastAPI(title="Serverless RAG Interface")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration from Environment
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "your-document-bucket")
QUERY_LAMBDA_NAME = os.getenv("QUERY_LAMBDA_NAME", "rag-query-function")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Ensure static directory exists
os.makedirs("app/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

class QueryRequest(BaseModel):
    query: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("app/static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Uploads the file directly to S3. This will trigger the embedding Lambda function."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        s3_client = boto3.client('s3', region_name=AWS_REGION)
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        
        # Upload directly to S3
        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET_NAME,
            unique_filename,
            ExtraArgs={"ContentType": "application/pdf"}
        )
        
        return {
            "message": "File uploaded successfully to S3. Embeddings generation triggered in background.", 
            "filename": unique_filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query")
async def query_rag(request: QueryRequest):
    """Invokes the AWS Lambda query function directly."""
    try:
        lambda_client = boto3.client('lambda', region_name=AWS_REGION)
        
        # Payload matched to what the Lambda API expects
        payload = {"body": json.dumps({"query": request.query})}
        
        response = lambda_client.invoke(
            FunctionName=QUERY_LAMBDA_NAME,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        response_payload = json.loads(response['Payload'].read())
        
        # Check if the Lambda executed successfully
        if 'FunctionError' in response:
            raise Exception(f"Lambda execution error: {response_payload}")
            
        body = json.loads(response_payload.get('body', '{}'))
        
        if response_payload.get('statusCode') != 200:
            raise Exception(body.get('error', 'Unknown error from Lambda'))
            
        return body
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying Lambda: {str(e)}")
