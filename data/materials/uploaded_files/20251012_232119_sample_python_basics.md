# Sample Study Material - Python Basics

## Introduction to Python

Python is a high-level, interpreted programming language known for its simplicity and readability. It was created by Guido van Rossum and first released in 1991.

## Key Features of Python

1. **Easy to Learn**: Python has a simple syntax that is easy to understand
2. **Interpreted Language**: Code is executed line by line
3. **Dynamically Typed**: No need to declare variable types
4. **Object-Oriented**: Supports OOP concepts like classes and inheritance
5. **Large Standard Library**: Comes with many built-in modules

## Basic Data Types

### Numbers
- **Integers**: Whole numbers (e.g., 1, 42, -5)
- **Floats**: Decimal numbers (e.g., 3.14, -0.5)
- **Complex**: Complex numbers (e.g., 3+4j)

### Strings
Strings are sequences of characters enclosed in quotes:
```python
name = "Python"
message = 'Hello World'
multiline = """This is a
multiline string"""
```

### Booleans
Boolean values are either True or False:
```python
is_student = True
is_working = False
```

### Lists
Lists are ordered, mutable collections:
```python
numbers = [1, 2, 3, 4, 5]
fruits = ["apple", "banana", "orange"]
mixed = [1, "hello", True, 3.14]
```

### Tuples
Tuples are ordered, immutable collections:
```python
coordinates = (10, 20)
rgb_color = (255, 128, 0)
```

### Dictionaries
Dictionaries store key-value pairs:
```python
student = {
    "name": "John",
    "age": 20,
    "major": "Computer Science"
}
```

## Control Flow

### If Statements
```python
age = 18
if age >= 18:
    print("You are an adult")
elif age >= 13:
    print("You are a teenager")
else:
    print("You are a child")
```

### For Loops
```python
# Iterate over a list
fruits = ["apple", "banana", "orange"]
for fruit in fruits:
    print(fruit)

# Iterate with range
for i in range(5):
    print(i)  # Prints 0, 1, 2, 3, 4
```

### While Loops
```python
count = 0
while count < 5:
    print(count)
    count += 1
```

## Functions

Functions are reusable blocks of code:
```python
def greet(name):
    return f"Hello, {name}!"

def add_numbers(a, b):
    return a + b

# Function with default parameter
def power(base, exponent=2):
    return base ** exponent
```

## Important Concepts

### Indentation
Python uses indentation to define code blocks. Always use consistent spacing (typically 4 spaces).

### Comments
```python
# This is a single-line comment

"""
This is a
multi-line comment
"""
```

### String Methods
Common string operations:
- `.upper()` - Convert to uppercase
- `.lower()` - Convert to lowercase
- `.strip()` - Remove whitespace
- `.split()` - Split string into list
- `.replace()` - Replace substring

### List Methods
Common list operations:
- `.append(item)` - Add item to end
- `.insert(index, item)` - Insert at position
- `.remove(item)` - Remove first occurrence
- `.pop()` - Remove and return last item
- `.sort()` - Sort the list

## Common Operators

### Arithmetic Operators
- `+` Addition
- `-` Subtraction
- `*` Multiplication
- `/` Division
- `//` Floor division
- `%` Modulus
- `**` Exponentiation

### Comparison Operators
- `==` Equal to
- `!=` Not equal to
- `>` Greater than
- `<` Less than
- `>=` Greater than or equal to
- `<=` Less than or equal to

### Logical Operators
- `and` - Both conditions must be True
- `or` - At least one condition must be True
- `not` - Negates the condition

## Best Practices

1. **Use descriptive variable names**: `student_count` instead of `sc`
2. **Follow PEP 8 style guide**: Python's official style guide
3. **Write comments**: Explain complex logic
4. **Keep functions small**: Each function should do one thing
5. **Use meaningful function names**: `calculate_average()` instead of `calc()`

## Common Mistakes to Avoid

1. **Forgetting colons**: After if, for, while, def statements
2. **Incorrect indentation**: All blocks must be properly indented
3. **Mixing tabs and spaces**: Use spaces consistently
4. **Modifying list while iterating**: Create a copy first
5. **Not handling exceptions**: Use try-except blocks for error handling

## Practice Questions

1. What is the difference between a list and a tuple?
2. How do you create a dictionary in Python?
3. What is the purpose of indentation in Python?
4. What is the difference between `==` and `=`?
5. How do you create a function in Python?

## Answers to Practice Questions

1. Lists are mutable (can be changed) while tuples are immutable (cannot be changed after creation)
2. Use curly braces with key-value pairs: `my_dict = {"key": "value"}`
3. Indentation defines code blocks and structure in Python
4. `==` compares values (equality), `=` assigns values
5. Use the `def` keyword followed by function name and parameters

## Additional Resources

- Official Python Documentation: https://docs.python.org
- Python Tutorial for Beginners: https://www.python.org/about/gettingstarted/
- Practice Platform: https://www.hackerrank.com/domains/python

---

*This is a sample study material. Upload materials like this to use with the AI Assistant's Materials Mode!*
