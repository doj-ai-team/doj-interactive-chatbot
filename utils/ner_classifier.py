import os
import json
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(temperature=0.1, groq_api_key=GROQ_API_KEY, model_name="llama-3.1-8b-instant")

def extract_entities_and_intent(user_query: str) -> dict:
    """
    Zero-Shot LLM Prompting to extract entities and classify intent.
    Returns a dictionary with keys: Act, Section, Offense, Court, Date, Punishment, IntentCategory
    """
    prompt = f"""
    You are a Legal Information Extraction system.
    Analyze the following user query and extract specific legal entities. If an entity is not mentioned, use the string "None".
    
    Valid Intent Categories: Cybercrime, Domestic violence, Fraud, Property dispute, Consumer complaint, Criminal Offense, Civil Offense, Legal Procedure/Concept, Greeting, General Inquiry, Other.
    
    Output ONLY a valid JSON object. Do not include any preamble or postamble.
    KEYS:
    "Act": [extracted act or "None"]
    "Section": [extracted section or "None"]
    "Offense": [extracted offense described or "None"]
    "Court": [extracted court or "None"]
    "Date": [extracted date or "None"]
    "Punishment": [extracted punishment or "None"]
    "IntentCategory": [Choose ONE from the Valid Intent Categories]

    User Query: "{user_query}"
    """
    try:
        response_obj = llm.invoke(prompt)
        response = response_obj.content.strip()
        
        # Robust JSON cleaning
        start = response.find('{')
        end = response.rfind('}')
        if start != -1 and end != -1:
            response = response[start:end+1]
        
        # Handle LLM outputting unquoted None
        response = response.replace(': None', ': "None"').replace(': none', ': "None"')
            
        extraction = json.loads(response)
        return extraction
    except Exception as e:
        print(f"NER Extraction Error: {e}")
        return {
            "Act": "None", "Section": "None", "Offense": "None", "Court": "None",
            "Date": "None", "Punishment": "None", "IntentCategory": "Other"
        }

if __name__ == "__main__":
    test_query = "My neighbor stole my car yesterday. What is the section for theft?"
    print(extract_entities_and_intent(test_query))
