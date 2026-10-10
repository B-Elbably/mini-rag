## mini-rag

This is a minimal FastAPI implementation of a retrieval-augmented generation
(RAG) application for processing text and PDF files.

## Requirements

- Python 3.8+
- Miniconda or another Python environment manager
- Docker and Docker Compose
- An OpenAI API key

## Setup

1. Clone the repository and enter the project directory.
2. Create and activate the conda environment:

   ```bash
   conda create -n mini-rag python=3.8
   conda activate mini-rag
   ```

3. Install the Python dependencies:

   ```bash
   cd src
   pip install -r requirements.txt
   ```

4. Create `src/.env` from `src/.env.example` and set the application values,
   especially `OPENAI_API_KEY`.

5. Create `docker/.env` from `docker/.env.example` and set the MongoDB root
   username and password.

## Start MongoDB

From the `docker` directory, start MongoDB:

```bash
cd docker
docker compose up -d
```

To stop it:

```bash
docker compose down
```

## Run the API

From the `src` directory:

```bash
cd src
uvicorn main:app --reload
```

The API is available at <http://127.0.0.1:8000>. Interactive API
documentation is available at <http://127.0.0.1:8000/docs>.

## Main endpoints

- `GET /api/v1/` - Check that the API is running.
- `POST /api/v1/data/upload/{project_id}` - Upload a text or PDF file.
- `POST /api/v1/data/process/{project_id}` - Split an uploaded file into
  chunks and store them in MongoDB.

Example upload:

```bash
curl -X POST \
  -F "file=@path/to/file.pdf" \
  http://127.0.0.1:8000/api/v1/data/upload/demo
```

Example processing request:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"file_id":"<uploaded-file-id>.pdf","chunk_size":100,"overlap_size":20,"do_reset":0}' \
  http://127.0.0.1:8000/api/v1/data/process/demo
```

The `file_id` must match the complete filename returned by the upload request.

## Configuration

The most important settings are defined in `src/.env`:

- `OPENAI_API_KEY` - API key used by the application.
- `FILE_ALLOWED_EXTENSIONS` - Allowed MIME types (`text/plain` and
  `application/pdf` by default).
- `FILE_MAX_SIZE_MB` - Maximum upload size.
- `FILE_DEFAULT_CHUNK_SIZE` - Upload read-buffer size.
- `MONGODB_URL` and `MONGODB_DATABASE` - MongoDB connection settings.

Do not commit `src/.env`, `docker/.env`, or API keys to version control. Use
the example files as templates for local configuration.