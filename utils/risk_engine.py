import os
import json
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(temperature=0.1, groq_api_key=GROQ_API_KEY, model_name="llama-3.1-8b-instant")

def evaluate_risk(offense_type: str, legal_context: str) -> dict:
    """
    Evaluates risk based on the offense type and provided legal context.
    Returns: Severity (Low/Medium/High), Bailable, Immediate Action Required, Punishment Range.
    """
    if not offense_type or offense_type.lower() == "none":
         return {
            "severity": "Unknown",
            "bailable": "Unknown",
            "immediate_action": "No",
            "punishment_range": "Unknown"
         }

    prompt = f"""
    You are a Legal Risk Scoring Engine.
    Based on the following Offense Type and Legal Context, determine the risk parameters.
    
    Offense Type: {offense_type}
    Legal Context: {legal_context}
    
    Output strictly as a JSON object with EXACTLY the following keys (do not include markdown codeblocks, just the raw JSON):
    "severity": [Low, Medium, or High]
    "bailable": [Bailable or Non-Bailable]
    "immediate_action": [Yes or No]
    "punishment_range": [Short summary of punishment, e.g., 'Up to 3 years or fine']
    """
    try:
        response = llm.invoke(prompt).content.strip()
        
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        risk_data = json.loads(response.strip())
        return risk_data
    except Exception as e:
         print(f"Risk Scoring Error: {e}")
         return {
             "severity": "Pending Analysis",
             "bailable": "Pending Analysis",
             "immediate_action": "Pending Analysis",
             "punishment_range": "Pending Analysis"
         }
