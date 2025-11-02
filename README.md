# Resume Processing API - FastAPI Application

A FastAPI application that accepts resume uploads, extracts candidate information using Hugging Face ML models, and stores data in Supabase and MongoDB.

## Prerequisites

- Python 3.8 or higher
- MongoDB database (local or cloud like MongoDB Atlas)
- Supabase account (for file storage)
- Hugging Face API token (optional, but recommended for Q&A features)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/arjunm369/KaStack-Arjun.git
cd KaStack-Arjun
```

### 2. Create and Activate Virtual Environment

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory by copying the example file:

```bash
cp .env.example .env
```

Edit the `.env` file and add your credentials:

- **SUPABASE_URL**: Your Supabase project URL (get from Supabase dashboard)
- **SUPABASE_KEY**: Your Supabase anon/public key
- **SUPABASE_BUCKET_NAME**: Storage bucket name (default: "resumes")
- **MONGODB_URL**: Your MongoDB connection string
- **MONGODB_DATABASE**: Database name (default: "resume_processor")
- **HUGGINGFACE_API_KEY**: Your Hugging Face API token (optional but recommended)

### 5. Run the Application

```bash
python run.py
```

Or directly with uvicorn:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 6. Access API

- **API Docs:** `http://localhost:8000/docs`
- **API Root:** `http://localhost:8000`

## API Endpoints

1. **POST** `/upload` - Upload resume (PDF/DOCX)
2. **GET** `/candidates` - List all candidates
3. **GET** `/candidate/{candidate_id}` - Get candidate details
4. **POST** `/ask/{candidate_id}` - Ask question about candidate

Use the interactive API docs at `http://localhost:8000/docs` to test all endpoints.

## Notes

- First run will download ML models (~500MB)
- Ensure MongoDB and Supabase are properly configured before running
- Hugging Face API key is optional but required for the Q&A endpoint to work properly
- API docs available at `/docs` endpoint

