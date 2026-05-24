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

    chat = client.chat.completions.create(
        model="anthropic/claude-haiku-4.5",
        messages=[{"role": "user", "content": args.p}],
        while True,
            response = client.chat.completions.create(..., messages=messages, ...)
            message = response.choices[0].message
            if message.tool_calls:
                messages.append(message)
                break
            for tool_call in message.tool_calls:
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": None,
                    }
                )
        tools=[
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
            }
        ],
    )

    if not chat.choices or len(chat.choices) == 0:
        raise RuntimeError("no choices in response")

    message = chat.choices[0].message
    if message.tool_calls:
        tool_messages = []
        for tool_call in message.tool_calls:
            if tool_call.function.name != "Read":
                raise RuntimeError(f"unknown tool: {tool_call.function.name}")

            arguments = json.loads(tool_call.function.arguments or "{}")
            file_path = arguments.get("file_path")
            if not file_path:
                raise RuntimeError("Read tool requires file_path")

            file_contents = read_file_contents(file_path)
            tool_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": file_contents,
                }
            )

        chat = client.chat.completions.create(
            model="anthropic/claude-haiku-4.5",
            messages=[
                {"role": "user", "content": args.p},
                message,
                *tool_messages,
            ],
        )

        if not chat.choices or len(chat.choices) == 0:
            raise RuntimeError("no choices after tool call")

        message = chat.choices[0].message

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    # TODO: Uncomment the following line to pass the first stage

    print(message.content)


if __name__ == "__main__":
    main()
