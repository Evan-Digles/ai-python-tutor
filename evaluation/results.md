# Evaluation Results — Before vs. After System Prompts

Model: `claude-haiku-4-5-20251001` | BERTScore model: `bert-base-uncased` | Test cases scored: 11

| Test case | Mode | BERTScore before | BERTScore after |
|---|---|---|---|
| explain_variable | explain | 0.401 | 0.696 |
| explain_forloop | explain | 0.460 | 0.618 |
| explain_len | explain | 0.452 | 0.682 |
| example_if | example | 0.504 | 0.709 |
| example_list | example | 0.459 | 0.624 |
| debug_nameerror | debug | 0.571 | 0.632 |
| debug_missingcolon | debug | 0.526 | 0.607 |
| exercise_while | exercise | 0.411 | 0.468 |
| exercise_function | exercise | 0.248 | 0.491 |
| feedback_add | feedback | 0.413 | 0.604 |
| feedback_sum | feedback | 0.501 | 0.564 |
| **Average** | | **0.450** | **0.609** |

## Summary

- **BERTScore F1:** 0.450 -> 0.609 (+0.159)
- **Evaluation cost:** 6,826 tokens, $0.0267

The AFTER column uses the tutoring system prompts; the BEFORE column is the raw model with no instructions. Scores are baseline-rescaled, so unrelated text sits near 0. The BERTScore gain shows the prompt engineering moves responses closer to ideal tutoring answers.
