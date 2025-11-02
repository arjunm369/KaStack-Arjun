# Resume Processing API - FastAPI Application

A FastAPI application that accepts resume uploads, extracts candidate information using Hugging Face ML models, and stores data in Supabase and MongoDB.



(VS Code)

### 1. Create and Activate Virtual Environment

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

python run.py
Or
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000


### 2. Access API

- **API Docs:** `http://localhost:8000/docs`
- **API Root:** `http://localhost:8000`

## API Endpoints

1. **POST** `/upload` - Upload resume (PDF/DOCX)
2. **GET** `/candidates` - List all candidates
3. **GET** `/candidate/{candidate_id}` - Get candidate details
4. **POST** `/ask/{candidate_id}` - Ask question about candidate

Use the interactive API docs at `http://localhost:8000/docs` to test all endpoints.

- `.env` file is already configured with credentials
- First run downloads ML models (~500MB)
- API docs available at `/docs` endpoint


