import google.generativeai as genai
import config

problem_statement = """
# PHP Regex Homework

## Problem 1
How to make below regex invalidated if it ends with space or arithmatic operator?
```php
$prog_exp = "/(?!^[^{])(?:\G{(?P<operands>[a-z_]+)\}(?P<ops>(\*|\+|\-|\/))?)+/i";
```
"""

# Create the model
model = genai.GenerativeModel('gemini-1.5-flash')

# Generate content
response = model.generate_content(problem_statement)

print(response.text)