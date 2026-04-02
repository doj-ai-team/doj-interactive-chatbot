import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from views.chatbotLegalv2 import gemini_generate, process_input

def test_language():
    user_input = "hi do you know about murder ase and section"
    print(f"Testing input: {user_input}")
    
    # Simulate the prompt construction in process_input
    intent = "Criminal Offense"
    formatter_instructions = f"""
    INSTRUCTIONS FOR AI GENERATION:
    1. If the user is asking a clear legal question regarding an offense, a dispute, or an incident (Intent: {intent}), you MUST output your final response STRICTLY in the following 5-point Markdown format. ...
    """
    
    prompt = f"""
No specific IPC section retrieved. Provide a general, educational summary under Indian law.

{formatter_instructions}

Conversation History:

User: {user_input}
AI:"""

    result = gemini_generate(prompt)
    print("--- Result ---")
    print(result.encode('utf-8', 'replace').decode('utf-8'))

if __name__ == '__main__':
    test_language()
