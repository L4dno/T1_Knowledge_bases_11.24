from typing import Literal, Any, List
from pydantic import BaseModel, Field

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
