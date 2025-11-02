import os
import re
from typing import Dict, Any, List
import PyPDF2
import docx
from io import BytesIO
from transformers import pipeline


class ResumeProcessor:
    def __init__(self):
        self.ner_model = None
        self.text_classifier = None
        
        try:
            self.ner_model = pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple"
            )
        except Exception as e:
            print(f"Warning: Could not load NER model: {e}. Using basic extraction.")
    
    async def extract_text(self, file_content: bytes, file_ext: str) -> str:
        try:
            if file_ext == ".pdf":
                pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
            
            elif file_ext == ".docx":
                doc = docx.Document(BytesIO(file_content))
                text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                return text
            
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
        
        except Exception as e:
            raise Exception(f"Error extracting text: {str(e)}")
    
    async def process_resume(self, resume_text: str) -> Dict[str, Any]:
        try:
            entities = []
            if self.ner_model:
                try:
                    chunks = [resume_text[i:i+512] for i in range(0, len(resume_text), 512)]
                    for chunk in chunks[:5]:
                        chunk_entities = self.ner_model(chunk)
                        entities.extend(chunk_entities)
                except Exception as e:
                    print(f"NER processing error: {e}")
            
            candidate_data = {
                "education": self._extract_education(resume_text),
                "experience": self._extract_experience(resume_text),
                "skills": self._extract_skills(resume_text),
                "hobbies": self._extract_hobbies(resume_text),
                "certifications": self._extract_certifications(resume_text),
                "projects": self._extract_projects(resume_text),
                "introduction": self._extract_introduction(resume_text)
            }
            
            return candidate_data
        
        except Exception as e:
            raise Exception(f"Error processing resume: {str(e)}")
    
    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        education = []
        
        degree_patterns = [
            r"(?i)(Bachelor|B\.S\.|B\.A\.|Master|M\.S\.|M\.A\.|MBA|PhD|Ph\.D\.|Doctorate)",
            r"(?i)(Bachelor of|Master of|Doctor of)"
        ]
        
        edu_section = self._extract_section(text, ["EDUCATION", "ACADEMIC", "QUALIFICATION"])
        
        lines = edu_section.split("\n")
        current_edu = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_edu:
                    education.append(current_edu)
                    current_edu = {}
                continue
            
            for pattern in degree_patterns:
                if re.search(pattern, line):
                    if "degree" not in current_edu:
                        current_edu["degree"] = line
                    break
            
            if re.search(r"(?i)(university|college|institute|school)", line):
                if "institution" not in current_edu:
                    current_edu["institution"] = line
            
            dates = re.findall(r"\d{4}", line)
            if dates:
                if "end_date" not in current_edu and len(dates) > 0:
                    current_edu["end_date"] = dates[-1]
                if "start_date" not in current_edu and len(dates) > 0:
                    current_edu["start_date"] = dates[0]
        
        if current_edu:
            education.append(current_edu)
        
        return education[:5]
    
    def _extract_experience(self, text: str) -> List[Dict[str, Any]]:
        experience = []
        
        exp_section = self._extract_section(text, ["EXPERIENCE", "WORK", "EMPLOYMENT", "PROFESSIONAL"])
        
        lines = exp_section.split("\n")
        current_exp = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_exp:
                    experience.append(current_exp)
                    current_exp = {}
                continue
            
            if re.search(r"(?i)(engineer|developer|manager|analyst|consultant|specialist|lead|senior|junior)", line):
                if "title" not in current_exp:
                    current_exp["title"] = line
            
            if re.search(r"(?i)(inc\.|ltd\.|corp\.|company|technologies|systems)", line):
                if "company" not in current_exp:
                    current_exp["company"] = line
            
            dates = re.findall(r"(\d{4}|\w+\s+\d{4})", line)
            if dates:
                if "end_date" not in current_exp:
                    current_exp["end_date"] = dates[-1] if len(dates) > 1 else None
                if "start_date" not in current_exp:
                    current_exp["start_date"] = dates[0]
            
            if line.startswith(("•", "-", "*")) or re.match(r"^\d+\.", line):
                if "description" not in current_exp:
                    current_exp["description"] = line
                else:
                    current_exp["description"] += " " + line
        
        if current_exp:
            experience.append(current_exp)
        
        return experience[:10]
    
    def _extract_skills(self, text: str) -> List[str]:
        skills = []
        
        skill_keywords = [
            "Python", "Java", "JavaScript", "SQL", "MongoDB", "PostgreSQL",
            "FastAPI", "React", "Node.js", "Docker", "AWS", "Git", "Linux",
            "Machine Learning", "Data Science", "TensorFlow", "PyTorch",
            "Pandas", "NumPy", "scikit-learn", "Kubernetes", "Redis",
            "Elasticsearch", "GraphQL", "REST API", "Microservices"
        ]
        
        skills_section = self._extract_section(text, ["SKILLS", "TECHNICAL SKILLS", "COMPETENCIES"])
        
        text_to_search = skills_section if skills_section else text
        
        for skill in skill_keywords:
            if re.search(rf"\b{re.escape(skill)}\b", text_to_search, re.IGNORECASE):
                if skill not in skills:
                    skills.append(skill)
        
        lines = skills_section.split("\n") if skills_section else []
        for line in lines:
            items = re.split(r"[,;•\-]", line)
            for item in items:
                item = item.strip()
                if len(item) > 2 and len(item) < 50:
                    if item not in skills and not re.search(r"^(skills|technical|proficient)", item, re.I):
                        skills.append(item)
        
        return skills[:30]
    
    def _extract_hobbies(self, text: str) -> List[str]:
        hobbies = []
        
        hobbies_section = self._extract_section(text, ["HOBBIES", "INTERESTS", "ACTIVITIES"])
        
        if hobbies_section:
            lines = hobbies_section.split("\n")
            for line in lines:
                items = re.split(r"[,;•\-]", line)
                for item in items:
                    item = item.strip()
                    if len(item) > 2 and len(item) < 50:
                        hobbies.append(item)
        
        return hobbies[:10]
    
    def _extract_certifications(self, text: str) -> List[str]:
        certifications = []
        
        cert_section = self._extract_section(text, ["CERTIFICATIONS", "CERTIFICATES", "LICENSES"])
        
        if cert_section:
            lines = cert_section.split("\n")
            for line in lines:
                if re.search(r"(?i)(certified|certificate|certification|license|credential)", line):
                    certifications.append(line.strip())
        
        return certifications[:10]
    
    def _extract_projects(self, text: str) -> List[Dict[str, Any]]:
        projects = []
        
        project_section = self._extract_section(text, ["PROJECTS", "PROJECT"])
        
        lines = project_section.split("\n") if project_section else []
        current_project = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_project:
                    projects.append(current_project)
                    current_project = {}
                continue
            
            if "name" not in current_project and len(line) < 100:
                current_project["name"] = line
            
            if line.startswith(("•", "-", "*")):
                if "description" not in current_project:
                    current_project["description"] = line
                else:
                    current_project["description"] += " " + line
        
        if current_project:
            projects.append(current_project)
        
        return projects[:10]
    
    def _extract_introduction(self, text: str) -> str:
        intro_section = self._extract_section(text, ["SUMMARY", "OBJECTIVE", "INTRODUCTION", "PROFILE", "ABOUT"])
        
        if intro_section:
            paragraphs = intro_section.split("\n\n")
            if paragraphs:
                return paragraphs[0][:500]
        
        lines = text.split("\n")[:5]
        return " ".join([line.strip() for line in lines if line.strip()])[:500]
    
    def _extract_section(self, text: str, section_names: List[str]) -> str:
        text_upper = text.upper()
        
        for section_name in section_names:
            pattern = rf"{section_name}[:\s]*(.*?)(?=\n[A-Z]{{2,}}\s*[:\n]|$)"
            match = re.search(pattern, text_upper, re.DOTALL | re.IGNORECASE)
            if match:
                start_pos = match.start()
                next_section = re.search(r"\n[A-Z]{2,}\s*[:\n]", text[start_pos + len(section_name):])
                if next_section:
                    end_pos = start_pos + len(section_name) + next_section.start()
                else:
                    end_pos = len(text)
                return text[start_pos:end_pos]
        
        return ""
