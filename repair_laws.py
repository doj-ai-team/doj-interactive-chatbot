import json

def repair_laws():
    infile = 'laws_raw.json'
    outfile = 'laws_raw.json' # Overwrite after testing or use temp
    temp_file = 'laws_raw_tmp.json'
    
    print(f"Reading {infile}...")
    with open(infile, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    # 1. Start with a clean GENERAL_LEGAL_CONCEPTS
    # We'll re-build the list to avoid corruption
    
    bail_tamil = "ஜாமீன் என்பது ஒரு சட்டப்பூர்வ நடைமுறையாகும், இதில் கைது செய்யப்பட்ட நபர், தேவைப்படும் போதெல்லாம் நீதிமன்றத்தில் ஆஜராக வேண்டும் என்ற நிபந்தனையின் பேரில் போலீஸ் அல்லது நீதிமன்ற காவலில் இருந்து விடுவிக்கப்படுகிறார். இது ஒரு உத்தரவாதம் போன்றது (பெரும்பாலும் 'ஜாமீன் பத்திரம்' அல்லது பணம் சம்பந்தப்பட்டது), வழக்கு தீர்மானிக்கப்படும் போது அந்த நபர் ஓடிவிட மாட்டார்."
    
    # We'll extract only the valid parts of GENERAL_LEGAL_CONCEPTS
    # Based on our previous view_file, lines 1-70 were mostly okay except line 8.
    
    fixed_head_lines = []
    for i in range(70):
        if i >= len(lines): break
        line = lines[i]
        if i == 7: # Line 8 (0-indexed 7) is the mangled Tamil for Bail
            # We need to preserve the other fields if possible, but let's just replace the whole line
             line = f'      "tamil_explanation": "{bail_tamil}",\n'
        fixed_head_lines.append(line)
    
    # Ensure it closes properly
    # If the last line isn't '      ]', we add it. 
    # Actually, line 70 was '    }', let's check.
    # 69:         "If a Warrant is issued: You must surrender before the court or be arrested by police."
    # 70:       ]
    # 71:     }
    
    # Let's just hardcode the closing of the first category
    fixed_head_lines.append('    }\n  ],\n')
    
    # 2. Extract IPC
    ipc_lines = []
    ipc_found = False
    for i in range(len(lines)):
        if '"IPC": {' in lines[i]:
            ipc_found = True
            ipc_lines = lines[i+1:]
            break
    
    if not ipc_found:
        print("Error: IPC section not found!")
        return

    # Find the last coherent section in IPC before the Tail corruption
    # The tail corruption started around "BNS": {
    last_valid_ipc_end = -1
    for i in range(len(ipc_lines)):
        if '"BNS": {' in ipc_lines[i] or '318 of the new BNS law.' in ipc_lines[i]:
            last_valid_ipc_end = i
            break
    
    if last_valid_ipc_end != -1:
        ipc_lines = ipc_lines[:last_valid_ipc_end]
    
    # Now backtrack to the last '    }' that closes a section
    final_ipc_lines = []
    for i in range(len(ipc_lines)-1, -1, -1):
        if ipc_lines[i].strip() == '}':
            final_ipc_lines = ipc_lines[:i+1]
            break
            
    if not final_ipc_lines:
        print("Error: Could not find valid end for IPC!")
        return

    # Remove trailing comma if present on the last line
    if final_ipc_lines[-1].strip().endswith(','):
        final_ipc_lines[-1] = final_ipc_lines[-1].rstrip().rstrip(',') + '\n'
        
    # Combine everything
    final_json_str = '{\n  "GENERAL_LEGAL_CONCEPTS": [\n'
    # Skip the first '{' and '"GENERAL_LEGAL_CONCEPTS": [' from head if they are already there
    # head starts with '{' (line 0) and '"GENERAL_LEGAL_CONCEPTS": [' (line 1)
    for l in fixed_head_lines[2:]:
        final_json_str += l
        
    final_json_str += '  "IPC": {\n'
    for l in final_ipc_lines:
        final_json_str += l
    final_json_str += '  }\n}\n'
    
    print(f"Writing repaired JSON to {temp_file}...")
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(final_json_str)
        
    # Validation
    try:
        json.loads(final_json_str)
        print("✅ SUCCESS: Repaired file is a valid JSON.")
        # Overwrite the original
        os.replace(temp_file, infile)
        print(f"Updated {infile} successfully.")
    except Exception as e:
        print(f"❌ FAILED: Still invalid JSON: {e}")
        # Save to a debug file to inspect
        with open('repair_debug.json', 'w', encoding='utf-8') as f:
            f.write(final_json_str)
        print("Saved debug output to repair_debug.json")

if __name__ == "__main__":
    repair_laws()
