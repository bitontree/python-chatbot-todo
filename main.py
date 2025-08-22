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
import bubbletea_chat as bt  # Importing Bubbletea

app = FastAPI()

# Add CORS middleware - THIS IS THE KEY FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain instead of "*"
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

# Bubbletea chatbot with enhanced UI components
@app.post("/chat")
async def chat(request: ChatRequest):
    """Main chat endpoint without Bubbletea components"""
    try:
        # Get AI interpretation
        ai_response = await ai_agent.interpret_command(request.message)
        action = ai_response.get("action", "unknown")
        task_content = ai_response.get("task")

        # Create a response message
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
        return f"⚠️ Error: {str(e)}"


@app.get("/health")
async def health():
    return {"status": "ok", "tasks_count": len(tasks)}

if __name__ == "__main__":
    
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
