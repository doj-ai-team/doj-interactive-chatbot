import requests
import json

try:
    url = "http://127.0.0.1:5000/chat"
    headers = {"Content-Type": "application/json"}
    data = {"user_input": "What are the rules for registering an FIR in India?", "chat_name": "test_123"}
    print(f"Sending POST to {url}...")
    response = requests.post(url, headers=headers, json=data, timeout=120)
    with open("test_output.txt", "w", encoding="utf-8") as f:
        f.write(f"Status Code: {response.status_code}\n")
        f.write(f"Response: {response.text}\n")
    print("Done writing to test_output.txt")
except Exception as e:
    print(f"Error: {e}")
