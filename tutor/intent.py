# [Claude Opus 4.7]: weighted phrases instead of the handout's single-token
# first-match. Strong intent verbs ("explain", "show me") outweigh weak topic
# words, so "explain what def means" scores as explain, not debug.
MODE_KEYWORDS: dict[str, dict[str, int]] = {
    # Keys are stored apostrophe-free; detect() strips apostrophes from input
    # so "what's" and "whats" both match.
    "explain": {
        "explain": 3, "what is": 3, "what are": 3, "whats": 3,
        "how does": 2, "how do": 2, "what does": 2, "why is": 2,
        "define": 2, "definition": 2, "meaning of": 2,
        "tell me about": 2, "dont understand": 2, "concept": 1,
    },
    "example": {
        "show me": 3, "example": 3, "show an": 3, "demonstrate": 3,
        "give me code": 2, "sample": 2, "what does it look like": 2,
    },
    "debug": {
        "doesnt work": 3, "does not work": 3, "not working": 3,
        "why doesnt": 3, "why does my": 3, "wont run": 3,
        "fix this": 3, "fix my": 3, "traceback": 3, "error": 2,
        "bug": 2, "broken": 2, "exception": 2, "crash": 2,
        "fails": 2, "failing": 2, "wrong output": 2, "unexpected": 1,
    },
    "exercise": {
        "give me a problem": 3, "give me an exercise": 3, "practice problem": 3,
        "exercise": 2, "practice": 2, "challenge": 2, "quiz": 2,
        "test me": 2, "give me a task": 2, "drill": 1,
    },
    "feedback": {
        "review my": 3, "feedback": 3, "is this correct": 3,
        "is this right": 3, "check my": 3, "how did i do": 3,
        "rate my": 3, "what do you think": 2, "look at my": 2,
        "improve my": 2, "is my code": 2,
    },
}

# [Claude Opus 4.7]: pasted code usually means "what's wrong" or "review this",
# so it nudges debug and feedback rather than picking a mode outright.
_CODE_SIGNAL_WEIGHT = 2

DEFAULT_MODE = "explain"

# Tie-break order: specific intents win over the general "explain" fallback.
_PRIORITY = ["debug", "feedback", "exercise", "example", "explain"]


def _contains_code(text: str) -> bool:
    """Return True if the input appears to contain a pasted code snippet.

    Deliberately conservative: a single-line question that merely mentions a
    token like 'def' or 'for loop' must not be treated as code.
    """
    if "```" in text:
        return True
    if "\n" in text:
        code_tokens = ("def ", "print(", "import ", "return ", "=", "    ")
        return any(token in text for token in code_tokens)
    return False


def detect(user_input: str) -> str:
    """Detect the most likely tutoring mode from the user's input.

    Scores each mode by weighted keyword matches, adds a structural signal
    when code is present, and returns the highest-scoring mode. Falls back
    to 'explain' when nothing matches.
    """
    # Strip straight and curly apostrophes so "doesn't" and "doesnt" both match.
    text = user_input.lower().replace("'", "").replace("’", "")

    scores = {mode: 0 for mode in MODE_KEYWORDS}
    for mode, keywords in MODE_KEYWORDS.items():
        for phrase, weight in keywords.items():
            if phrase in text:
                scores[mode] += weight

    if _contains_code(text):
        scores["debug"] += _CODE_SIGNAL_WEIGHT
        scores["feedback"] += _CODE_SIGNAL_WEIGHT

    best_score = max(scores.values())
    if best_score == 0:
        return DEFAULT_MODE
    for mode in _PRIORITY:
        if scores[mode] == best_score:
            return mode
    return DEFAULT_MODE
