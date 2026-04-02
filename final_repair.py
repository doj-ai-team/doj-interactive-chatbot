import json
import os

def final_repair():
    infile = 'laws_raw.json'
    outfile = 'laws_raw_fixed.json'
    
    # Tamil translation for Bail (corrected)
    bail_tamil = "ஜாமீன் என்பது ஒரு சட்டப்பூர்வ நடைமுறையாகும், இதில் கைது செய்யப்பட்ட நபர், தேவைப்படும் போதெல்லாம் நீதிமன்றத்தில் ஆஜராக வேண்டும் என்ற நிபந்தனையின் பேரில் போலீஸ் அல்லது நீதிமன்ற காவலில் இருந்து விடுவிக்கப்படுகிறார். இது ஒரு உத்தரவாதம் போன்றது (பெரும்பாலும் 'ஜாமீன் பத்திரம்' அல்லது பணம் சம்பந்தப்பட்டது), வழக்கு தீர்மானிக்கப்படும் போது அந்த நபர் ஓடிவிட மாட்டார்."

    print(f"Repairing {infile}...")
    
    with open(infile, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    # Step 1: Fix Early Lines
    # Head lines up to IPC start
    fixed_lines = []
    for i, line in enumerate(lines):
        if i == 7: # Line 8 is the mangled Tamil
            # We must be careful not to keep the trailing garbage on that line
            # The original line 8 had: "tamil_explanation": "...", "procedure": "..."
            # Let's rebuild it cleanly.
            fixed_lines.append(f'      "tamil_explanation": "{bail_tamil}",\n')
            fixed_lines.append(f'      "procedure": "To get bail, you generally need to apply through a lawyer in the relevant Court (Magistrate or Sessions Court). The court will decide based on the seriousness of the offense and the likelihood of the person appearing for trial.",\n')
            continue
        
        # If we see "procedure" on line 8 (which was part of the original line 8 after garbage),
        # we might have already added it. Let's check.
        if i == 7: continue # Already handled separately
        
        # Add normally
        fixed_lines.append(line)
        
        # Stop if we hit something that looks like the end of the last valid section before corruption
        # Or if we reach the end of the file
        if i > 5800: # Near the end where it starts breaking
            break

    # Step 2: Ensure valid structure
    # We'll try to find the last complete IPC section and close it.
    
    # Let's search for the last "}" that looks like it closes a section object
    last_brace_index = -1
    for i in range(len(fixed_lines)-1, -1, -1):
        if fixed_lines[i].strip() == "}":
            last_brace_index = i
            break
    
    if last_brace_index != -1:
        # Cut after this brace
        repaired_lines = fixed_lines[:last_brace_index+1]
        
        # Now we need to determine if we are inside IPC or at the root.
        # Based on structure, if we have "IPC": { ... }, we need a closing } for IPC and a closing } for root.
        
        # Let's check how many open braces we have
        content = "".join(repaired_lines)
        open_count = content.count('{')
        close_count = content.count('}')
        
        needed = open_count - close_count
        print(f"Open: {open_count}, Close: {close_count}, Needed: {needed}")
        
        for _ in range(needed):
             repaired_lines.append("}\n")
    else:
        print("No closing brace found!")
        return

    # Final string
    repaired_str = "".join(repaired_lines)
    
    # Try parsing
    try:
        json.loads(repaired_str)
        print("✅ SUCCESS: Repaired JSON is valid.")
        with open(infile, 'w', encoding='utf-8') as f:
            f.write(repaired_str)
        print(f"Updated {infile} successfully.")
    except Exception as e:
        print(f"❌ FAILED: Still invalid JSON: {e}")
        # Find where it breaks
        import traceback
        traceback.print_exc()
        with open('repair_debug.json', 'w', encoding='utf-8') as f:
            f.write(repaired_str)

if __name__ == "__main__":
    final_repair()
