from typing import Dict, List
import os
from dataclasses import dataclass
import google.generativeai as genai
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
import PyPDF2
import docx
import io
from .db_connect import DatabaseConnect

load_dotenv()  # Add this at the top of your file

@dataclass
class LLMConfig:
    provider: str
    api_key: str
    model: str = None

class LLMConnect:
    def __init__(self, config: LLMConfig):
        self.config = config
        self._initialize_client()
        self.db = DatabaseConnect()
        
        # Check database connection
        db_status = self.db.check_connection()
        if db_status["status"] != "connected":
            print(f"Warning: Database connection failed - {db_status['error']}")

    def _initialize_client(self):
        if self.config.provider.lower() == "gemini":
            genai.configure(api_key=self.config.api_key)
            self.client = genai.GenerativeModel('gemini-2.0-flash')
        elif self.config.provider.lower() == "openai":
            self.client = OpenAI(api_key=self.config.api_key)
        elif self.config.provider.lower() == "grok":
            print("Using Grok API")
            self.client = OpenAI(
                api_key=os.getenv("XAI_API_KEY"),
                base_url="https://api.x.ai/v1"
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.provider}")

    def _process_file(self, file) -> str:
        """Process different file types and return content as text"""
        file_content = ""
        try:
            if file.name.endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
                for page in pdf_reader.pages:
                    file_content += page.extract_text() + "\n"
            elif file.name.endswith('.txt'):
                file_content = file.getvalue().decode('utf-8')
            elif file.name.endswith(('.doc', '.docx')):
                doc = docx.Document(io.BytesIO(file.read()))
                file_content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            return file_content
        except Exception as e:
            return f"Error processing file: {str(e)}"

    def format_response_with_bullets(self, text: str) -> str:
        """Convert response into bullet points if not already formatted"""
        lines = text.strip().split('\n')
        if not any(line.strip().startswith('•') for line in lines):
            # Split into sentences and create bullet points
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            return '\n'.join([f'• {s}.' for s in sentences])
        return text

    def generate_response(self, messages: List[Dict[str, str]], uploaded_file=None, user_email: str = None) -> str:
        try:
            # Format the prompt to request concise, bullet-pointed responses
            prompt_suffix = "\nPlease provide a brief response in bullet points with the most relevant information."
            
            # Store original query before modification
            original_query = messages[-1]['content']
            
            if uploaded_file:
                file_content = self._process_file(uploaded_file)
                context = f"Context from file '{uploaded_file.name}':\n{file_content}\n\nQuestion: {original_query}{prompt_suffix}"
                messages[-1]['content'] = context
            else:
                messages[-1]['content'] = original_query + prompt_suffix

            # Generate response
            if self.config.provider.lower() == "gemini":
                response = self.client.generate_content([
                    msg["content"] for msg in messages
                ])
                response_text = response.text
                
            elif self.config.provider.lower() == "openai":
                response = self.client.chat.completions.create(
                    model=self.config.model or "gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7
                )
                response_text = response.choices[0].message.content
            elif self.config.provider.lower() == "grok":
                response = self.client.chat.completions.create(
                model="grok-beta",  # or "x-ai/grok-3-beta" for Grok 3
                messages=messages,
                max_tokens=5000,
                temperature=0.7
            )
                response_text = response.choices[0].message.content
            else:
                raise ValueError(f"Unsupported LLM provider: {self.config.provider}")
            # Save to database if user_email is provided
            try:
                if user_email and self.db.is_connected:
                    self.db.save_chat(
                        user_email=user_email,
                        query=original_query,  # Use original query without prompt suffix
                        response=response_text,
                        file_name=uploaded_file.name if uploaded_file else None
                    )
            except Exception as db_error:
                print(f"Database error: {str(db_error)}")
                # Continue execution even if database save fails
                
            return response_text
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            print(f"Error details: {str(e)}")
            return error_msg

def get_llm_client(provider: str = "openai") -> LLMConnect:
    """Factory function to create LLM client"""
    
    if provider.lower() == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        config = LLMConfig(provider="gemini", api_key=api_key)
        
    elif provider.lower() == "openai":
        api_key = os.getenv("OPENAI_API_KEY") 
        config = LLMConfig(
            provider="openai",
            api_key=api_key,
            model="gpt-3.5-turbo"
        )
    elif provider.lower() == "grok":
        api_key = os.getenv("GROK_API_KEY")
        config = LLMConfig(provider="grok", api_key=api_key)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
        
    return LLMConnect(config)