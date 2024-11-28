from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Generator, Any, List
from sentence_transformers import SentenceTransformer
from store import VectorStore
from llm import Ollama
import logging
import os

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Модель входных данных для запросов
class QueryModel(BaseModel):
    body: str
    model_name: str | None = None  # Название модели (опционально)

# Модель ответа
class ResponseModel(BaseModel):
    body: str
    context: str

# Основной сервис
class MLservice:
    def __init__(
        self,
        clickhouse_uri: str,
        ollama_uri: str = 'http://localhost:11434/api/generate',
        embedding_model: str = "intfloat/multilingual-e5-small",
        table_name: str = "vector_search",
    ) -> None:
        model = SentenceTransformer(embedding_model, use_auth_token='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')  
        
        self.store = VectorStore(clickhouse_uri, model, table_name=table_name)
        self.ollama = Ollama(ollama_uri)

    def get_response(self, query: str, model_name: str | None = None) -> tuple[str, str]:
        """Возвращает ответ и контекст от Ollama модели"""
        docs = self.store.search_similarity(query, 3)
        return self.ollama.get_response(query, docs, model_name=model_name)

    def get_stream_response(
        self, query: str, model_name: str | None = None
    ) -> Generator[str, Any, None]:
        """Возвращает потоковый ответ от Ollama модели"""
        docs = self.store.search_similarity(query, 3)
        for chunk in self.ollama.get_stream_response(query, docs, model_name=model_name):
            yield chunk["message"]["content"]  # type: ignore
        yield "Ссылки:" + "\n".join([doc.metadata for doc in docs])

    def add_documents_from_files(self, file_paths: List[str]):
        """Обработать файлы и добавить их в ClickHouse."""
        self.store.add_documents_from_files(file_paths)


# Инициализация ML-сервиса
clickhouse_uri = "clickhouse://default:@localhost:8123/default"
ollama_uri = "http://localhost:11434/api/generate"

ml_service = MLservice(
    clickhouse_uri=clickhouse_uri,
    ollama_uri=ollama_uri,
)

@app.get("/hello_model")
def return_status():
    return {"status": "OK"}

@app.post("/respond", response_model=ResponseModel)
def respond(query: QueryModel):
    """
    Синхронный запрос для получения ответа от ML-сервиса.
    """
    try:
        log.info(f"Processing query: {query.body}")
        body, context = ml_service.get_response(query.body, query.model_name)
        return {"body": body, "context": context}
    except Exception as e:
        log.error(f"Error in respond: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/respond_stream")
def respond_stream(query: QueryModel):
    """
    Потоковый запрос для получения ответа от ML-сервиса.
    """
    try:
        log.info(f"Processing streaming query: {query.body}")

        def stream_response():
            for chunk in ml_service.get_stream_response(query.body, query.model_name):
                yield f"{chunk}\n"

        return StreamingResponse(stream_response(), media_type="text/plain")
    except Exception as e:
        log.error(f"Error in respond_stream: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    """
    Эндпоинт для загрузки файла (PDF или TXT) и сохранения его в ClickHouse.
    """
    try:
        # Сохраняем файл локально
        file_path = f"./uploaded_files/{file.filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Добавляем файл в ClickHouse
        ml_service.add_documents_from_files([file_path])

        return {"message": f"File {file.filename} uploaded and processed successfully"}
    except Exception as e:
        log.error(f"Error in upload_file: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


