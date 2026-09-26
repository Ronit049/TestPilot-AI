import os
import re
import subprocess
import sys
import tempfile

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

st.set_page_config(
    page_title="TestPilot AI",
    page_icon="🧪",
    layout="wide"
)

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

MODEL = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """
You are TestPilot AI, an expert Python software testing agent.

Your job is to:
1. Analyze Python source code.
2. Identify functions, branches, edge cases and invalid inputs.
3. Generate high-quality pytest test cases.
4. Analyze test execution failures.
5. Improve the generated tests based on actual execution feedback.

Always return clean Python code when code is requested.
Do not use markdown code fences when returning test code.
Generated tests must import the source module using:

from target import ...

The source file will always be named target.py.
"""


# ---------------------------------------------------------
# Session State
# ---------------------------------------------------------

if "analysis" not in st.session_state:
    st.session_state.analysis = ""

if "generated_tests" not in st.session_state:
    st.session_state.generated_tests = ""

if "execution_result" not in st.session_state:
    st.session_state.execution_result = ""

if "final_code" not in st.session_state:
    st.session_state.final_code = ""


# ---------------------------------------------------------
# Groq Client
# ---------------------------------------------------------

def get_client():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        st.error(
            "GROQ_API_KEY not found. "
            "Please create a .env file and add your Groq API key."
        )
        st.stop()

    return Groq(api_key=api_key)


# ---------------------------------------------------------
# AI Function
# ---------------------------------------------------------

def ask_ai(prompt):

    client = get_client()

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# ---------------------------------------------------------
# Clean AI Code
# ---------------------------------------------------------

def clean_code(code):

    code = code.strip()

    # Remove markdown code fences if AI returns them
    code = re.sub(r"^```python\s*", "", code)
    code = re.sub(r"^```\s*", "", code)
    code = re.sub(r"\s*```$", "", code)

    return code.strip()

def limit_test_code(code):
    lines = code.splitlines()

    # Remove excessive blank lines
    cleaned = []
    previous_blank = False

    for line in lines:
        if not line.strip():
            if previous_blank:
                continue
            previous_blank = True
        else:
            previous_blank = False

        cleaned.append(line)

    return "\n".join(cleaned).strip()

# ---------------------------------------------------------
# Analyze Source Code
# ---------------------------------------------------------

def analyze_code(source_code):

    prompt = f"""
Analyze the following Python source code.

SOURCE CODE:

{source_code}

Provide:

1. Functions/classes present
2. Inputs and outputs
3. Normal cases
4. Edge cases
5. Invalid inputs
6. Important branches
7. Potential bugs or risky assumptions
8. Recommended test scenarios

Do not generate test code yet.
"""

    return ask_ai(prompt)


# ---------------------------------------------------------
# Generate Tests
# ---------------------------------------------------------

def generate_tests(source_code, analysis):

    prompt = f"""
You are a concise Python testing agent.

SOURCE CODE:
{source_code}

ANALYSIS:
{analysis}

Generate a SMALL and CLEAN pytest test file.

Rules:
- Create only the most important tests.
- Maximum 3-5 test functions.
- Prefer simple readable tests.
- Cover normal case and important edge case.
- Do not test every possible input.
- Do not create unnecessary helper functions.
- Do not create long explanations.
- Import only from `target`.
- Keep the generated code short.
- Return ONLY Python code.
- Do NOT use markdown code fences.

The final test code should be roughly similar in size and simplicity
to the input code.
"""

    return limit_test_code(clean_code(ask_ai(prompt)))

# ---------------------------------------------------------
# Run Pytest
# ---------------------------------------------------------

def run_tests(source_code, test_code):

    with tempfile.TemporaryDirectory() as temp_dir:

        target_path = os.path.join(
            temp_dir,
            "target.py"
        )

        test_path = os.path.join(
            temp_dir,
            "test_generated.py"
        )

        # Write source code
        with open(
            target_path,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(source_code)

        # Write generated tests
        with open(
            test_path,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(test_code)

        try:

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "test_generated.py",
                    "-q"
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=20
            )

            output = (
                result.stdout
                + "\n"
                + result.stderr
            )

            return output.strip()

        except subprocess.TimeoutExpired:

            return "ERROR: Test execution timed out."


# ---------------------------------------------------------
# Improve Tests
# ---------------------------------------------------------

def improve_source_code(
    source_code,
    test_code,
    execution_result
):

    prompt = f"""
You are TestPilot AI's Code Improvement Agent.

ORIGINAL SOURCE CODE:
{source_code}

GENERATED TESTS:
{test_code}

TEST EXECUTION RESULT:
{execution_result}

Improve the ORIGINAL SOURCE CODE based on the test results.

Rules:
- Return the complete improved source code.
- Do NOT return pytest tests.
- Do NOT return test cases.
- Do NOT include explanations.
- Do NOT use markdown code fences.
- Keep the original function names.
- Make only necessary changes.
- Keep the code clean and concise.
- Return ONLY valid Python source code.
"""

    return clean_code(ask_ai(prompt))

# ---------------------------------------------------------
# UI
# ---------------------------------------------------------

st.title("🧪 TestPilot AI")

st.markdown(
    """
### Self-Improving Test Generation Agent

**Analyze → Generate → Execute → Observe → Improve**
"""
)

st.divider()


# ---------------------------------------------------------
# Source Code Input
# ---------------------------------------------------------

st.subheader("💻 Enter Python Source Code")

default_code = """def add(a, b):
    return a + b


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
"""

source_code = st.text_area(
    "Python source code",
    value=default_code,
    height=250,
    placeholder="Paste your Python code here..."
)


# ---------------------------------------------------------
# Main Button
# ---------------------------------------------------------

if st.button(
    "🚀 Generate, Run & Improve",
    type="primary",
    use_container_width=True
):

    if not source_code.strip():

        st.warning("Please enter Python source code.")

    else:

        # Reset old results
        st.session_state.analysis = ""
        st.session_state.generated_tests = ""
        st.session_state.execution_result = ""
        st.session_state.final_code = ""

        # -------------------------------------------------
        # Step 1: Analyze
        # -------------------------------------------------

        with st.spinner("🧠 AI is analyzing your code..."):

            analysis = analyze_code(source_code)

        st.session_state.analysis = analysis

        # -------------------------------------------------
        # Step 2: Generate Tests
        # -------------------------------------------------

        with st.spinner("🧪 AI is generating pytest tests..."):

            generated_tests = generate_tests(
                source_code,
                analysis
            )

        st.session_state.generated_tests = generated_tests

        # -------------------------------------------------
        # Step 3: Execute Tests
        # -------------------------------------------------

        with st.spinner("▶️ Running generated tests..."):

            execution_result = run_tests(
                source_code,
                generated_tests
            )

        st.session_state.execution_result = execution_result

        # -------------------------------------------------
        # Step 4: Self Improvement
        # -------------------------------------------------

        failed = (
            "failed" in execution_result.lower()
            or "error" in execution_result.lower()
            or "error" in execution_result.lower()
        )

    if failed:

        # -------------------------------------------------
        # Step 4: Improve ORIGINAL SOURCE CODE
        # -------------------------------------------------

        with st.spinner(
            "🔄 Tests failed. AI is improving the source code..."
        ):

            improved_source = improve_source_code(
                source_code,
                generated_tests,
                execution_result
            )

        # Store improved SOURCE CODE as final result
        st.session_state.final_code = improved_source

        # -------------------------------------------------
        # Step 5: Test the Improved Source Code
        # -------------------------------------------------

        with st.spinner(
            "▶️ Testing the improved source code..."
        ):

            improved_result = run_tests(
                improved_source,
                generated_tests
            )

        st.session_state.execution_result = (
            "INITIAL RUN:\n\n"
            + execution_result
            + "\n\n"
            + "=" * 60
            + "\n\n"
            + "IMPROVED CODE RUN:\n\n"
            + improved_result
        )

    else:

        # Tests passed, so original source code is already valid
        st.session_state.final_code = source_code


# ---------------------------------------------------------
# Results
# ---------------------------------------------------------

if st.session_state.analysis:

    st.divider()

    st.subheader("🧠 1. AI Code Analysis")

    st.markdown(
        st.session_state.analysis
    )


# ---------------------------------------------------------
# Generated Tests
# ---------------------------------------------------------

if st.session_state.generated_tests:

    st.divider()

    st.subheader("🧪 2. AI-Generated Test Code")

    st.code(
        st.session_state.generated_tests,
        language="python"
    )

    st.download_button(
        "⬇️ Download Generated Tests",
        data=st.session_state.generated_tests,
        file_name="generated_tests.py",
        mime="text/x-python",
        key="download_generated"
    )


# ---------------------------------------------------------
# Execution Result
# ---------------------------------------------------------

if st.session_state.execution_result:

    st.divider()

    st.subheader("▶️ 3. Test Execution Result")

    if "failed" in st.session_state.execution_result.lower():

        st.error("Some tests failed.")

    elif "error" in st.session_state.execution_result.lower():

        st.warning("Execution completed with errors.")

    else:

        st.success("Tests executed successfully.")

    st.code(
        st.session_state.execution_result,
        language="text"
    )


# ---------------------------------------------------------
# FINAL RESULTED CODE
# ---------------------------------------------------------

if st.session_state.final_code:

    st.divider()

    st.subheader("🎯 4. Final Resulted Code")

    st.success(
        "This is the final test code produced by TestPilot AI "
        "after the self-improvement workflow."
    )

    st.code(
        st.session_state.final_code,
        language="python"
    )

    st.download_button(
        "⬇️ Download Final Resulted Code",
        data=st.session_state.final_code,
        file_name="final_tests.py",
        mime="text/x-python",
        key="download_final"
    )


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.divider()

st.caption(
    "TestPilot AI • Self-Improving Test Generation Agent • "
    "Hackathon Prototype"
)