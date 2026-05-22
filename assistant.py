#!/usr/bin/env python3
# @vivekjangiir
"""
Personal CLI Assistant
━━━━━━━━━━━━━━━━━━━━━
Author  : @vivekjangiir
GitHub  : https://github.com/vivekjangiir/CLI-assistant
Powered by Groq (free) + DuckDuckGo search
"""

import datetime
import json
import os
import sys
from pathlib import Path

import click
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

CONFIG_DIR  = Path.home() / ".cli_assistant"
CONFIG_FILE = CONFIG_DIR / "config.json"
TODOS_FILE  = CONFIG_DIR / "todos.json"
NOTES_FILE  = CONFIG_DIR / "notes.json"

console = Console()

BANNER = """[bold cyan]
  ██████╗██╗     ██╗      █████╗ ███████╗███████╗████████╗
 ██╔════╝██║     ██║     ██╔══██╗██╔════╝██╔════╝╚══██╔══╝
 ██║     ██║     ██║     ███████║███████╗███████╗   ██║
 ██║     ██║     ██║     ██╔══██║╚════██║╚════██║   ██║
 ╚██████╗███████╗███████╗██║  ██║███████║███████║   ██║
  ╚═════╝╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝[/bold cyan]
[dim]  Personal CLI Assistant  •  by [bold]@vivekjangiir[/bold]  •  v1.0.0[/dim]"""


def show_welcome():
    console.print(BANNER)
    t = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan",
              border_style="cyan", expand=True)
    t.add_column("Command",     style="bold white", no_wrap=True)
    t.add_column("Description", style="white")
    t.add_column("Example",     style="dim",        no_wrap=True)

    rows = [
        ('ask [cyan]"question"[/cyan]',       "Ask AI anything (web-augmented)",             'ai ask "How does async work?"'),
        ("chat",                               "Interactive AI chat session",                  "ai chat"),
        ('search [cyan]"query"[/cyan]',        "Search the web (no key needed)",               'ai search "best Python libs"'),
        ('todo add [cyan]"task"[/cyan]',       "Add a task  [-p low/medium/high]",             'ai todo add "Fix bug" -p high'),
        ("todo list",                          "List open tasks  [--all]",                     "ai todo list"),
        ("todo done [cyan]<id>[/cyan]",        "Mark a task complete",                         "ai todo done 3"),
        ("todo remove [cyan]<id>[/cyan]",      "Delete a task",                                "ai todo remove 3"),
        ("todo clear",                         "Remove all completed tasks",                   "ai todo clear"),
        ('note add [cyan]"text"[/cyan]',       "Save a quick note  [-t tag]",                  'ai note add "key=X" -t dev'),
        ("note list",                          "Browse notes  [-t tag] [-s search]",           "ai note list -t dev"),
        ("note remove [cyan]<id>[/cyan]",      "Delete a note",                                "ai note remove 2"),
        ("file find [cyan]<pattern>[/cyan]",   "Find files by name  [-e ext] [-d dir]",        "ai file find report -e pdf"),
        ("file summarize [cyan]<path>[/cyan]", "AI summary of any file",                       "ai file summarize notes.txt"),
        ("code explain [cyan]<file>[/cyan]",   "Explain code  [-l line-range]",                "ai code explain app.py -l 1-40"),
        ('code generate [cyan]"desc"[/cyan]',  "Generate code from plain English  [-l lang]",  'ai code generate "parse JSON" -l go'),
        ("code debug [cyan]<file>[/cyan]",     "Find bugs  [-e error-message]",                "ai code debug app.py"),
        ("config --api-key [cyan]KEY[/cyan]",  "Set your Groq API key (one-time)",             "ai config --api-key YOUR_KEY"),
        ("config --show",                      "Show current settings",                         "ai config --show"),
    ]

    sections = {0: "🤖  AI & Search", 3: "✅  Tasks", 8: "📝  Notes",
                11: "🗂  Files", 13: "⚙  Code", 16: "🔧  Config"}
    for i, (cmd, desc, ex) in enumerate(rows):
        if i in sections:
            t.add_section()
            t.add_row(f"[bold yellow]{sections[i]}[/bold yellow]", "", "")
        t.add_row(cmd, desc, ex)

    console.print(t)
    console.print(
        "\n[dim]Tip: run [bold]ai config --api-key YOUR_KEY[/bold] once, "
        "then every command above works.  Free key → [cyan]https://console.groq.com[/cyan][/dim]\n"
    )


# ── config helpers ────────────────────────────

def ensure_config():
    CONFIG_DIR.mkdir(exist_ok=True)
    if not TODOS_FILE.exists(): TODOS_FILE.write_text("[]")
    if not NOTES_FILE.exists(): NOTES_FILE.write_text("[]")
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(json.dumps(
            {"api_key": "", "model": "llama-3.3-70b-versatile"}, indent=2))


def load_config() -> dict:
    ensure_config()
    return json.loads(CONFIG_FILE.read_text())


def save_config(cfg: dict):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))


def _load_dotenv():
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def get_groq_client():
    _load_dotenv()
    cfg = load_config()
    api_key = cfg.get("api_key") or os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        console.print(Panel(
            "[bold red]No API key set![/bold red]\n\n"
            "1. Get a [bold]free[/bold] key at [cyan]https://console.groq.com[/cyan]\n"
            "2. Run: [bold]ai config --api-key YOUR_KEY[/bold]",
            border_style="red", title="Setup Required"))
        sys.exit(1)
    try:
        from groq import Groq
    except ImportError:
        console.print("[red]groq not installed. Run: pip install groq[/red]")
        sys.exit(1)
    return Groq(api_key=api_key), cfg.get("model", "llama-3.3-70b-versatile")


# ── AI ────────────────────────────────────────

def ask_ai(prompt: str, system: str = None, context: str = None) -> str:
    client, model = get_groq_client()
    system = system or "You are a helpful personal assistant. Be concise and practical. Use markdown."
    messages = [{"role": "system", "content": system}]
    if context:
        messages.append({"role": "user", "content": f"Context:\n{context}\n\nQuestion: {prompt}"})
    else:
        messages.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(model=model, messages=messages, max_tokens=2048)
    return resp.choices[0].message.content


# ── Web search ────────────────────────────────

def web_search(query: str, max_results: int = 5) -> list:
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results))
    except Exception:
        return []


# ── Todo / Note helpers ───────────────────────

def load_todos()  -> list: ensure_config(); return json.loads(TODOS_FILE.read_text())
def save_todos(t: list):    TODOS_FILE.write_text(json.dumps(t, indent=2))
def load_notes()  -> list: ensure_config(); return json.loads(NOTES_FILE.read_text())
def save_notes(n: list):    NOTES_FILE.write_text(json.dumps(n, indent=2))
def next_id(items: list) -> int: return max((i.get("id", 0) for i in items), default=0) + 1


# ══════════════════════════════════════════════
# CLI root
# ══════════════════════════════════════════════

@click.group(invoke_without_command=True)
@click.version_option("1.0.0", prog_name="ai")
@click.pass_context
def cli(ctx):
    """🤖  Personal CLI Assistant by @vivekjangiir"""
    ensure_config()
    if ctx.invoked_subcommand is None:
        show_welcome()


# ── config ────────────────────────────────────

@cli.command()
@click.option("--api-key", help="Your Groq API key")
@click.option("--model",   help="Model name")
@click.option("--show",    is_flag=True)
def config(api_key, model, show):
    """Configure your API key and model."""
    cfg = load_config()
    if api_key:
        cfg["api_key"] = api_key; save_config(cfg)
        console.print("[green]✓ API key saved.[/green]")
    if model:
        cfg["model"] = model; save_config(cfg)
        console.print(f"[green]✓ Model set to {model}[/green]")
    if show or (not api_key and not model):
        t = Table(title="⚙  Configuration", box=box.ROUNDED, border_style="cyan")
        t.add_column("Setting", style="cyan"); t.add_column("Value")
        t.add_row("Config dir", str(CONFIG_DIR))
        t.add_row("Model", cfg.get("model", "llama-3.3-70b-versatile"))
        masked = ("●" * 16 + cfg["api_key"][-4:]) if cfg.get("api_key") else "[red]not set[/red]"
        t.add_row("API key", masked)
        console.print(t)
        console.print("\n[dim]Free key → https://console.groq.com[/dim]")


# ── ask ───────────────────────────────────────

@cli.command()
@click.argument("question", nargs=-1, required=True)
@click.option("--no-search", is_flag=True, help="Skip web search context")
def ask(question, no_search):
    """Ask the AI anything (web-augmented by default)."""
    q = " ".join(question)
    context = None
    with console.status("[cyan]Thinking...[/cyan]"):
        if not no_search:
            results = web_search(q, max_results=3)
            if results:
                context = "Web results:\n" + "\n".join(
                    f"- {r.get('title','')}: {r.get('body','')[:250]}" for r in results)
        answer = ask_ai(q, context=context)
    console.print(Panel(Markdown(answer), title="[bold cyan]Assistant[/bold cyan]", border_style="cyan"))


# ── search ────────────────────────────────────

@cli.command()
@click.argument("query", nargs=-1, required=True)
@click.option("-n", "--results", default=6, show_default=True)
def search(query, results):
    """Search the web (no API key needed)."""
    q = " ".join(query)
    with console.status(f"[cyan]Searching '{q}'...[/cyan]"):
        hits = web_search(q, max_results=results)
    if not hits:
        console.print("[yellow]No results found.[/yellow]"); return
    t = Table(title=f"🔍  {q}", box=box.ROUNDED, show_header=True, show_lines=True, expand=True)
    t.add_column("#",       style="dim",       width=3)
    t.add_column("Title",   style="bold white", ratio=3)
    t.add_column("Summary", style="white",      ratio=5)
    t.add_column("URL",     style="cyan dim",   ratio=4)
    for i, r in enumerate(hits, 1):
        t.add_row(str(i), (r.get("title") or "")[:70],
                  (r.get("body") or "")[:160] + "...", (r.get("href") or "")[:80])
    console.print(t)


# ── todo ──────────────────────────────────────

@cli.group()
def todo():
    """Manage your todo list."""


@todo.command("add")
@click.argument("task", nargs=-1, required=True)
@click.option("-p","--priority", type=click.Choice(["low","medium","high"]), default="medium", show_default=True)
def todo_add(task, priority):
    """Add a task."""
    todos = load_todos()
    item  = {"id": next_id(todos), "task": " ".join(task), "done": False,
             "priority": priority, "created": datetime.datetime.now().strftime("%Y-%m-%d")}
    todos.append(item); save_todos(todos)
    c = {"high":"red","medium":"yellow","low":"green"}[priority]
    console.print(f"[green]✓ Added[/green]  [{c}]{priority}[/{c}]  —  {item['task']}")


@todo.command("list")
@click.option("-a","--all","show_all", is_flag=True)
@click.option("-p","--priority", type=click.Choice(["low","medium","high"]))
def todo_list(show_all, priority):
    """List your tasks."""
    todos = load_todos()
    if priority: todos = [t for t in todos if t["priority"] == priority]
    if not show_all: todos = [t for t in todos if not t["done"]]
    if not todos:
        console.print("[dim]Nothing here. Add: ai todo add 'your task'[/dim]"); return
    colors = {"high":"red","medium":"yellow","low":"green"}
    t = Table(title="📋  Todo List", box=box.ROUNDED, border_style="cyan")
    t.add_column("ID", style="dim", width=4); t.add_column("", width=2)
    t.add_column("Priority", width=8); t.add_column("Task")
    t.add_column("Date", style="dim", width=11)
    for item in todos:
        c = colors.get(item["priority"],"white")
        text = f"[dim]{item['task']}[/dim]" if item["done"] else item["task"]
        t.add_row(str(item["id"]), "✅" if item["done"] else "⬜",
                  f"[{c}]{item['priority']}[/{c}]", text, item.get("created",""))
    console.print(t)


@todo.command("done")
@click.argument("task_id", type=int)
def todo_done(task_id):
    """Mark a task as done."""
    todos = load_todos()
    for item in todos:
        if item["id"] == task_id:
            item["done"] = True; save_todos(todos)
            console.print(f"[green]✅ Done:[/green] {item['task']}"); return
    console.print(f"[red]Task {task_id} not found.[/red]")


@todo.command("remove")
@click.argument("task_id", type=int)
def todo_remove(task_id):
    """Delete a task."""
    save_todos([t for t in load_todos() if t["id"] != task_id])
    console.print(f"[green]✓ Removed task {task_id}[/green]")


@todo.command("clear")
@click.confirmation_option(prompt="Remove all completed tasks?")
def todo_clear():
    """Remove all completed tasks."""
    save_todos([t for t in load_todos() if not t["done"]])
    console.print("[green]✓ Cleared completed tasks.[/green]")


# ── note ──────────────────────────────────────

@cli.group()
def note():
    """Save and search quick notes."""


@note.command("add")
@click.argument("text", nargs=-1, required=True)
@click.option("-t","--tag", multiple=True)
def note_add(text, tag):
    """Save a note."""
    notes = load_notes()
    item  = {"id": next_id(notes), "text": " ".join(text), "tags": list(tag),
             "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
    notes.append(item); save_notes(notes)
    console.print("[green]✓ Note saved.[/green]")


@note.command("list")
@click.option("-t","--tag")
@click.option("-s","--search","term")
def note_list(tag, term):
    """List your notes."""
    notes = load_notes()
    if tag:  notes = [n for n in notes if tag in n.get("tags",[])]
    if term: notes = [n for n in notes if term.lower() in n["text"].lower()]
    if not notes:
        console.print("[dim]No notes found.[/dim]"); return
    for n in notes:
        tags_str = "  ".join(f"[cyan]#{t}[/cyan]" for t in n.get("tags",[]))
        console.print(Panel(f"{n['text']}\n\n[dim]{n['created']}[/dim]  {tags_str}",
                            title=f"[bold]Note #{n['id']}[/bold]", border_style="blue"))


@note.command("remove")
@click.argument("note_id", type=int)
def note_remove(note_id):
    """Delete a note."""
    save_notes([n for n in load_notes() if n["id"] != note_id])
    console.print(f"[green]✓ Removed note {note_id}[/green]")


# ── file ──────────────────────────────────────

@cli.group()
def file():
    """File and folder utilities."""


@file.command("find")
@click.argument("pattern")
@click.option("-d","--dir","search_dir", default=".", show_default=True)
@click.option("-e","--ext")
@click.option("-n","--limit", default=40, show_default=True)
def file_find(pattern, search_dir, ext, limit):
    """Find files by name pattern."""
    glob = f"**/*{pattern}*.{ext}" if ext else f"**/*{pattern}*"
    hits = list(Path(search_dir).expanduser().glob(glob))[:limit]
    if not hits:
        console.print(f"[yellow]No matches for '{pattern}'[/yellow]"); return
    t = Table(title=f"🗂  Files matching '{pattern}'", box=box.ROUNDED)
    t.add_column("Path", style="cyan"); t.add_column("Size", width=10)
    t.add_column("Modified", style="dim", width=12)
    for f in hits:
        try:
            s = f.stat()
            sz  = f"{s.st_size/1024:.1f} KB" if s.st_size >= 1024 else f"{s.st_size} B"
            mod = datetime.datetime.fromtimestamp(s.st_mtime).strftime("%Y-%m-%d")
        except Exception:
            sz, mod = "?", "?"
        t.add_row(str(f), sz, mod)
    console.print(t)


@file.command("summarize")
@click.argument("filepath")
def file_summarize(filepath):
    """Summarize a file with AI."""
    p = Path(filepath).expanduser()
    if not p.exists():
        console.print(f"[red]Not found: {filepath}[/red]"); return
    try:
        content = p.read_text(encoding="utf-8", errors="ignore")[:5000]
    except Exception as e:
        console.print(f"[red]Could not read: {e}[/red]"); return
    with console.status("[cyan]Summarizing...[/cyan]"):
        out = ask_ai(f"Summarize this file. Filename: {p.name}",
                     system="You are a file analyst. Give a clear, structured summary.",
                     context=content)
    console.print(Panel(Markdown(out), title=f"[bold]📄  {p.name}[/bold]", border_style="green"))


# ── code ──────────────────────────────────────

@cli.group()
def code():
    """Code explanation, generation, and debugging."""


@code.command("explain")
@click.argument("filepath")
@click.option("-l","--lines")
def code_explain(filepath, lines):
    """Explain code in a file."""
    p = Path(filepath).expanduser()
    if not p.exists():
        console.print(f"[red]Not found: {filepath}[/red]"); return
    content = p.read_text(encoding="utf-8", errors="ignore")
    if lines:
        all_lines = content.splitlines()
        if "-" in lines:
            a, b = map(int, lines.split("-"))
            content = "\n".join(all_lines[a-1:b])
        else:
            n = int(lines)
            content = "\n".join(all_lines[max(0,n-5):n+5])
    else:
        content = content[:4000]
    with console.status("[cyan]Analyzing...[/cyan]"):
        out = ask_ai(f"Explain this code. File: {p.name}",
                     system="You are a code tutor. Be clear and educational. Use markdown.",
                     context=content)
    console.print(Panel(Markdown(out), title=f"[bold]🔍  {p.name}[/bold]", border_style="yellow"))


@code.command("generate")
@click.argument("description", nargs=-1, required=True)
@click.option("-l","--lang", default="python", show_default=True)
@click.option("-o","--output")
def code_generate(description, lang, output):
    """Generate code from a plain-English description."""
    desc = " ".join(description)
    with console.status("[cyan]Generating...[/cyan]"):
        out = ask_ai(f"Write {lang} code for: {desc}",
                     system=f"You are an expert {lang} developer. Output clean, well-commented code in a markdown code block.")
    console.print(Panel(Markdown(out), title=f"[bold]⚙  Generated {lang} Code[/bold]", border_style="yellow"))
    if output:
        lines_out = out.splitlines()
        if lines_out and lines_out[0].startswith("```"): lines_out = lines_out[1:]
        if lines_out and lines_out[-1].strip() == "```": lines_out = lines_out[:-1]
        Path(output).write_text("\n".join(lines_out))
        console.print(f"[green]✓ Saved to {output}[/green]")


@code.command("debug")
@click.argument("filepath")
@click.option("-e","--error")
def code_debug(filepath, error):
    """Find bugs in a file."""
    p = Path(filepath).expanduser()
    if not p.exists():
        console.print(f"[red]Not found: {filepath}[/red]"); return
    content = p.read_text(encoding="utf-8", errors="ignore")[:4000]
    prompt = "Find bugs and suggest fixes."
    if error:
        prompt += f"\n\nError: {error}"
    with console.status("[cyan]Debugging...[/cyan]"):
        out = ask_ai(prompt,
                     system="You are a debugging expert. Be specific about issues and fixes.",
                     context=f"File: {p.name}\n\n{content}")
    console.print(Panel(Markdown(out), title=f"[bold]🐛  Debug: {p.name}[/bold]", border_style="red"))


# ── chat ──────────────────────────────────────

@cli.command()
def chat():
    """Start an interactive AI chat session.

    \b
    Commands inside chat:
      /search <query>  web search
      /clear           wipe history
      /exit            quit
    """
    client, model = get_groq_client()
    history: list = []
    console.print(Panel(
        "[bold cyan]Chat session  •  @vivekjangiir[/bold cyan]\n\n"
        "[dim]/search <q>   /clear   /exit[/dim]",
        border_style="cyan"))

    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye![/dim]"); break
        txt = user_input.strip()
        if not txt: continue
        if txt.lower() in ("/exit", "/quit"):
            console.print("[dim]Goodbye![/dim]"); break
        if txt.lower() == "/clear":
            history = []; console.print("[green]✓ History cleared.[/green]"); continue
        if txt.lower().startswith("/search "):
            q = txt[8:]
            with console.status("[cyan]Searching...[/cyan]"):
                hits = web_search(q, max_results=4)
            for r in hits:
                console.print(f"[cyan]●[/cyan] [bold]{r.get('title','')}[/bold]\n"
                               f"  {(r.get('body') or '')[:160]}\n"
                               f"  [dim]{r.get('href','')}[/dim]")
            continue
        content_for_api = txt
        if any(kw in txt.lower() for kw in ("what is","who is","how to","latest","current","news","price","today")):
            hits = web_search(txt, max_results=2)
            if hits:
                ctx = "\n".join(f"- {r.get('title','')}: {(r.get('body') or '')[:200]}" for r in hits)
                content_for_api = f"[Web context]\n{ctx}\n\n[User] {txt}"
        history.append({"role": "user", "content": content_for_api})
        with console.status("[bold cyan]Thinking...[/bold cyan]"):
            msgs = [{"role": "system", "content": "You are a helpful, concise personal assistant. Use markdown where helpful."}]
            msgs += history[-12:]
            resp  = client.chat.completions.create(model=model, messages=msgs, max_tokens=1024)
            reply = resp.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        console.print(f"\n[bold green]Assistant[/bold green]")
        console.print(Markdown(reply))


if __name__ == "__main__":
    cli()
