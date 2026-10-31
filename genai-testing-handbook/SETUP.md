# Setup — This Machine

Checked on 2026-09-08:

| Tool | Status |
|---|---|
| Python | 3.13.14 (Microsoft Store install) — OK |
| Node | v24.18.0, npm 11.13.0 — OK |
| Git | 2.49.0 — OK |
| Docker | **not installed** — optional, only needed for self-hosted Langfuse |
| Ollama | **not installed** — install this, it is your free lab |
| Python pkgs | `anthropic`, `openai`, `python-dotenv`, `deepeval`, `pytest` already present globally |
| Still missing | `tiktoken`, `ragas`, API keys, Ollama |

Because the eval packages are already installed globally, you can skip straight to step 5 if you want to move fast. The venv in step 1 is still worth doing — it stops one project's package upgrade from breaking another.

Run everything below from PowerShell in `<project-dir>`.

---

## 1. Python virtual environment

```powershell
cd <project-dir>
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

If `Activate.ps1` is blocked by execution policy:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## 2. Core Python packages

```powershell
pip install anthropic openai python-dotenv tiktoken pytest requests
```

Then the eval stack:

```powershell
pip install deepeval ragas datasets
```

If a wheel fails to build on Python 3.13, install Python 3.12 from python.org and rebuild the venv with `py -3.12 -m venv .venv`. The eval libraries lag the newest Python by a release or two.

## 3. Node tooling (promptfoo)

No global install needed — always run it via npx so you get the current version:

```powershell
npx promptfoo@latest --version
```

## 4. API keys

Create `<project-dir>\.env` (already git-ignored by `.gitignore` in this folder):

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

You need **one** paid key to do real work. Budget note: a few dollars covers all eight weeks if you keep eval datasets around 20–50 cases and cache results. Set a hard spend limit in the provider console on day one — that is also your first lesson in denial-of-wallet testing.

Never commit `.env`. Never paste a key into a prompt, a test fixture, or a bug report.

## 5. Ollama — the free lab (install this)

Download the Windows installer from ollama.com, then:

```powershell
ollama pull llama3.1:8b
ollama run llama3.1:8b "Say hello in exactly five words."
```

It serves an OpenAI-compatible API at `http://localhost:11434/v1`, so promptfoo and DeepEval can both point at it. Use this for anything repetitive, and for **all** red-teaming practice — attack payloads against a local model cost nothing and touch no one else's system.

A 7–8B model needs roughly 8 GB of RAM free. If it is slow, use `llama3.2:3b`.

## 6. Verify the install

```powershell
python labs\verify_setup.py
```

It checks the venv, the imports, the `.env` keys, and whether Ollama is reachable — and tells you what is missing.

## 7. First run

```powershell
cd labs\promptfoo
npx promptfoo@latest eval
npx promptfoo@latest view
```

That opens the results grid in your browser. When you can read that grid and explain why a row failed, Week 3 is done.

---

## Optional later

- **Langfuse** (tracing) — needs Docker Desktop for self-hosting, or use their cloud free tier. Week 7.
- **garak** — `pip install garak`, point it at Ollama. Week 6.
- **VS Code + Python extension** — nicer than editing eval YAML in Notepad.
