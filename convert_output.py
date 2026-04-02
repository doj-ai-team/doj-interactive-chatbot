import os
try:
    with open('test_problem3_output.txt', 'rb') as f:
        content = f.read()
    text = content.decode('utf-16')
    with open('test_problem3_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Converted to test_problem3_utf8.txt")
except Exception as e:
    print(f"Error: {e}")
