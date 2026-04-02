import json
import os
import re
import uuid
import datetime
from dotenv import load_dotenv
import sys
from upstash_redis import Redis

# LLM
from langchain_groq import ChatGroq

# HuggingFace + FAISS
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.embeddings import FakeEmbeddings


from transformers import AutoTokenizer, AutoModel

from utils.knowledge_graph import get_kg
from views.workflow import WORKFLOWS

# Load Centralized Resources
RESOURCES_PATH = "data/resources.json"
RESOURCES = {}
if os.path.exists(RESOURCES_PATH):
    with open(RESOURCES_PATH, "r", encoding="utf-8") as f:
        RESOURCES = json.load(f)

load_dotenv()

# ---------------- Redis Init ----------------
class MockRedis:
    def __init__(self, filepath="data/local_redis.json"):
        self.filepath = filepath
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    def get(self, key):
        return self.data.get(key)
        
    def set(self, key, value):
        self.data[key] = value
        self._save()
        
    def delete(self, key):
        if key in self.data:
            del self.data[key]
            self._save()

    def keys(self, pattern):
        return list(self.data.keys())

    def expire(self, key, seconds):
        # Fallback MockRedis expiration (no-op or you could implement actual background deletion if needed)
        pass

redis_url = os.getenv("UPSTASH_REDIS_URL")
if redis_url:
    try:
        redis_client = Redis(url=redis_url, token=os.getenv("UPSTASH_REDIS_TOKEN"))
    except:
        print("Failed to connect to Upstash Redis. Using in-memory MockRedis.", file=sys.stderr)
        redis_client = MockRedis()
else:
    print("UPSTASH_REDIS_URL not found. Using in-memory MockRedis.", file=sys.stderr)
    redis_client = MockRedis()

# ---------------- LangChain Groq Init ----------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_llm = ChatGroq(
    temperature=0.4, 
    groq_api_key=GROQ_API_KEY, 
    model_name="llama-3.1-8b-instant",
    model_kwargs={
        "frequency_penalty": 1.2,
        "presence_penalty": 1.2,
        "top_p": 0.95
    }
)

SYSTEM_PROMPT = """
CRITICAL LANGUAGE ADHERENCE:
You MUST reply in the EXACT SAME LANGUAGE as the user's latest message. 
- If the user asks in English, reply ONLY in English.
- If the user asks in Hindi, reply ONLY in Hindi.
- If the user asks in Tamil, reply ONLY in Tamil.
- Do NOT switch to Hindi if the query is in English. 
- Do NOT use a mix of languages unless the user specifically does so.

FEW-SHOT EXAMPLES:
User: hi
AI: Hello! How can I assist you with Indian legal information today?
User: नमस्ते
AI: नमस्ते! आज मैं भारतीय कानूनी जानकारी में आपकी क्या सहायता कर सकता हूँ?
User: வணக்கம்
AI: வணக்கம்! இன்று நான் உங்களுக்கு எப்படி உதவ முடியும்?

ROLE AND CONTEXT:
You are an AI Legal Information and Guidance Assistant specialized in Indian law, created for the Department of Justice.
Provide authoritative, comprehensive, and detailed step-by-step explanations grounded in the Indian Penal Code (IPC), Bharatiya Nyaya Sanhita (BNS), Bharatiya Nagarik Suraksha Sanhita (BNSS), Indian Evidence Act, IT Act, and Consumer Protection Act.
Your responses must be self-contained, ensuring the user has a clear understanding of the law and the necessary procedures without needing to immediately consult another source for basic understanding.
You must perfectly understand slang, dialects, and grammatical errors from the user and respond appropriately.
This is an educational legal summary, not legal advice. You MUST NOT act as a lawyer.
Always include a subtle reminder to consult a qualified legal professional for specific cases, but only after providing a thorough answer.
If a specific section’s text is not available in the provided context, give a thorough explanation of the legal concept based on general legal principles.

CRITICAL BEHAVIOR INSTRUCTION:
Do NOT apologize for the information you provide. Maintain an authoritative but helpful tone. You are NOT allowed to adopt erroneous information simply because the user claims you are wrong. Do not use sarcasm. 
Your ultimate goal is to provide such high-quality, professional guidance that the user feels they are interacting with a premium legal expert system (GPT-level).

CRITICAL REGIONAL LANGUAGE QUALITY:
When responding in regional languages (Tamil, Hindi, etc.), YOU MUST NOT repeat the same sentence or concept twice. Break down your thoughts. Be extremely thorough and native in your phrasing.

REDUCING OFFICIAL WORKLOAD:
- Your ultimate goal is to reduce the burden on officials by providing answers so complete that the user does not need to follow up for basic queries.
- For concepts like 'Bail', 'FIR', 'Cognizable Offenses', etc., give authoritative and exhaustive explanations.
- If a user asks "How to...", do not just give a link; explain every single step in detail (Step 1, Step 2, etc.).

MULTILINGUAL LEGAL BRIDGE:
- Most Indian laws are in English. When the user asks in Hindi or Tamil, you must act as a precise translator and explainer.
- Accurately convey English legal nuances into the user's regional language.
- Do not just translate words; translate meanings and procedures clearly.
"""

# ---------------- Lazy Global Vars ----------------
MODEL_NAME = "law-ai/InLegalBERT"
model_cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")

_embedding_model = None
_vectorstore = None
_laws_data = None

def get_laws_data():
    global _laws_data
    if _laws_data is None:
        try:
            with open("laws_raw.json", "r", encoding="utf-8") as f:
                _laws_data = json.load(f)
        except Exception as e:
            print(f"Error loading laws_raw.json: {e}")
            _laws_data = {}
    return _laws_data


def get_embedding_model():
    """Load InLegalBERT only once, when first needed, prioritizing local cache with robust fallbacks."""
    global _embedding_model
    if _embedding_model is None:
        model_to_use = MODEL_NAME
        print(f"Initializing embedding model: {model_to_use}...")
        
        # 1. Try local InLegalBERT
        try:
            AutoTokenizer.from_pretrained(model_to_use, cache_dir=model_cache_dir, local_files_only=True)
            AutoModel.from_pretrained(model_to_use, cache_dir=model_cache_dir, local_files_only=True)
            print(f"{model_to_use} loaded from local cache.")
        except Exception:
            print(f"{model_to_use} not in cache. Trying online...")
            # 2. Try online InLegalBERT
            try:
                AutoTokenizer.from_pretrained(model_to_use, cache_dir=model_cache_dir, timeout=10)
                AutoModel.from_pretrained(model_to_use, cache_dir=model_cache_dir, timeout=10)
                print(f"{model_to_use} downloaded successfully.")
            except Exception as e:
                print(f"Failed to load {model_to_use}: {e}")
                # 3. Last Resort Fallback: use a standard lightweight model likely to be present or faster to download
                model_to_use = "sentence-transformers/all-MiniLM-L6-v2"
                print(f"CRITICAL: Falling back to lightweight model: {model_to_use}")
        
        try:
            _embedding_model = HuggingFaceEmbeddings(
                model_name=model_to_use,
                cache_folder=model_cache_dir,
                model_kwargs={'device': 'cpu', 'local_files_only': True}
            )
        except Exception as e:
             print(f"CRITICAL: HuggingFaceEmbeddings failed. Using FakeEmbeddings as zero-latency emergency fallback: {e}")
             _embedding_model = FakeEmbeddings(size=768) # InLegalBERT size
             
    return _embedding_model


def build_faiss_index():
    """Rebuild FAISS index from laws_raw.json (all categories)."""
    print("Rebuilding FAISS index with inLegalBERT embeddings...")
    laws_data = get_laws_data()
    if not laws_data:
        print("Error: laws_raw.json not found or empty.")
        return None

    docs = []
    # Iterate over all top-level categories (IPC, Events_2025, etc.)
    for category, content_obj in laws_data.items():
        if isinstance(content_obj, dict):
            for section, details in content_obj.items():
                title = details.get("title", "")
                content = details.get("content", "")
                text = f"Category: {category} | {section}: {title}\n{content}"
                docs.append(Document(page_content=text, metadata={"section": section, "title": title, "category": category}))
        elif isinstance(content_obj, list):
            for i, details in enumerate(content_obj):
                title = details.get("title", f"Entry {i}")
                content = details.get("content", "")
                section = details.get("section", f"entry_{i}")
                text = f"Category: {category} | {section}: {title}\n{content}"
                docs.append(Document(page_content=text, metadata={"section": section, "title": title, "category": category}))

    if not docs:
        print("No documents found to index.")
        return None

    new_vectorstore = FAISS.from_documents(docs, get_embedding_model())
    new_vectorstore.save_local("ipc_embed_db_inlegalbert")
    print(f"FAISS index rebuilt successfully with {len(docs)} documents.")
    return new_vectorstore


def get_vectorstore():
    """Lazy-load FAISS vectorstore."""
    global _vectorstore
    if _vectorstore is None:
        try:
            _vectorstore = FAISS.load_local(
                "ipc_embed_db_inlegalbert",
                get_embedding_model(),
                allow_dangerous_deserialization=True
            )
            _ = _vectorstore.similarity_search("test", k=1)
            print("FAISS index loaded successfully.")
        except Exception as e:
            print(f"Error loading FAISS index: {e}")
            _vectorstore = build_faiss_index()
    return _vectorstore


# ---------------- Hybrid Retrieval ----------------
def hybrid_retrieve(query: str, k: int = 5, score_threshold: float = 0.65):
    context_parts = []
    source = "GEN"
    kg = get_kg()

    # 1️⃣ JSON lookup if explicit section asked
    section_match = re.search(r'\bsection\s*(\d+[a-z]?)\b', query.lower())
    if section_match:
        section_number = section_match.group(1)
        
        laws_data = get_laws_data()
            
        found_in_json = False
        # Check all main categories for this section
        for category in ["IPC", "IT_ACT", "BNS"]:
            if category in laws_data and section_number in laws_data[category]:
                details = laws_data[category][section_number]
                section_text = f"Category: {category} | Section {section_number}: {details.get('title','')}\n{details.get('content','')}"
                context_parts.append(section_text)
                source = f"JSON+KG ({category})"
                found_in_json = True
                
                # Expand in KG if it's IPC (KG currently mostly supports IPC)
                if category == "IPC":
                    node_id = f"IPC_{section_number}"
                    expanded_context = kg.expand_query(node_id)
                    if expanded_context:
                        context_parts.append(f"--- GRAPH EXPANDED KNOWLEDGE FOR {node_id} ---\n{expanded_context}")
                break

    # 2️⃣ Keyword-based category search (BNS, IT Act)
    if "bns" in query.lower() or "new law" in query.lower():
        laws_data = get_laws_data()
        if "BNS" in laws_data:
            bns_context = "\n".join([f"BNS {k}: {v.get('title')}\n{v.get('content')}" for k, v in laws_data["BNS"].items()])
            context_parts.append(f"--- RELEVANT BNS SECTIONS ---\n{bns_context}")
            source = "JSON_BNS"

    if "it act" in query.lower() or "cyber" in query.lower() or "online" in query.lower():
        laws_data = get_laws_data()
        if "IT_ACT" in laws_data:
            it_context = "\n".join([f"IT Act {k}: {v.get('title')}\n{v.get('content')}" for k, v in laws_data["IT_ACT"].items()])
            context_parts.append(f"--- RELEVANT IT ACT SECTIONS ---\n{it_context}")
            source = "JSON_IT"

    # 2️⃣ FAISS semantic search with gating + KG Expansion
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search_with_score(query, k=k)
    
    if results:
        top_doc, top_score = results[0]
        if top_score < score_threshold or any(word in query.lower() for word in ["ipc", "section", "article", "act"]):
            source = "HYBRID_GRAPH" if source == "GEN" else "HYBRID_GRAPH"
            for doc, score in results:
                # Raw page content
                context_parts.append(f"{doc.metadata.get('section','')} - {doc.metadata.get('title','')}\n{doc.page_content}")
                
                # Expand specific sections in the graph
                sec_match = re.search(r'Section (\d+)', doc.metadata.get('section',''))
                if sec_match:
                    sec_id = f"IPC_{sec_match.group(1)}"
                    expanded_context = kg.expand_query(sec_id)
                    if expanded_context:
                        context_parts.append(f"--- GRAPH EXPANDED NEIGHBORS FOR {sec_id} ---\n{expanded_context}")
        else:
            print(f"FAISS results below threshold ({top_score:.4f}), using GEN instead.")

    # 3️⃣ Centralized Resources lookup (Problem 2)
    resource_links = []
    query_lower = query.lower()
    
    # Simple keyword mapping for resources
    category_map = {
        "cyber": "cybercrime", "fraud": "cybercrime", "online": "cybercrime",
        "consumer": "consumer", "complaint": "consumer",
        "aid": "legal_aid", "help": "legal_aid",
        "woman": "women_rights", "domestic": "women_rights", "harassment": "women_rights",
        "rti": "rti", "information": "rti",
        "court": "ecourts", "status": "ecourts", "case": "ecourts",
        "act": "indiacode", "section": "indiacode"
    }

    matched_resource_keys = set()
    for kw, r_key in category_map.items():
        if kw in query_lower:
            matched_resource_keys.add(r_key)

    for r_key in matched_resource_keys:
        # Check all resource sections
        for section in RESOURCES.values():
            if r_key in section:
                res = section[r_key]
                resource_links.append(f"Official Resource: {res['title']} - {res['url']}\nDescription: {res.get('description', '')}")

    if resource_links:
        context_parts.append("--- OFFICIAL GOVERNMENT RESOURCES ---\n" + "\n\n".join(resource_links))

    # 4️⃣ General Legal Concepts lookup (Problem 3 & 5)
    laws_data = get_laws_data()
    
    det_lang = detect_language(query)

    if "GENERAL_LEGAL_CONCEPTS" in laws_data:
        concepts = laws_data["GENERAL_LEGAL_CONCEPTS"]
        for item in concepts:
            # Match against concept name and aliases (multilingual)
            aliases = [a.lower() for a in item.get("aliases", [])]
            match_found = False
            if item.get("concept", "").lower() in query_lower:
                match_found = True
            else:
                for alias in aliases:
                    if alias in query_lower:
                        match_found = True
                        break
            
            if match_found:
                explanation = item.get('simplified_explanation', '')
                # Problem 5: Use translated explanation if language matches
                if det_lang == "Hindi" and "hindi_explanation" in item:
                    explanation = item['hindi_explanation']
                elif det_lang == "Tamil" and "tamil_explanation" in item:
                    explanation = item['tamil_explanation']

                concept_text = f"CONCEPT: {item['concept']}\nExplanation: {explanation}"
                if "procedure" in item: concept_text += f"\nProcedure: {item['procedure']}"
                if "types" in item: concept_text += f"\nTypes: " + "; ".join(item['types'])
                context_parts.append(f"--- GENERAL LEGAL CONCEPT: {item['concept']} ---\n{concept_text}")
                source = "JSON_CONCEPT"

    context = "\n\n".join(context_parts)
    # Return matched resources separately for logo rendering
    matched_resources = []
    for r_key in matched_resource_keys:
        for section in RESOURCES.values():
            if r_key in section:
                res = section[r_key]
                matched_resources.append({
                    "title": res['title'],
                    "url": res['url'],
                    "description": res.get('description', ''),
                    "domain": res['url'].split('//')[-1].split('/')[0]
                })

    return context.strip(), source, matched_resources


# ---------------- Redis Chat Helpers ----------------
def load_chat(chat_name: str) -> dict:
    chat_data = redis_client.get(chat_name)
    if chat_data:
        # Compatibility with older chats
        data = json.loads(chat_data)
        if "title" not in data: data["title"] = "Previous Chat"
        if "created_at" not in data: data["created_at"] = datetime.datetime.now().isoformat()
        if "updated_at" not in data: data["updated_at"] = datetime.datetime.now().isoformat()
        if "id" not in data: data["id"] = chat_name
        return data
    now_iso = datetime.datetime.now().isoformat()
    return {"id": chat_name, "title": "New Chat", "created_at": now_iso, "updated_at": now_iso, "generated": [], "past": [], "source": []}


def save_chat(chat_name: str, chat_data: dict, user_id=None) -> None:
    chat_data["updated_at"] = datetime.datetime.now().isoformat()
    if user_id is not None:
        chat_data["user_id"] = user_id
    elif "user_id" not in chat_data:
        chat_data["user_id"] = None

    redis_client.set(chat_name, json.dumps(chat_data))
    
    # If anonymous user or guest UUID (string instead of DB int), set expiration for 1 hour to prevent persistent growth
    if chat_data.get("user_id") is None or isinstance(chat_data.get("user_id"), str):
        if hasattr(redis_client, "expire"):
            try:
                redis_client.expire(chat_name, 3600)
            except Exception as e:
                pass


def create_new_chat(user_id=None) -> str:
    new_chat_id = str(uuid.uuid4())
    now_iso = datetime.datetime.now().isoformat()
    chat_data = {
        "id": new_chat_id,
        "title": "New Chat", 
        "created_at": now_iso,
        "updated_at": now_iso,
        "user_id": user_id,
        "generated": [], 
        "past": [], 
        "source": []
    }
    save_chat(new_chat_id, chat_data, user_id)
    return new_chat_id


def delete_chat_record(chat_name: str) -> bool:
    if hasattr(redis_client, "delete"):
        redis_client.delete(chat_name)
    else: # Fallback for upstash Redis
        redis_client.delete(chat_name)
    return True


def get_chat_list(user_id=None) -> list:
    if user_id is None:
        return []

    keys = redis_client.keys('*')
    chats = []
    for k in keys:
        c_data = redis_client.get(k)
        if c_data:
            parsed = json.loads(c_data)
            # Add backwards compatibility
            if "title" not in parsed: parsed["title"] = "Previous Chat"
            if "updated_at" not in parsed: parsed["updated_at"] = datetime.datetime.now().isoformat()
            if "id" not in parsed: parsed["id"] = k
            
            # Only include chats that belong to this user
            if parsed.get("user_id") == user_id:
                chats.append(parsed)
            
    # Sort by recent updated_at
    chats.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return chats


def detect_language(text: str) -> str:
    """Programmatic detection for Hindi and Tamil scripts to provide hard hints to LLM."""
    if any('\u0900' <= char <= '\u097F' for char in text):
        return "Hindi"
    if any('\u0b80' <= char <= '\u0bff' for char in text):
        return "Tamil"
    return "English"


# ---------------- Groq Generation ----------------
def _is_blocked_or_empty(resp_text: str) -> bool:
    if not resp_text: return True
    return False

def clean_repeated_sentences(text: str) -> str:
    """Aggressively removes repetitive text loops typical in regional LLMs by sequence truncation, while strictly preserving Markdown formatting and newlines."""
    
    # Exact Sentence Deduplication (catches single sentence repeating endlessly across lines)
    lines = text.split("\n")
    cleaned_lines = []
    seen_sentences_norm = set()
    
    for line in lines:
        if not line.strip():
            cleaned_lines.append("")
            continue
            
        sentences = re.split(r'([.!?।])', line)
        cleaned_sentence_parts = []
        
        for i in range(0, len(sentences)-1, 2):
            s = sentences[i].strip()
            punct = sentences[i+1] if i+1 < len(sentences) else ""
            s_norm = re.sub(r'\s+', '', s.lower())
            
            if len(s_norm) > 10:
                if s_norm not in seen_sentences_norm:
                    seen_sentences_norm.add(s_norm)
                    cleaned_sentence_parts.append(s + punct)
            else:
                cleaned_sentence_parts.append(s + punct)
                
        cleaned_line = " ".join(cleaned_sentence_parts).replace("  ", " ").strip()
        
        # If the line was completely stripped of sentences due to duplicates, keep the line anyway
        # if it had bullets or headers (so we don't break markdown lists/headers)
        if not cleaned_sentence_parts and line.strip():
            cleaned_line = line.strip()

        if cleaned_line:
            if not cleaned_lines or cleaned_line != cleaned_lines[-1]:
                cleaned_lines.append(cleaned_line)

    # Ensure no empty multi-lines remain
    final_text = "\n".join(cleaned_lines).strip()
    return re.sub(r'\n{3,}', '\n\n', final_text)


def gemini_generate(prompt: str) -> str:
    # Use proper message roles for better instruction following
    messages = [
        SystemMessage(content=SYSTEM_PROMPT.strip()),
        HumanMessage(content=prompt.strip())
    ]
    try:
        response = groq_llm.invoke(messages).content.strip()
        return clean_repeated_sentences(response)
    except Exception as e:
        print(f"Groq API Error: {e}", file=sys.stderr)
        if "429" in str(e) or "quota" in str(e).lower():
            return "⚠️ **Groq API Quota Exceeded.** The system is currently rate-limited. Please wait a minute before sending another message."
        return f"⚠️ **AI Generation Error.** The model failed to generate a response: {e}"


# ---------------- Main Processing ----------------
def process_input(chat_name: str, user_input: str, language: str = "English", return_source=False):
    if len(user_input) > 2000:
        user_input = user_input[:2000] + " ...[Truncated]"
        
    current_chat = load_chat(chat_name)
    
    # --- ChatGPT Auto-Naming Logic ---
    if current_chat.get("title") == "New Chat" and len(current_chat.get("past", [])) == 0:
        try:
            new_title = user_input[:30] + ("..." if len(user_input) > 30 else "")
            if new_title:
                current_chat["title"] = new_title
        except Exception as e:
            print(f"Failed to auto-name chat: {e}")

    history_pairs = list(zip(current_chat.get("past", []), current_chat.get("generated", [])))
    history_prompt = "\n".join([f"User: {q}\nAI: {a}" for q, a in history_pairs[-2:]])

    # --- 1️⃣ Fast Keyword Workflow Classification ---
    intent = "Other"
    offense = "None"
    
    # Check for relevant workflows
    matched_workflow = None
    workflow_suggestion = ""
    for flow_key, flow_data in WORKFLOWS.items():
        if flow_key.lower() in user_input.lower():
            matched_workflow = flow_data
            intent = "Workflow Match"
            offense = flow_key
            steps_str = "\n".join([f"Step {i+1}: {step}" for i, step in enumerate(flow_data['steps'])])
            workflow_suggestion = f"\n\n--- SUGGESTED WORKFLOW: {flow_data['title']} ---\n{steps_str}"
            if flow_data.get('links'):
                workflow_suggestion += f"\nLink: {flow_data['links'][0]['url']}"
            break

    # Enhance FAISS query with intent and offense if identified
    enhanced_query = user_input
    if offense != "None" and offense != "Unknown":
        enhanced_query += f" (Focus: {offense}, Category: {intent})"

    # Hybrid retrieval - Reduced to top 3 to prevent token length explosion (Groq TPM limit)
    context_text, source_type, matched_resources = hybrid_retrieve(enhanced_query, k=3)
    
    if workflow_suggestion:
        context_text += workflow_suggestion

    if context_text and len(context_text.strip()) > 30 and source_type != "GEN":
        # Hard truncate context to max 3000 characters to prevent 413 Rate Limit Error
        if len(context_text) > 3000:
            context_text = context_text[:3000] + "\n...[Context Truncated for Length]..."
            
        context_prompt = f"Relevant Law & Similar Cases Excerpts:\n\n{context_text}\n\nNow answer the user’s question with a comprehensive and detailed step-by-step explanation."
    else:
        source_type = "GEN"
        context_prompt = "No specific IPC section retrieved. Provide a thorough and detailed educational summary under Indian law, explaining each concept in detail."

    # --- Programmatic Language Detection ---
    det_lang = detect_language(user_input)
    language_prompt = f"[SYSTEM: YOU MUST REPLY STRICTLY IN {det_lang.upper()} AS DETECTED IN USER INPUT]"

    # --- 2️⃣ Structured Output Formatter ---
    formatter_instructions = f"""
    INSTRUCTIONS FOR AI GENERATION:
    1. If the user is asking a clear legal question regarding an offense, a dispute, or an incident, or a specific legal procedure or concept (Intent: {intent}), you MUST output your final response STRICTLY in the following 6-point Markdown format. Ensure you provide deep, step-by-step explanations for each point. Mention modern equivalents like BNS or BNSS alongside IPC if applicable.
        
        ### 1. Relevant Section(s) & Act(s)
        [List the exact sections from BNS, IPC, IT Act, Consumer Protection Act, etc. and name the acts clearly.]

        ### 2. Legal Explanation (Simplified)
        [Provide a thorough, deep, and detailed explanation of the law in plain, everyday language. If the context has a "Simplified Explanation", utilize it. Break it down into points if necessary. Explain how each part of the law applies to the specific details mentioned by the user. Do not be brief; explain the "why" and "how" without using confusing jargon. Be comprehensive and authoritative.]


        ### 3. Punishment / Penalty
        [Detail the specific punishments, fines, or terms of imprisonment. Explain any aggravating or mitigating factors if the law provides them. Be very specific about the range of penalties.]

        ### 4. Legal Procedure
        [Explain each and every step required for the citizen to achieve their goal or file their case. This MUST be a step-by-step guide (Step 1, Step 2, etc.). Include:
        - Exact sequence of actions.
        - Where to go (Police Station, Court, Online Portal).
        - What documents are needed.
        - Mention if the offense is cognizable/non-cognizable, bailable/non-bailable.
        - Provide official links like cybercrime.gov.in or ecourts.gov.in only as secondary reference after explaining the steps.]

        ### 5. Recommended Action
        [Gives exhaustive practical next steps. Be proactive in suggesting what the user should do immediately (e.g., preserving evidence, witness contact info, filing a specific type of report).]

        ### 6. Official Resources & Portals
        [Provide direct links to official government portals, court services, or Acts repositories gathered from the context. Explain what the user can do on each portal (e.g., "File a complaint at...", "Check case status at..."). Ensure these links are clickable.]
        
    2. If the user is engaging in casual conversation, greeting you, or asking a general informational question about a system (like "what is ecourts?"), completely ignore the 5-point format. Provide a detailed and comprehensive answer that explains the topic thoroughly, including how it works, why it exists, and practical steps to use it. Your explanation should be complete and satisfy the user's curiosity without them needing to visit another site, although you should still provide official portal links for their reference.
    """

    prompt = f"""{language_prompt}

{context_prompt}

{formatter_instructions}

Conversation History:
{history_prompt}

User: {user_input}
AI:"""

    response = gemini_generate(prompt)
    
    # --- 3️⃣ Citation Validation (Knowledge Graph Anti-Hallucination) ---
    kg = get_kg()
    is_valid, _ = kg.validate_citation(response)
    
    hallucination_match = re.search(r'(?i)(?:section\s*)?(\d+[a-z]?)\s*(?:of\s*)?(IPC|BNS|IT Act)?', response)
    
    # AI FACT-CHECKER LAYER
    # If a section was cited but wasn't found in the graph, we do a hard LLM fact-check
    if hallucination_match and not is_valid:
        print(f"Detected Hallucination Risk for: {hallucination_match.group(0)}. Running Fact-Checker...")
        
        fact_check_prompt = f"""
        You are a strict Legal Verification System.
        
        Context provided to the AI:
        {context_text}
        
        AI Generated Response to check:
        {response}
        
        Question: Does the generated response cite a specific Indian Penal Code (IPC) section number that is NOT explicitly mentioned or explained in the Context provided?
        Answer exclusively YES or NO.
        """
        
        verification = gemini_generate(fact_check_prompt).strip().upper()
        
        if "YES" in verification:
            print("Fact-Checker Flagged: Hallucination confirmed. Regenerating safely...")
            strict_prompt = prompt + "\n\nCRITICAL SYSTEM WARNING: Your previous draft hallucinated a Section number. You MUST NOT invent or guess any Section numbers. If the exact Section number is not in the provided excerpts, state that you cannot provide the specific section and give a general legal answer."
            response = gemini_generate(strict_prompt)
            source_type = "GEN_CORRECTED"

    if response.lower().startswith("i'm sorry") or "cannot provide" in response.lower():
        det_lang = detect_language(user_input)
        response = f"{gemini_generate(f'[STRICTLY REPLY IN {det_lang.upper()}] ' + user_input)}"

    current_chat["past"].append(user_input)
    current_chat["generated"].append(response)
    current_chat["source"].append(source_type)
    # Store citations if any
    if "citations" not in current_chat: current_chat["citations"] = []
    current_chat["citations"].append(matched_resources)
    
    # Save the chat with existing user_id if present
    save_chat(chat_name, current_chat, current_chat.get("user_id"))

    print(f"Answer Source: {source_type} | User: {user_input}")
    
    low_confidence = (source_type == "GEN")
    
    if return_source:
        return response, source_type, low_confidence, matched_resources
    return response, low_confidence, matched_resources
