# TrustWise

A simple dashboard for text analysis featuring Vectara hallucination scoring and gibberish detection capabilities.

## Tech Stack

### Backend

- FastAPI (Python web framework)
- PostgreSQL (Database)
- HuggingFace Transformers
- PyTorch
- Python 3.13

### Frontend

- Vue.js 3
- TypeScript
- Vite
- ApexCharts for data visualization
- Axios for API communication

Note: The first query to each model may be slow as the models are downloaded from Huggingface.

## Getting Started

### Docker Compose (Recommended)

The easiest way to run the application is using Docker Compose:

```bash
docker compose up
```

This will start:

- Frontend: <http://localhost:8080>
- Backend API: <http://localhost:8000>
- PostgreSQL: localhost:5432

Database credentials:

- Database: trustwise_db
- Username: postgres
- Password: password

### Database Initialization

Important: The database needs to be initialized before using the application.

You may directly run the script from the host machine(will connect at localhost:5432) by doing `python db_init.py` or you can modify the database credentials to use environment databaseb url defined in docker-compose.yml and after starting the containers with `docker compose up`, run:

```bash
docker compose exec api python db_init.py
```

This command will:

1. Connect to the PostgreSQL database
2. Create necessary tables and schemas
3. Set up initial database structure

### API Documentation

The API documentation is available via Swagger UI at:
<http://localhost:8000/docs>

Available endpoints:

- POST `/predict/vectara`: Calculate similarity scores between two texts
- POST `/predict/gibberish`: Detect if text is gibberish
- GET `/results/vectara`: Retrieve all Vectara prediction results
- GET `/results/gibberish`: Retrieve all gibberish detection results

### Standalone Setup

#### Backend

```bash
cd api
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

## Development

The project uses Docker Compose with development mode enabled:

- Backend files are synced in real-time
- Hot-reload is enabled for both frontend and backend
- Node modules are persisted in a Docker volume

## Environment Variables

Backend environment variables (set in docker-compose.yml):

- `DATABASE_URL`: PostgreSQL connection string
