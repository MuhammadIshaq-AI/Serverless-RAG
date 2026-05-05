# Serverless-RAG

A fully serverless Retrieval-Augmented Generation (RAG) pipeline orchestrated with a FastAPI frontend, AWS Lambda, Amazon S3, Pinecone (Vector Database), and an EC2-hosted local Ollama model.

## Features
- **FastAPI Web Interface**: A modern, glassmorphism-styled web interface for drag-and-drop PDF uploads and real-time chat querying.
- **Event-Driven Architecture**: PDFs uploaded via the web interface are sent to an S3 Bucket, which automatically triggers an AWS Lambda function for asynchronous chunking and embedding.
- **Local LLM Integration**: Connects to your self-hosted Ollama instance running on AWS EC2 to generate embeddings and LLM responses, ensuring data privacy.
- **Vector Search**: Seamless integration with Pinecone for fast and scalable semantic search over embedded chunks.
- **Direct Lambda Invocation**: Real-time queries from the frontend directly invoke the AWS Query Lambda without needing an API Gateway.

## Project Structure
```text
Serverless-RAG/
├── app/                    # FastAPI Backend & Web Frontend
│   ├── main.py             # FastAPI server (Upload to S3, Invoke Query Lambda)
│   └── static/             # CSS, JS, HTML UI
├── src/                    # AWS Lambda Code
│   ├── api/                
│   │   ├── upload.py       # S3-Triggered Lambda: downloads PDF, chunks, embeds, indexes
│   │   └── query.py        # Directly Invoked Lambda: embeds query, vector search, LLM generation
│   ├── core/               # Core business logic
│   │   ├── chunking.py     # PDF parsing and text splitting
│   │   ├── llm.py          # API client for EC2 Ollama
│   │   └── vector_db.py    # Pinecone integration
│   └── utils/              
│       └── config.py       # Environment variable configurations
├── build.ps1               # PowerShell script to package code for AWS Lambda
├── requirements.txt        # Python dependencies
└── .env.example            # Environment variables example
```

## Setup & Deployment

### 1. AWS Lambda Setup
1. **Package the Code**:
   Run `.\build.ps1` to create `lambda_package.zip`.
2. **Create AWS Lambdas**:
   - Create **Upload Lambda** (Handler: `api.upload.handler`).
   - Create **Query Lambda** (Handler: `api.query.handler`).
3. **Configure S3 Trigger**:
   - Create an Amazon S3 Bucket.
   - Configure the **Upload Lambda** to be triggered by `s3:ObjectCreated:*` events on that bucket.
4. **Environment Variables**: Set the `PINECONE_*` and `OLLAMA_*` variables in both Lambdas.

### 2. FastAPI Web App Setup
You can run the web app locally or on an EC2 instance. Ensure the machine running this app has AWS credentials configured (`~/.aws/credentials` or ENV vars) with `s3:PutObject` and `lambda:InvokeFunction` permissions.
```bash
pip install -r requirements.txt

# Set Environment Variables
export S3_BUCKET_NAME="your-s3-bucket-name"
export QUERY_LAMBDA_NAME="name-of-your-query-lambda"
export AWS_REGION="us-east-1"

# Run Server
uvicorn app.main:app --reload
```
Open `http://localhost:8000` to access the RAG interface.

## EC2 Ollama Setup
Ensure your EC2 instance is running and has Ollama installed:
```bash
ollama run llama3
ollama run nomic-embed-text
```
Ensure the EC2 Security Group allows inbound HTTP traffic on port `11434` from the AWS Lambda security group.
