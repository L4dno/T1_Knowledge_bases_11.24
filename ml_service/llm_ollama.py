from typing import Iterator
from store import result_document
from ollama import Client

class Ollama:
    def __init__(
        self,
        uri: str = "http://localhost:11434/api/generate",
        template: str | None = None,
    ) -> None:
        self.client = Client(host=uri)
        self.template = (
            template
            or """Отвечай только на русском. Если пишешь на другом языке, переводи его на русский.
Если не знаешь ответа, скажи: "Затрудняюсь ответить на этот вопрос", не пробуй угадывать.

Context:
источник {document_name1}:
{context1}

источник {document_name2}:
{context2}

источник {document_name3}:
{context3}

Вопрос: {question} на русском языке. Ответь на вопрос основываясь на данных документах
Развернутый ответ:
"""
        )

    def _get_prompt(self, query: str, docs: list[result_document]) -> str:
        """Формирование prompt для языковой модели."""
        context = "\n\n".join(
            f"Контекст {i+1}:\n{doc.text}\nИсточник: {doc.metadata}" 
            for i, doc in enumerate(docs[:3])
        )
        return f"{self.template}\n\n{context}\n\nВопрос: {query}"

    def get_response(self, query: str, model_name: str | None = None) -> tuple[str, str]:
        """Возвращает ответ и контекст от Ollama модели"""
        docs = self.retrieve_relevant_documents(query, k=3)  # Получаем документы
        return self.get_model_response(query, docs, model_name)

    def get_model_response(self, query: str, docs: list[result_document], model_name: str | None) -> tuple[str, str]:
        """Получаем ответ от модели Ollama"""
        prompt = self._get_prompt(query, docs)
        response = self.client.chat(
            model=model_name or "default_model_name",  # Используем имя модели, если оно передано, иначе - дефолт
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0},
        )
        return response["message"]["content"], prompt

    def get_stream_response(self, query: str, docs: list[result_document], model_name: str) -> Iterator[str]:
        """Получение потокового ответа."""
        prompt = self._get_prompt(query, docs)
        stream = self.client.chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0},
            stream=True,
        )
        for chunk in stream:
            yield chunk["message"]["content"]

