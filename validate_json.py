import os
import json

def validate_json():
    errors = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.json') and not file.startswith('.'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        json.load(f)
                    print(f"✅ {path} is valid.")
                except Exception as e:
                    print(f"❌ {path} is INVALID: {e}")
                    errors.append(path)
    
    if errors:
        print(f"\nTotal errors: {len(errors)}")
    else:
        print("\nAll JSON files are valid!")

if __name__ == "__main__":
    validate_json()
