from litellm import completion

PROMPT = """You are a helpful assistant.
Make it better.
"""

def generate():
    return completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Tell me a joke fast."}]
    )
