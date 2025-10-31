# api/chat.py
from fastapi import APIRouter, HTTPException
from datetime import datetime
from agents.orchestrator import food_agent
from models.schemas import ChatRequest, ChatResponse

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        resp = food_agent(req.message, user_id=req.user_id, chat_history=None, api_key=req.api_key)
        return ChatResponse(response=resp, timestamp=datetime.now().isoformat())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health():
    from agents.tools import all_tools
    return {
        "status": "healthy",
        "tools": [t.__name__ for t in all_tools],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/tools")
async def list_tools():
    from agents.tools import all_tools
    return {
        "tools": [
            {"name": t.__name__, "doc": (t.__doc__ or "").strip()}
            for t in all_tools
        ]
    }
