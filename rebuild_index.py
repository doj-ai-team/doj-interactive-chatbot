import sys
import traceback

try:
    from views.chatbotLegalv2 import build_faiss_index
    print("Rebuilding FAISS Index with mock cases...")
    build_faiss_index()
    print("Done!")
except Exception as e:
    print("Caught Exception!")
    traceback.print_exc()
