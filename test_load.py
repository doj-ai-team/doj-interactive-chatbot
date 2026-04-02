import time
from transformers import AutoTokenizer, AutoModel

print("Loading InLegalBERT...")
t0 = time.time()
try:
    AutoTokenizer.from_pretrained("law-ai/InLegalBERT")
    AutoModel.from_pretrained("law-ai/InLegalBERT")
    print(f"✅ Model loaded successfully from cache in {time.time() - t0:.2f} seconds.")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
