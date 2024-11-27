from typing import Any, Iterator, Mapping
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
Если не знаешь ответа, скажи что не знаешь ответа, не пробуй отвечать.
"""
        )

    def _get_prompt(self, query: str, docs: list[result_document]) -> str:
        return self.template.format(
            context1=docs[0].text if len(docs) > 0 else "",
            url1=docs[0].metadata if len(docs) > 0 else "",
            context2=docs[1].text if len(docs) > 1 else "",
            url2=docs[1].metadata if len(docs) > 1 else "",
            context3=docs[2].text if len(docs) > 2 else "",
            url3=docs[2].metadata if len(docs) > 2 else "",
            question=query,
        )

    def get_response(self, query: str, docs: list[result_document], model_name: str) -> tuple[str, str]:
        """
        Получить синхронный ответ от указанной модели Ollama.
        """
        prompt = self._get_prompt(query, docs)
        response = self.client.chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0},
        )
        return response["message"]["content"], "Ссылки:\n" + "\n".join([doc.metadata for doc in docs])  # type: ignore

    def get_stream_response(
        self, query: str, docs: list[result_document], model_name: str
    ) -> Iterator[str]:
        """
        Получить потоковый ответ от указанной модели Ollama.
        """
        prompt = self._get_prompt(query, docs)
        stream = self.client.chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0},
            stream=True,
        )
        for chunk in stream:
            yield chunk["message"]["content"]  # type: ignore
