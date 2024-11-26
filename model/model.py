from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
import clickhouse_connect
from config import config

app = FastAPI()
model = SentenceTransformer('jxm/cde-small-v1')
clickhouse_client = clickhouse_connect.get_client(host=config.CLICKHOUSE_HOST, port=config.CLICKHOUSE_PORT, username='default', password='')
vector_store = FAISS.load_local("faiss_index")
llm = OpenAI(api_key=config.GEMINI_API_KEY)
qa_chain = RetrievalQA(llm=llm, retriever=vector_store.as_retriever())

class Query(BaseModel):
    question: str

@app.post("/ask")
async def ask(query: Query):
    # Получение векторов и поиск
    user_query_vector = model.encode(query.question)
    retrieved_docs = vector_store.similarity_search(user_query_vector, k=5)
    
    # Генерация ответа
    answer = qa_chain.run({"query": query.question, "context": retrieved_docs})
    return {"answer": answer}

@app.post("/index")
async def index_document(document: str, metadata: dict):
    # Векторизация
    doc_vector = model.encode(document)
    # Добавление в FAISS
    vector_store.add_texts([document], metadata=[metadata])
    # Сохранение оригинала в ClickHouse
    clickhouse_client.command("INSERT INTO documents VALUES", [(document, metadata)])
    return {"status": "Document indexed successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)