import re
import json

def rebuild():
    infile = 'laws_raw.json'
    outfile = 'laws_raw.json'
    
    with open(infile, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read()

    # 1. Extract GENERAL_LEGAL_CONCEPTS
    concepts = []
    # Simplified extraction: find things that look like concept objects
    concept_pattern = re.compile(r'\{\s*"concept":\s*"(.*?)".*?"procedure":\s*"(.*?)"\s*\}', re.DOTALL)
    # Wait, my previous repair made it better but it might still be broken.
    
    # Let's just manually fix the first few lines and then use regex for IPC.
    new_data = {
        "GENERAL_LEGAL_CONCEPTS": [
            {
                "concept": "Bail",
                "aliases": ["bail", "anticipatory bail", "जमानत", "ஜாமீன்"],
                "simplified_explanation": "Bail is a legal process where a person who has been arrested is released from police or court custody, on the condition that they appear in court whenever required. It is like a guarantee (often involving a 'bail bond' or money) that the person will not run away while the case is being decided.",
                "hindi_explanation": "जमानत एक कानूनी प्रक्रिया है जिसमें गिरफ्तार व्यक्ति को पुलिस या अदालत की हिरासत से इस शर्त पर रिहा किया जाता है कि वे जब भी आवश्यकता हो अदालत में उपस्थित होंगे। यह एक गारंटी की तरह है (अक्सर इसमें 'बेल बॉन्ड' या पैसा शामिल होता है) कि मामला तय होने तक व्यक्ति भाग नहीं जाएगा।",
                "tamil_explanation": "ஜாமீன் என்பது ஒரு சட்டப்பூர்வ நடைமுறையாகும், இதில் கைது செய்யப்பட்ட நபர், தேவைப்படும் போதெல்லாம் நீதிமன்றத்தில் ஆஜராக வேண்டும் என்ற நிபந்தனையின் பேரில் போலீஸ் அல்லது நீதிமன்ற காவலில் இருந்து விடுவிக்கப்படுகிறார். இது ஒரு உத்தரவாதம் போன்றது (பெரும்பாலும் 'ஜாமீன் பத்திரம்' அல்லது பணம் சம்பந்தப்பட்டது), வழக்கு தீர்மானிக்கப்படும் போது அந்த நபர் ஓடிவிட மாட்டார்.",
                "procedure": "To get bail, you generally need to apply through a lawyer in the relevant Court (Magistrate or Sessions Court). The court will decide based on the seriousness of the offense and the likelihood of the person appearing for trial.",
                "next_steps": [
                    "Consult a Criminal Defense Lawyer immediately.",
                    "Arrange for a 'Surety' (a person who guarantees your appearance).",
                    "Prepare identifying documents (Aadhaar, PAN) for yourself and the surety.",
                    "Apply for bail in the jurisdictional Magistrate or Sessions Court."
                ]
            },
            {
              "concept": "FIR",
              "aliases": ["FIR", "First Information Report", "प्रथम सूचना रिपोर्ट", "முதல் தகவல் அறிக்கை"],
              "simplified_explanation": "An FIR is the very first document prepared by the police when they receive information about the commission of a 'cognizable' (serious) offense. It sets the criminal justice process in motion.",
              "hindi_explanation": "एफ़आईआर पुलिस द्वारा तैयार किया गया पहला दस्तावेज़ है जब उन्हें किसी 'संज्ञेय' (गंभीर) अपराध के होने की जानकारी मिलती है। यह आपराधिक न्याय प्रक्रिया को गति में लाता है।",
              "tamil_explanation": "ஒரு 'காக்னிசபிபுள்' (தீவிரமான) குற்றம் நடந்ததாக காவல்துறைக்குத் தகவல் கிடைக்கும்போது அவர்களால் தயாரிக்கப்படும் முதல் ஆவணம் எஃப்ஐஆர் ஆகும். இது குற்றவியல் நீதி செயல்முறையைத் தொடங்குகிறது.",
              "procedure": "You can go to the nearest police station and provide details of the crime orally or in writing. The police are duty-bound to record it if a serious crime is reported."
            },
            {
              "concept": "Cognizable Offense",
              "aliases": ["cognizable", "serious offense", "संज्ञेय अपराध", "கைது செய்யக்கூடிய குற்றம்"],
              "simplified_explanation": "These are serious crimes (like murder, theft, or kidnapping) where the police have the authority to arrest someone suspected of the crime immediately, without waiting for a warrant from a court.",
              "hindi_explanation": "ये गंभीर अपराध (जैसे हत्या, चोरी या अपहरण) हैं जहां पुलिस के पास अदालत से वारंट की प्रतीक्षा किए बिना तुरंत अपराध के संदिग्ध किसी व्यक्ति को गिरफ्तार करने का अधिकार है।",
              "tamil_explanation": "இவை கொலை, திருட்டு அல்லது கடத்தல் போன்ற தீவிரமான குற்றங்கள், இங்கு காவல்துறையினர் நீதிமன்றத்திலிருந்து வாரண்ட் கிடைக்கும் வரை காத்திருக்காமல், குற்றம் செய்ததாக சந்தேகிக்கப்படும் எவரையும் உடனடியாகக் கைது செய்ய அதிகாரம் கொண்டுள்ளனர்.",
              "punishment_context": "Usually involves offenses punishable by 3 years or more of imprisonment."
            },
            {
              "concept": "Non-Cognizable Offense",
              "aliases": ["non-cognizable", "minor offense", "असंज्ञेய अपराध", "கைது செய்ய முடியாத குற்றம்"],
              "simplified_explanation": "These are less serious offenses (like minor assault or defamation) where the police CANNOT arrest someone without a warrant from a Magistrate. They also cannot start an investigation without the court's permission.",
              "hindi_explanation": "ये कम गंभीर अपराध (जैसे मामूली मारपीट या मानहानि) हैं जहां पुलिस मजिस्ट्रेट के वारंट के बिना किसी को गिरफ्तार नहीं कर सकती है। वे अदालत की अनुमति के बिना जांच भी शुरू नहीं कर सकते।",
              "tamil_explanation": "இவை குறைவான தீவிரமான குற்றங்கள் (சின்னஞ்சிறிய தாக்குதல் அல்லது அவதூறு போன்றவை), இங்கு காவல்துறையினர் मजिस्ट्रेट-இடமிருந்து வாரண்ட் இல்லாமல் யாரையும் கைது செய்ய முடியாது. நீதிமன்றத்தின் அனுமதி இல்லாமல் அவர்கள் விசாரணையைத் தொடங்கவும் முடியாது.",
              "procedure": "In such cases, the police usually record a 'Non-Cognizable Report' (NCR) and advise you to approach the court."
            },
            {
              "concept": "Summons vs Warrant",
              "aliases": ["summons", "warrant", "समन", "वारंट", "அழைப்பாணை", "பிடியாணை"],
              "simplified_explanation": "A Summons is an official order from a court asking you to appear at a specific time and place. A Warrant is a more serious order directing the police to arrest you and bring you before the court.",
              "hindi_explanation": "समन अदालत का एक आधिकारिक आदेश है जिसमें आपको एक विशिष्ट समय और स्थान पर उपस्थित होने के लिए कहा जाता है। वारंट एक अधिक गंभीर आदेश है जो पुलिस को आपको गिरफ्तार करने और अदालत के सामने पेश करने का निर्देश देता है।",
              "tamil_explanation": "அழைப்பாணை (Summons) என்பது ஒரு குறிப்பிட்ட நேரம் மற்றும் இடத்தில் ஆஜராகுமாறு நீதிமன்றத்திலிருந்து வரும் அதிகாரப்பூர்வ உத்தரவு ஆகும். வாரண்ட் (Warrant) என்பது காவல்துறையினர் உங்களைக் கைது செய்து நீதிமன்றத்தில் ஆஜர்படுத்துமாறு உத்தரவிடும் ஒரு தீவிரமான கட்டளை ஆகும்.",
              "action": "Always obey a summons immediately to avoid it being turned into a warrant for your arrest."
            }
        ],
        "IPC": {}
    }

    # 2. Extract IPC sections
    # Regex to find "sectionXXX": { "title": "...", "content": "..." }
    # We use a pattern that matches the start of a section and captures until the closing brace of that section.
    # This is tricky due to content containing braces.
    
    # Alternative: split by '"section'
    parts = re.split(r'"(section[0-9al\.]+)"\s*:\s*\{', data)
    
    # parts[0] is garbage before first section
    # parts[1] is section name, parts[2] is the body, etc.
    
    for i in range(1, len(parts), 2):
        sec_name = parts[i]
        body = parts[i+1]
        
        # Try to extract title and content from body
        title_match = re.search(r'"title":\s*"(.*?)"', body, re.DOTALL)
        content_match = re.search(r'"content":\s*"(.*?)"', body, re.DOTALL)
        
        if title_match and content_match:
            title = title_match.group(1).replace('\n', ' ').strip()
            content = content_match.group(1).strip()
            # Basic sanitization for the extracted content
            # (In a real scenario we'd need to handle escaped quotes better)
            new_data["IPC"][sec_name] = {
                "title": title,
                "content": content
            }

    # 3. Write out cleaned JSON
    with open(outfile, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Rebuilt {outfile} with {len(new_data['IPC'])} IPC sections.")

if __name__ == "__main__":
    rebuild()
