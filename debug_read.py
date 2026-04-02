import os
with open('test_problem3_output.txt', 'rb') as f:
    content = f.read()
    # Try different encodings
    for enc in ['utf-16', 'utf-16-le', 'utf-8', 'latin-1']:
        try:
            text = content.decode(enc)
            print(f"--- ENCODING: {enc} ---")
            print(text)
            break
        except:
            continue
