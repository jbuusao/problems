# JP'S SHL Coding Assessment Simulator

This simulator, that was Gen AI generated, provides 20 typical SHL problems that you can try out my submitting your solutions, that are tested against baselined solutions. You can compare your solution against the baselined solution. You can also load additional problems, that would be generated using the prompt template below

---

## Prompt Template:

```
Generate 10 coding problems suitable for SHL assessments in JSON format. 
Each problem should follow this exact structure and style:

**Requirements:**
- Problems should test fundamental programming concepts commonly found in SHL assessments
- Difficulty should be intermediate level (solvable in 15-30 minutes)
- Include practical, real-world scenarios when possible
- Provide comprehensive test cases that cover edge cases
- Solutions should be clean, readable, and efficient

**Problem Categories to Include:**
- Array/List manipulation
- String processing and validation
- Data structure operations (dictionaries, sets, stacks, queues)
- Algorithm implementation (sorting, searching, recursion)
- Mathematical calculations and logic
- Data parsing and transformation
- Pattern matching and regular expressions
- Object-oriented programming concepts
- Business logic implementation

**JSON Structure (STRICT FORMAT):**
```json
{
  "problems": [
    {
      "id": [UNIQUE_INTEGER],
      "title": "[DESCRIPTIVE_TITLE]",
      "statement": "[DETAILED_PROBLEM_DESCRIPTION_WITH_EXAMPLES]",
      "function_signature": "def function_name(parameters):",
      "categories": [LIST_OF_PROBLEM_CATEGORIES],
      "python_constructs": [LIST_OF_PYTHON_CONSTRUCTS_USED_IN_SUGGESTED_SOLUTION],
      "hints": [
        "[HINT_1_GENTLE_GUIDANCE]",
        "[HINT_2_MORE_SPECIFIC]",
        "[HINT_3_IMPLEMENTATION_DETAIL]"
      ],
      "solution": "[COMPLETE_PYTHON_SOLUTION_WITH_PROPER_INDENTATION]",
      "test_cases": [
        {"input": [[ARGUMENTS_AS_LIST]], "expected": [EXPECTED_RESULT]},
        {"input": [[EDGE_CASE_ARGUMENTS]], "expected": [EDGE_CASE_RESULT]},
        {"input": [[ANOTHER_TEST_CASE]], "expected": [ANOTHER_RESULT]}
      ]
    }
  ]
}
```

**Specific Guidelines:**

1. **Problem Statement Format:**
   - Start with a clear, concise description
   - Include 1-2 concrete examples with input/output
   - Specify any constraints or special requirements
   - Use professional, technical language. Also include line breaks to improve readibility

2. **Function Signatures:**
   - Use descriptive function names
   - Parameter names should be clear and meaningful
   - Follow Python naming conventions

3. **Hints Structure:**
   - Hint 1: High-level approach or concept
   - Hint 2: Specific algorithm or data structure suggestion
   - Hint 3: Implementation detail or edge case consideration

4. **Solution Requirements:**
   - Include proper error handling where appropriate
   - Use efficient algorithms (avoid O(n²) when O(n) is possible)
   - Include necessary imports
   - Follow PEP 8 style guidelines
   - Add brief comments for complex logic

5. **Test Cases:**
   - Minimum 3-4 test cases per problem
   - Include normal cases, edge cases, and boundary conditions
   - Cover empty inputs, single elements, and large datasets
   - Imoportant: Ensure all test cases pass with the provided solution
   - Important: ensure that the generated JSON format for the test cases are syntactically correct

6. **Problem Types to Consider:**
   - Data validation (email, phone, credit card)
   - Business calculations (tax, discounts, interest)
   - Text processing (word counting, formatting)
   - Data aggregation and analysis
   - Algorithm challenges (sorting, searching)
   - Pattern recognition and parsing

**Example Problem Types:**
- Credit card number validation
- Employee payroll calculations
- Log file analysis
- Shopping cart operations
- Data format conversion
- Graph traversal problems
- Time/date calculations
- Statistical analysis
- File processing
- API response parsing

Generate problems that are:
- ✅ Practical and realistic
- ✅ Well-tested and debugged (please check that the reference solution passes the test cases)
- ✅ Appropriately challenging
- ✅ Clearly documented
- ✅ Ready for immediate use in the SHL preparation tool

Please ensure all JSON are valid and properly formatted.
```

---

## Usage Instructions:

1. **Copy the prompt above**
2. **Specify the number of problems** you want (replace [NUMBER])
3. **Paste into your AI assistant**
4. **Save the generated JSON** to your problems file
5. **Load into the SHL preparation tool**

## Customization Options:

- **Difficulty Level**: Add "beginner", "intermediate", or "advanced" to the prompt
- **Specific Topics**: Request problems focused on particular areas (e.g., "focus on data structures")
- **Industry Context**: Ask for problems from specific domains (e.g., "finance-related problems")
- **Programming Concepts**: Target specific concepts (e.g., "object-oriented programming problems")

## Quality Assurance:

The generated problems will include:
- ✅ Complete, working solutions
- ✅ Comprehensive test cases
- ✅ Progressive hint systems
- ✅ Professional problem statements
- ✅ SHL-appropriate difficulty levels