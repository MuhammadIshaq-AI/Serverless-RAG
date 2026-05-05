import json
from src.core.llm import OllamaClient
from src.core.vector_db import PineconeManager

def handler(event, context):
    """
    AWS Lambda handler for querying the RAG system.
    Expects a JSON body with 'query'.
    """
    try:
        body = json.loads(event.get("body", "{}"))
        user_query = body.get("query")
        
        if not user_query:
            return {"statusCode": 400, "body": json.dumps({"error": "No query provided"})}
            
        llm = OllamaClient()
        db = PineconeManager()
        
        # 1. Generate embedding for the query
        query_embedding = llm.get_embeddings(user_query)
        
        # 2. Retrieve relevant context from Pinecone
        matches = db.query(query_embedding, top_k=5)
        
        context_texts = [match["metadata"]["text"] for match in matches if "metadata" in match]
        context_str = "\n---\n".join(context_texts)
        
        # 3. Generate response using Ollama
        response = llm.generate_response(user_query, context_str)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "query": user_query,
                "response": response,
                "context_used": context_texts
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
