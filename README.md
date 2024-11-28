## Методы `class ML_service` main.py:

`__init__`:
* Настраивает соединение с ClickHouse через VectorStore.
* Загружает эмбеддинг-модель SentenceTransformer для генерации эмбеддингов.
* Подключается к API Ollama для работы с языковыми моделями.

`get_response(query, model_name)`:
* Получает список похожих документов через VectorStore.search_similarity (поиск в ClickHouse).
* Передает запрос и документы в Ollama для генерации ответа.
* Возвращает синхронный ответ в формате (текст ответа, контекст).

`get_stream_response(query, model_name)`:
* Получает список похожих документов через VectorStore.search_similarity.
* Передает запрос и документы в Ollama для генерации стримингового ответа.
* Генерирует поэтапный поток текста (сначала части ответа, затем список ссылок на документы).


запуск 
1. Склонируйте репозиторий
```bash
git clone https://github.com/L4dno/T1_Knowledge_bases_11.24.git
``` 

2. Откройте консоль и перейдите в директорию ML сервиса
```bash
cd ml_service
```

3. Введите эту команду
```bash
docker-compose up --build
```

4. Введите в консоль
```bash
uvicorn main:app --reload
```

4. Откройте страницу в браузере по адресу `http://0.0.0.0:8000/`