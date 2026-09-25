# TestPilot AI — PS-10

Self-Improving Test Generation Agent for the 6-hour Agentic AI hackathon.

## Workflow

User Code → Code Analyzer Agent → Test Generator Agent → PyTest Runner → Failure Analyzer/Test Improver → Re-run Tests

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your Groq API key:

```env
GROQ_API_KEY=your_api_key_here
```

Run:

```bash
streamlit run app.py
```

## Demo

Paste Python code, then click **Generate & Run Tests**. The app analyzes the code, generates pytest tests, executes them, and if they fail, asks the AI to improve the tests and runs them again.

This is a controlled hackathon prototype. Do not execute arbitrary untrusted code with this local subprocess runner in production.
