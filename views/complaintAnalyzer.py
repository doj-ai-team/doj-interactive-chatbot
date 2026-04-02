import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(temperature=0.2, groq_api_key=GROQ_API_KEY, model_name="llama-3.1-8b-instant")

def analyze_complaint(complaint_text):
    """
    Analyzes an FIR or citizen complaint to extract relevant laws and precise actionable steps.
    :param complaint_text: str
    :return: dict with structured analysis
    """
    
    # Truncate text to avoid Groq token limit errors
    if len(complaint_text) > 3000:
        truncated_text = complaint_text[:3000] + "\n...[Content Truncated for Length]..."
    else:
        truncated_text = complaint_text

    # Build Gemini prompt
    prompt = f"""
You are an AI Legal Complaint Analyzer for the Indian Department of Justice.

Analyze the given FIR or citizen complaint text. You must extract the core issue and provide a highly structured, actionable legally sound plan for the citizen. Always include modern Indian laws (BNS, BNSS, IT Act, Consumer Protection Act) where relevant alongside or instead of IPC.

Response format MUST be strictly as follows (Markdown enabled):

**Core Issue Summary**: (Brief 1-2 sentence summary of what happened)
**Identified Offenses**: (List the potential legal violations)
**Relevant Acts & Sections**: (Exact sections from BNS, IPC, IT Act, etc. that apply)
**Immediate Required Actions**: (List 3-4 exact immediate steps the citizen must take. E.g., 'File a cybercrime report at cybercrime.gov.in', 'Preserve screenshot evidence', 'Visit the nearest Police Station to file a formal FIR')
**Long-Term Legal Strategy**: (What is the general procedure for this type of case going forward?)
**Disclaimer**: This is an AI-generated complaint analysis for guidance purposes and does not constitute formal legal advice.

Here is the complaint text:
{truncated_text}
"""
    try:
        response = llm.invoke(prompt).content.strip()
    except Exception as e:
        print(f"Groq API Error in complaint analysis: {e}")
        if "429" in str(e) or "quota" in str(e).lower():
            response = "**Error**: API Quota Exceeded. Please try again later."
        else:
            response = "**Error**: The AI failed to generate an analysis."

    return {
        "analysis": response
    }
