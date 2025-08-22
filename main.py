from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict, Any

from ai_agent import AIAgent
from config import Config
from datetime import datetime
import uuid

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

@app.post("/chat")
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    try:
        # Get AI interpretation
        ai_response = await ai_agent.interpret_command(request.message)
        action = ai_response.get("action", "unknown")
        task_content = ai_response.get("task")

        # Execute action
        if action == "add" and task_content:
            task = create_task(task_content)
            message = f"✅ Added: {task.content}"
        elif action == "remove" and task_content:
            removed = find_and_remove_task(task_content)
            message = f"✅ Removed: {task_content}" if removed else f"❌ Not found: {task_content}"
        elif action == "show":
            if tasks:
                task_list = "\n".join([f"• {task.content}" for task in tasks])
                message = f"📋 Tasks ({len(tasks)}):\n{task_list}"
            else:
                message = "📋 No tasks found"
        elif action == "clear":
            count = len(tasks)
            tasks.clear()
            message = f"🗑️ Cleared {count} tasks"
        else:
            message = "❓ Try: 'add [task]', 'show tasks', 'remove [task]', or 'clear all'"

        return {
            "response": message,
            "action": action,
            "tasks": [{"id": t.id, "content": t.content, "created_at": t.created_at} for t in tasks]
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "tasks_count": len(tasks)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
