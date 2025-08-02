import streamlit as st
import json
import re
import traceback
import sys
from io import StringIO
from collections import defaultdict
from urllib.parse import urlparse, parse_qs
import time

# Page configuration
st.set_page_config(
    page_title="SHL Coding Exam Prep",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Try to import streamlit-ace for better code editing
try:
    from streamlit_ace import st_ace
    ACE_AVAILABLE = True
except ImportError:
    ACE_AVAILABLE = False
    st.warning("streamlit-ace not found. Using basic text area for code editing.")

# Custom CSS for better styling
st.markdown("""
<style>
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    .hint-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        margin: 1rem 0;
    }
    .problem-stats {
        display: flex;
        gap: 1rem;
        margin: 0.5rem 0;
    }
    .stat-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .success-badge {
        background-color: #28a745;
        color: white;
    }
    .failure-badge {
        background-color: #dc3545;
        color: white;
    }
    .total-badge {
        background-color: #6c757d;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'problems' not in st.session_state:
        st.session_state.problems = load_problems()
    if 'selected_problem' not in st.session_state:
        st.session_state.selected_problem = None
    if 'user_stats' not in st.session_state:
        st.session_state.user_stats = defaultdict(lambda: {'success': 0, 'failure': 0})
    if 'show_hints' not in st.session_state:
        st.session_state.show_hints = defaultdict(bool)
    if 'current_hint_index' not in st.session_state:
        st.session_state.current_hint_index = defaultdict(int)

def get_default_problems():
    """Get the default 20 problems hardcoded in memory"""
    return {
        1: {
            "id": 1,
            "title": "Remove Duplicates",
            "statement": "Write a function that takes a list of integers and returns a new list with duplicates removed, maintaining the original order of first appearance.\n\nExample:\n- Input: [1, 2, 2, 3, 1, 4, 3]\n- Output: [1, 2, 3, 4]",
            "function_signature": "def remove_duplicates(nums):",
            "hints": [
                "Think about using a data structure to track what you've already seen",
                "A set can help you check for duplicates efficiently",
                "Iterate through the list and only add elements you haven't seen before"
            ],
            "solution": "def remove_duplicates(nums):\n    seen = set()\n    result = []\n    for num in nums:\n        if num not in seen:\n            seen.add(num)\n            result.append(num)\n    return result",
            "test_cases": [
                {"input": [[1, 2, 2, 3, 1, 4, 3]], "expected": [1, 2, 3, 4]},
                {"input": [[]], "expected": []},
                {"input": [[1, 1, 1]], "expected": [1]},
                {"input": [[5, 4, 3, 2, 1]], "expected": [5, 4, 3, 2, 1]}
            ]
        },
        2: {
            "id": 2,
            "title": "Email Validation",
            "statement": "Create a function that validates email addresses based on these rules:\n- Exactly one '@' symbol\n- At least one character before '@'\n- At least one '.' after '@'\n- At least one character after the final '.'\n- Only alphanumeric, dots, underscores, and one '@' allowed\n\nExample:\n- Valid: 'user@example.com'\n- Invalid: 'user@.com'",
            "function_signature": "def is_valid_email(email):",
            "hints": [
                "Check the count of '@' symbols first",
                "Split the email by '@' to get local and domain parts",
                "Verify the domain has proper dot placement",
                "Use regular expressions for character validation"
            ],
            "solution": "def is_valid_email(email):\n    import re\n    if email.count('@') != 1:\n        return False\n    \n    parts = email.split('@')\n    local, domain = parts[0], parts[1]\n    \n    if len(local) == 0:\n        return False\n    \n    if '.' not in domain:\n        return False\n    \n    if domain.endswith('.') or domain.split('.')[-1] == '':\n        return False\n    \n    allowed_pattern = r'^[a-zA-Z0-9._]+@[a-zA-Z0-9._]+$'\n    return bool(re.match(allowed_pattern, email))",
            "test_cases": [
                {"input": ["user@example.com"], "expected": True},
                {"input": ["user@.com"], "expected": False},
                {"input": ["@example.com"], "expected": False},
                {"input": ["user@example."], "expected": False},
                {"input": ["user@@example.com"], "expected": False}
            ]
        },
        3: {
            "id": 3,
            "title": "Department Average Salary",
            "statement": "Given employee records with name, department, and salary, find the department with the highest average salary.\n\nExample Input:\n[{\"name\": \"Alice\", \"department\": \"Engineering\", \"salary\": 75000}, {\"name\": \"Bob\", \"department\": \"Sales\", \"salary\": 50000}]\n\nExpected Output: \"Engineering\"",
            "function_signature": "def highest_avg_salary_dept(employees):",
            "hints": [
                "Group employees by department",
                "Calculate the total salary and count for each department",
                "Compute average salary for each department",
                "Return the department with the highest average"
            ],
            "solution": "def highest_avg_salary_dept(employees):\n    if not employees:\n        return None\n    \n    dept_totals = {}\n    dept_counts = {}\n    \n    for emp in employees:\n        dept = emp['department']\n        salary = emp['salary']\n        \n        dept_totals[dept] = dept_totals.get(dept, 0) + salary\n        dept_counts[dept] = dept_counts.get(dept, 0) + 1\n    \n    highest_avg = 0\n    best_dept = None\n    \n    for dept in dept_totals:\n        avg = dept_totals[dept] / dept_counts[dept]\n        if avg > highest_avg:\n            highest_avg = avg\n            best_dept = dept\n    \n    return best_dept",
            "test_cases": [
                {"input": [[{"name": "Alice", "department": "Engineering", "salary": 75000}, {"name": "Bob", "department": "Sales", "salary": 50000}]], "expected": "Engineering"},
                {"input": [[]], "expected": None},
                {"input": [[{"name": "John", "department": "HR", "salary": 60000}, {"name": "Jane", "department": "HR", "salary": 65000}]], "expected": "HR"}
            ]
        },
        4: {
            "id": 4,
            "title": "Palindrome Checker",
            "statement": "Write a function that checks if a string is a palindrome (reads the same forwards and backwards), ignoring spaces, punctuation, and case.\n\nExample:\n- Input: \"A man, a plan, a canal: Panama\"\n- Output: True",
            "function_signature": "def is_palindrome(s):",
            "hints": [
                "Remove all non-alphanumeric characters",
                "Convert to lowercase for case-insensitive comparison",
                "Compare the string with its reverse",
                "Regular expressions can help clean the string"
            ],
            "solution": "def is_palindrome(s):\n    import re\n    cleaned = re.sub(r'[^a-zA-Z0-9]', '', s).lower()\n    return cleaned == cleaned[::-1]",
            "test_cases": [
                {"input": ["A man, a plan, a canal: Panama"], "expected": True},
                {"input": ["race a car"], "expected": False},
                {"input": [""], "expected": True},
                {"input": ["a"], "expected": True}
            ]
        },
        5: {
            "id": 5,
            "title": "Find Missing Number",
            "statement": "Given an array containing n-1 numbers from 1 to n with one number missing, find the missing number.\n\nExample:\n- Input: [1, 2, 4, 5, 6] (n=6)\n- Output: 3",
            "function_signature": "def find_missing_number(nums):",
            "hints": [
                "Calculate what the sum should be for numbers 1 to n",
                "Use the formula: sum = n * (n + 1) / 2",
                "Subtract the actual sum from the expected sum",
                "The difference is the missing number"
            ],
            "solution": "def find_missing_number(nums):\n    n = len(nums) + 1\n    expected_sum = n * (n + 1) // 2\n    actual_sum = sum(nums)\n    return expected_sum - actual_sum",
            "test_cases": [
                {"input": [[1, 2, 4, 5, 6]], "expected": 3},
                {"input": [[2, 3, 4, 5]], "expected": 1},
                {"input": [[1, 2, 3, 4]], "expected": 5},
                {"input": [[1]], "expected": 2}
            ]
        },
        6: {
            "id": 6,
            "title": "Word Frequency Counter",
            "statement": "Create a function that counts the frequency of each word in a text string, ignoring case and punctuation.\n\nExample:\n- Input: \"The quick brown fox jumps over the lazy dog\"\n- Output: {\"the\": 2, \"quick\": 1, \"brown\": 1, ...}",
            "function_signature": "def word_frequency(text):",
            "hints": [
                "Use regular expressions to extract words",
                "Convert all words to lowercase",
                "Use a dictionary to count occurrences",
                "The pattern \\b[a-zA-Z]+\\b matches whole words"
            ],
            "solution": "def word_frequency(text):\n    import re\n    words = re.findall(r'\\b[a-zA-Z]+\\b', text.lower())\n    frequency = {}\n    for word in words:\n        frequency[word] = frequency.get(word, 0) + 1\n    return frequency",
            "test_cases": [
                {"input": ["The quick brown fox jumps over the lazy dog"], "expected": {"the": 2, "quick": 1, "brown": 1, "fox": 1, "jumps": 1, "over": 1, "lazy": 1, "dog": 1}},
                {"input": [""], "expected": {}},
                {"input": ["Hello hello HELLO"], "expected": {"hello": 3}}
            ]
        },
        7: {
            "id": 7,
            "title": "Valid Parentheses",
            "statement": "Check if a string containing only parentheses characters '(', ')', '{', '}', '[', ']' is valid (properly nested and closed).\n\nExample:\n- Input: \"({[]})\"\n- Output: True\n- Input: \"([)]\"\n- Output: False",
            "function_signature": "def is_valid_parentheses(s):",
            "hints": [
                "Use a stack data structure",
                "Push opening brackets onto the stack",
                "For closing brackets, check if they match the top of the stack",
                "The stack should be empty at the end"
            ],
            "solution": "def is_valid_parentheses(s):\n    stack = []\n    mapping = {')': '(', '}': '{', ']': '['}\n    \n    for char in s:\n        if char in mapping:\n            if not stack or stack.pop() != mapping[char]:\n                return False\n        else:\n            stack.append(char)\n    \n    return len(stack) == 0",
            "test_cases": [
                {"input": ["({[]})"], "expected": True},
                {"input": ["([)]"], "expected": False},
                {"input": ["()"], "expected": True},
                {"input": ["("], "expected": False},
                {"input": [""], "expected": True}
            ]
        },
        8: {
            "id": 8,
            "title": "Fibonacci Sequence",
            "statement": "Generate the first n numbers in the Fibonacci sequence efficiently.\n\nExample:\n- Input: n = 7\n- Output: [0, 1, 1, 2, 3, 5, 8]",
            "function_signature": "def fibonacci(n):",
            "hints": [
                "Handle edge cases for n <= 0, n = 1, n = 2",
                "Use iteration instead of recursion for efficiency",
                "Build the sequence step by step",
                "Each number is the sum of the previous two"
            ],
            "solution": "def fibonacci(n):\n    if n <= 0:\n        return []\n    elif n == 1:\n        return [0]\n    elif n == 2:\n        return [0, 1]\n    \n    fib = [0, 1]\n    for i in range(2, n):\n        fib.append(fib[i-1] + fib[i-2])\n    \n    return fib",
            "test_cases": [
                {"input": [7], "expected": [0, 1, 1, 2, 3, 5, 8]},
                {"input": [0], "expected": []},
                {"input": [1], "expected": [0]},
                {"input": [2], "expected": [0, 1]}
            ]
        },
        9: {
            "id": 9,
            "title": "Anagram Groups",
            "statement": "Group a list of strings into anagram groups (words that contain the same letters).\n\nExample:\n- Input: [\"eat\", \"tea\", \"tan\", \"ate\", \"nat\", \"bat\"]\n- Output: [[\"eat\", \"tea\", \"ate\"], [\"tan\", \"nat\"], [\"bat\"]]",
            "function_signature": "def group_anagrams(strs):",
            "hints": [
                "Anagrams have the same characters when sorted",
                "Use sorted characters as a key",
                "Group strings by their sorted character key",
                "Use a dictionary to collect groups"
            ],
            "solution": "def group_anagrams(strs):\n    from collections import defaultdict\n    \n    anagram_groups = defaultdict(list)\n    \n    for s in strs:\n        key = ''.join(sorted(s))\n        anagram_groups[key].append(s)\n    \n    return list(anagram_groups.values())",
            "test_cases": [
                {"input": [["eat", "tea", "tan", "ate", "nat", "bat"]], "expected": [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]},
                {"input": [[""]], "expected": [[""]]},
                {"input": [["a"]], "expected": [["a"]]}
            ]
        },
        10: {
            "id": 10,
            "title": "Stock Price Analysis",
            "statement": "Given daily stock prices, find the maximum profit possible from buying and selling once.\n\nExample:\n- Input: [7, 1, 5, 3, 6, 4]\n- Output: 5 (buy at 1, sell at 6)",
            "function_signature": "def max_profit(prices):",
            "hints": [
                "Track the minimum price seen so far",
                "For each price, calculate profit if selling at that price",
                "Keep track of the maximum profit seen",
                "You can only sell after you buy"
            ],
            "solution": "def max_profit(prices):\n    if len(prices) < 2:\n        return 0\n    \n    min_price = prices[0]\n    max_profit = 0\n    \n    for price in prices[1:]:\n        max_profit = max(max_profit, price - min_price)\n        min_price = min(min_price, price)\n    \n    return max_profit",
            "test_cases": [
                {"input": [[7, 1, 5, 3, 6, 4]], "expected": 5},
                {"input": [[7, 6, 4, 3, 1]], "expected": 0},
                {"input": [[1, 2]], "expected": 1},
                {"input": [[1]], "expected": 0}
            ]
        },
        11: {
            "id": 11,
            "title": "Binary Tree Depth",
            "statement": "Calculate the maximum depth (height) of a binary tree represented as nested dictionaries.\n\nExample:\n- Input: {\"val\": 1, \"left\": {\"val\": 2}, \"right\": {\"val\": 3, \"left\": {\"val\": 4}}}\n- Output: 3",
            "function_signature": "def max_depth(root):",
            "hints": [
                "Use recursion to traverse the tree",
                "Base case: if root is None, return 0",
                "Recursively find depth of left and right subtrees",
                "Return 1 + maximum of left and right depths"
            ],
            "solution": "def max_depth(root):\n    if not root:\n        return 0\n    \n    left_depth = max_depth(root.get('left')) if 'left' in root else 0\n    right_depth = max_depth(root.get('right')) if 'right' in root else 0\n    \n    return 1 + max(left_depth, right_depth)",
            "test_cases": [
                {"input": [{"val": 1, "left": {"val": 2}, "right": {"val": 3, "left": {"val": 4}}}], "expected": 3},
                {"input": [None], "expected": 0},
                {"input": [{"val": 1}], "expected": 1}
            ]
        },
        12: {
            "id": 12,
            "title": "URL Parameter Parser",
            "statement": "Parse URL query parameters into a dictionary.\n\nExample:\n- Input: \"https://example.com?name=John&age=25&city=NYC\"\n- Output: {\"name\": \"John\", \"age\": \"25\", \"city\": \"NYC\"}",
            "function_signature": "def parse_url_params(url):",
            "hints": [
                "Use urllib.parse module for URL parsing",
                "Extract the query part from the URL",
                "Split parameters by '&' and key-value pairs by '='",
                "Handle URL encoding if necessary"
            ],
            "solution": "def parse_url_params(url):\n    from urllib.parse import urlparse, parse_qs\n    \n    parsed_url = urlparse(url)\n    params = parse_qs(parsed_url.query)\n    \n    result = {}\n    for key, value_list in params.items():\n        result[key] = value_list[0] if value_list else ''\n    \n    return result",
            "test_cases": [
                {"input": ["https://example.com?name=John&age=25&city=NYC"], "expected": {"name": "John", "age": "25", "city": "NYC"}},
                {"input": ["https://example.com"], "expected": {}},
                {"input": ["https://example.com?single=value"], "expected": {"single": "value"}}
            ]
        },
        13: {
            "id": 13,
            "title": "Matrix Rotation",
            "statement": "Rotate a 2D matrix 90 degrees clockwise in-place.\n\nExample:\n- Input: [[1,2,3],[4,5,6],[7,8,9]]\n- Output: [[7,4,1],[8,5,2],[9,6,3]]",
            "function_signature": "def rotate_matrix(matrix):",
            "hints": [
                "First transpose the matrix (swap rows and columns)",
                "Then reverse each row",
                "This achieves a 90-degree clockwise rotation",
                "Modify the matrix in-place"
            ],
            "solution": "def rotate_matrix(matrix):\n    n = len(matrix)\n    \n    # Transpose the matrix\n    for i in range(n):\n        for j in range(i, n):\n            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]\n    \n    # Reverse each row\n    for i in range(n):\n        matrix[i].reverse()\n    \n    return matrix",
            "test_cases": [
                {"input": [[[1,2,3],[4,5,6],[7,8,9]]], "expected": [[7,4,1],[8,5,2],[9,6,3]]},
                {"input": [[[1,2],[3,4]]], "expected": [[3,1],[4,2]]},
                {"input": [[[1]]], "expected": [[1]]}
            ]
        },
        14: {
            "id": 14,
            "title": "Prime Number Generator",
            "statement": "Generate all prime numbers up to a given limit using an efficient algorithm.\n\nExample:\n- Input: 20\n- Output: [2, 3, 5, 7, 11, 13, 17, 19]",
            "function_signature": "def generate_primes(limit):",
            "hints": [
                "Use the Sieve of Eratosthenes algorithm",
                "Create a boolean array to mark prime numbers",
                "Start with 2 and mark all its multiples as non-prime",
                "Continue with the next unmarked number"
            ],
            "solution": "def generate_primes(limit):\n    if limit < 2:\n        return []\n    \n    sieve = [True] * (limit + 1)\n    sieve[0] = sieve[1] = False\n    \n    for i in range(2, int(limit**0.5) + 1):\n        if sieve[i]:\n            for j in range(i*i, limit + 1, i):\n                sieve[j] = False\n    \n    return [i for i in range(2, limit + 1) if sieve[i]]",
            "test_cases": [
                {"input": [20], "expected": [2, 3, 5, 7, 11, 13, 17, 19]},
                {"input": [1], "expected": []},
                {"input": [2], "expected": [2]},
                {"input": [10], "expected": [2, 3, 5, 7]}
            ]
        },
        15: {
            "id": 15,
            "title": "Merge Intervals",
            "statement": "Given a list of intervals, merge overlapping intervals.\n\nExample:\n- Input: [[1,3],[2,6],[8,10],[15,18]]\n- Output: [[1,6],[8,10],[15,18]]",
            "function_signature": "def merge_intervals(intervals):",
            "hints": [
                "Sort intervals by start time",
                "Iterate through sorted intervals",
                "Merge current interval with previous if they overlap",
                "An interval [a,b] overlaps with [c,d] if b >= c"
            ],
            "solution": "def merge_intervals(intervals):\n    if not intervals:\n        return []\n    \n    intervals.sort(key=lambda x: x[0])\n    merged = [intervals[0]]\n    \n    for current in intervals[1:]:\n        last = merged[-1]\n        \n        if current[0] <= last[1]:\n            merged[-1] = [last[0], max(last[1], current[1])]\n        else:\n            merged.append(current)\n    \n    return merged",
            "test_cases": [
                {"input": [[[1,3],[2,6],[8,10],[15,18]]], "expected": [[1,6],[8,10],[15,18]]},
                {"input": [[[1,4],[4,5]]], "expected": [[1,5]]},
                {"input": [[[1,4],[2,3]]], "expected": [[1,4]]}
            ]
        },
        16: {
            "id": 16,
            "title": "Shopping Cart Calculator",
            "statement": "Calculate total cost including tax and discounts for a shopping cart.\n\nRules:\n- Electronics: 8% tax\n- Clothing: 5% tax\n- Books: 0% tax\n- Discount: 10% off if total > $100\n\nExample:\n- Input: [{\"name\": \"Laptop\", \"price\": 500, \"category\": \"Electronics\"}]\n- Output: 540.0 (500 + 8% tax)",
            "function_signature": "def calculate_total(items):",
            "hints": [
                "Create a dictionary for tax rates by category",
                "Calculate tax for each item based on its category",
                "Sum all item totals including tax",
                "Apply discount if total exceeds $100"
            ],
            "solution": "def calculate_total(items):\n    tax_rates = {\n        'Electronics': 0.08,\n        'Clothing': 0.05,\n        'Books': 0.00\n    }\n    \n    subtotal = 0\n    for item in items:\n        price = item['price']\n        category = item['category']\n        tax_rate = tax_rates.get(category, 0)\n        \n        item_total = price * (1 + tax_rate)\n        subtotal += item_total\n    \n    if subtotal > 100:\n        subtotal *= 0.9\n    \n    return round(subtotal, 2)",
            "test_cases": [
                {"input": [[{"name": "Laptop", "price": 500, "category": "Electronics"}]], "expected": 486.0},
                {"input": [[{"name": "Book", "price": 20, "category": "Books"}]], "expected": 20.0},
                {"input": [[{"name": "Shirt", "price": 60, "category": "Clothing"}]], "expected": 63.0}
            ]
        },
        17: {
            "id": 17,
            "title": "Log File Parser",
            "statement": "Parse log entries and count occurrences of different log levels.\n\nExample:\n- Input: [\"2023-01-01 10:00:00 INFO User logged in\", \"2023-01-01 10:01:00 ERROR Connection failed\"]\n- Output: {\"INFO\": 1, \"ERROR\": 1}",
            "function_signature": "def parse_log_levels(log_entries):",
            "hints": [
                "Use regular expressions to find log levels",
                "Look for patterns like INFO, ERROR, WARN, DEBUG",
                "Count occurrences of each level",
                "The pattern \\b(DEBUG|INFO|WARN|ERROR|FATAL)\\b works well"
            ],
            "solution": "def parse_log_levels(log_entries):\n    import re\n    \n    level_counts = {}\n    \n    for entry in log_entries:\n        match = re.search(r'\\b(DEBUG|INFO|WARN|ERROR|FATAL)\\b', entry)\n        if match:\n            level = match.group(1)\n            level_counts[level] = level_counts.get(level, 0) + 1\n    \n    return level_counts",
            "test_cases": [
                {"input": [["2023-01-01 10:00:00 INFO User logged in", "2023-01-01 10:01:00 ERROR Connection failed"]], "expected": {"INFO": 1, "ERROR": 1}},
                {"input": [["DEBUG Starting application", "INFO App started", "DEBUG Loading config"]], "expected": {"DEBUG": 2, "INFO": 1}},
                {"input": [["No log level here"]], "expected": {}}
            ]
        },
        18: {
            "id": 18,
            "title": "Password Strength Validator",
            "statement": "Validate password strength based on criteria:\n- At least 8 characters\n- Contains uppercase and lowercase letters\n- Contains at least one digit\n- Contains at least one special character (!@#$%^&*)\n\nExample:\n- Input: \"Password123!\"\n- Output: True",
            "function_signature": "def is_strong_password(password):",
            "hints": [
                "Check length first",
                "Use regular expressions for each criteria",
                "Check for uppercase: [A-Z]",
                "Check for lowercase: [a-z]",
                "Check for digits: \\d",
                "Check for special chars: [!@#$%^&*]"
            ],
            "solution": "def is_strong_password(password):\n    import re\n    \n    if len(password) < 8:\n        return False\n    \n    if not re.search(r'[A-Z]', password):\n        return False\n    \n    if not re.search(r'[a-z]', password):\n        return False\n    \n    if not re.search(r'\\d', password):\n        return False\n    \n    if not re.search(r'[!@#$%^&*]', password):\n        return False\n    \n    return True",
            "test_cases": [
                {"input": ["Password123!"], "expected": True},
                {"input": ["weak"], "expected": False},
                {"input": ["NoDigits!"], "expected": False},
                {"input": ["nouppercas123!"], "expected": False}
            ]
        },
        19: {
            "id": 19,
            "title": "Data Structure Converter",
            "statement": "Convert a flat list of records into a nested dictionary structure.\n\nExample:\n- Input: [{\"country\": \"USA\", \"state\": \"CA\", \"city\": \"LA\", \"population\": 4000000}]\n- Output: {\"USA\": {\"CA\": {\"LA\": 4000000}}}",
            "function_signature": "def convert_to_nested(records):",
            "hints": [
                "Iterate through each record",
                "Navigate through the nested structure for each record",
                "Create nested dictionaries as needed",
                "Set the final value at the deepest level"
            ],
            "solution": "def convert_to_nested(records):\n    result = {}\n    \n    for record in records:\n        current = result\n        keys = ['country', 'state', 'city']\n        \n        for key in keys[:-1]:\n            if record[key] not in current:\n                current[record[key]] = {}\n            current = current[record[key]]\n        \n        current[record[keys[-1]]] = record['population']\n    \n    return result",
            "test_cases": [
                {"input": [[{"country": "USA", "state": "CA", "city": "LA", "population": 4000000}]], "expected": {"USA": {"CA": {"LA": 4000000}}}},
                {"input": [[{"country": "USA", "state": "NY", "city": "NYC", "population": 8000000}, {"country": "USA", "state": "CA", "city": "SF", "population": 800000}]], "expected": {"USA": {"NY": {"NYC": 8000000}, "CA": {"SF": 800000}}}}
            ]
        },
        20: {
            "id": 20,
            "title": "Binary Search Implementation",
            "statement": "Implement binary search on a sorted array and return the index of the target element.\n\nExample:\n- Input: arr = [1, 3, 5, 7, 9, 11], target = 7\n- Output: 3\n- Input: arr = [1, 3, 5, 7, 9, 11], target = 6\n- Output: -1 (not found)",
            "function_signature": "def binary_search(arr, target):",
            "hints": [
                "Use two pointers: left and right",
                "Calculate middle index",
                "Compare middle element with target",
                "Adjust left or right pointer based on comparison",
                "Return -1 if target not found"
            ],
            "solution": "def binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    \n    while left <= right:\n        mid = (left + right) // 2\n        \n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    \n    return -1",
            "test_cases": [
                {"input": [[1, 3, 5, 7, 9, 11], 7], "expected": 3},
                {"input": [[1, 3, 5, 7, 9, 11], 6], "expected": -1},
                {"input": [[1], 1], "expected": 0},
                {"input": [[], 1], "expected": -1}
            ]
        }
    }

def load_problems():
    """Load problems from memory and merge with uploaded problems"""
    # Start with default problems
    all_problems = get_default_problems()
    
    # Add uploaded problems if any
    if hasattr(st.session_state, 'uploaded_problems') and st.session_state.uploaded_problems:
        # Merge uploaded problems, giving them IDs starting from 21
        next_id = max(all_problems.keys()) + 1
        for problem in st.session_state.uploaded_problems.values():
            # Create a copy of the problem with a new ID if it conflicts
            new_problem = problem.copy()
            if problem['id'] in all_problems:
                new_problem['id'] = next_id
                next_id += 1
            all_problems[new_problem['id']] = new_problem
    
    return all_problems

def execute_user_code(user_code, test_cases):
    """Execute user code safely and run test cases"""
    results = []
    
    try:
        # Create a namespace for execution
        namespace = {}
        
        # Execute the user's code
        exec(user_code, namespace)
        
        # Extract the function (assume it's the first function defined)
        function_name = None
        for name, obj in namespace.items():
            if callable(obj) and not name.startswith('_'):
                function_name = name
                break
        
        if not function_name:
            return False, "No function found in your code"
        
        user_function = namespace[function_name]
        
        # Run test cases
        passed = 0
        total = len(test_cases)
        
        for i, test_case in enumerate(test_cases):
            try:
                # Prepare input arguments
                args = test_case['input']
                expected = test_case['expected']
                
                # Call the function
                if len(args) == 1:
                    result = user_function(args[0])
                else:
                    result = user_function(*args)
                
                # Compare result
                if result == expected:
                    results.append(f"✅ Test case {i+1}: PASSED")
                    passed += 1
                else:
                    results.append(f"❌ Test case {i+1}: FAILED - Expected {expected}, got {result}")
                    
            except Exception as e:
                results.append(f"❌ Test case {i+1}: ERROR - {str(e)}")
        
        success = passed == total
        summary = f"Passed {passed}/{total} test cases"
        
        return success, summary + "\n\n" + "\n".join(results)
        
    except Exception as e:
        return False, f"Code execution error: {str(e)}\n\n{traceback.format_exc()}"

def display_problem_stats(problem_id):
    """Display statistics for a problem"""
    stats = st.session_state.user_stats[problem_id]
    total = stats['success'] + stats['failure']
    
    if total > 0:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<span class="stat-badge success-badge">✅ {stats["success"]}</span>', 
                       unsafe_allow_html=True)
        with col2:
            st.markdown(f'<span class="stat-badge failure-badge">❌ {stats["failure"]}</span>', 
                       unsafe_allow_html=True)
        with col3:
            st.markdown(f'<span class="stat-badge total-badge">📊 {total}</span>', 
                       unsafe_allow_html=True)

def main():
    init_session_state()
    
    st.title("🎯 SHL Coding Exam Preparation Tool")
    st.markdown("Practice coding problems similar to those found in SHL assessments")
    
    # Sidebar for problem selection
    with st.sidebar:
        st.header("📋 Problems")
        
        # File uploader for additional problems
        with st.expander("📁 Upload Additional Problems"):
            st.markdown("**Upload a JSON file to add more problems**")
            uploaded_file = st.file_uploader(
                "Select JSON file",
                type=['json'],
                help="Upload a JSON file containing additional problems in the same format"
            )
            
            if uploaded_file is not None:
                try:
                    # Read and parse the uploaded file
                    content = uploaded_file.read().decode('utf-8')
                    problems_data = json.loads(content)
                    
                    # Store in session state and reload
                    if 'problems' in problems_data:
                        st.session_state.uploaded_problems = {problem['id']: problem for problem in problems_data['problems']}
                    else:
                        # Assume the uploaded file is a list of problems
                        st.session_state.uploaded_problems = {problem['id']: problem for problem in problems_data}
                    
                    # Reload all problems (this will merge default + uploaded)
                    st.session_state.problems = load_problems()
                    st.success(f"✅ {len(st.session_state.uploaded_problems)} additional problems loaded!")
                    st.rerun()  # Refresh the app
                    
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON format: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error loading file: {str(e)}")
        
        st.markdown("---")
        
        # Overall progress
        total_problems = len(st.session_state.problems)
        solved_problems = sum(1 for problem_id in st.session_state.problems.keys() 
                            if st.session_state.user_stats[problem_id]['success'] > 0)
        
        # Avoid division by zero
        progress_percentage = (solved_problems/total_problems*100) if total_problems > 0 else 0
        
        st.metric("Progress", f"{solved_problems}/{total_problems}", 
                 f"{progress_percentage:.1f}%")
        
        st.markdown("---")
        
        # Problem list
        for problem_id, problem in st.session_state.problems.items():
            stats = st.session_state.user_stats[problem_id]
            success_rate = ""
            if stats['success'] + stats['failure'] > 0:
                rate = stats['success'] / (stats['success'] + stats['failure']) * 100
                success_rate = f" ({rate:.0f}%)"
            
            status_icon = "✅" if stats['success'] > 0 else "⭕"
            
            if st.button(f"{status_icon} {problem['title']}{success_rate}", 
                        key=f"problem_{problem_id}",
                        use_container_width=True):
                st.session_state.selected_problem = problem_id
                st.session_state.show_hints[problem_id] = False
                st.session_state.current_hint_index[problem_id] = 0
    
    # Main content area
    if st.session_state.selected_problem is None:
        st.markdown("""
        ## Welcome to the SHL Coding Exam Prep Tool! 👋
        
        This tool helps you practice coding problems similar to those found in SHL assessments.
        
        ### 🎯 Features:
        - **20 Built-in Problems**: Ready-to-use coding challenges covering common topics
        - **Upload Additional Problems**: Add your own problems via JSON file upload
        - **Real-time Testing**: Instant feedback on your solutions
        - **Progressive Hints**: Get help when you're stuck
        - **Progress Tracking**: Monitor your success rate and improvement
        
        ### 🚀 How to use:
        1. **Select a problem** from the sidebar (20 problems available by default)
        2. **Read the problem statement** and examples carefully
        3. **Write your solution** in the code editor
        4. **Submit** to test against multiple test cases
        5. **Use hints** if you need guidance
        6. **Track your progress** and identify areas for improvement
        
        ### 📁 Adding More Problems:
        You can upload additional problems by:
        - Using the "Upload Additional Problems" section in the sidebar
        - Uploading a JSON file with problems in the same format
        - Problems will be merged with the existing 20 default problems
        
        **Select a problem from the sidebar to get started!**
        """)
        return
    
    # Display selected problem
    problem = st.session_state.problems[st.session_state.selected_problem]
    
    st.header(f"Problem {problem['id']}: {problem['title']}")
    
    # Problem statistics
    display_problem_stats(problem['id'])
    
    # Problem statement
    st.subheader("📝 Problem Statement")
    st.markdown(problem['statement'])
    
    # Function signature
    st.subheader("✏️ Function Signature")
    st.code(problem['function_signature'], language='python')
    
    # Hints section
    st.subheader("💡 Hints")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Show Next Hint", key="hint_button"):
            st.session_state.show_hints[problem['id']] = True
            current_idx = st.session_state.current_hint_index[problem['id']]
            if current_idx < len(problem['hints']) - 1:
                st.session_state.current_hint_index[problem['id']] += 1
    
    with col2:
        if st.button("Reset Hints", key="reset_hints"):
            st.session_state.show_hints[problem['id']] = False
            st.session_state.current_hint_index[problem['id']] = 0
    
    if st.session_state.show_hints[problem['id']]:
        hint_idx = st.session_state.current_hint_index[problem['id']]
        for i in range(hint_idx + 1):
            st.markdown(f'<div class="hint-box">💡 <strong>Hint {i+1}:</strong> {problem["hints"][i]}</div>', 
                       unsafe_allow_html=True)
    
    # Code editor
    st.subheader("👨‍💻 Your Solution")
    
    # Pre-fill with function signature
    default_code = problem['function_signature'] + "\n    # Your code here\n    pass"
    
    if ACE_AVAILABLE:
        user_code = st_ace(
            value=default_code,
            language='python',
            theme='monokai',
            key=f"ace_editor_{problem['id']}",
            height=300,
            auto_update=True,
            font_size=14,
            tab_size=4,
            wrap=False,
            annotations=None,
            markers=None
        )
    else:
        user_code = st.text_area(
            "Write your solution:",
            value=default_code,
            height=300,
            key=f"code_editor_{problem['id']}"
        )
    
    # Submit button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🚀 Submit Solution", type="primary"):
            if user_code.strip():
                with st.spinner("Testing your solution..."):
                    success, result = execute_user_code(user_code, problem['test_cases'])
                    
                    # Update statistics
                    if success:
                        st.session_state.user_stats[problem['id']]['success'] += 1
                        st.markdown(f'<div class="success-box">🎉 <strong>Success!</strong><br>{result}</div>', 
                                   unsafe_allow_html=True)
                    else:
                        st.session_state.user_stats[problem['id']]['failure'] += 1
                        st.markdown(f'<div class="error-box">❌ <strong>Failed!</strong><br>{result}</div>', 
                                   unsafe_allow_html=True)
            else:
                st.error("Please write some code before submitting!")
    
    with col2:
        if st.button("👀 Show Solution"):
            st.subheader("📚 Reference Solution")
            st.code(problem['solution'], language='python')
            
            # Test the reference solution
            success, result = execute_user_code(problem['solution'], problem['test_cases'])
            st.markdown(f'<div class="success-box">✅ <strong>Reference Solution Test Results:</strong><br>{result}</div>', 
                       unsafe_allow_html=True)
    
    # Test cases preview
    with st.expander("👁️ View Test Cases"):
        st.markdown("**Test Cases:**")
        for i, test_case in enumerate(problem['test_cases']):
            st.markdown(f"**Test {i+1}:**")
            st.markdown(f"- Input: `{test_case['input']}`")
            st.markdown(f"- Expected Output: `{test_case['expected']}`")

if __name__ == "__main__":
    main()