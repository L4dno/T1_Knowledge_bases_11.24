from typing import Literal, Any, List, Optional
from pydantic import BaseModel, Field
import logging

log = logging.getLogger(__name__)

class Document(BaseModel):
    """Класс для хранения текста и метаданных."""

    page_content: str
    """Текст документа."""
    metadata: dict = Field(default_factory=lambda: {"src": ""})
    """Метаданные (например, источник файла)."""
    type: Literal["Document"] = "Document"

    def __init__(self, page_content: str, **kwargs: Any) -> None:
        """Инициализация с поддержкой передачи текста как аргумента."""
        super().__init__(page_content=page_content, **kwargs)

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Сериализуемость для LangChain."""
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Получение пространства имен для интеграции с LangChain."""
        return ["langchain", "schema", "document"]

    def get_metadata(self, key: str) -> Optional[Any]:
        """
        Получить значение определенного ключа из метаданных.
        :param key: Ключ для извлечения.
        :return: Значение ключа, если существует.
        """
        return self.metadata.get(key)

    def update_metadata(self, key: str, value: Any) -> None:
        """
        Обновить метаданные документа.
        :param key: Ключ для обновления.
        :param value: Значение, которое нужно установить.
        """
        self.metadata[key] = value
        log.info(f"Metadata updated: {key} = {value}")

    def delete_document(self, vector_store, doc_name: str) -> bool:
        """
        Удалить документ из базы знаний.
        :param vector_store: Экземпляр хранилища векторов.
        :param doc_name: Имя документа для удаления.
        :return: True, если успешно, иначе False.
        """
        try:
            query_check = f"SELECT COUNT(*) FROM vector_search WHERE DocName = '{doc_name}'"
            result = vector_store.client.execute(query_check)

            if not result or result[0][0] == 0:
                log.error(f"Document '{doc_name}' not found in the vector store.")
                return False

            query_delete = f"ALTER TABLE vector_search DELETE WHERE DocName = '{doc_name}'"
            vector_store.client.execute(query_delete)
            log.info(f"Document '{doc_name}' deleted successfully.")
            return True
        except Exception as e:
            log.error(f"Error deleting document '{doc_name}': {e}")
            return False
