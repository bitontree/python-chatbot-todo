from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict, Any
import os
import uvicorn
from ai_agent import AIAgent
from config import Config
from datetime import datetime
import uuid
import openai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_agent = AIAgent()

# Simple storage
tasks = []

class ChatRequest(BaseModel):
    message: str

    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Message cannot be empty')
        return v.strip()

class Task(BaseModel):
    id: str
    content: str
    created_at: datetime

def create_task(content: str) -> Task:
    """Create new task"""
    if len(tasks) >= Config.MAX_TASKS:
        raise ValueError("Too many tasks")

    task = Task(
        id=str(uuid.uuid4()),
        content=content[:Config.MAX_TASK_LENGTH],
        created_at=datetime.now()
    )
    tasks.append(task)
    return task

def find_and_remove_task(task_name: str) -> bool:
    """Find and remove task"""
    for i, task in enumerate(tasks):
        if task_name.lower() in task.content.lower():
            tasks.pop(i)
            return True
    return False

# Helper function to handle OpenAI API failures and fallback
async def handle_openai_failure(message: str) -> Dict[str, Any]:
    """Fallback if OpenAI fails, process commands manually."""
    message_lower = message.lower().strip()

    if message_lower.startswith("add"):
        task_content = message_lower.replace("add", "", 1).strip()
        if task_content:
            task = create_task(task_content)
            return f"✅ Added: {task.content}"
        else:
            return "📋 No tasks content provided"

    elif message_lower.startswith("remove"):
        task_name = message_lower.replace("remove", "", 1).strip()
        if task_name:
            removed = find_and_remove_task(task_name)
            return f"✅ Removed: {task_name}" if removed else f"❌ Not found: {task_name}"
        else:
            return "❌ No task name provided."

    elif "show" in message_lower or "list" in message_lower:
        if tasks:
            task_list = "\n".join([f"• {task.content}" for task in tasks])
            return f"📋 Tasks ({len(tasks)}):\n{task_list}"
        else:
            return "📋 No tasks found"

    elif "clear" in message_lower:
        count = len(tasks)
        tasks.clear()
        return f"🗑️ Cleared {count} tasks"

    else:
        return "❓ Try: 'add [task]', 'show tasks', 'remove [task]', or 'clear all'"

# Chatbot endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    try:
        # Try to get AI interpretation
        ai_response = await ai_agent.interpret_command(request.message)
        
        action = ai_response.get("action", "unknown")
        task_content = ai_response.get("task")

        if "error" in ai_response:
            error_message = ai_response["error"]
            # Manually handle the error and process task commands locally if OpenAI fails
            return await handle_openai_failure(request.message)
        
        # Normal processing if OpenAI returns a valid action
        if action == "add" and task_content:
            task = create_task(task_content)
            return f"✅ Added: {task.content}"

        elif action == "remove" and task_content:
            removed = find_and_remove_task(task_content)
            return f"✅ Removed: {task_content}" if removed else f"❌ Not found: {task_content}"

        elif action == "show":
            if tasks:
                task_list = "\n".join([f"• {task.content}" for task in tasks])
                return f"📋 Tasks ({len(tasks)}):\n{task_list}"
            else:
                return "📋 No tasks found"

        elif action == "clear":
            count = len(tasks)
            tasks.clear()
            return f"🗑️ Cleared {count} tasks"

        else:
            return "❓ Try: 'add [task]', 'show tasks', 'remove [task]', or 'clear all'"

    except Exception as e:
        # Catch all unexpected errors
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "ok", "tasks_count": len(tasks)}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
