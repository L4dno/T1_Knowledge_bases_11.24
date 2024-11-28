from typing import Iterator
from store import result_document
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os 
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
huggingface_access_token = os.getenv('huggingface_access_token')


class TransformerModel:
    def __init__(
        self,
        model_name: str = "gemma2",  # по умолчанию используем GPT-2, но модель может изменяться
        template: str | None = None,
        hugging_face_api_token: str | None = huggingface_access_token,
        max_length: int | None = 150,
        num_return_sequences: int | None = 1,
        no_repeat_ngram_size: int | None = 2,
        top_p: float | None = 0.9,
        top_k: int | None = 50,
        temperature: float | None = 0.7,
        return_dict_in_generate: bool | None = True,
        output_scores: bool | None = True,
    ) -> None:
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, token = hugging_face_api_token)

        self.model = AutoModelForCausalLM.from_pretrained(self.model_name, token = hugging_face_api_token)
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
        self.max_length = max_length
        self.num_return_sequences = num_return_sequences
        self.no_repeat_ngram_size = no_repeat_ngram_size
        self.top_p = top_p
        self.top_k = top_k
        self.temperature = temperature
        self.return_dict_in_generate = return_dict_in_generate
        self.output_scores = output_scores

    def _get_prompt(self, query: str, docs: list[result_document]) -> str:
        """Формирование prompt для языковой модели."""
        context = "\n\n".join(
            f"Контекст {i+1}:\n{doc.text}\nИсточник: {doc.metadata}" 
            for i, doc in enumerate(docs[:3])
        )
        return f"{self.template}\n\n{context}\n\nВопрос: {query}"

    def get_response(self, query: str, model_name: str | None = None) -> tuple[str, str]:
        """Возвращает ответ и контекст от модели transformers"""
        docs = self.retrieve_relevant_documents(query, k=3)  # Получаем документы
        return self.get_model_response(query, docs, model_name)

    def get_model_response(self, query: str, docs: list[result_document], model_name: str | None) -> tuple[str, str]:
        """Получаем ответ от модели transformers"""
        prompt = self._get_prompt(query, docs)
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, padding=True)

        # Генерация текста
        outputs = self.model.generate(
            **inputs,
            max_length=self.max_length,
            num_return_sequences=self.num_return_sequences,
            no_repeat_ngram_size=self.no_repeat_ngram_size,
            top_p=self.top_p,
            top_k=self.top_k,
            temperature=self.temperature
        )


        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text, prompt

    def get_stream_response(self, query: str, docs: list[result_document], model_name: str) -> Iterator[str]:
        """Потоковое получение ответа."""
        prompt = self._get_prompt(query, docs)
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, padding=True)

        # Для потока мы будем генерировать ответ по частям
        output_ids = self.model.generate(
            **inputs,
            max_length=self.max_length,
            num_return_sequences=self.num_return_sequences,
            no_repeat_ngram_size=self.no_repeat_ngram_size,
            top_p=self.top_p,
            top_k=self.top_k,
            temperature=self.temperature,
            return_dict_in_generate=self.return_dict_in_generate,
            output_scores=self.output_scores
        )


        # Генерация и пост-обработка ответа по частям
        generated_text = self.tokenizer.decode(output_ids.sequences[0], skip_special_tokens=True)
        for part in generated_text.split("\n"):
            yield part
