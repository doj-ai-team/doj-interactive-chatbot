import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from views.chatbotLegalv2 import process_input

chat_name = "debug_test_chat"
user_input = "How do I report a cybercrime?"

print(f"Calling process_input with input: '{user_input}'...")

try:
    # We call it with return_source=True as app.py does
    response, source_type, low_confidence, citations = process_input(chat_name, user_input, language="English", return_source=True)
    print("✅ Success!")
    print(f"Source Type: {source_type}")
    print(f"Citations: {len(citations)}")
    print(f"Response Preview: {response[:100]}...")
except Exception as e:
    print("❌ Error caught!")
    import traceback
    traceback.print_exc()
