# Python Chatbot Todo

A FastAPI-based chatbot application that manages todo tasks through natural language commands.

## Features

- Add tasks using natural language
- Remove tasks by name
- Show all current tasks
- Clear all tasks
- AI-powered command interpretation
- RESTful API endpoints

## Prerequisites

- Python 3.9 or higher
- Windows PowerShell (for Windows users)

## Installation & Setup

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd python-chatbot-todo
```

### 2. Create a virtual environment
```bash
# Windows
python -m venv .venv

# macOS/Linux
python3 -m venv .venv
```

### 3. Activate the virtual environment
```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows Command Prompt
.\.venv\Scripts\activate.bat

# macOS/Linux
source .venv/bin/activate
```


### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Set up environment variables (optional)
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
PORT=8080
```

## Running the Application

### Start the server
```bash
python main.py
```

The application will start on `http://127.0.0.1:8080` (or the port specified in your environment variables).

### Verify the server is running
Open your browser and navigate to:
- Health check: `http://127.0.0.1:8080/health`

## Usage

### API Endpoints

#### Chat Endpoint
- **POST** `/chat`
- **Body:** `{"message": "your command here"}`

#### Health Check
- **GET** `/health`

### Example Commands

Try these natural language commands:

- **Add a task:** "add buy groceries"
- **Show tasks:** "show tasks"
- **Remove a task:** "remove buy groceries"
- **Clear all:** "clear all"


## Project Structure

```
python-chatbot-todo/
├── ai_agent.py      # AI agent for command interpretation
├── config.py        # Configuration settings
├── main.py          # FastAPI application entry point
├── requirements.txt # Python dependencies
└── README.md        # This file
```


## Deactivating the Virtual Environment

When you're done working with the project:

```bash
deactivate
```
