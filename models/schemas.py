# models/schemas.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    user_id: str
    message: str
    api_key: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    timestamp: str
    debug: Optional[Dict[str, Any]] = None
