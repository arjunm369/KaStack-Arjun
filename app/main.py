from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
from dotenv import load_dotenv

from app.services.supabase_service import SupabaseService
from app.services.mongodb_service import MongoDBService
from app.services.resume_processor import ResumeProcessor
from app.services.qa_service import QAService
from app.models.candidate import Candidate, CandidateSummary, QuestionRequest

load_dotenv()

app = FastAPI(title="Resume Processing API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase_service = SupabaseService()
mongodb_service = MongoDBService()
resume_processor = ResumeProcessor()
qa_service = QAService()


@app.get("/")
async def root():
    return {"message": "Resume Processing API", "status": "running"}


@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in [".pdf", ".docx"]:
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Only PDF and DOCX files are allowed."
            )
        
        file_content = await file.read()
        
        supabase_metadata = await supabase_service.upload_file(
            file_content, 
            file.filename
        )
        
        resume_text = await resume_processor.extract_text(file_content, file_ext)
        candidate_data = await resume_processor.process_resume(resume_text)
        
        candidate_data["candidate_id"] = supabase_metadata["id"]
        candidate_doc = await mongodb_service.save_candidate(candidate_data)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Resume uploaded and processed successfully",
                "candidate_id": candidate_doc["candidate_id"],
                "supabase_metadata": supabase_metadata,
                "extracted_data": candidate_data
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


@app.get("/candidates", response_model=List[CandidateSummary])
async def list_candidates():
    try:
        candidates = await mongodb_service.get_all_candidates_summary()
        return candidates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching candidates: {str(e)}")


@app.get("/candidate/{candidate_id}", response_model=Candidate)
async def get_candidate(candidate_id: str):
    try:
        candidate = await mongodb_service.get_candidate_by_id(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return candidate
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching candidate: {str(e)}")


@app.post("/ask/{candidate_id}")
async def ask_question(candidate_id: str, question: QuestionRequest):
    try:
        candidate = await mongodb_service.get_candidate_by_id(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        answer = await qa_service.answer_question(question.question, candidate)
        
        return JSONResponse(
            status_code=200,
            content={
                "candidate_id": candidate_id,
                "question": question.question,
                "answer": answer
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
