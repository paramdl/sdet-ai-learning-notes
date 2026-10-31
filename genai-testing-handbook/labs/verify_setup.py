"""Checks the GenAI learning environment and reports what is still missing.

Run:  python labs\verify_setup.py
"""

import importlib
import os
import shutil
import subprocess
import sys
import urllib.request

OK = "[ OK ]"
NO = "[MISS]"

results = []


def check(label, passed, hint=""):
    results.append((passed, label, hint))
    print(f"{OK if passed else NO} {label}" + (f"  -> {hint}" if not passed and hint else ""))


print("\n--- environment ---")
check(f"Python {sys.version.split()[0]}", sys.version_info >= (3, 10), "install Python 3.12+")
in_venv = sys.prefix != sys.base_prefix
check("running inside a virtualenv", in_venv, "activate with .\\.venv\\Scripts\\Activate.ps1")

print("\n--- python packages ---")
for pkg, hint in [
    ("anthropic", "pip install anthropic"),
    ("openai", "pip install openai"),
    ("dotenv", "pip install python-dotenv"),
    ("tiktoken", "pip install tiktoken"),
    ("pytest", "pip install pytest"),
    ("deepeval", "pip install deepeval"),
    ("ragas", "pip install ragas"),
]:
    try:
        importlib.import_module(pkg)
        check(pkg, True)
    except ImportError:
        check(pkg, False, hint)

print("\n--- api keys ---")
try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    pass

anth = os.getenv("ANTHROPIC_API_KEY", "")
oai = os.getenv("OPENAI_API_KEY", "")
check("ANTHROPIC_API_KEY set", bool(anth), "add it to .env")
check("OPENAI_API_KEY set", bool(oai), "add it to .env (optional if you use Anthropic)")
if anth or oai:
    which = "ANTHROPIC" if anth else "OPENAI"
    print(f"       using {which}; key ends ...{(anth or oai)[-4:]}")

print("\n--- node tooling ---")
node = shutil.which("node")
check("node on PATH", bool(node), "install Node.js LTS")
npx = shutil.which("npx") or shutil.which("npx.cmd")
check("npx on PATH", bool(npx), "comes with npm")

print("\n--- local model (ollama) ---")
try:
    with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2) as r:
        import json

        models = [m["name"] for m in json.load(r).get("models", [])]
    check("ollama reachable on :11434", True)
    print(f"       models: {', '.join(models) if models else 'none pulled yet -> ollama pull llama3.1:8b'}")
except Exception:
    check("ollama reachable on :11434", False, "install from ollama.com, then: ollama pull llama3.1:8b")

failed = [r for r in results if not r[0]]
print("\n" + "=" * 50)
if failed:
    print(f"{len(failed)} item(s) still to do:")
    for _, label, hint in failed:
        print(f"  - {label}" + (f": {hint}" if hint else ""))
else:
    print("All set. Start with: cd labs\\promptfoo && npx promptfoo@latest eval")
print("=" * 50)
