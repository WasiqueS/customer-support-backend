# Customer Support AI Backend

This is a FastAPI-based backend system for a customer support assistant that allows agents and users to create support tickets and get AI-powered suggestions using Groq AI (Mixtral model). The AI responses are streamed in real-time. The project includes authentication, database integration with PostgreSQL, and Docker-based deployment.

---

## 🚀 Features

- JWT-based authentication
- Agent & User roles with ticket access control
- Ticket creation and listing APIs
- AI assistant response generation with **streaming**
- PostgreSQL database integration via SQLAlchemy
- Docker & Docker Compose for easy setup

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

git clone https://github.com/yourusername/customer-support-ai.git
cd customer-support-ai

2. Environment Configuration

Create a .env file or update environment variables directly:

DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<database>
SECRET_KEY=<you_secret_key> # generate secret key command(python -c "import secrets; print(secrets.token_urlsafe(32)))
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GROQ_API_KEY=<your_groq_api_key> # Create groq API Key

3. Build and Run with Docker

docker-compose up --build
This will:
Start the FastAPI app
Launch a PostgreSQL container
Create necessary tables automatically

4. Running Locally (Without Docker)

✅ Option A: Using pip
Create and activate a virtual environment

python -m venv env
source env/bin/activate  # On Windows use: env\Scripts\activate

Install dependencies
pip install -r requirements.txt

Run the app
uvicorn app.main:app --reload

✅ Option B: Using poetry
Install poetry (if not already installed)

pip install poetry
Install dependencies

poetry config virtualenvs.create false  # Optional: install in current shell environment
poetry install

Run the app
uvicorn app.main:app --reload

⚙️ API Endpoints
Full docs available at: http://localhost:8000/docs

🔐 Authentication
POST /register: Register user or agent

POST /login: Obtain JWT token

🎫 Tickets
POST /tickets: Create a support ticket

GET /tickets: List tickets (filtered by ticket_id)

💬 Messages
POST /tickets/{ticket_id}/messages: Add a message to a ticket

GET /tickets/{ticket_id}/messages: Get all messages for a ticket

GET /tickets/{ticket_id}/ai-response: Get streamed AI assistant message (agent only)

🧗 Challenges Faced
AI Streaming with SSE:
Integrating Server-Sent Events (SSE) for real-time AI response streaming required careful handling of async functions and user-specific access.