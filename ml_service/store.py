from clickhouse_driver import connect, Client
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from document import Document
from typing import NamedTuple, List
from collections import namedtuple
import os
import PyPDF2 
import json
import uuid
from document_extract import extract_text_from_txt
import logging
# from docx import Document as DocxDocument
from bs4 import BeautifulSoup
import docx2txt
import numpy as np

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


# Определение result_document
result_document = namedtuple(
    "result_document", ["text", "metadata", "embedding", "score"]
)

class VectorStore:
    def __init__(
        self,
        uri: str,
        embedding_model: SentenceTransformer,
        table_name: str = "vector_search",
    ) -> None:
        self.client = Client.from_url(uri)
        self.table_name = table_name
        self.model = embedding_model

    def process_txt(self, file_path: str) -> Document:
        """Обработка .txt файла."""
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return Document(page_content=content, metadata={"src": file_path, "type": "txt"})

    def process_pdf(self, file_path: str) -> Document:
        """Обработка .pdf файла."""
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            content = "".join([page.extract_text() for page in reader.pages])
        return Document(page_content=content, metadata={"src": file_path, "type": "pdf"})

    def process_docx(self, file_path: str) -> Document:
        """Обработка .docx файла (используем docx2txt)."""
        content = docx2txt.process(file_path)
        return Document(page_content=content, metadata={"src": file_path, "type": "docx"})


    def process_html(self, file_path: str) -> Document:
        """Обработка .html файла (можно использовать BeautifulSoup)."""
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
            content = soup.get_text()
        return Document(page_content=content, metadata={"src": file_path, "type": "html"})

    def add_documents_from_files(self, file_paths: List[str]):
        """
        Обрабатывает файлы и добавляет их содержимое в таблицу ClickHouse.
        """
        try:
            for file_path in file_paths:
                content = None

                # Извлечение текста в зависимости от типа файла
                if file_path.lower().endswith(".txt"):
                    content = self.process_txt(file_path).page_content
                elif file_path.lower().endswith(".pdf"):
                    content = self.process_pdf(file_path).page_content
                elif file_path.lower().endswith(".docx"):
                    content = self.process_docx(file_path).page_content
                elif file_path.lower().endswith(".html"):
                    content = self.process_html(file_path).page_content
                else:
                    log.warning(f"Unsupported file format: {file_path}")
                    continue

                # Проверка, что текст не пустой
                if not content.strip():
                    log.warning(f"Empty content in file: {file_path}")
                    continue

                # Генерация эмбеддинга
                embedding = self.model.encode(content).tolist()

                # Проверка формата эмбеддинга
                if not isinstance(embedding, list) or not all(isinstance(x, float) for x in embedding):
                    raise ValueError(f"Embedding must be a list of floats. File: {file_path}")

                # Подготовка данных для вставки
                data = [
                    (str(uuid.uuid4()), content, embedding)  # ID, текст, эмбеддинг
                ]

                # Добавление данных в ClickHouse
                self.client.execute(
                    f"INSERT INTO {self.table_name} (DocName, Metadata, Text, Embedding) VALUES",
                    data,
                )

                log.info(f"File {file_path} processed successfully.")
                self.show_table()

        except Exception as e:
            log.error(f"Error adding documents: {e}")
            raise

    def show_table(self):
        """Метод для вывода содержимого таблицы для отладки."""
        try:
            query = f"SELECT * FROM {self.table_name} LIMIT 10"
            result = self.client.execute(query)
            for row in result:
                print(row)
        except Exception as e:
            log.error(f"Error displaying table contents: {e}")
            raise

    def retrieve_relevant_documents(self, query: str, k: int = 5) -> List[result_document]:
        """
        Извлекает наиболее релевантные документы из базы данных с использованием эмбеддингов.
        """
        # Генерация эмбеддинга для запроса
        query_embedding = self.model.encode(query).tolist()

        # Запрос для извлечения документов, близких к запросу
        query_str = f"""
        SELECT DocName, Text, Embedding
        FROM {self.table_name}
        """
        result = self.client.execute(query_str)

        # Считаем схожесть между эмбеддингом запроса и эмбеддингами документов
        document_scores = []
        for doc_name, doc_text, doc_embedding in result:
            doc_embedding = np.array(doc_embedding)
            score = np.dot(query_embedding, doc_embedding)  # Косинусное сходство
            document_scores.append(result_document(doc_text, doc_name, doc_embedding, score))

        # Сортируем документы по схожести
        document_scores.sort(key=lambda x: x.score, reverse=True)

        # Возвращаем топ-k наиболее релевантных документов
        return document_scores[:k]

