import argparse
import os
import sys
import json

from openai import OpenAI

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")


def read_file_contents(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as handle:
        return handle.read()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "Read",
                "description": "Read a file from disk and return its contents.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Absolute or relative path to the file to read.",
                        }
                    },
                    "required": ["file_path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "Write",
                "description": "Write contents to a file on disk.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Absolute or relative path to the file to write.",
                        },
                        "contents": {
                            "type": "string",
                            "description": "The contents to write to the file.",
                        },
                    },
                    "required": ["file_path", "contents"],
                },
            },
        }
    ]

    messages = [{"role": "user", "content": args.p}]

    while True:
        response = client.chat.completions.create(
            model="anthropic/claude-haiku-4.5",
            messages=messages,
            tools=tools,
        )

        if not response.choices:
            raise RuntimeError("no choices in response")

        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            break

        for tool_call in message.tool_calls:
            if tool_call.function.name != "Read", "Write":
                raise RuntimeError(f"unknown tool: {tool_call.function.name}")

            arguments = json.loads(tool_call.function.arguments or "{}")
            file_path = arguments.get("file_path")
            if not file_path:
                raise RuntimeError("Read tool requires file_path")

            file_contents = read_file_contents(file_path)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": file_contents,
                }
            )

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    # TODO: Uncomment the following line to pass the first stage

    print(message.content)


if __name__ == "__main__":
    main()
