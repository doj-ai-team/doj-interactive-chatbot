import time
from views.chatbotLegalv2 import process_input

start = time.time()
print("Starting query...")
response, source, resources = process_input("test_chat", "What is the section for murder?")
print(f"Elapsed: {time.time() - start:.2f} seconds")
print(f"Source: {source}")
print(f"Response: {response[:100]}...")
