# NorseAI Backend

A production-grade AI-powered mathematics tutoring system built with FastAPI, LangGraph, and advanced machine learning techniques. NorseAI provides personalized, adaptive learning experiences for students studying AMC8 (American Mathematics Competition 8) mathematics through an intelligent conversational interface.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Core Components](#core-components)
- [System Flow](#system-flow)
- [Installation & Setup](#installation--setup)
- [API Documentation](#api-documentation)
- [Key Algorithms](#key-algorithms)
- [Database Architecture](#database-architecture)
- [Configuration](#configuration)

## Overview

NorseAI Backend is an intelligent tutoring system that combines:

- **Adaptive Learning**: Bayesian Knowledge Tracing (BKT) algorithm to track and adapt to student mastery levels
- **Conversational AI**: LangGraph-based state machine orchestrating multiple AI agents for natural dialogue
- **Personalized Instruction**: Dynamic problem generation and lesson progression based on real-time assessment
- **Multi-Modal Responses**: Text-to-speech integration for audio responses
- **Knowledge Graph**: Comprehensive AMC8 concept mapping with 200+ mathematical concepts

### Key Features

- **Intelligent Query Classification**: Automatically distinguishes mathematical from non-mathematical queries
- **Parallel Processing**: Evaluator and Grader agents run concurrently for efficient response generation
- **State Management**: Redis for session state, MongoDB for persistent storage
- **Streaming Responses**: Server-Sent Events (SSE) for real-time chat responses with audio streaming
- **Assessment System**: Comprehensive pre-lesson and post-lesson assessments with automatic knowledge graph updates

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│   FastAPI App   │
│   (REST API)    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│         Chat Service                 │
│  (Session Management & Orchestration) │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      LangGraph State Machine         │
│  (Multi-Agent Orchestration Graph)   │
└────────┬────────────────────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Classifier│ │Evaluator│ │ Grader │ │Teacher│
└────────┘ └────────┘ └────────┘ └────────┘
    │         │         │         │
    └─────────┴─────────┴─────────┘
              │
              ▼
    ┌─────────────────┐
    │  BKT Algorithm  │
    │ (Knowledge Graph│
    │    Updates)     │
    └─────────────────┘
```

### Graph Flow

The system uses LangGraph to orchestrate a sophisticated state machine:

1. **Classifier Node**: Determines if input is mathematical or non-mathematical
2. **Math Router**: Routes mathematical queries to parallel processing
3. **Evaluator Node**: Analyzes student responses for understanding and misconceptions
4. **Grader Node**: Grades student work and identifies concept mastery
5. **BKT Node**: Updates Bayesian Knowledge Tracing graph based on performance
6. **Lesson Tracker Node**: Manages lesson state progression
7. **Teacher Node**: Generates personalized instructional responses

## Technology Stack

### Core Framework
- **FastAPI 0.116.1**: Modern, high-performance web framework
- **Uvicorn**: ASGI server for production deployment
- **Python 3.10+**: Primary programming language

### AI & ML
- **LangChain 0.3.27**: LLM orchestration and agent framework
- **LangGraph 0.6.2**: State machine and multi-agent coordination
- **Ollama**: Local LLM inference (via langchain-ollama)
- **ChromaDB 1.0.15**: Vector database for RAG (Retrieval-Augmented Generation)

### Databases
- **PostgreSQL** (via asyncpg): User authentication and session management
- **MongoDB** (via pymongo/motor): Problem database, conversation history, assessments
- **Redis**: Session state and graph checkpointing

### Additional Libraries
- **SymPy**: Symbolic mathematics engine for complex calculations
- **Pydantic**: Data validation and settings management
- **bcrypt**: Secure password hashing
- **python-dotenv**: Environment configuration

## Core Components

### 1. Services Layer (`src/services/`)

#### `chat_service.py`
**Purpose**: Central orchestration service managing student sessions and chat interactions.

**Key Responsibilities**:
- Session lifecycle management (initialization, cleanup, persistence)
- Conversation history management with automatic archiving
- Streaming response generation with TTS integration
- State synchronization between Redis (ephemeral) and MongoDB (persistent)

**Architecture Decisions**:
- Uses async/await for non-blocking I/O operations
- Implements conversation length limits (24 messages) with automatic archiving
- Maintains active session dictionary for in-memory state
- Integrates TTS streaming for real-time audio generation

#### `teacher.py`
**Purpose**: Primary instructional agent generating personalized teaching responses.

**Key Features**:
- ReAct agent pattern with tool access (problem retrieval, archived conversations)
- Dynamic prompt generation based on:
  - Current learning objective
  - Student mastery level (BKT graph)
  - Lesson state progression
  - Conversation context
- Problem embedding: Automatically retrieves and embeds problems in responses
- Response parsing: Extracts display text, context, and problem solutions

#### `evaluator.py` & `grader.py`
**Purpose**: Parallel assessment agents analyzing student responses.

**Evaluator**:
- Analyzes student understanding and identifies misconceptions
- Uses math_engine tool for complex mathematical verification
- Outputs structured evaluation text

**Grader**:
- Grades student work on concept-by-concept basis
- Validates concepts against AMC8 concept list
- Outputs structured grade dictionary: `{concept: "correct"/"incorrect"}`

**Architecture**: Both run in parallel after classification, improving response latency.

#### `bkt.py` (Bayesian Knowledge Tracing)
**Purpose**: Adaptive learning algorithm tracking student mastery over time.

**Algorithm Details**:
- **P_will_learn**: Probability of learning in single interaction (default: 0.03)
- **P_slip**: Probability of mistake when concept is known (default: 0.08)
- **P_guess**: Probability of correct guess when unknown (default: 0.15)
- **Damping Factors**: Configurable sensitivity (0.3-1.0) based on:
  - Problem difficulty (1-5 scale)
  - Current mastery level (<0.3, 0.3-0.6, >0.6)
  - Lesson state (walkthrough vs. independent problem)

**Learning Objective Management**:
- **Rule 1**: If any concept before current objective < 0.75 → move backward
- **Rule 2**: If current objective mastery > 0.95 → advance to next concept
- **Rule 3**: Otherwise → maintain current objective with "steady" status

#### `lesson_tracker.py`
**Purpose**: Manages lesson state machine and progression.

**Lesson States**:
- `START_LESSON`: Introduction and greeting
- `GIVE_FIRST_PROBLEM`: Initial problem presentation
- `FIRST_PROBLEM_WALKTHROUGH`: Interactive problem solving
- `GIVE_SECOND_PROBLEM`: Second problem (difficulty adjusted by mastery)
- `SECOND_PROBLEM_WALKTHROUGH`: Second problem walkthrough
- `GIVE_THIRD_PROBLEM`: Final problem
- `THIRD_PROBLEM_WALKTHROUGH`: Final walkthrough
- `END_LESSON`: Summary and conclusion
- `CHECK`: Mastery verification before advancement
- `BEHIND`: Remediation for struggling students

**Logic**: Uses LLM agent to determine state transitions based on student progress and conversation context.

#### `assessment_service.py`
**Purpose**: Manages pre-lesson and post-lesson assessments.

**Features**:
- Generates 25-problem assessments from AMC8 database
- Evaluates student answers and calculates scores
- Updates knowledge graph using BKT with assessment-specific damping factors
- Stores assessment history for progress tracking

#### `graph.py`
**Purpose**: Defines the LangGraph state machine structure.

**Graph Structure**:
```
START → classifier → [mathematical: math_router | non-mathematical: lesson_tracker]
                     ↓
            math_router → evaluator (parallel)
                      → grader (parallel)
                     ↓
            bkt_router → [conditional: bkt | no-bkt]
                     ↓
            lesson_tracker → teacher → END
```

**Design Rationale**:
- Parallel execution of evaluator and grader reduces latency
- Conditional BKT execution prevents updates during lesson transitions
- Single teacher node handles all instructional responses

### 2. Routes Layer (`src/routes/`)

#### Authentication (`auth.py`)
- `POST /auth/signup`: User registration with bcrypt password hashing
- `POST /auth/login`: User authentication with session token generation
- `POST /auth/logout`: Session termination and cleanup
- `GET /auth/user-info`: Current user information retrieval

#### Chat (`chat.py`)
- `POST /chat/init/{student_id}`: Initialize chat session with optional user graph
- `POST /chat/s/{student_id}`: Streaming chat endpoint (SSE)
- `DELETE /chat/session/{student_id}`: Manual session termination
- `GET /chat/status/{student_id}`: Current session status

#### Assessment (`assessment.py`)
- `GET /assessment/give`: Retrieve assessment problems
- `POST /assessment/submit`: Submit answers and receive results
- `POST /assessment/store`: Store assessment with timing data
- `GET /assessment/retrieve`: Retrieve past assessment results
- `POST /assessment/update-graph`: Update knowledge graph from assessment

#### User Graph (`user_graph.py`)
- `GET /user_graph/{student_id}`: Retrieve student's knowledge graph
- `POST /user_graph/{student_id}`: Update knowledge graph

### 3. Models Layer (`src/models/`)

**Request Models** (`requests.py`):
- `ChatRequest`: Message content for chat
- `UserSignup/UserLogin`: Authentication credentials
- `AssessmentSubmitRequest`: Assessment answers
- `UserGraphRequest`: Knowledge graph updates

**Response Models** (`responses.py`):
- Structured Pydantic models for all API responses
- Type-safe response validation

### 4. Core Infrastructure (`src/core/`)

#### `lifespan.py`
**Purpose**: Application lifecycle management.

**Startup**:
- Creates PostgreSQL connection pool (min: 1, max: 30 connections)
- Configures connection timeout and pool settings

**Shutdown**:
- Cleans up all active chat sessions
- Closes database connection pool gracefully

#### `middleware.py`
**Purpose**: CORS configuration for cross-origin requests.

**Configuration**:
- Configurable origins, methods, and headers
- Credentials support enabled

#### `dependencies.py`
**Purpose**: FastAPI dependency injection for database connections.

**Pattern**: Uses `Depends()` to inject database connections from pool into route handlers.

### 5. Utilities (`src/utils/`)

#### `utils.py`
**Key Functions**:
- `parse_response()`: Extracts teacher response, problem ID, and solution from LLM output
- `format_eval()`: Parses evaluator output for structured analysis
- `format_grade()`: Extracts concept-level grading from grader output
- `convert_redis_messages()`: Converts LangChain serialized messages to BaseMessage instances
- `get_list_of_obj()`: Generates lesson objectives based on current state
- `extract_json_value()`: Incremental JSON parsing for streaming responses

#### `knowledge_info.py`
**Purpose**: Defines AMC8 knowledge domain.

**Data Structures**:
- `amc8_knowledge_graph`: Dictionary mapping 200+ concepts to mastery probabilities (0.0-1.0)
- `amc8_concepts`: Ordered list of concepts defining learning progression

**Concepts Organized By**:
- Algebra (expressions, equations, functions)
- Geometry (shapes, theorems, coordinate geometry)
- Number Theory (primes, modular arithmetic, divisibility)
- Combinatorics & Probability (counting, permutations, expected value)

#### `logging.py`
**Purpose**: Centralized logging configuration.

**Levels**:
- Level 0: Errors and critical issues
- Level 1: Important operations (session management, state changes)
- Level 2: Detailed debugging (prompt formatting, agent responses)

## System Flow

### Chat Request Flow

1. **Request Received** (`POST /chat/s/{student_id}`)
   - Validates message content
   - Retrieves or creates session

2. **Session Initialization** (if new)
   - Loads persisted state from MongoDB
   - Loads Redis state (if exists)
   - Applies user graph from assessment (if provided)
   - Initializes LangGraph with Redis checkpointer

3. **Conversation Management**
   - Checks conversation length
   - Archives old messages if > 24 messages
   - Adds user message to state

4. **Graph Execution**
   - Streams through LangGraph nodes
   - Classifier determines query type
   - Mathematical queries: Evaluator + Grader (parallel) → BKT → Lesson Tracker → Teacher
   - Non-mathematical queries: Lesson Tracker → Teacher

5. **Response Generation**
   - Teacher node generates response with tools
   - TTS processor streams audio in background
   - Response chunks streamed via SSE
   - Audio chunks base64-encoded and streamed

6. **State Persistence**
   - Final state retrieved from Redis
   - Updated session state stored
   - Lesson completion triggers MongoDB persistence

### Assessment Flow

1. **Assessment Generation** (`GET /assessment/give`)
   - Selects 25 random problems (1 per problem number)
   - Returns problem set with IDs

2. **Answer Submission** (`POST /assessment/submit`)
   - Evaluates each answer against correct solution
   - Calculates total score
   - Returns detailed results

3. **Graph Update** (`POST /assessment/update-graph`)
   - For each problem:
     - Identifies tested concepts
     - Applies BKT algorithm with difficulty-based damping
     - Updates knowledge graph probabilities
   - Returns updated graph for lesson initialization

## Installation & Setup

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 12+ (for user database)
- MongoDB 4.4+ (for problem database and state persistence)
- Redis 6.0+ (for session state)
- Ollama (for LLM inference) or compatible LLM service

### Environment Variables

Create a `.env` file in the project root:

```env
# PostgreSQL Configuration
USER_DB_PASSWORD=your_postgres_password
DB_HOST=172.16.0.154
DB_PORT=5432

# MongoDB Configuration
MONGODB_HOST=172.16.0.177
MONGODB_PORT=27019

# Redis Configuration (hardcoded in state_manager.py, consider moving to env)
# REDIS_HOST=172.16.0.177
# REDIS_PORT=6379
```

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```sql
   -- PostgreSQL
   CREATE DATABASE norseai;
   CREATE USER admin WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE norseai TO admin;
   ```

   MongoDB and Redis should be running and accessible at configured hosts.

5. **Initialize ChromaDB Collections**
   - The system will create collections on first use
   - Collections: `AMC8_math`, `student_persona`, `math_related`, `AMC8_problems`, `conversation_history`

6. **Run the application**
   ```bash
   python -m src.main
   # Or with uvicorn directly:
   uvicorn src.main:app --host 0.0.0.0 --port 6700
   ```

### Development Mode

For development with auto-reload:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 6700
```

## API Documentation

### Base URL
```
http://localhost:6700
```

### Interactive API Docs
- Swagger UI: `http://localhost:6700/docs`
- ReDoc: `http://localhost:6700/redoc`

### Key Endpoints

#### Chat Endpoints

**Initialize Session**
```http
POST /chat/init/{student_id}
Content-Type: application/json

{
  "user_graph": {
    "arithmetic": 0.5,
    "linear equations": 0.8,
    ...
  }
}
```

**Stream Chat**
```http
POST /chat/s/{student_id}
Content-Type: application/json

{
  "message": "How do I solve 2x + 5 = 15?"
}
```

**Response Format** (SSE):
```
data: {"type": "audio_stream", "audio_chunk": "base64_encoded_audio"}
data: {"type": "ai_response", "content": "To solve 2x + 5 = 15...", "evaluation": "...", "grade": "..."}
```

#### Assessment Endpoints

**Get Assessment**
```http
GET /assessment/give
```

**Submit Assessment**
```http
POST /assessment/submit
Content-Type: application/json

{
  "student_answers": [
    {"problem_id": "507f1f77bcf86cd799439011", "student_answer": "42"},
    ...
  ]
}
```

## Key Algorithms

### Bayesian Knowledge Tracing (BKT)

The BKT algorithm updates concept mastery probabilities based on student performance:

**Correct Answer Update**:
```
P_learned = (P_known × (1 - P_slip)) / (P_known × (1 - P_slip) + (1 - P_known) × P_guess)
P_updated = P_known + damping × (P_learned + (1 - P_learned) × P_will_learn - P_known)
```

**Incorrect Answer Update**:
```
P_learned = (P_known × P_slip) / (P_known × P_slip + (1 - P_known) × (1 - P_guess))
P_updated = P_known + damping × (P_learned + (1 - P_learned) × P_will_learn - P_known)
```

**Damping Factors** (context-dependent):
- Walkthrough problems: 0.7-0.85 (correct), 0.4-0.65 (incorrect)
- Independent problems: 0.75-0.95 (correct), 0.5-0.75 (incorrect)
- Assessment problems: 0.7-0.95 (correct), 0.35-0.75 (incorrect)

### Problem Difficulty Selection

Problems are selected based on current mastery:
- Mastery < 0.3: Difficulty 1-2 (easier problems)
- Mastery 0.3-0.6: Difficulty 3-4 (medium problems)
- Mastery > 0.6: Difficulty 4-5 (harder problems)

## Database Architecture

### PostgreSQL Schema

**Users Table**:
```sql
CREATE TABLE users (
    student_id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sessions (
    session_token VARCHAR(255) PRIMARY KEY,
    student_id INTEGER REFERENCES users(student_id),
    expires_at TIMESTAMP NOT NULL
);
```

### MongoDB Collections

**Problems Collection**:
```javascript
{
  _id: ObjectId,
  problem_number: Number,  // 1-25 for AMC8
  problem: String,          // Raw problem text
  display_problem: String,  // Formatted for display
  solution: String,         // Solution explanation
  correct_answer: String,   // Answer letter/number
  concepts: [String],       // Array of concept names
  difficulty: Number        // 1-5 scale
}
```

**Assessments Collection**:
```javascript
{
  _id: ObjectId,
  assessment_id: String,    // student_id + timestamp
  student_id: Number,
  problem_id: String,
  student_answer: String,
  time_spent: Number        // seconds
}
```

**Conversation History Collection**:
```javascript
{
  _id: ObjectId,
  student_id: String,
  role: String,             // "student" or "teacher"
  content: String,
  timestamp: Date
}
```

### Redis Structure

**Checkpoint Keys**:
- Pattern: `{thread_id}:checkpoint:{checkpoint_id}`
- Stores LangGraph state snapshots
- Includes messages, lesson state, BKT graph, etc.

## Configuration

### Settings (`src/config/settings.py`)

**Database Pool**:
- Min pool size: 1
- Max pool size: 30
- Timeout: 20 seconds

**Conversation Management**:
- Max conversation length: 24 messages
- Keep recent: 12 messages (archives older messages)

**CORS**:
- Origins: `["*"]` (configure for production)
- Credentials: Enabled
- Methods: All
- Headers: All

### Production Considerations

1. **Security**:
   - Restrict CORS origins to frontend domain
   - Use environment variables for all secrets
   - Implement rate limiting
   - Add authentication middleware for protected routes

2. **Performance**:
   - Configure connection pool sizes based on load
   - Implement Redis connection pooling
   - Add caching for frequently accessed data
   - Consider CDN for static assets

3. **Monitoring**:
   - Add structured logging (JSON format)
   - Implement health check endpoints
   - Add metrics collection (Prometheus/Grafana)
   - Set up error tracking (Sentry)

4. **Scalability**:
   - Use Redis Cluster for high availability
   - Implement horizontal scaling with load balancer
   - Consider message queue for async processing
   - Database read replicas for assessment queries

## Development Guidelines

### Code Style

- Follow PEP 8 Python style guide
- Use type hints for function signatures
- Document complex algorithms and business logic
- Keep functions focused and single-purpose

### Testing

**Recommended Testing Structure**:
```
src/testing/
├── unit/
│   ├── test_bkt.py
│   ├── test_utils.py
│   └── test_services.py
├── integration/
│   ├── test_chat_flow.py
│   └── test_assessment_flow.py
└── fixtures/
    └── sample_data.py
```

### Adding New Features

1. **New Graph Node**:
   - Create service class in `src/services/`
   - Implement `build_node(state: State)` method
   - Add to `Nodes` class in `nodes.py`
   - Update graph in `graph.py`

2. **New API Endpoint**:
   - Define request/response models in `models/`
   - Create route handler in `routes/`
   - Add to router in `main.py`

3. **New Tool**:
   - Define in `tools.py` with `@tool` decorator
   - Add to agent's tool list in `nodes.py`

### Logging Best Practices

- Use appropriate log levels (0: error, 1: info, 2: debug)
- Include context (student_id, session_id) in logs
- Avoid logging sensitive data (passwords, tokens)
- Use structured logging for production

### Error Handling

- Use FastAPI's `HTTPException` for API errors
- Log errors with full traceback
- Return user-friendly error messages
- Implement retry logic for external services

## Contributors

Andrew Su

