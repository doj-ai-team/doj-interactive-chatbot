import requests
import json
import os

# Ensure the Flask app is running before executing this script
URL = "http://127.0.0.1:5000/chat"
PAYLOAD = {
    "user_input": "How do I report a cybercrime?",
    "chat_name": "verification_chat",
    "language": "English"
}
HEADERS = {"Content-Type": "application/json"}

print(f"Testing {URL} with query: '{PAYLOAD['user_input']}'...")

try:
    response = requests.post(URL, json=PAYLOAD, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        print("✅ Response received successfully.")
        
        # Check for response text
        if "response" in data and len(data["response"]) > 0:
            print("✅ 'response' field present and non-empty.")
            print(f"Preview: {data['response'][:100]}...")
        else:
            print("❌ 'response' field missing or empty.")
            
        # Check for citations
        if "citations" in data:
            print(f"✅ 'citations' field present. Found {len(data['citations'])} citations.")
            for c in data["citations"]:
                print(f"  - {c.get('title')} ({c.get('url')})")
            if len(data["citations"]) > 0:
                print("✅ Citations correctly structured.")
            else:
                print("⚠️ No citations found (Expected if keywords match resources).")
        else:
            print("❌ 'citations' field missing.")
            
        # Check for source
        print(f"✅ Source: {data.get('source')}")
        
    else:
        print(f"❌ Failed with status code: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"❌ Error: {e}")
