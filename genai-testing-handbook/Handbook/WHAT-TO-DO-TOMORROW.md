# What To Do First Tomorrow

> One page. One task. Ninety minutes. Do not read anything else in this handbook first.

---

## The task: measure your determinism baseline

**Why this first, out of everything in a 35-chapter book:**

It is the single experiment that converts GenAI testing from an abstract idea into something you have personally observed. Every method in this handbook — pass-rates instead of assertions, semantic thresholds, N-run sampling, delta gates — exists because of the behaviour you are about to measure with your own hands. Reading about non-determinism teaches you nothing. Watching twenty identical requests return sixteen different answers teaches you everything, in about four minutes.

It also produces a number you will use for the rest of the project, and a story you will tell in interviews.

---

## Step 1 — Setup (30 minutes)

Install Ollama from **ollama.com**, then:

```bash
ollama pull llama3.1:8b
```

```powershell
cd <project-dir>
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install openai numpy
```

No API key. No cost. Everything below runs offline on your own machine.

---

## Step 2 — Write this file (20 minutes)

Type it out rather than copying it. Typing is how the API shape gets into your head.

`<project-dir>\labs\determinism.py`

```python
"""Measure how non-deterministic an LLM actually is.

This is the experiment that justifies every method in the handbook.
"""
import numpy as np
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL = "llama3.1:8b"

SYSTEM = "You are a support agent. Answer in at most 2 sentences."
PROMPT = "How do I reset my password?"


def ask(temperature: float) -> str:
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": PROMPT}],
        temperature=temperature,
        max_tokens=150,
    )
    return r.choices[0].message.content.strip()


def embed(text: str) -> np.ndarray:
    v = client.embeddings.create(model="nomic-embed-text", input=text).data[0].embedding
    return np.array(v)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def baseline(temperature: float, n: int = 20) -> dict:
    outs = [ask(temperature) for _ in range(n)]
    vecs = [embed(o) for o in outs]
    sims = [cosine(vecs[i], vecs[j])
            for i in range(n) for j in range(i + 1, n)]
    return {
        "temperature": temperature,
        "runs": n,
        "unique_outputs": len(set(outs)),
        "all_identical": len(set(outs)) == 1,
        "mean_similarity": round(float(np.mean(sims)), 4),
        "min_similarity": round(float(np.min(sims)), 4),
        "samples": outs[:3],
    }


if __name__ == "__main__":
    for temp in (0.0, 1.0):
        r = baseline(temp)
        print(f"\n{'=' * 60}\nTEMPERATURE {temp}")
        print(f"  unique outputs:   {r['unique_outputs']} / {r['runs']}")
        print(f"  all identical:    {r['all_identical']}")
        print(f"  mean similarity:  {r['mean_similarity']}")
        print(f"  min similarity:   {r['min_similarity']}")
        print("  first 3 samples:")
        for s in r["samples"]:
            print(f"    - {s[:100]}")
```

You will need the embedding model too:

```bash
ollama pull nomic-embed-text
```

---

## Step 3 — Run it (5 minutes)

```powershell
python labs\determinism.py
```

---

## Step 4 — Write down what you see (20 minutes)

Create `labs/determinism-baseline.md` and record:

1. **The numbers** for temperature 0 and temperature 1.0.
2. **Was temperature 0 identical across all 20 runs?** Almost certainly not entirely. Note how many unique outputs you got.
3. **The minimum pairwise similarity at temperature 0** — this is the floor a semantic assertion would have to clear.
4. **One sentence on what this means for testing.** Write it in your own words, not the handbook's.

Then answer this, honestly, in writing:

> *If I had written `assert response == "You can reset your password in Account Settings."`, how many of those 20 runs would have passed?*

---

## What you now know

- **`temperature=0` does not guarantee identical output.** You measured it; you are not taking anyone's word for it.
- **Your semantic threshold has an empirical floor.** If your minimum similarity at temperature 0 was 0.94, then a threshold of 0.85 is safe for this endpoint and 0.98 is not. That is calibration, and you have just done it.
- **The right assertion shape is a rate, not a boolean.** This follows directly from the numbers in front of you.

You have also produced the first artefact of your portfolio, and the answer to one of the most common interview questions in this field.

---

## Then, in order

| Next | Where |
|---|---|
| Read the fundamentals | [PART-01-GENAI-FOUNDATIONS.md](PART-01-GENAI-FOUNDATIONS.md) |
| See the whole path | [LEARNING-ORDER.md](LEARNING-ORDER.md) |
| Follow a daily schedule | [STUDY-PLANS.md](STUDY-PLANS.md) — the 30-day plan starts here |
| Avoid the classic traps | [COMMON-MISTAKES.md](COMMON-MISTAKES.md) |

**Day 2 is Part 1. Day 3 is the token experiment** — count the same paragraph in English, Tamil, and Hindi, and record the ratio. That one takes twenty minutes and produces a finding you can use at work.

---

## One last thing

Do not read this handbook cover to cover before starting. It is 35 chapters and it is a reference, not a course. The people who learn this field are the ones who run the experiment on Tuesday and read the chapter on Wednesday, because by then they have a question the chapter answers.

Run the script tomorrow.
