import sys
import os
from views.chatbotLegalv2 import hybrid_retrieve

def test_retrieval(query):
    print(f"\nTesting Query: {query}")
    context, source, resources = hybrid_retrieve(query)
    print(f"Source: {source}")
    print("Context Preview:")
    print(context[:1000])
    
    if "2025" in context and "stampede" in context.lower():
        print("\n✅ SUCCESS: 2025 Stampede data retrieved!")
    else:
        print("\n❌ FAILURE: 2025 Stampede data not found in context.")

if __name__ == "__main__":
    test_retrieval("Tell me about the Karur stampede of 2025")
    test_retrieval("What happened at the Maha Kumbh in 2025?")
