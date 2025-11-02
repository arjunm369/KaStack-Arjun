import os
from datetime import datetime
from supabase import create_client, Client
from typing import Dict


class SupabaseService:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.bucket_name = os.getenv("SUPABASE_BUCKET_NAME", "resumes")
    
    async def upload_file(self, file_content: bytes, filename: str) -> Dict:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"{timestamp}_{filename}"
        
        try:
            response = self.supabase.storage.from_(self.bucket_name).upload(
                file_path,
                file_content,
                file_options={"content-type": "application/octet-stream"}
            )
        except Exception as e:
            raise Exception(f"Error uploading file to Supabase storage: {str(e)}")
        
        try:
            file_url = self.supabase.storage.from_(self.bucket_name).get_public_url(file_path)
        except Exception as e:
            file_url = None
            print(f"Warning: Could not generate public URL: {e}")
        
        metadata = {
            "id": file_path,
            "filename": filename,
            "file_path": file_path,
            "file_url": file_url,
            "upload_time": datetime.now().isoformat(),
            "file_size": len(file_content)
        }
        
        try:
            db_response = self.supabase.table("resume_uploads").insert(metadata).execute()
            if db_response.data:
                metadata["id"] = db_response.data[0].get("id", file_path)
        except Exception as e:
            print(f"Note: Could not save to Supabase database table (RLS or table missing): {str(e)}")
            print("This is non-critical - file upload succeeded and data will be stored in MongoDB.")
        
        return metadata
