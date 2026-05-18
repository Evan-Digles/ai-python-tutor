# Pricing for claude-haiku-4-5-20251001 (USD per token)
INPUT_COST_PER_TOKEN = 1.00 / 1_000_000   # $1.00 per million input tokens
OUTPUT_COST_PER_TOKEN = 5.00 / 1_000_000  # $5.00 per million output tokens


def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """Return total cost in USD for a given token usage."""
    return (input_tokens * INPUT_COST_PER_TOKEN) + (output_tokens * OUTPUT_COST_PER_TOKEN)


def format_cost(cost: float) -> str:
    """Format a cost value as a USD string to 4 decimal places."""
    return f"${cost:.4f}"


def format_tokens(count: int) -> str:
    """Format a token count with comma separators."""
    return f"{count:,}"
