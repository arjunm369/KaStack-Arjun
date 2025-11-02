import os
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.candidate import Candidate, CandidateSummary, Education, Experience


class MongoDBService:
    def __init__(self):
        mongodb_url = os.getenv("MONGODB_URL")
        if not mongodb_url:
            raise ValueError("MONGODB_URL must be set in environment variables")
        
        self.client = AsyncIOMotorClient(mongodb_url)
        self.db = self.client.get_database(os.getenv("MONGODB_DATABASE", "resume_processor"))
        self.collection = self.db.get_collection("candidates")
    
    async def save_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            candidate_doc = {
                "candidate_id": candidate_data["candidate_id"],
                "education": candidate_data.get("education", []),
                "experience": candidate_data.get("experience", []),
                "skills": candidate_data.get("skills", []),
                "hobbies": candidate_data.get("hobbies", []),
                "certifications": candidate_data.get("certifications", []),
                "projects": candidate_data.get("projects", []),
                "introduction": candidate_data.get("introduction", "")
            }
            
            result = await self.collection.update_one(
                {"candidate_id": candidate_doc["candidate_id"]},
                {"$set": candidate_doc},
                upsert=True
            )
            
            return candidate_doc
        
        except Exception as e:
            raise Exception(f"Error saving to MongoDB: {str(e)}")
    
    async def get_candidate_by_id(self, candidate_id: str) -> Optional[Candidate]:
        try:
            doc = await self.collection.find_one({"candidate_id": candidate_id})
            if not doc:
                return None
            
            if "_id" in doc:
                del doc["_id"]
            
            return Candidate(**doc)
        
        except Exception as e:
            raise Exception(f"Error fetching candidate: {str(e)}")
    
    async def get_all_candidates_summary(self) -> List[CandidateSummary]:
        try:
            cursor = self.collection.find({})
            candidates = await cursor.to_list(length=None)
            
            summaries = []
            for doc in candidates:
                if "_id" in doc:
                    del doc["_id"]
                
                summary = CandidateSummary(
                    candidate_id=doc.get("candidate_id", ""),
                    introduction=doc.get("introduction", "")[:200],
                    skills=doc.get("skills", [])[:10],
                    experience_count=len(doc.get("experience", [])),
                    education_count=len(doc.get("education", []))
                )
                summaries.append(summary)
            
            return summaries
        
        except Exception as e:
            raise Exception(f"Error fetching candidates summary: {str(e)}")
