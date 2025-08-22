import openai
from config import Config
import json
from typing import Dict, Any

class AIAgent:
    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

    async def interpret_command(self, user_input: str) -> Dict[str, Any]:
        """Interpret user command and return action"""
        try:
            response = self.client.chat.completions.create(
                model=Config.MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a task manager. Respond with JSON only.
                        Commands:
                        - "add [task]" -> {"action": "add", "task": "enhanced task"}
                        - "remove [task]" -> {"action": "remove", "task": "task name"}
                        - "show"/"list" -> {"action": "show", "task": null}
                        - "clear all" -> {"action": "clear", "task": null}
                        Make tasks actionable and clear. Example:
                        Input: "add buy milk" -> {"action": "add", "task": "Buy milk from store"}
                        """
                    },
                    {"role": "user", "content": user_input}
                ],
                max_tokens=100,
                temperature=0.3
            )
            content = response.choices[0].message.content.strip()
            return json.loads(content)
        except Exception as e:
            return {"action": "unknown", "task": None, "error": str(e)}
