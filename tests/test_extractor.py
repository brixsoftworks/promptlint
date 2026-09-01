from promptlint.extractor import extract_prompts_from_python


def test_extract_multiline_prompt():
    code = '''
PROMPT = """You are a helpful assistant.
Please do the task.
"""
'''
    prompts = extract_prompts_from_python(code)
    assert len(prompts) == 1
    assert "You are a helpful assistant" in prompts[0].text
    assert prompts[0].context_name == "PROMPT"


def test_extract_llm_function_call():
    code = """
def run():
    completion(
        model="gpt-4",
        prompt="Translate to French: Hello world"
    )
"""
    prompts = extract_prompts_from_python(code)
    assert len(prompts) == 1
    assert prompts[0].text == "Translate to French: Hello world"
    assert prompts[0].context_name == "completion(prompt=...)"


def test_extract_no_prompts():
    code = """
def run():
    x = 1 + 1
    y = "short string"
"""
    prompts = extract_prompts_from_python(code)
    assert len(prompts) == 0
