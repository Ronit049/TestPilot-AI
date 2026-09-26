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
Project Diagram :
```
             👨‍💻 DEVELOPER
                   │
                   │ Python Code
                   ▼
          ┌─────────────────┐
          │ 🧠 CODE ANALYZER│
          └────────┬────────┘
                   │
             Testing Plan
                   ▼
          ┌─────────────────┐
          │ 🧪 TEST         │
          │    GENERATOR    │
          └────────┬────────┘
                   │
              PyTest Code
                   ▼
          ┌─────────────────┐
          │ ▶️ TEST RUNNER  │
          └────────┬────────┘
                   │
              Test Result
              /          \
           PASS            FAIL
            │                │
            │                ▼
            │       🔧 IMPROVEMENT
            │          AGENT
            │                │
            │                ▼
            │          Improved Test
            │                │
            └───────◄────────┘

```
# Why not Claude or GPT?
| Factor                            | Groq        | OpenAI GPT                          | Claude                              |
| --------------------------------- | ----------- | ----------------------------------- | ----------------------------------- |
| API integration                   | Simple      | Simple                              | Simple                              |
| Fast inference                    | Very strong | Strong                              | Strong                              |
| Code generation                   | Good        | Good/very strong depending on model | Good/very strong depending on model |
| Good for hackathon demo           | ✅          | ✅                                 | ✅                                   |
| Requires their respective API key | Yes         | Yes                                 | Yes                                 |
| Our current code                  | ✅          | ❌                                 | ❌                                   |


## Demo

Paste Python code, then click **Generate & Run Tests**. The app analyzes the code, generates pytest tests, executes them, and if they fail, asks the AI to improve the tests and runs them again.

This is a controlled hackathon prototype. Do not execute arbitrary untrusted code with this local subprocess runner in production.

## 👨‍💻 About the Author

Hi, I'm **Ronit Raj**, a Computer Science student and aspiring **Software & AI Developer** passionate about building practical projects and exploring **Agentic AI, Generative AI, Web Development, and Data Structures & Algorithms**.

I enjoy turning ideas into real-world applications, experimenting with new technologies, and continuously improving my problem-solving and development skills.

### 🚀 What I Work With
- 🐍 Python | C++ | Java | JavaScript
- 🤖 Generative AI | Agentic AI | LLM Applications
- 🌐 HTML | CSS | React | Tailwind CSS
- 🧠 Data Structures & Algorithms
- 🗄️ SQL | MySQL | MongoDB
- 🛠️ Git | GitHub | Linux | FastAPI

### 🔗 Connect With Me

- **GitHub:** [Ronit049](https://github.com/Ronit049)
- **LinkedIn:** [Ronit Raj](www.linkedin.com/in/ronit-raj7497)
- **Portfolio:** [rsr-portfolio.vercel.app](https://rsr-portfolio.vercel.app/)

> 💡 *Building, learning, and improving — one project at a time.*