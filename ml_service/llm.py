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
Если не знаешь ответа, скажи, что не знаешь ответа, не пробуй угадывать.
"""
        )

    def _get_prompt(self, query: str, docs: list[result_document]) -> str:
        """Формирование prompt для языковой модели."""
        context = "\n\n".join(
            f"Контекст {i+1}:\n{doc.text}\nИсточник: {doc.metadata}"
            for i, doc in enumerate(docs[:3])
        )
        return f"{self.template}\n\n{context}\n\nВопрос: {query}"

    def get_response(self, query: str, docs: list[result_document], model_name: str) -> tuple[str, str]:
        """Получение синхронного ответа."""
        prompt = self._get_prompt(query, docs)
        response = self.client.chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0},
        )
        return response["message"]["content"], "Ссылки:\n" + "\n".join([doc.metadata for doc in docs])

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
