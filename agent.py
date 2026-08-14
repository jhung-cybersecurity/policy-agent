from src.tools import TOOLS, run_tool
from dotenv import load_dotenv
load_dotenv()
import json
import anthropic

client = anthropic.Anthropic()
MAX_ITERS = 6

messages = [{"role": "user", "content": "Is water damage covered?"}]

SYSTEM = """You are an insurance policy assistant.

<rules>
1. read the reliable field in the result
2. answer only from retrieved chunks, never use your own knowledge of insurance, even if you know the answer.
3. if reliable is false, retry up to 2 times. A retry is either rephrasing the query or calling  list_documents and narrowing with doc_filter. After 2 failed retries, stop and tell the user no grounded source was found.
4. cite the source when reliable is true.
5. search first, only call list_documents if the search fails.
6. Never mention similarity scores, thresholds, or tool names in your answer to the user. Explain in plain language that no reliable source was found.
</rules>
"""

response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    system=SYSTEM,
    tools=TOOLS,
    messages=messages,
)

iters = 0
while response.stop_reason == "tool_use" and iters < MAX_ITERS:
    iters += 1
    tool_results = []

    # One response can contain MULTIPLE tool_use blocks. Handle all of them.
    for block in response.content:
        if block.type == "tool_use":
            print(f"[iter {iters}] {block.name}({block.input})")
            try:
                result = run_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })
            except Exception as exc:
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(exc),
                    "is_error": True,
                })

    messages.append({"role": "assistant", "content": response.content})
    messages.append({"role": "user", "content": tool_results})

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        system=SYSTEM,
        tools=TOOLS,
        messages=messages,
    )

for block in response.content:
    if block.type == "text":
        print(block.text)