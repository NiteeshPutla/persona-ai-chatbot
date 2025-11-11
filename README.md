# Persona-Switching Agentic Chatbot

A sophisticated AI chatbot that can dynamically switch between different expert personas, maintaining separate conversation threads with persistent memory. Built with LangGraph, LangChain, FastAPI, and SQLite.

## Features

- **Agentic Framework**: Uses LangGraph for state management and context switching
- **Dynamic Persona Switching**: Seamlessly switch between personas (mentor, investor, advisor, etc.)
- **Persistent Threads**: Each persona conversation exists in its own thread with full history
- **Long-Term Memory**: Conversations persist across sessions using SQLite
- **Fast Context Switching**: Instantly recall full conversation context when switching threads
- **RESTful API**: Simple FastAPI endpoints for chat and history retrieval

## Architecture

### Components

1. **Database Layer** (`database.py`): SQLite-based persistence for threads and messages
2. **Persona Manager** (`persona_manager.py`): Handles persona detection and prompt generation
3. **Agent** (`agent.py`): LangGraph-based agentic framework for state management
4. **API** (`main.py`): FastAPI endpoints for chat and history

### Flow

```
User Message → Persona Detection → Thread Routing → Context Loading → LLM Processing → Response → Persistence
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (or configure for other LLM providers)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Persona-ai-chat-bot
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv chatbot
   source chatbot/bin/activate  # On Windows: chatbot\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

   Or export it directly:
   ```bash
   export OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Run the application**:
   ```bash
   python run.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   Or as a Python module:
   ```bash
   python -m app.main
   ```

6. **Access the API**:
   - API will be available at `http://localhost:8000`
   - Interactive API docs at `http://localhost:8000/docs`
   - Alternative docs at `http://localhost:8000/redoc`

## API Endpoints

### 1. Chat Endpoint

**POST** `/chat`

Send a message to the chatbot. The agent will automatically detect persona switch requests and manage threads.

**Request Body**:
```json
{
  "user_id": "user123",
  "message": "act like my mentor",
  "thread_name": null  // Optional: specify thread name directly
}
```

**Response**:
```json
{
  "response": "I'm here to guide you as your mentor...",
  "thread_name": "mentor",
  "thread_id": 1
}
```

**Example cURL**:
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "act like my mentor"
  }'
```

### 2. Chat History Endpoint

**GET** `/chat_history?user_id=user123`

Retrieve all chat history for a user, organized by thread.

**Query Parameters**:
- `user_id` (required): The user identifier

**Response**:
```json
{
  "user_id": "user123",
  "threads": {
    "mentor": {
      "thread_id": 1,
      "persona_prompt": "You are an experienced business mentor...",
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T11:45:00",
      "messages": [
        {
          "role": "user",
          "content": "act like my mentor",
          "timestamp": "2024-01-15T10:30:00"
        },
        {
          "role": "assistant",
          "content": "I'm here to guide you...",
          "timestamp": "2024-01-15T10:30:05"
        }
      ]
    },
    "investor": {
      "thread_id": 2,
      "persona_prompt": "You are a seasoned venture capitalist...",
      "created_at": "2024-01-15T11:00:00",
      "updated_at": "2024-01-15T11:30:00",
      "messages": [...]
    }
  }
}
```

**Example cURL**:
```bash
curl -X GET "http://localhost:8000/chat_history?user_id=user123"
```

### 3. Health Check

**GET** `/health`

Check API health status.

**Example cURL**:
```bash
curl -X GET "http://localhost:8000/health"
```

## Usage Examples

### Example Workflow

1. **Initialize a mentor persona**:
   ```bash
   curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user123",
       "message": "act like my mentor"
     }'
   ```

2. **Continue conversation as mentor**:
   ```bash
   curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user123",
       "message": "how can I scale my product?"
     }'
   ```

3. **Switch to investor persona**:
   ```bash
   curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user123",
       "message": "now I will do a sales pitch, act like an investor"
     }'
   ```

4. **Continue as investor**:
   ```bash
   curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user123",
       "message": "My product is a B2B SaaS for dog groomers..."
     }'
   ```

5. **Switch back to mentor thread**:
   ```bash
   curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user123",
       "message": "back to my mentor thread, should I focus on organic growth?"
     }'
   ```

6. **Retrieve full chat history**:
   ```bash
   curl -X GET "http://localhost:8000/chat_history?user_id=user123"
   ```

## Persona Detection

The system automatically detects persona switch requests using patterns like:
- "act like my mentor"
- "be an investor"
- "switch to advisor"
- "back to mentor thread"
- "resume investor conversation"

Supported built-in personas:
- `mentor`: Business mentor focused on long-term growth
- `investor`: Skeptical VC focused on metrics and returns
- `advisor`: Strategic advisor focused on operations
- `coach`: Leadership coach focused on development

Custom personas are automatically created when requested.

## Database

The application uses SQLite by default (stored as `chatbot.db`). The database schema includes:

- **user_threads**: Stores conversation threads with persona prompts
- **chat_messages**: Stores individual messages within threads

To use a different database (e.g., PostgreSQL), modify the `DatabaseManager` class in `database.py`.

## Configuration

All configuration is managed through environment variables or a `.env` file. The configuration is centralized in `app/core/config.py`.

### Available Settings

- `OPENAI_API_KEY` (required): Your OpenAI API key
- `MODEL_NAME` (default: `gpt-3.5-turbo`): LLM model to use
- `TEMPERATURE` (default: `0.7`): LLM temperature
- `DATABASE_URL` (default: `sqlite:///chatbot.db`): Database connection string
- `LOG_LEVEL` (default: `INFO`): Logging level
- `HOST` (default: `0.0.0.0`): Server host
- `PORT` (default: `8000`): Server port

### Example .env file

```env
OPENAI_API_KEY=your_key_here
MODEL_NAME=gpt-4
TEMPERATURE=0.7
DATABASE_URL=sqlite:///chatbot.db
LOG_LEVEL=INFO
```

## Project Structure

```
Persona-ai-chat-bot/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── api/
│   │   ├── routes.py         # API endpoints
│   │   └── schemas.py        # Pydantic request/response models
│   ├── core/
│   │   ├── config.py         # Centralized configuration
│   │   ├── exceptions.py     # Custom exceptions
│   │   ├── logging_config.py # Logging setup
│   │   └── dependencies.py   # Dependency injection
│   ├── services/
│   │   └── agent_service.py  # Service layer
│   ├── agent/
│   │   └── graph.py          # LangGraph agent implementation
│   ├── models/
│   │   └── database.py       # Database models
│   ├── repositories/
│   │   └── thread_repository.py  # Data access layer
│   └── utils/
│       └── persona_manager.py    # Persona detection and management
├── tests/                   # Test suite
│   ├── test_api.py
│   ├── test_repositories.py
│   └── test_persona_manager.py
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── .env                   # Environment variables 
└── chatbot.db            # SQLite database 
```

## Testing

Run the test suite:

```bash
pip install -r requirements.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_repositories.py

# Run with coverage
pytest --cov=app --cov-report=html
```

## Architecture

The project follows a clean architecture pattern with:

- **API Layer** (`app/api/`): FastAPI routes and schemas
- **Service Layer** (`app/services/`): Business logic
- **Agent Layer** (`app/agent/`): LangGraph agent implementation
- **Repository Layer** (`app/repositories/`): Data access
- **Models** (`app/models/`): Database models
- **Core** (`app/core/`): Configuration, exceptions, logging, dependencies



## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**:
   - Ensure `.env` file exists with `OPENAI_API_KEY` set
   - Or export the environment variable before running

2. **Database Locked Error**:
   - Ensure only one instance of the application is running
   - Check file permissions on `chatbot.db`

3. **Import Errors**:
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt` again



