# 🤖 Personal CLI Assistant

> A smart, beautiful terminal companion — AI answers, web search, tasks, notes, file tools, and code helpers, all from your command line.

**By [@vieveksharmaa](https://github.com/vieveksharmaa)**  
Powered by [Groq](https://console.groq.com) (free API) + DuckDuckGo search

---

## ✨ Features

| Category | What it does |
|---|---|
| 🤖 **AI Ask** | Ask anything — auto web-augmented answers |
| 💬 **Chat** | Interactive session with memory + web search |
| 🔍 **Search** | Web search with rich table results (no key needed) |
| ✅ **Tasks** | Add, list, complete, and clear todos with priorities |
| 📝 **Notes** | Tagged notes you can search and filter |
| 🗂 **Files** | Find files by name, AI-summarize any file |
| ⚙ **Code** | Explain, generate, and debug code with AI |

---

## 🚀 Setup

### 1. Clone the repo
```bash
git clone https://github.com/vieveksharmaa/CLI-assistant.git
cd CLI-assistant
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

Or on Windows, just double-click **`install.bat`** — it installs everything and registers the `ai` command globally.

### 3. Get a free API key
Go to **[console.groq.com](https://console.groq.com)** → sign up → create an API key (free, no credit card).

### 4. Configure
```bash
ai config --api-key YOUR_GROQ_KEY
```

That's it — you're ready.

---

## 📖 All Commands

Run `ai` with no arguments to see the full command reference in your terminal.

### 🤖 AI & Search

```bash
# Ask anything (web-augmented by default)
ai ask "How does async/await work in Python?"
ai ask "What is the latest iPhone model?"
ai ask "Explain Docker in simple terms" --no-search

# Web search (no API key needed)
ai search "best open source LLMs 2025"
ai search "Python tutorials" -n 10
```

### 💬 Interactive Chat

```bash
ai chat
# Inside chat:
#   /search <query>  — search the web
#   /clear           — wipe message history
#   /exit            — quit
```

### ✅ Tasks

```bash
ai todo add "Fix the login bug" -p high
ai todo add "Read chapter 3"               # default priority: medium
ai todo list                               # show open tasks
ai todo list --all                         # include completed
ai todo list -p high                       # filter by priority
ai todo done 3                             # mark task #3 complete
ai todo remove 3                           # delete task #3
ai todo clear                              # remove all completed
```

### 📝 Notes

```bash
ai note add "Meeting at 3pm tomorrow" -t work
ai note add "API rate limit is 60 req/min" -t dev -t api
ai note list                               # all notes
ai note list -t dev                        # filter by tag
ai note list -s "rate limit"               # search text
ai note remove 2                           # delete note #2
```

### 🗂 Files

```bash
ai file find report                        # find files with "report" in name
ai file find config -e json                # only .json files
ai file find notes -d ~/Documents          # search in specific folder
ai file summarize meeting_notes.txt        # AI summary of any file
```

### ⚙ Code

```bash
ai code explain app.py                     # explain the whole file
ai code explain app.py -l 10-50            # explain lines 10–50
ai code generate "REST API with Flask"     # generate code
ai code generate "parse a CSV" -l go       # choose language
ai code generate "sort algo" -o sort.py    # save output to file
ai code debug app.py                       # find bugs
ai code debug app.py -e "TypeError: ..."  # debug with error context
```

### 🔧 Config

```bash
ai config --api-key YOUR_KEY               # set API key
ai config --model llama-3.1-8b-instant    # switch model (faster/lighter)
ai config --show                           # view current settings
```

---

## 🔑 Supported Models (Groq free tier)

| Model | Speed | Best for |
|---|---|---|
| `llama-3.3-70b-versatile` | Fast | General use (default) |
| `llama-3.1-8b-instant` | Very fast | Quick answers, chat |
| `mixtral-8x7b-32768` | Fast | Long context |
| `gemma2-9b-it` | Fast | Lightweight tasks |

Switch with: `ai config --model MODEL_NAME`

---

## 📁 Data Storage

All your data is stored locally in `~/.cli_assistant/`:

```
~/.cli_assistant/
├── config.json     ← API key + model setting
├── todos.json      ← your tasks
└── notes.json      ← your notes
```

No data leaves your machine except the AI queries sent to Groq.

---

## 🛠 Requirements

- Python 3.8+
- [groq](https://pypi.org/project/groq/) — AI backend
- [click](https://pypi.org/project/click/) — CLI framework
- [rich](https://pypi.org/project/rich/) — Beautiful terminal output
- [duckduckgo-search](https://pypi.org/project/duckduckgo-search/) — Free web search

---

## 📄 License

MIT — free to use, modify, and share.

---

<p align="center">Built with ❤️ by <a href="https://github.com/vivekjangiir">@vivekjangiir</a></p>
