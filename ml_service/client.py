from typing import Any, Generator
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from store import VectorStore
from llm import Ollama
import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# FastAPI instance
app = FastAPI()

# Pydantic models for request and response validation
class Query(BaseModel):
    body: str
    model_name: str  # Название модели передается в запросе

class Response(BaseModel):
    body: str
    context: str

# Main service class
class MLService:
    def __init__(
        self,
        clickhouse_uri: str,
        ollama_uri: str,
        embedding_model: str = "Tochka-AI/ruRoPEBert-e5-base-2k",
        table_name: str = "vector_search",
    ) -> None:
        self.model = SentenceTransformer(embedding_model)
        self.store = VectorStore(clickhouse_uri, self.model, table_name=table_name)
        self.ollama = Ollama(ollama_uri)

    def get_response(self, query: str, model_name: str) -> tuple[str, str]:
        """Return response and context from Ollama model."""
        docs = self.store.search_similarity(query, 3)
        return self.ollama.get_response(query, docs, model_name)

    def get_stream_response(self, query: str, model_name: str) -> Generator[str, Any, None]:
        """Return streaming response from Ollama model."""
        docs = self.store.search_similarity(query, 3)
        for chunk in self.ollama.get_stream_response(query, docs, model_name):
            yield chunk
        yield "Ссылки:\n" + "\n".join([doc.metadata for doc in docs])


# Initialize the ML service
clickhouse_uri = "clickhouse://default:@localhost:8123/default"
ollama_uri = "http://localhost:11434/api/generate"

if not clickhouse_uri:
    log.error("CLICKHOUSE_URI is not set")
    raise RuntimeError("Missing CLICKHOUSE_URI")

if not ollama_uri:
    log.error("OLLAMA_URI is not set")
    raise RuntimeError("Missing OLLAMA_URI")

ml_service = MLService(clickhouse_uri=clickhouse_uri, ollama_uri=ollama_uri)

# Define API endpoints
@app.post("/respond", response_model=Response)
def respond(query: Query):
    """
    Handle synchronous responses.
    """
    try:
        body, context = ml_service.get_response(query.body, query.model_name)
        return {"body": body, "context": context}
    except Exception as e:
        log.error(f"Error in respond: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/respond_stream")
def respond_stream(query: Query):
    """
    Handle streaming responses.
    """
    try:
        stream_response = ml_service.get_stream_response(query.body, query.model_name)
        if stream_response is None:
            log.error("stream_response is None")
            raise ValueError("stream_response is None")

        for chunk in stream_response:
            if chunk is None:
                log.error("Chunk is None")
                raise ValueError("Chunk is None")
            yield f"{chunk}\n"

        return StreamingResponse(stream_response, media_type="text/plain")
    except Exception as e:
        log.error(f"Error in respond_stream: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e

