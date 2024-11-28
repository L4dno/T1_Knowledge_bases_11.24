from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Generator, Any, List
import logging
import os
import json
from sentence_transformers import SentenceTransformer
from llm_transformers import TransformerModel
from store import VectorStore  # Необходимо для поиска по векторным данным

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Модель входных данных для запросов
class QueryModel(BaseModel):
    body: str
    model_name: str | None = None  # Название модели (опционально)
    max_length: int = 150  # Длина генерируемого ответа (количество токенов)
    temperature: float = 0.7  # Температура для генерации
    top_k: int = 50  # Количество наиболее вероятных токенов для выбора
    top_p: float = 0.9  # Вероятностный порог для ядерного сэмплинга
    hf_access_token: str | None = None  # Токен доступа к Hugging Face моделям, которые (либо большие, либо дообучены с помощью PEFT)

# Модель ответа
class ResponseModel(BaseModel):
    body: str
    context: str

class DocumentResponse(BaseModel):
    doc_name: str
    metadata: dict
    text: str
    
# Основной сервис
class MLservice:
    def __init__(
        self,
        clickhouse_uri: str = "clickhouse://default:@localhost:9000/default",
        embedding_model: str = "intfloat/multilingual-e5-small",
        table_name: str = "vector_search",
    ) -> None:
        self.model = TransformerModel()  # Модель для генерации текста
        self.store = VectorStore(clickhouse_uri, self.model, table_name=table_name)
        self.embedding_model = SentenceTransformer(embedding_model)  # Модель для векторизации текста

    def get_response(self, query: str, model_name: str | None = None, max_length: int = 150, temperature: float = 0.7, top_k: int = 50, top_p: float = 0.9) -> tuple[str, str]:
        """Возвращает ответ и контекст от модели transformers с использованием RAG."""
        # Шаг 1: Получаем релевантные документы из базы данных
        docs = self.store.search_similarity(query, k=3)
        
        # Шаг 2: Генерация ответа на основе документов и запроса
        return self.model.get_model_response(query, docs, model_name, max_length, temperature, top_k, top_p)

    def get_stream_response(
        self, query: str, model_name: str | None = None, max_length: int = 150, temperature: float = 0.7, top_k: int = 50, top_p: float = 0.9
    ) -> Generator[str, Any, None]:
        """Возвращает потоковый ответ от модели transformers с использованием RAG."""
        # Шаг 1: Получаем релевантные документы из базы данных
        docs = self.store.search_similarity(query, k=3)
        
        # Шаг 2: Генерация ответов по частям с использованием модели
        for chunk in self.model.get_stream_response(query, docs, model_name, max_length, temperature, top_k, top_p):
            yield chunk

    def add_documents_from_files(self, file_paths: List[str]):
        """Обработать файлы и добавить их в ClickHouse."""
        self.store.add_documents_from_files(file_paths)


# Инициализация ML-сервиса
clickhouse_uri = "clickhouse://default:@localhost:9000/default"

ml_service = MLservice(
    clickhouse_uri=clickhouse_uri,
)

@app.get("/hello_model")
def return_status():
    return {"status": "OK"}

@app.post("/respond", response_model=ResponseModel)
def respond(query: QueryModel):
    """
    Синхронный запрос для получения ответа от ML-сервиса с использованием RAG.
    """
    try:
        log.info(f"Processing query: {query.body}")
        body, context = ml_service.get_response(
            query.body,
            query.model_name,
            query.max_length,
            query.temperature,
            query.top_k,
            query.top_p,
        )
        return {"body": body, "context": context}
    except Exception as e:
        log.error(f"Error in respond: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/respond_stream")
def respond_stream(query: QueryModel):
    """
    Потоковый запрос для получения ответа от ML-сервиса с использованием RAG.
    """
    try:
        log.info(f"Processing streaming query: {query.body}")

        def stream_response():
            for chunk in ml_service.get_stream_response(
                query.body,
                query.model_name,
                query.max_length,
                query.temperature,
                query.top_k,
                query.top_p,
            ):
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
        file_path = f"./uploaded_files/{file.filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Добавляем файл в ClickHouse
        ml_service.add_documents_from_files([file_path])  # Это сохранит файлы и их контент в ClickHouse

        return {"message": f"File {file.filename} uploaded and processed successfully"}
    except Exception as e:
        log.error(f"Error in upload_file: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/get_document/", response_model=DocumentResponse)
async def get_document(doc_name: str):
    """
    Эндпоинт для получения документа по его имени из базы данных.
    """
    vector_store = VectorStore(clickhouse_uri, embedding_model=None)
    try:
        query = f"SELECT DocName, Metadata, Text FROM vector_search WHERE DocName = '{doc_name}'"
        result = vector_store.client.execute(query)

        if not result:
            raise HTTPException(status_code=404, detail="Document not found")

        doc_name, metadata, text = result[0]

        return DocumentResponse(doc_name=doc_name, metadata=json.loads(metadata), text=text)
    
    except Exception as e:
        log.error(f"Error retrieving document {doc_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/delete_document/")
async def delete_document(doc_name: str):
    """
    Эндпоинт для удаления документа по его имени из базы знаний.
    """
    vector_store = VectorStore(clickhouse_uri, embedding_model=None)
    try:
        # Проверяем, существует ли документ
        query_check = f"SELECT COUNT(*) FROM vector_search WHERE DocName = '{doc_name}'"
        result = vector_store.client.execute(query_check)

        if not result or result[0][0] == 0:
            raise HTTPException(status_code=404, detail="Document not found")

        # Удаляем документ из базы данных
        query_delete = f"ALTER TABLE vector_search DELETE WHERE DocName = '{doc_name}'"
        vector_store.client.execute(query_delete)

        return {"message": f"Document '{doc_name}' deleted successfully"}
    except Exception as e:
        log.error(f"Error deleting document {doc_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
