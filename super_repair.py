import json
import os

def super_repair():
    infile = 'laws_raw.json'
    outfile = 'laws_raw.json'
    
    bail_tamil = "ஜாமீன் என்பது ஒரு சட்டப்பூர்வ நடைமுறையாகும், இதில் கைது செய்யப்பட்ட நபர், தேவைப்படும் போதெல்லாம் நீதிமன்றத்தில் ஆஜராக வேண்டும் என்ற நிபந்தனையின் பேரில் போலீஸ் அல்லது நீதிமன்ற காவலில் இருந்து விடுவிக்கப்படுகிறார். இது ஒரு உத்தரவாதம் போன்றது (பெரும்பாலும் 'ஜாமீன் பத்திரம்' அல்லது பணம் சம்பந்தப்பட்டது), வழக்கு தீர்மானிக்கப்படும் போது அந்த நபர் ஓடிவிட மாட்டார்."

    print(f"Super Repairing {infile}...")
    
    with open(infile, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    fixed_lines = []
    
    # Line 1-7
    for i in range(min(7, len(lines))):
        fixed_lines.append(lines[i])
    
    # Line 8 (fixed)
    fixed_lines.append(f'      "tamil_explanation": "{bail_tamil}",\n')
    fixed_lines.append(f'      "procedure": "To get bail, you generally need to apply through a lawyer in the relevant Court (Magistrate or Sessions Court). The court will decide based on the seriousness of the offense and the likelihood of the person appearing for trial.",\n')
    fixed_lines.append('      "next_steps": [\n')
    fixed_lines.append('        "Consult a Criminal Defense Lawyer immediately.",\n')
    fixed_lines.append('        "Arrange for a \'Surety\' (a person who guarantees your appearance).",\n')
    fixed_lines.append('        "Prepare identifying documents (Aadhaar, PAN) for yourself and the surety.",\n')
    fixed_lines.append('        "Apply for bail in the jurisdictional Magistrate or Sessions Court."\n')
    fixed_lines.append('      ]\n')
    fixed_lines.append('    },\n')

    # Now skip the corrupted/duplicate block (lines 16 to 89 in original file)
    # Wait, original line 16 was the end of "Bail".
    # Original line 17 was "FIR".
    # So we should resume from original line 17.
    # But wait, original lines 71-89 were the duplicates.
    
    # Let's just keep everything from line 17 to 70.
    for i in range(16, 70):
        if i < len(lines):
            # Skip line 7-15 as we rebuilt them
             fixed_lines.append(lines[i])
    
    # Add original line 70 (closes fifth concept)
    if 70 < len(lines):
        fixed_lines.append(lines[70])
        
    # Skip original lines 71 to 89 (corruption/duplicates)
    
    # Resume from original line 90 (which is "  ],")
    for i in range(90, len(lines)):
        # Stop at line 5780 (before the trailing trash)
        if i > 5780:
            break
        fixed_lines.append(lines[i])

    # Now close the IPC object and Root object
    # Let's count open/close braces in the current fixed_lines
    content = "".join(fixed_lines)
    open_count = content.count('{')
    close_count = content.count('}')
    
    needed = open_count - close_count
    print(f"Open: {open_count}, Close: {close_count}, Needed: {needed}")
    
    # We expect needed to be 2: one for the last IPC section and one for IPC itself.
    # Plus one for the root.
    # Wait, "IPC": {  starts with 1 open.
    # Each section is { ... }, so that adds 1 more.
    
    # Let's just blindly add braces until it's valid or we reach a limit.
    for i in range(needed):
        fixed_lines.append("}\n")
    
    final_str = "".join(fixed_lines)
    
    try:
        json.loads(final_str)
        print("✅ SUCCESS: Repaired JSON is valid.")
        with open(outfile, 'w', encoding='utf-8') as f:
            f.write(final_str)
    except Exception as e:
        print(f"❌ FAILED: Still invalid: {e}")
        # Try one more or one less brace
        for try_braces in [needed-1, needed+1, 0]:
             test_lines = fixed_lines[:len(fixed_lines)-needed] + (["}\n"] * try_braces)
             test_str = "".join(test_lines)
             try:
                 json.loads(test_str)
                 print(f"✅ SUCCESS with {try_braces} braces.")
                 with open(outfile, 'w', encoding='utf-8') as f:
                     f.write(test_str)
                 return
             except:
                 pass
        
        with open('super_repair_debug.json', 'w', encoding='utf-8') as f:
            f.write(final_str)

if __name__ == "__main__":
    super_repair()
