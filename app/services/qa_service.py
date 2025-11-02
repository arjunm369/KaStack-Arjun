import os
import requests
from typing import Dict, Any
from app.models.candidate import Candidate


class QAService:
    def __init__(self):
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.api_url = os.getenv(
            "HUGGINGFACE_API_URL",
            "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
        )
        
        self.qa_model_url = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
        
        if not self.hf_api_key:
            print("Warning: HUGGINGFACE_API_KEY not set. Q&A endpoint will not work properly.")
    
    async def answer_question(self, question: str, candidate: Candidate) -> str:
        try:
            context = self._format_candidate_context(candidate)
            
            prompt = f"""Based on the following candidate information, answer the question.

Candidate Information:
{context}

Question: {question}

Answer:"""
            
            headers = {
                "Authorization": f"Bearer {self.hf_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": {
                    "question": question,
                    "context": context
                }
            }
            
            try:
                response = requests.post(
                    self.qa_model_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, dict) and "answer" in result:
                        return result["answer"]
                    elif isinstance(result, list) and len(result) > 0:
                        return result[0].get("answer", "Unable to generate answer.")
                
                elif response.status_code == 503:
                    print("Q&A model is loading, falling back to text generation...")
                    return await self._fallback_answer(question, context, headers)
                else:
                    print(f"Q&A model error: {response.status_code}, falling back...")
                    return await self._fallback_answer(question, context, headers)
            
            except Exception as e:
                print(f"Error with Q&A model: {e}, using fallback...")
                return await self._fallback_answer(question, context, headers)
        
        except Exception as e:
            raise Exception(f"Error generating answer: {str(e)}")
    
    async def _fallback_answer(self, question: str, context: str, headers: Dict) -> str:
        try:
            gen_model_url = "https://api-inference.huggingface.co/models/gpt2"
            
            prompt = f"Context: {context[:1000]}\n\nQuestion: {question}\n\nAnswer:"
            
            payload = {"inputs": prompt, "parameters": {"max_length": 150, "temperature": 0.7}}
            
            response = requests.post(
                gen_model_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                    if "Answer:" in generated_text:
                        answer = generated_text.split("Answer:")[-1].strip()
                        return answer[:200]
            
            return self._rule_based_answer(question, context)
        
        except Exception as e:
            print(f"Fallback error: {e}")
            return self._rule_based_answer(question, context)
    
    def _rule_based_answer(self, question: str, context: str) -> str:
        question_lower = question.lower()
        
        if "graduation" in question_lower or "graduate" in question_lower or "degree" in question_lower:
            if "end_date" in context or "202" in context:
                import re
                dates = re.findall(r"20\d{2}", context)
                if dates:
                    return f"The candidate completed their graduation in {dates[-1]}."
        
        if "experience" in question_lower or "work" in question_lower:
            exp_count = context.lower().count("title") or context.lower().count("company")
            return f"The candidate has {exp_count} work experience entries."
        
        if "skills" in question_lower:
            return "The candidate's skills are listed in their profile. Please check the candidate details for the complete list."
        
        return "Based on the candidate's profile, the information is available. Please refer to the candidate details for specific information."
    
    def _format_candidate_context(self, candidate: Candidate) -> str:
        context_parts = []
        
        if candidate.introduction:
            context_parts.append(f"Introduction: {candidate.introduction}")
        
        if candidate.education:
            context_parts.append("Education:")
            for edu in candidate.education:
                degree = edu.degree if edu.degree else 'N/A'
                institution = edu.institution if edu.institution else 'N/A'
                edu_str = f"  - {degree} from {institution}"
                if edu.end_date:
                    edu_str += f" (completed {edu.end_date})"
                context_parts.append(edu_str)
        
        if candidate.experience:
            context_parts.append("Experience:")
            for exp in candidate.experience:
                title = exp.title if exp.title else 'N/A'
                company = exp.company if exp.company else 'N/A'
                exp_str = f"  - {title} at {company}"
                if exp.start_date and exp.end_date:
                    exp_str += f" ({exp.start_date} - {exp.end_date})"
                context_parts.append(exp_str)
        
        if candidate.skills:
            context_parts.append(f"Skills: {', '.join(candidate.skills[:20])}")
        
        if candidate.certifications:
            context_parts.append(f"Certifications: {', '.join(candidate.certifications)}")
        
        return "\n".join(context_parts)
