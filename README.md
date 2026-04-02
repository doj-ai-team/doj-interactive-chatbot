# Department of Justice - Interactive AI Chatbot

A high-performance, full-stack AI conversational assistant built for the **Department of Justice (Govt. of India)**. This project leverages Retrieval-Augmented Generation (RAG) coupled with a human-in-the-loop learning system to provide verified, legally grounded guidance to citizens regarding Indian laws, courts, and dispute resolution.

## Features
- **Cinematic Glassmorphism UI:** A sleek, fully dark-mode responsive interface built with Tailwind CSS.
- **Sub-3 Second Latency:** Ultra-fast FAISS Vector Search combined with in-memory caching for zero delay processing.
- **Multilingual Support:** English, Hindi, and Tamil language understanding and contextually accurate generation capability.
- **Verified Learning Loop:** If the AI confidence is low, it asks the citizen for input, holding unverified knowledge in a moderation queue for DoJ Admins to approve before committing to the AI's permanent memory.
- **Case Analytics & Generation:** Automated case text structuring, risk analysis, and drafting capabilities intended strictly for judicial officials.

## Tech Stack
- **Backend:** Python, Flask server setup.
- **AI/ML:** LangChain, FAISS (Vector DB), INLegalBERT (Embeddings Engine), Google Gemini/Groq APIs (LLM).
- **Frontend:** HTML, JavaScript, TailwindCSS, Jinja2 templating.
- **Database:** SQLite / SQLAlchemy

## Installation and Setup

### 1. Prerequisites
- Python 3.9 or higher

### 2. Clone the repository
```bash
git clone https://github.com/doj-ai-team/doj-interactive-chatbot.git
cd doj-interactive-chatbot
```

### 3. Set up Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Environment Variables Configuration
**Do NOT commit API keys.** \
Create a file named `.env` in the root directory. Inside `.env`, add your Groq/Gemini API keys and other configuration variables:
```ini
# Add your GROQ API key here
GROQ_API_KEY=your_groq_api_key_here

# Required for Upstash Redis (Optional, defaults to MockRedis)
UPSTASH_REDIS_URL=your_redis_url
UPSTASH_REDIS_TOKEN=your_redis_token

# Secret Key for Flask sessions
SECRET_KEY=any_random_secure_string_here
```

### 6. Run the application
Run the `app.py` script to start the server:
```bash
python app.py
```
After starting the server, go to `http://127.0.0.1:5000` in your web browser.

## Administrator Credentials (Local SQLite defaults)
- **Role**: Admin
- **Email/User**: `admin@doj.gov.in` 
- **Passcode**: `admin123` (for local dev purposes only)
