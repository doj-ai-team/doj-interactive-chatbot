import os
import sys

# Ensure we can import from views
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from views.chatbotLegalv2 import process_input

def test_detailed_responses():
    test_queries = [
        "How can I register a FIR for theft? Explain the steps clearly.",
        "What are the steps to get legal aid in India?",
        "What is eCourts and how do I use it to check my case status?"
    ]
    
    chat_name = "verification_chat_123"
    
    print("Starting verification of detailed responses...\n")
    
    for i, query in enumerate(test_queries):
        print(f"--- Test {i+1}: {query} ---")
        try:
            # chat_name, user_input, language="English", return_source=False
            response, low_confidence, resources = process_input(chat_name, query)
            print(f"AI Response:\n{response}\n")
            print("-" * 50)
        except Exception as e:
            print(f"Error testing query '{query}': {e}")

if __name__ == '__main__':
    test_detailed_responses()
