import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from views.chatbotLegalv2 import hybrid_retrieve, process_input

def test_hindi_retrieval():
    print("--- Testing Hindi Retrieval (Bail) ---")
    query = "जमानत क्या है?"
    context, source, resources = hybrid_retrieve(query)
    
    print(f"Query: {query}")
    print(f"Source: {source}")
    if "जमानत" in context and "JSON_CONCEPT" in source:
        print("PASS: Hindi explanation for Bail found in context.")
    else:
        print("FAIL: Hindi explanation NOT found or source mismatch.")
        print(f"Source: {source}")
        print(f"Context snippet: {context[:500]}...")

def test_tamil_retrieval():
    print("\n--- Testing Tamil Retrieval (FIR) ---")
    query = "முதல் தகவல் அறிக்கை என்றால் என்ன?"
    context, source, resources = hybrid_retrieve(query)
    
    print(f"Query: {query}")
    print(f"Source: {source}")
    if "முதல் தகவல் அறிக்கை" in context and "JSON_CONCEPT" in source:
        print("PASS: Tamil explanation for FIR found in context.")
    else:
        print("FAIL: Tamil explanation NOT found or source mismatch.")
        print(f"Source: {source}")
        print(f"Context snippet: {context[:500]}...")

def test_hindi_full_response():
    print("\n--- Testing Full Hindi Response ---")
    chat_name = "test_hindi_chat"
    user_input = "संज्ञेय अपराध क्या है?"
    
    try:
        response, low_confidence, resources = process_input(chat_name, user_input)
        print("Checking if response is in Hindi and has structured format")
        # Check for Devanagari characters
        if any('\u0900' <= char <= '\u097F' for char in response):
            print("PASS: Response contains Hindi script.")
        else:
            print("FAIL: Response does NOT contain Hindi script.")
            
        print("\nResponse Snippet:")
        print(response[:800] + "...")
        
    except Exception as e:
        print(f"Error during process_input: {e}")

if __name__ == "__main__":
    test_hindi_retrieval()
    test_tamil_retrieval()
    test_hindi_full_response()
