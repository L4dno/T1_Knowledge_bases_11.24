from clickhouse_driver import connect, Client
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from document import Document
from typing import NamedTuple, List
from collections import namedtuple
import os
import PyPDF2  # Импортируем библиотеку PyPDF2


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

    def create_table(self):
        """Создание таблицы в ClickHouse для хранения данных."""
        self.client.execute("SET allow_experimental_annoy_index = 1")
        self.client.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_name}
            (
                DocName String,
                Metadata String,
                Text String,
                Embedding Array(Float32),
                INDEX ann_index Embedding TYPE annoy('cosineDistance')
            )
            ENGINE = MergeTree
            ORDER BY DocName;
            """
        )

    def create_embs(self, documents: List[Document]):
        """Создание и сохранение эмбеддингов и текста в ClickHouse."""
        embeddings = [
            (doc.metadata.get("src", ""), doc.metadata, doc.page_content, self.model.encode(doc.page_content).tolist())
            for doc in tqdm(documents)
        ]

        self.client.execute(f"INSERT INTO {self.table_name} VALUES", embeddings)

    def search_similarity(self, query: str, k: int = 1) -> list[result_document]:
        """Поиск похожих документов."""
        emb_q = self.model.encode(query).tolist()

        res = self.client.execute(
            f"""
            SELECT DocName, Metadata, Text, L2Distance(Embedding, %(emb)s) AS score
            FROM {self.table_name}
            ORDER BY score ASC
            LIMIT %(k)s
            """,
            {"emb": emb_q, "k": k},
        )
        if not res:
            return []

        return [
            result_document(
                text=row[2], metadata=row[1], embedding=row[3], score=row[3]
            )
            for row in res
        ]

    def process_pdf(self, file_path: str) -> Document:
        """Прочитать PDF файл и преобразовать его в документ."""
        # Открываем PDF файл с помощью PyPDF2
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()

        # Возвращаем Document с текстом и метаданными
        return Document(
            page_content=text,
            metadata={"src": file_path, "type": "pdf"}
        )

    def process_txt(self, file_path: str) -> Document:
        """Прочитать TXT файл и преобразовать его в документ."""
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()

        # Возвращаем Document с текстом и метаданными
        return Document(
            page_content=text,
            metadata={"src": file_path, "type": "txt"}
        )

    def add_documents_from_files(self, file_paths: List[str]):
        """Обработать файлы и добавить их в ClickHouse."""
        documents = []
        for file_path in file_paths:
            if file_path.lower().endswith(".pdf"):
                documents.append(self.process_pdf(file_path))
            elif file_path.lower().endswith(".txt"):
                documents.append(self.process_txt(file_path))
            else:
                print(f"Не поддерживаемый формат файла: {file_path}")
                continue

        self.create_embs(documents)
