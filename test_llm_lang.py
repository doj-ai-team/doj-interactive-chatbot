import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from views.chatbotLegalv2 import gemini_generate, process_input

def test_language():
    user_input = "Hello!Do you know about eCourts?"
    prompt = f"""
No specific IPC section retrieved. Provide a general, educational summary under Indian law.

    INSTRUCTIONS FOR AI GENERATION:
    1. If the user is asking a clear legal question regarding an offense, a dispute, or an incident (Intent: Other), you MUST output your final response STRICTLY in the following 5-point Markdown format. Ensure you mention modern equivalents like BNS or BNSS alongside IPC if applicable.
        
        ### 1. Relevant Section(s) & Act(s)
        [List the exact sections from BNS, IPC, IT Act, Consumer Protection Act, etc.]

        ### 2. Legal Explanation
        [Provide a clear, simple explanation of the law and how it applies to the case]

        ### 3. Punishment / Penalty
        [Detail the specific punishments, fines, or terms of imprisonment based on the law]

        ### 4. Legal Procedure
        [Explain the legal procedure to file a case (e.g. cognizable vs non-cognizable, bailable vs non-bailable) and include official links like cybercrime.gov.in or ecourts.gov.in if applicable]

        ### 5. Recommended Action
        [Give practical next steps for the citizen (e.g. File FIR at nearest station, consult a lawyer, gather evidence)]
        
    2. If the user is engaging in casual conversation, greeting you, or asking a general informational question about a system (like "what is ecourts?"), completely ignore the 5-point format. Respond naturally and conversationally, and include official portal links.
    3. DETECT LANGUAGE: You MUST automatically detect the language the user used in their prompt and reply strictly in exactly that same language. Do NOT default to Hindi, English, or any other language unless the user wrote their prompt in that language. You must completely adapt to the user's language, dialect, and grammar. Respond fluently.
    
Conversation History:


User: {user_input}
AI:"""
    result_1 = gemini_generate(prompt)
    print(result_1.encode('utf-8', 'replace').decode('utf-8'))
    print("----- Using full process_input -----")
    res_vals = process_input("test_chat_123", user_input)
    response = res_vals[0]
    print(str(response).encode('utf-8', 'replace').decode('utf-8'))

if __name__ == '__main__':
    test_language()
