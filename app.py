# food_agent.py
# Multi-Agent Food Ordering System — LangGraph + LangChain style (refactor to match goal_agent pattern)
# Requirements:
#   pip install fastapi uvicorn psycopg2-binary langchain langgraph python-dotenv requests

import os
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Annotated, TypedDict

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.chat import router as chat_router
import uvicorn

app = FastAPI(title="Food Agent (LangGraph)", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_router, prefix="/api")

if __name__ == "__main__":
    
    uvicorn.run(app, port=8000)

