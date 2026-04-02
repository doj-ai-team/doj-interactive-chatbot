import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from views.chatbotLegalv2 import hybrid_retrieve, process_input

def test_concept_retrieval():
    print("--- Testing Concept Retrieval (Bail) ---")
    query = "What is bail and what are its types?"
    context, source, resources = hybrid_retrieve(query)
    
    print(f"Query: {query}")
    print(f"Source: {source}")
    print("Context contains GENERAL_LEGAL_CONCEPT:")
    if "GENERAL LEGAL CONCEPT: Bail" in context:
        print("PASS: Bail concept found in context.")
    else:
        print("FAIL: Bail concept NOT found in context.")
        print(f"Context snippet: {context[:500]}...")

def test_fir_workload_reduction():
    print("\n--- Testing FIR Retrieval & Workflow Integration ---")
    query = "How to file an FIR?"
    context, source, resources = hybrid_retrieve(query)
    
    print(f"Query: {query}")
    print(f"Source: {source}")
    if "GENERAL LEGAL CONCEPT: FIR" in context:
        print("PASS: FIR concept found in context.")
    else:
        print("FAIL: FIR concept NOT found in context.")

def test_full_response_structure():
    print("\n--- Testing Full response for Bail ---")
    chat_name = "test_workload_chat"
    user_input = "What is anticipatory bail?"
    
    try:
        response, low_confidence, resources = process_input(chat_name, user_input)
        print("Checking if response mentions 'Anticipatory Bail' and '6-point format'")
        print(f"Response Length: {len(response)}")
        if "### 1." in response and ("### 5." in response or "### 6." in response):
            print("PASS: Structured format detected (found sections 1 and 5/6).")
        else:
            print("FAIL: Structured format missing (checked for ### 1. and ### 5/6.).")
            
        if "anticipatory bail" in response.lower():
            print("PASS: Anticipatory Bail concept found.")
        else:
            print("FAIL: Anticipatory Bail NOT found in final response.")
            
        print("\nResponse Snippet:")
        print(response[:800] + "...")
        
    except Exception as e:
        print(f"Error during process_input: {e}")

if __name__ == "__main__":
    test_concept_retrieval()
    test_fir_workload_reduction()
    test_full_response_structure()
