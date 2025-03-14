<h1 align="center">AI Explore</h1>
<p align="center">
🤯 A code collection for learning and exploration.
</p>

## Quick start

### Prerequisites

- [uv](https://github.com/astral-sh/uv)
- [Python 3.11](https://www.python.org)
- API Key:
  - [Gemini API Key](https://aistudio.google.com/apikey)

### Run Repo

**Step 1**: Clone the repository

```bash
git clone https://github.com/lencx/ai-explore.git
cd ai-explore
```

**Step 2**: Copy `.env.example` to `.env`, and then set your API Key (e.g., `GEMINI_API_KEY`) in the `.env` file.

**Step 3**: Sync and activate a virtual environment

```bash
uv sync

# On macOS/Linux
source .venv/bin/activate

# On Windows (PowerShell)
.venv\Scripts\activate
```

**Step 4**: Run the script

```bash
python gemini/chat.py

# You can also run other scripts like:
# python gemini/another_script.py
```
