import sys
import traceback

try:
    from views.chatbotLegalv2 import process_input
    print("Testing process_input...")
    response, source, low_conf, citations = process_input("test_chat", "tell me about cyber fraud in BNS", return_source=True)
    print("Response:", response[:100])
except Exception as e:
    print("Caught Exception!")
    traceback.print_exc()
