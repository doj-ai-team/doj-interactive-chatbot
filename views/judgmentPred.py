import json
import os
import numpy as np
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
from PIL import Image
import pytesseract
import tensorflow as tf
from tensorflow.keras.layers import GRU, Dense, Dropout, Input, Masking, Bidirectional
from tensorflow.keras.models import Model
from langchain_groq import ChatGroq

# === ENV & MODEL SETUP ===
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(temperature=0.2, groq_api_key=GROQ_API_KEY, model_name="llama-3.1-8b-instant")

class AttentionLayer(tf.keras.layers.Layer):
    def __init__(self, attention_dim=200, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)
        self.attention_dim = attention_dim

    def build(self, input_shape):
        self.W = self.add_weight(
            shape=(input_shape[-1], self.attention_dim),
            initializer="glorot_uniform",
            trainable=True
        )
        self.b = self.add_weight(
            shape=(self.attention_dim,),
            initializer="zeros",
            trainable=True
        )
        self.u = self.add_weight(
            shape=(self.attention_dim, 1),
            initializer="glorot_uniform",
            trainable=True
        )
        super(AttentionLayer, self).build(input_shape)

    def call(self, x):
        u_t = tf.math.tanh(tf.linalg.matmul(x, self.W) + self.b)
        a = tf.linalg.matmul(u_t, self.u)
        a = tf.nn.softmax(tf.squeeze(a, -1))
        weighted_input = x * tf.expand_dims(a, -1)
        return tf.reduce_sum(weighted_input, axis=1)

def load_bi_gru_model():
    input_text = Input(shape=(None, 768), dtype='float32', name='text')
    masked_input = Masking(mask_value=-99.)(input_text)
    gru_out = Bidirectional(GRU(100, return_sequences=True))(masked_input)
    gru_out = Bidirectional(GRU(100, return_sequences=True))(gru_out)
    attention_out = AttentionLayer(attention_dim=200)(gru_out)
    dropout_out = Dropout(0.5)(attention_out)
    dense_out = Dense(30, activation='relu')(dropout_out)
    final_out = Dense(1, activation='sigmoid')(dense_out)
    model = Model(inputs=input_text, outputs=final_out)
    return model

bi_gru_model = load_bi_gru_model()

# === FUNCTIONS ===

def extract_text_from_file(file_obj, file_type):
    text = ""
    if file_type == "pdf":
        pdf_reader = PdfReader(file_obj)
        text = "\n\n".join([page.extract_text().strip() for page in pdf_reader.pages if page.extract_text()])
        
        # Fallback to OCR if the PDF is scanned (no extractable text)
        if not text.strip():
            try:
                import fitz
                doc = fitz.open(file_obj)
                for page in doc:
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    text += pytesseract.image_to_string(img) + "\n\n"
            except ImportError:
                print("PyMuPDF (fitz) is not installed. Skipping OCR fallback.")
                text = "Error: This PDF appears to be scanned, and OCR dependencies (PyMuPDF) are not installed."
            except Exception as e:
                print(f"Fallback OCR Error: {e}")
                text = "Error: OCR engine (Tesseract) is not installed or configured on this system."
                
    elif file_type == "docx":
        doc = DocxDocument(file_obj)
        text = "\n\n".join([p.text.strip() for p in doc.paragraphs if p.text])
    elif file_type == "image":
        image = Image.open(file_obj)
        try:
            text = pytesseract.image_to_string(image)
        except Exception as e:
            print(f"OCR Error: {e}")
            text = "Error: OCR engine (Tesseract) is not installed or configured on this system."
    elif file_type == "txt":
        with open(file_obj, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
    return text


def analyze_case(case_details):
    """
    Analyze the case details using Bi-GRU + Gemini for a structured risk estimation.
    :param case_details: str
    :return: dict with analysis
    """
    # Replace with real embeddings in production
    embedded_input = np.random.randn(1, 512, 768)
    bi_gru_prediction = bi_gru_model.predict(embedded_input)
    risk_score = float(bi_gru_prediction[0][0])
    risk_level = "High Risk" if risk_score > 0.7 else ("Medium Risk" if risk_score > 0.3 else "Low Risk")

    # Truncate text to avoid Groq token limit errors (similar to chatbotLegalv2.py)
    if len(case_details) > 3000:
        truncated_details = case_details[:3000] + "\n...[Content Truncated for Length]..."
    else:
        truncated_details = case_details

    # Build Gemini prompt
    prompt = f"""
You are an AI Legal Assistant specialized in Indian law.

Analyze the given legal document text and output a highly structured summary. You must classify the document into one of the following Hierarchical Legal Topics:
- Criminal Law (Theft, Assault, Fraud, Cybercrime, etc.)
- Civil Law (Property, Contract, Family, Tort)
- Consumer Law

Also use the provided model risk estimation (Estimated Legal Risk: {risk_level}) as context for the severity level.

Response format MUST be strictly as follows (Markdown enabled):

**Detected Legal Topic**: (Assign the hierarchical category and subcategory)
**Case Overview**: (Brief summary)
**Parties Involved**: (Identify from text)
**Alleged Offences**: (List out the offences)
**Relevant Sections**: (Identify laws involved)
**Severity Level**: ({risk_level})
**Recommended Next Step**: (What should be done next legally)
**Disclaimer**: This is AI-generated for educational and case-analysis purposes, not definitive legal advice or a binding verdict.

Here is the document text:
{truncated_details}
"""
    try:
        gemini_response = llm.invoke(prompt).content.strip()
    except Exception as e:
        print(f"Groq API Error in prediction: {e}")
        if "429" in str(e) or "quota" in str(e).lower():
            gemini_response = "**Error**: API Quota Exceeded. Please try again later."
        else:
            gemini_response = "**Error**: The AI failed to generate a response."

    return {
        "analysis": gemini_response
    }

# === EXAMPLE USAGE ===
# (Uncomment to test standalone)

# file_text = extract_text_from_file("example.pdf", "pdf")
# result = predict_verdict(file_text)
# print(result["verdict"])
# print(result["analysis"])
