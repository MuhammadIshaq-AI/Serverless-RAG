import os

class Config:
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "serverless-rag")
    
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    OLLAMA_LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "gemma3:270m")
    
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
