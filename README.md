# Food Ordering System using AI (LangChain + LangGraph + FastAPI)

A modular, production-ready multi-agent food ordering system powered by LLMs, LangChain, LangGraph, and FastAPI. Easily extensible for real-world restaurant, cafe, or delivery use cases.

---

## Features
- **Conversational AI**: Natural chat interface for menu queries, order creation, order status, and modifications.
- **Multi-Agent Orchestration**: Specialized agents for menu, order, query, and modification tasks.
- **Tool-Driven Actions**: All business logic (CRUD) is implemented as LangChain tools.
- **PostgreSQL Database**: Robust, scalable order storage with connection pooling.
- **Modular Codebase**: Clean separation of API, agents, tools, database, and models.
- **FastAPI Backend**: Modern, async-ready REST API with OpenAPI docs.
- **Easy Configuration**: All settings via `.env` or `config.py`.
- **CORS Enabled**: Ready for frontend integration.

---

## Project Structure
```
food_ordering_system/
│
├── app.py                  # FastAPI entrypoint (minimal)
├── config.py               # Global config (menu, DB, env)
│
├── api/
│   └── chat.py             # FastAPI endpoints (chat, health, tools)
│
├── db/
│   └── manager.py          # DatabaseManager class and DB logic
│
├── agents/
│   ├── tools.py            # All @tool functions (CRUD, menu, etc.)
│   └── orchestrator.py     # food_agent, graph, and orchestration logic
│
├── models/
│   └── schemas.py          # Pydantic models (ChatRequest, ChatResponse)
│
├── requirements.txt        # Python dependencies
└── README.md
```

---

## Quickstart

1. **Clone the repo & install dependencies**
   ```bash
   git clone <repo-url>
   cd food_ordering_system
   pip install -r requirements.txt
   ```

2. **Set up your environment**
   - Copy `.env.example` to `.env` and fill in your DB and LLM keys.
   - Or edit `config.py` directly for menu and DB config.

3. **Start PostgreSQL**
   - Ensure a PostgreSQL server is running and accessible.
   - Create a database (default: `food_ordering`).

4. **Run the API**
   ```bash
   python app.py
   ```
   - API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

5. **Try the Chat Endpoint**
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H 'Content-Type: application/json' \
     -d '{"user_id": "demo123", "message": "I want 2 chicken sandwiches"}'
   ```

---

## API Endpoints
- `POST /api/chat` — Main chat endpoint
- `GET /api/health` — Health check
- `GET /api/tools` — List all available tools

---

## Customization
- **Menu**: Edit `config.py` to change menu items and prices.
- **Agents/Tools**: Add new tools in `agents/tools.py` and register them in `all_tools`.
- **Database**: Update `config.py` or `.env` for DB connection.
- **LLM Provider**: Change model/provider in `agents/orchestrator.py` or via env.

---

## Requirements
- Python 3.9+
- PostgreSQL 12+
- See `requirements.txt` for Python packages

---

## Credits
- [LangChain](https://github.com/langchain-ai/langchain)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [FastAPI](https://fastapi.tiangolo.com/)
- [PostgreSQL](https://www.postgresql.org/)

---







## 🏗️ System Architecture

```mermaid
flowchart TD
    A[User (Web/Mobile)] --> B[Load Balancer]
    B --> C[FastAPI App Cluster]
    subgraph C1[FastAPI App Instances]
        C1A[FastAPI App #1]
        C1B[FastAPI App #2]
        C1C[FastAPI App #3]
    end
    C --> D[API Layer (api/chat.py)]
    D --> E[LLM Orchestration Layer (agents/orchestrator.py)]
    E --> F[LangChain Tools (agents/tools.py)]
    F --> G[Database Manager (db/manager.py)]
    G --> H[(PostgreSQL Database)]

    %% Supporting Modules
    I[Menu Config (config.py)] -.-> F
    J[Pydantic Models (models/schemas.py)] -.-> D

    %% Scalability Components
    B --> K[Auto Scaling (Kubernetes / ECS)]
    K --> B
    G --> L[(Read Replicas / Caching - Redis)]
