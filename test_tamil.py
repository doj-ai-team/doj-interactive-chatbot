import requests
import json
import sys

def test_tamil_looping():
    url = "http://localhost:5000/chat"
    headers = {"Content-Type": "application/json"}
    payload = {
        "user_input": "who is high court judge of chennai",
        "chat_name": "tamil_loop_test",
        "language": "Tamil"
    }
    
    print("Sending Tamil request...")
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        with open("tamil_test_output_latest.txt", "w", encoding="utf-8") as f:
            f.write(data.get("response", ""))
        
        print(f"Reply length: {len(data.get('response', ''))}")
        print("Done writing to tamil_test_output_latest.txt")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_tamil_looping()
