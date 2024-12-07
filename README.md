## Структура 
```
├───ml_service
│   docker-compose.yaml
│   Dockerfile
│   document.py
│   document_extract.py
│   llm_ollama.py
│   llm_transformers.py
│   main.py
│   requirements.txt
│   store.py
```

## Методы `class ML_service` main.py:

1. `__init__`:
* Настраивает соединение с ClickHouse через VectorStore.
* Загружает эмбеддинг-модель SentenceTransformer для генерации эмбеддингов.
* Подключается к API Ollama для работы с языковыми моделями.

2. `get_response(query, model_name, max_length, temperature, top_k, top_p)`:
Cоздаются и инициализируются:
* TransformerModel — модель для генерации текстов.
* VectorStore — хранилище векторных данных, использующее базу данных ClickHouse.
* SentenceTransformer — модель для векторизации текста

3. `get_stream_response(query, model_name, max_length, temperature, top_k, top_p)`:

* Получает список похожих документов через `VectorStore.retrieve_relevant_documents`
* Передает запрос и документы в Ollama для генерации стримингового ответа.
* Генерирует поэтапный поток текста (сначала части ответа, затем список ссылок на документы).

4. `add_documents_from_files` — Добавление документов в **ClickHouse**:
* Загружает файлы в базу данных ClickHouse с помощью метода add_documents_from_files из VectorStore.
* Файлы могут быть загружены в формате PDF, TXT или другие поддерживаемые форматы.

## Какие возможности есть у пользователя при взаимодействии с ML сервисом:
* Смена токенизатора
* Смена языковой модели
* Смена модели поиска эмбеддингов для раг пайплайна
* Подгрузка файлов (`*.pdf`, `*.txt`, `*.docx`, `*.html`) в базу знаний **clickhouse**
* Пользователь может добавлять системный промпт через nocode приложение  
 
## Запуск
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

5. Откройте страницу в браузере по адресу `http://0.0.0.0:8000/`


## API Documentation

### 1. **POST /respond_stream**
- **Описание**: Потоковый запрос для получения ответа от ML-сервиса с использованием RAG (Retrieval-Augmented Generation). Ответ генерируется частями и отправляется клиенту по мере готовности.
  
#### Запрос:
- **Тип запроса**: `POST`
- **URL**: `/respond_stream`
- **Тело запроса**:
    ```json
    {
      "body": "string",            // Основной текст запроса для генерации ответа
      "model_name": "string",      // (опционально) Название модели для использования
      "max_length": 150,           // (опционально) Максимальная длина ответа (в токенах)
      "temperature": 0.7,          // (опционально) Температура для генерации (степень случайности)
      "top_k": 50,                 // (опционально) Количество наиболее вероятных токенов для выбора
      "top_p": 0.9                // (опционально) Вероятностный порог для ядерного сэмплинга
    }
    ```
  
#### Ответ:
- **Тип ответа**: `text/plain`
- **Тело ответа**:
    - Ответ модели будет сгенерирован и отправлен клиенту частями (по мере готовности).
  
#### Пример:
- **Запрос**:
    ```json
    {
      "body": "Как мне улучшить свою продуктивность?",
      "model_name": "gpt-3",
      "max_length": 100,
      "temperature": 0.8,
      "top_k": 40,
      "top_p": 0.95
    }
    ```
- **Ответ** (поток):
    ```
    Чтобы повысить свою продуктивность, стоит начать с...
    Разделите задачи на более мелкие части, чтобы...
    ```

---

### 2. **POST /upload_file**
- **Описание**: Эндпоинт для загрузки файла (PDF или TXT) и сохранения его содержимого в ClickHouse для дальнейшего поиска и обработки.

#### Запрос:
- **Тип запроса**: `POST`
- **URL**: `/upload_file`
- **Тело запроса**:
    - Загружаемый файл должен быть отправлен в теле запроса.

#### Ответ:
- **Тип ответа**: `application/json`
- **Тело ответа**:
    ```json
    {
      "message": "File <filename> uploaded and processed successfully"
    }
    ```
    где `<filename>` — это имя загруженного файла.

#### Пример:
- **Запрос**: Загрузка файла `document.pdf`
  
- **Ответ**:
    ```json
    {
      "message": "File document.pdf uploaded and processed successfully"
    }
    ```

---

### 3. **GET /get_document/**
- **Описание**: Эндпоинт для получения документа по его имени из базы данных.

#### Запрос:
- **Тип запроса**: `GET`
- **URL**: `/get_document/`
- **Параметры запроса**:
    - `doc_name`: Имя документа, который требуется получить.

#### Ответ:
- **Тип ответа**: `application/json`
- **Тело ответа**:
    ```json
    {
      "doc_name": "string",       // Название документа
      "metadata": {               // Метаинформация документа (например, дата создания, автор)
        "key": "value"
      },
      "text": "string"            // Текст документа
    }
    ```
  
#### Пример:
- **Запрос**:
    ```
    GET /get_document/?doc_name=example_document
    ```
  
- **Ответ**:
    ```json
    {
      "doc_name": "example_document",
      "metadata": {
        "author": "John Doe",
        "created_at": "2024-11-28"
      },
      "text": "This is an example document content."
    }
    ```

---

### 4. **DELETE /delete_document/**
- **Описание**: Эндпоинт для удаления документа по его имени из базы данных.

#### Запрос:
- **Тип запроса**: `DELETE`
- **URL**: `/delete_document/`
- **Параметры запроса**:
    - `doc_name`: Имя документа, который требуется удалить.

#### Ответ:
- **Тип ответа**: `application/json`
- **Тело ответа**:
    ```json
    {
      "message": "Document '<doc_name>' deleted successfully"
    }
    ```
    где `<doc_name>` — это имя удаленного документа.

#### Пример:
- **Запрос**:
    ```
    DELETE /delete_document/?doc_name=example_document
    ```

- **Ответ**:
    ```json
    {
      "message": "Document 'example_document' deleted successfully"
    }
    ```

---

### Общие рекомендации:
- **Ответы с ошибками**:
  - В случае ошибок сервер возвращает статус 500 с сообщением "Internal Server Error".
  - В случае ошибки "Не найден документ" сервер возвращает статус 404 с сообщением "Document not found".
