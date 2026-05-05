# Serverless-RAG

A fully serverless Retrieval-Augmented Generation (RAG) pipeline orchestrated with AWS Lambda, Pinecone (Vector Database), and an EC2-hosted local Ollama model.

## Features
- **Serverless Architecture**: Built on AWS Lambda for scalable and cost-effective processing.
- **Local LLM Integration**: Connects to your self-hosted Ollama instance running on AWS EC2 to generate embeddings and LLM responses, ensuring data privacy and cost control over expensive proprietary models.
- **Vector Search**: Seamless integration with Pinecone for fast and scalable semantic search over embedded chunks.
- **Manual Deployment**: Code is structured to be easily packaged and uploaded to your manually created AWS Lambda functions.

## Project Structure
```text
Serverless-RAG/
├── src/
│   ├── api/                # Lambda handler entry points
│   │   ├── upload.py       # Handles document upload, chunking, embedding, indexing
│   │   └── query.py        # Handles query, embedding, vector search, LLM generation
│   ├── core/               # Core business logic
│   │   ├── chunking.py     # PDF parsing and text splitting
│   │   ├── llm.py          # API client for EC2 Ollama
│   │   └── vector_db.py    # Pinecone integration
│   └── utils/              # Utilities
│       └── config.py       # Environment variable configurations
├── build.ps1               # PowerShell script to package code for AWS Lambda
├── requirements.txt        # Python dependencies
└── .env.example            # Environment variables example
```

## Setup & Deployment

1. **Package the Code**:
   Run the included PowerShell script to bundle the dependencies and source code into a single `.zip` file:
   ```powershell
   .\build.ps1
   ```
   This will generate a `lambda_package.zip` file.

2. **Create AWS Lambdas**:
   Create two separate Lambda functions in the AWS Console (Runtime: Python 3.9+).
   - Upload the generated `lambda_package.zip` to both functions.
   - For the **Upload Lambda**, set the Handler to: `api.upload.handler`
   - For the **Query Lambda**, set the Handler to: `api.query.handler`

3. **Configure Environment Variables**:
   In the AWS Lambda console for both functions, set the following environment variables:
   - `PINECONE_API_KEY`: Your Pinecone API Key
   - `PINECONE_ENVIRONMENT`: Your Pinecone Environment
   - `PINECONE_INDEX_NAME`: Your Pinecone Index Name (e.g., serverless-rag)
   - `OLLAMA_BASE_URL`: HTTP URL of your EC2 instance (e.g., `http://<ec2-ip>:11434`)
   - `OLLAMA_EMBEDDING_MODEL`: `nomic-embed-text`
   - `OLLAMA_LLM_MODEL`: `llama3`

## EC2 Ollama Setup
Ensure your EC2 instance is running and has Ollama installed with the required models:
```bash
ollama run llama3
ollama run nomic-embed-text
```
Ensure the EC2 Security Group allows inbound HTTP traffic on port `11434` from the AWS Lambda security group.
