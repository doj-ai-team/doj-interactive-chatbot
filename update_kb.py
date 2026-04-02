import json
import os

LAWS_FILE = r'c:\Users\mugun\OneDrive\Desktop\Department_Of_Justice_Chatbot\laws_raw.json'

new_events = {
    "Recent_Events_2025_Karur": {
        "title": "Karur Stampede (September 27, 2025)",
        "content": "A tragic stampede occurred at the TVK (Tamilaga Vettri Kazhagam) rally led by Vijay in Karur, Tamil Nadu. The incident took place due to extreme overcrowding, with an estimated 30,000 people attending a venue designed for 10,000. The stampede resulted in 41 deaths and over 50 injuries. Judicial inquiries were initiated under the guidelines of crowd management for large political gatherings."
    },
    "Recent_Events_2025_Prayagraj": {
        "title": "Maha Kumbh Stampede, Prayagraj (January 29, 2025)",
        "content": "A stampede broke out at the Sangam area during the Maha Kumbh Mela in Prayagraj, killing 30 people and injuring 60 others. The cause was identified as a sudden rush toward the bathing ghats during the auspicious 'Mauni Amavasya' period. Lack of proper barricading and announcement systems was cited in the preliminary investigation."
    },
    "Recent_Events_2025_Tirupati": {
        "title": "Tirupati Vishnu Nivasam Stampede (January 8, 2025)",
        "content": "A stampede occurred at the Vishnu Nivasam pilgrims' complex in Tirupati when thousands of devotees tried to enter for Sarva Darshan tokens. Six people lost their lives and 20 were injured. TTD (Tirumala Tirupati Devasthanams) revised its token distribution system following the incident to ensure better crowd control."
    },
    "Recent_Events_2025_Delhi": {
        "title": "New Delhi Railway Station Stampede (February 15, 2025)",
        "content": "A stampede at the New Delhi Railway Station on a foot-overbridge claimed 18 lives. The bottleneck occurred when two crowded trains arrived simultaneously on adjacent platforms. The incident highlighted the need for improved station infrastructure and real-time crowd monitoring by Railway Police."
    }
}

def update_laws():
    if not os.path.exists(LAWS_FILE):
        print("Laws file not found!")
        return
    
    with open(LAWS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create category if not exists
    if "Events_2025" not in data:
        data["Events_2025"] = {}
    
    # Update with new events
    data["Events_2025"].update(new_events)
    
    with open(LAWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"Successfully added {len(new_events)} recent events to laws_raw.json in 'Events_2025' category.")

if __name__ == "__main__":
    update_laws()
