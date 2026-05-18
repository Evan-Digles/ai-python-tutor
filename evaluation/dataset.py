"""Test cases for the before/after evaluation.

Each case has a student prompt, the tutoring mode it targets, and a gold-standard
reference answer written in the expected structured format. The reference is what
a well-formed tutor response should look like; BERTScore measures how close the
model's actual output gets to it.
"""

TEST_CASES: list[dict] = [
    {
        "id": "explain_variable",
        "mode": "explain",
        "prompt": "What is a variable in Python?",
        "reference": (
            "**Concept:** A variable is a name that stores a value so you can use "
            "it again later.\n\n"
            "```python\nage = 10\nprint(age)\n```\n\n"
            "**Try:** Create a variable called name and print it."
        ),
    },
    {
        "id": "explain_forloop",
        "mode": "explain",
        "prompt": "What is a for loop?",
        "reference": (
            "**Concept:** A for loop repeats a block of code once for each item "
            "in a sequence.\n\n"
            "```python\nfor i in range(3):\n    print(i)\n```\n\n"
            "**Try:** Write a for loop that prints the numbers 1 to 5."
        ),
    },
    {
        "id": "explain_len",
        "mode": "explain",
        "prompt": "What does the len() function do?",
        "reference": (
            "**Concept:** The len() function returns the number of items in a "
            "sequence such as a string or list.\n\n"
            "```python\nletters = ['a', 'b', 'c']\nprint(len(letters))\n```\n\n"
            "**Try:** Use len() to find how many characters are in the word 'python'."
        ),
    },
    {
        "id": "example_if",
        "mode": "example",
        "prompt": "Show me an example of an if statement.",
        "reference": (
            "**Concept:** An if statement runs code only when a condition is true.\n\n"
            "```python\nage = 20\nif age >= 18:\n    print('Adult')\n```\n\n"
            "**What this does:** Since age is 20, the condition is true, so it "
            "prints 'Adult'.\n\n"
            "**Try:** Change age to 15 and see what happens."
        ),
    },
    {
        "id": "example_list",
        "mode": "example",
        "prompt": "Show an example of a Python list.",
        "reference": (
            "**Concept:** A list stores multiple values in a single ordered "
            "variable.\n\n"
            "```python\nfruits = ['apple', 'banana', 'cherry']\nprint(fruits[0])\n```\n\n"
            "**What this does:** It creates a list of three fruits and prints the "
            "first one, 'apple'.\n\n"
            "**Try:** Add a fourth fruit to the list and print it."
        ),
    },
    {
        "id": "debug_nameerror",
        "mode": "debug",
        "prompt": (
            "Why doesn't this work?\n\n"
            "```python\nname = input('Enter name: ')\nprint('Hello, ' + Name)\n```"
        ),
        "reference": (
            "**The problem:** This raises a NameError because 'Name' is "
            "capitalized but the variable was defined as 'name'. Python names "
            "are case-sensitive.\n\n"
            "```python\nname = input('Enter name: ')\n"
            "print('Hello, ' + name)  # use the same lowercase name\n```\n\n"
            "**Why this fixes it:** Python treats 'name' and 'Name' as two "
            "different variables, and 'Name' was never defined.\n\n"
            "**Tip:** Keep variable names consistent and watch capitalization."
        ),
    },
    {
        "id": "debug_missingcolon",
        "mode": "debug",
        "prompt": (
            "My code gives a syntax error:\n\n"
            "```python\nfor i in range(5)\n    print(i)\n```"
        ),
        "reference": (
            "**The problem:** This is a SyntaxError because the for line is "
            "missing a colon at the end.\n\n"
            "```python\nfor i in range(5):  # added the missing colon\n"
            "    print(i)\n```\n\n"
            "**Why this fixes it:** Python requires a colon after a for "
            "statement to start the loop body.\n\n"
            "**Tip:** Lines that start a block (for, if, def, while) always "
            "end with a colon."
        ),
    },
    {
        "id": "exercise_while",
        "mode": "exercise",
        "prompt": "Give me an exercise about while loops.",
        "reference": (
            "**Exercise:** Write a program that uses a while loop to count down "
            "from 5 to 1 and then prints 'Done'.\n\n"
            "**Requirements:**\n"
            "- Use a while loop, not a for loop\n"
            "- Print each number on its own line\n\n"
            "**Hint:** Start a variable at 5 and subtract 1 each time the loop runs."
        ),
    },
    {
        "id": "exercise_function",
        "mode": "exercise",
        "prompt": "Create a practice problem about functions.",
        "reference": (
            "**Exercise:** Write a function called square that takes one number "
            "and returns that number multiplied by itself.\n\n"
            "**Requirements:**\n"
            "- Define the function with def\n"
            "- Return the result instead of printing it\n\n"
            "**Hint:** A function returns a value using the return keyword."
        ),
    },
    {
        "id": "feedback_add",
        "mode": "feedback",
        "prompt": (
            "Can you give me feedback on my code?\n\n"
            "```python\ndef add(a, b):\n    result = a + b\n    return result\n```"
        ),
        "reference": (
            "**What works:** The function is correctly defined, takes two "
            "parameters, and returns the sum. The logic is right.\n\n"
            "**What to improve:** The extra 'result' variable isn't needed — you "
            "can return the sum directly for cleaner code.\n\n"
            "```python\ndef add(a, b):\n"
            "    return a + b  # return directly, no temporary variable\n```\n\n"
            "**Key takeaway:** Return simple expressions directly instead of "
            "storing them in a one-use variable."
        ),
    },
    {
        "id": "feedback_sum",
        "mode": "feedback",
        "prompt": (
            "How is my code? Any feedback?\n\n"
            "```python\nnumbers = [1, 2, 3, 4]\ntotal = 0\n"
            "for i in range(len(numbers)):\n    total = total + numbers[i]\n"
            "print(total)\n```"
        ),
        "reference": (
            "**What works:** The code correctly adds up all the numbers in the "
            "list and prints the total, 10.\n\n"
            "**What to improve:** You can loop directly over the list items "
            "instead of using range(len(...)), which is simpler and more "
            "readable.\n\n"
            "```python\nnumbers = [1, 2, 3, 4]\ntotal = 0\n"
            "for n in numbers:  # loop over items directly\n"
            "    total += n      # += is shorthand for total = total + n\n"
            "print(total)\n```\n\n"
            "**Key takeaway:** In Python, loop over a list's items directly "
            "rather than over its indexes."
        ),
    },
]
