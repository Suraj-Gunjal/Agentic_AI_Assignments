import os
from ollama import Client

from app.tools import TOOLS, FUNCTIONS


MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:3b"
)

SYSTEM_PROMPT = """
You are TodoPilot, an intelligent agentic command-line
to-do manager.

Your job is to understand the user's natural language
request and use the available tools to manage tasks.

Rules:

1. Use tools whenever the user wants to add, view,
   search, complete, delete or summarize tasks.

2. Never invent task IDs.

3. If the user refers to a task by its name, search
   for it first.

4. Never claim an action succeeded unless the tool
   actually succeeds.

5. Keep responses concise and useful.

6. Use get_summary when the user asks for statistics.

7. The task list is persistent and the tools contain
   the actual state.
"""


class TodoAgent:

    def __init__(self):

        self.client = Client(
            host=os.getenv(
                "OLLAMA_HOST",
                "http://localhost:11434"
            )
        )

        self.history = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

    def ask(self, message):

        self.history.append(
            {
                "role": "user",
                "content": message
            }
        )

        for _ in range(6):

            response = self.client.chat(
                model=MODEL,
                messages=self.history,
                tools=TOOLS,
                options={
                    "temperature": 0.2
                }
            )

            assistant_message = response["message"]

            self.history.append(
                assistant_message
            )

            tool_calls = assistant_message.get(
                "tool_calls",
                []
            )

            if not tool_calls:

                return assistant_message.get(
                    "content",
                    ""
                ).strip()

            for call in tool_calls:

                function_name = call["function"]["name"]

                arguments = call["function"].get(
                    "arguments",
                    {}
                )

                function = FUNCTIONS.get(
                    function_name
                )

                if function is None:

                    result = {
                        "error":
                        f"Unknown tool: {function_name}"
                    }

                else:

                    try:

                        result = function(
                            **arguments
                        )

                    except Exception as error:

                        result = {
                            "error": str(error)
                        }

                self.history.append(
                    {
                        "role": "tool",
                        "tool_name": function_name,
                        "content": str(result)
                    }
                )

        return (
            "I could not complete the operation. "
            "Please try again."
        )