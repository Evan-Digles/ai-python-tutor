# AI Python Tutor

An AI-powered tutoring system for introductory Python programming, built with
the Anthropic Claude API and Streamlit. Created for COSC 461 (Artificial Intelligence).

## Requirements

- Python 3.10+
- An Anthropic API key

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your API key**

   Copy `.env.example` to `.env` and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_key_here
   ```

3. **Run the app**
   ```bash
   python -m streamlit run app.py
   ```
   Then open http://localhost:8501 in your browser.

## Tutoring modes

- **Explain** — Clear explanations of Python concepts
- **Example** — Annotated code examples
- **Debug** — Error identification and fixes
- **Exercise** — Generates a practice problem, then grades your submitted answer
- **Feedback** — Constructive feedback on code you provide
- **Auto** — Detects which mode fits your question (manual selection always overrides)

The sidebar shows live token usage and estimated cost for the session.

## Evaluation

The `evaluation/` directory contains a before/after comparison of the tutoring
system prompts, scored with BERTScore. It makes API calls and writes results
to `evaluation/results.md`.

```bash
pip install -r requirements-eval.txt
python -m evaluation.evaluate
```

### Results

Across 11 test cases, the tutoring system prompts raised the average
BERTScore F1 against reference tutoring answers from 0.450 (raw model, no
instructions) to 0.609. The full table is in
[evaluation/results.md](evaluation/results.md).

## How it was built

This project was built with Claude Code, as the assignment required the use
of AI. Claude drafted the code and I reviewed and modified it.

## About this README

The "Results" and "How it was built" sections were added with Claude for
the portfolio copy of the project. The rest is as submitted for the course.
