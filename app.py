import os
import re
import subprocess
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

st.set_page_config(page_title="TestPilot AI", page_icon="🧪", layout="wide")

SYSTEM_PROMPT = '''You are TestPilot, an AI software testing agent.
Your job is to analyze Python source code, generate pytest tests, inspect test failures,
and improve the tests. Return practical, runnable Python code.
Never modify the user's source code unless explicitly asked.
'''


def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


def ask_llm(prompt: str) -> str:
    client = get_client()
    if client is None:
        raise RuntimeError("GROQ_API_KEY is missing. Add it to your .env file.")

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


def clean_code(text: str) -> str:
    match = re.search(r"```python\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"```\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def analyze_code(source_code: str) -> str:
    prompt = f'''Analyze this Python source code for testing purposes.

Identify:
1. Functions/classes that should be tested.
2. Normal cases.
3. Edge cases.
4. Invalid-input cases.
5. Important branches that may need coverage.

Give a concise testing plan.

SOURCE CODE:
```python
{source_code}
```'''
    return ask_llm(prompt)


def generate_tests(source_code: str, analysis: str) -> str:
    prompt = f'''Generate a runnable pytest test file for the following Python source code.

Rules:
- The source file is ALWAYS named `target.py`.
- Import functions ONLY using:
  from target import ...
- Generate runnable pytest code.
- Do not use `mymodule`.
- Do not use markdown outside the code block.
- Return ONLY the pytest Python code.

TESTING ANALYSIS:
{analysis}

SOURCE CODE:
```python
{source_code}
```'''
    return clean_code(ask_llm(prompt))


def improve_tests(source_code: str, test_code: str, test_output: str) -> str:
    prompt = f'''The generated pytest suite has produced the following execution result.

Improve the tests while preserving the original testing goal.

Rules:
- Fix incorrect imports, assertions, assumptions, or test inputs.
- Add a missing edge case if the failure reveals one.
- Return ONLY the complete replacement pytest file.
- Assume the source file is `target.py`.

SOURCE CODE:
```python
{source_code}
```

CURRENT TESTS:
```python
{test_code}
```

TEST EXECUTION RESULT:
```text
{test_output}
```'''
    return clean_code(ask_llm(prompt))


def run_tests(source_code: str, test_code: str):
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "target.py").write_text(source_code, encoding="utf-8")
        (tmp_path / "test_generated.py").write_text(test_code, encoding="utf-8")
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "test_generated.py", "-q"],
                cwd=tmp,
                capture_output=True,
                text=True,
                timeout=20,
            )
            return {
                "passed": result.returncode == 0,
                "returncode": result.returncode,
                "output": (result.stdout + "\n" + result.stderr).strip(),
            }
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "returncode": -1,
                "output": "Test execution timed out after 20 seconds.",
            }


st.title("🧪 TestPilot AI")
st.caption("Self-Improving Test Generation Agent — PS-10")
st.info("Workflow: Code Analyzer → Test Generator → Test Runner → Failure Analyzer → Test Improver")

with st.sidebar:
    st.header("⚙️ Setup")
    st.code("GROQ_API_KEY=your_api_key_here", language="text")
    st.code("pip install -r requirements.txt", language="bash")
    st.code("streamlit run app.py", language="bash")

default_code = """def add(a, b):
    return a + b


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def is_even(n):
    return n % 2 == 0
"""

source_code = st.text_area("Paste your Python source code", value=default_code, height=300)

if "analysis" not in st.session_state:
    st.session_state.analysis = ""
if "tests" not in st.session_state:
    st.session_state.tests = ""
if "result" not in st.session_state:
    st.session_state.result = None
if "iterations" not in st.session_state:
    st.session_state.iterations = 0

col1, col2 = st.columns(2)
with col1:
    analyze_btn = st.button("🔍 Analyze Code", use_container_width=True)
with col2:
    generate_btn = st.button("🚀 Generate & Run Tests", use_container_width=True)

if analyze_btn:
    if not source_code.strip():
        st.warning("Please enter Python code.")
    else:
        with st.spinner("Analyzer Agent is analyzing the code..."):
            try:
                st.session_state.analysis = analyze_code(source_code)
                st.success("Analysis completed.")
            except Exception as e:
                st.error(str(e))

if generate_btn:
    if not source_code.strip():
        st.warning("Please enter Python code.")
    else:
        try:
            with st.spinner("Agent 1: analyzing code..."):
                analysis = analyze_code(source_code)
                st.session_state.analysis = analysis
            with st.spinner("Agent 2: generating pytest tests..."):
                tests = generate_tests(source_code, analysis)
                st.session_state.tests = tests
            with st.spinner("Test Runner: executing generated tests..."):
                result = run_tests(source_code, tests)
                st.session_state.result = result

            if not result["passed"]:
                with st.spinner("Agent 3: analyzing failure and improving tests..."):
                    improved_tests = improve_tests(source_code, tests, result["output"])
                st.session_state.tests = improved_tests
                st.session_state.iterations = 1
                with st.spinner("Test Runner: running improved tests..."):
                    st.session_state.result = run_tests(source_code, improved_tests)
            else:
                st.session_state.iterations = 0
            st.success("Agent workflow completed.")
        except Exception as e:
            st.error(f"Workflow error: {e}")

if st.session_state.analysis:
    st.subheader("🧠 Agent Analysis")
    st.markdown(st.session_state.analysis)

if st.session_state.tests:
    st.subheader("🧪 Generated PyTest Suite")
    st.code(st.session_state.tests, language="python")

if st.session_state.result:
    result = st.session_state.result
    st.subheader("📊 Test Result")
    if result["passed"]:
        st.success("All generated tests passed.")
    else:
        st.error("Some tests failed after the improvement cycle.")
    st.write(f"Improvement iterations: **{st.session_state.iterations}**")
    with st.expander("Execution Output"):
        st.code(result["output"], language="text")

st.divider()
st.caption("Hackathon prototype — PS-10: Self-Improving Test Generation Agent")
