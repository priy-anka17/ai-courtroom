# ⚖️ AI Courtroom — Multi-Agent Debate Arena

A cutting-edge multi-agent AI system that simulates a **full courtroom trial** on any claim or topic. Five specialized AI agents collaborate through a LangGraph state machine to research, argue, cross-examine, and deliver a verdict.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-courtroom.streamlit.app)

## 🏛️ How It Works

```
User's Claim → 🔍 Research → 🔴 Prosecution → 🟢 Defense → ⚔️ Cross-Exam → ⚖️ Verdict
```

| Agent | Role | Description |
|-------|------|-------------|
| 🔍 **Research Clerk** | Evidence Gathering | Searches the web for real evidence on both sides |
| 🔴 **Prosecution** | Argues FOR | Builds the strongest case supporting the claim |
| 🟢 **Defense** | Argues AGAINST | Dismantles the prosecution's case with counter-evidence |
| ⚔️ **Cross-Examiner** | Analysis | Identifies weaknesses, logical fallacies in both arguments |
| ⚖️ **Judge** | Final Verdict | Weighs all evidence and delivers SUSTAINED / OVERRULED / PARTIALLY SUSTAINED |

## 🚀 Tech Stack

- **LangGraph** — State machine orchestration for the 5-agent pipeline
- **Groq / Llama 3.1** — Ultra-fast LLM inference for all agents
- **LangChain** — Agent framework and prompt management
- **DuckDuckGo Search** — Real-time web evidence gathering
- **Streamlit** — Courtroom-themed interactive UI
- **Plotly** — Radar charts & score visualizations

## 📊 Features

- **Live courtroom simulation** with 5 specialized AI agents
- **Real web evidence** — agents search the internet for facts and data
- **Adversarial debate** — prosecution and defense argue opposing sides
- **Cross-examination analysis** — identifies logical fallacies and weak arguments
- **Visual verdict dashboard** — radar charts, confidence scores, argument comparisons
- **Trial history** — track past debates and verdicts
- **8 sample debate topics** built-in

## 🛠️ Setup

```bash
# Clone the repo
git clone https://github.com/priy-anka17/ai-courtroom.git
cd ai-courtroom

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .\.venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -r requirements.txt

# Add your Groq API key
cp .env.example .env
# Edit .env and add your key

# Run the app
streamlit run app.py
```

## 🔑 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Your Groq API key ([get one free](https://console.groq.com/keys)) | Required |
| `LLM_MODEL` | LLM model name | `llama-3.1-8b-instant` |

## 📁 Project Structure

```
ai-courtroom/
├── app.py                 # Streamlit UI with courtroom theme
├── config.py              # Configuration and environment loading
├── agents/
│   ├── __init__.py        # Package exports
│   ├── graph.py           # LangGraph state machine (5-node pipeline)
│   ├── nodes.py           # Agent node functions (research, prosecution, defense, cross-exam, judge)
│   └── tools.py           # DuckDuckGo search tools
├── .streamlit/config.toml # Dark courtroom theme
├── requirements.txt       # Python dependencies
└── README.md
```

## 🎯 Sample Debates

Try these claims in the courtroom:
- *"AI will replace most white-collar jobs within 10 years"*
- *"Remote work is more productive than office work"*
- *"Cryptocurrency will eventually replace traditional banking"*
- *"Nuclear energy is the best solution to climate change"*
- *"Universal Basic Income is economically viable and necessary"*

## 📜 License

MIT
