from supabase import create_client, Client
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnect:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.client = None
        self.is_connected = self._initialize_connection()
    
    def _initialize_connection(self) -> bool:
        """Initialize and test Supabase connection"""
        try:
            if not self.supabase_url or not self.supabase_key:
                raise ValueError("Supabase credentials not found in environment variables")
            
            self.client = create_client(self.supabase_url, self.supabase_key)
            
            # Test connection by making a simple query
            self.client.table('chat_history').select("*").limit(1).execute()
            return True
            
        except Exception as e:
            print(f"Supabase connection failed: {str(e)}")
            return False

    def check_connection(self) -> dict:
        """Return connection status and details"""
        return {
            "status": "connected" if self.is_connected else "disconnected",
            "url": self.supabase_url[:30] + "..." if self.supabase_url else None,
            "error": None if self.is_connected else "Could not connect to Supabase"
        }

    def save_chat(self, user_email: str, query: str, response: str, file_name: str = None) -> bool:
        """Save chat history to Supabase"""
        try:
            if not self.is_connected:
                print("Database not connected")
                return False
            
            data = {
                "user_email": user_email,
                "query": query,
                "response": response,
                "file_name": file_name,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("chat_history").insert(data).execute()
            
            if hasattr(result, 'data'):
                print(f"Chat saved successfully for user: {user_email}")
                return True
            else:
                print(f"Failed to save chat: {result}")
                return False
            
        except Exception as e:
            print(f"Error saving to database: {str(e)}")
            return False