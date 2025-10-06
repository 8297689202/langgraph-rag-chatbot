# AI Chat Assistant with LangGraph & RAG

An intelligent chat assistant built with LangGraph that routes queries between real-time weather information and PDF document Q&A using Retrieval-Augmented Generation (RAG).

## Overview

This project implements an agentic AI pipeline that:
- Classifies user intent (weather vs document queries)
- Fetches real-time weather data via OpenWeatherMap API
- Performs semantic search and Q&A on uploaded PDF documents using RAG
- Maintains conversation history with session management
- Provides LLM observability through LangSmith

## Architecture
User Query → Intent Classification (LangGraph) → Route Decision
↓
┌───────────────┴────────────────┐
↓                                ↓
Weather Path                      Document Path
↓                                ↓
Extract City → Fetch API        Vector Search (Qdrant)
↓                                ↓
└────────→ LLM Response ←────────┘

### Key Components

- **LangGraph Agent** (`agent.py`): Orchestrates the decision-making pipeline with nodes for intent classification, routing, and response generation
- **Weather Tool** (`weather.py`): Fetches real-time weather data from OpenWeatherMap API
- **RAG Tool** (`rag.py`): Handles PDF loading, vector storage (Qdrant), semantic retrieval, and reranking (Flashrank)
- **Database** (`database.py`): SQLite-based chat history with session and PDF tracking
- **Streamlit UI** (`app.py`): Interactive chat interface with PDF upload and session management

## Features

- **Intent Classification**: Automatically routes queries to appropriate handlers
- **Weather Queries**: Real-time weather information for any city
- **PDF Q&A**: Upload PDFs and ask questions using RAG with semantic search
- **Session Management**: Maintains separate conversation contexts
- **PDF Isolation**: Each PDF gets its own Qdrant collection to prevent contamination
- **Reranking**: Uses Flashrank for improved retrieval accuracy
- **LangSmith Integration**: Full observability of LLM calls and agent decisions
- **Comprehensive Tests**: Unit tests for all components using pytest

## Prerequisites

- Python 3.10+
- OpenAI API key
- OpenWeatherMap API key
- LangSmith API key (optional, for tracing)
- Qdrant (running locally or cloud)

## Installation

### 1. Clone the repository
git clone <your-repo-url>
cd <project-directory>

### 2. Create virtual environment
python -m venv venv
source venv/bin/activate  

On Windows:venv\Scripts\activate

### 3.Install dependencies
pip install -r requirements.txt

### 4. Set up Qdrant
Option A: Docker (Recommended)

docker pull qdrant/qdrant
docker run -p 6333:6333 qdrant/qdrant

Option B: Qdrant Cloud
Sign up at https://cloud.qdrant.io/ and update the URL in rag.py


### 5. Configure environment variables
### Create a .env file in the project root:
    cp .env.example .env
### Edit .env with your API keys:
    OPENAI_API_KEY=sk-...
    OPENWEATHERMAP_API_KEY=your_weather_api_key
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_API_KEY=lsv2_pt_...
    LANGCHAIN_PROJECT=your_project_name

### Usage
Running the Streamlit Application
streamlit run app.py
The app will open at http://localhost:8501



### Using the Application

1.Upload a PDF: Click "Browse files" in the sidebar to upload a PDF document
2.Ask Questions:
    -Weather: "What's the weather in Tokyo?"
    -Document: "What are the main findings in this paper?"

3.Manage Sessions: Create new sessions or switch between previous conversations
4.View History: Access previous chat sessions in the sidebar

Running Tests
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agent.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

## Project Structure
project/
├── agent.py              # LangGraph agent pipeline
├── weather.py            # Weather API integration
├── rag.py               # RAG tool with Qdrant
├── database.py          # SQLite chat history
├── app.py               # Streamlit UI
├── tests/
│   ├── test_weather.py  # Weather tool tests
│   ├── test_rag.py      # RAG tool tests
│   ├── test_agent.py    # Agent pipeline tests
│   └── test_database.py # Database tests
├── requirements.txt     # Python dependencies
├── .env.example        # Environment template
├── .gitignore          # Git ignore rules
└── README.md           # This file

# LangSmith Evaluation
LangSmith is integrated for full observability of LLM calls and agent decisions. View traces at: https://smith.langchain.com/

Key metrics tracked:
    -Intent classification accuracy
    -LLM token usage and costs
    -Retrieval quality and latency
    -End-to-end execution time
    -Agent decision paths

### Screenshots
Screenshots demonstrating LangSmith tracing are included in the `/screenshots` directory:

### Weather query
1. **Weather Query - Full Execution Flow** (`1.png`) - Complete LangGraph trace showing classify_intent → extract_city → fetch_weather → generate_response pipeline
2. **Intent Classification with LLM** (`2.png`) - ChatOpenAI call showing the classification prompt and "weather" output
3. **RAG Query - Full Execution Flow** (`3.png`) - Complete trace showing classify_intent → query_documents → generate_response with VectorStoreRetriever
4. **Vector Retrieval & Context** (`4.png`) - Document retrieval from Qdrant with semantic search results and reranking scores

These traces demonstrate proper LangGraph routing, LLM integration, and RAG functionality with full observability.

## Technical Details
### Intent Classification
    Uses GPT-4o-mini to classify queries as "weather" or "document" based on user input.

### Weather Flow
 -Extract city name from query
 -Call OpenWeatherMap API
 -Format data into natural language response

### RAG Flow

-Load PDF and split into chunks (1000 chars, 200 overlap)
-Generate embeddings using OpenAI's text-embedding-3-small
-Store in Qdrant with per-PDF collections
-Retrieve top 5 semantically similar chunks
-Rerank using Flashrank (ms-marco-MiniLM-L-12-v2)
 -Generate answer with top 3 chunks as context

#### Database Schema
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_query TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    intent TEXT,
    pdf_name TEXT,
    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now'))
)

## Testing Approach
All tests use mocking to avoid external API calls:

Weather tests: Mock HTTP requests to OpenWeatherMap
RAG tests: Mock Qdrant client and vector operations
Agent tests: Mock LLM responses and tool outputs
Database tests: Use temporary SQLite databases

## Known Limitations

Browser storage (localStorage/sessionStorage) not supported in Streamlit artifacts
PDFs must be re-uploaded if Qdrant is restarted (data not persisted)
Single-user design (no authentication)
English language only

## Future Enhancements

Multi-user support with authentication
Support for multiple file formats (DOCX, TXT, etc.)
Advanced search filters and sorting
Export chat history
Custom LLM model selection
Multilingual support

### Author
Ayush Gaur
ayushgaur228@gmail.com


