import google.generativeai as genai
import os
import json
from random import randint, choice
from datetime import datetime, timedelta

os.environ["API_KEY"] = ""

genai.configure(api_key=os.environ["API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")

performers_by_genre = {
    "pop": [
        "Billie Eilish", "Ariana Grande", "Olivia Rodrigo", "Post Malone", "Harry Styles", 
        "Dua Lipa", "Ed Sheeran", "Cardi B", "Drake", "Lizzo"
    ],
    "rock": [
        "Foo Fighters", "The Killers", "Imagine Dragons", "Green Day", "Muse", 
        "Red Hot Chili Peppers", "Coldplay", "The Strokes", "Arctic Monkeys", "Linkin Park"
    ],
    "hip-hop": [
        "Travis Scott", "Kendrick Lamar", "Lil Nas X", "Drake", "Cardi B", 
        "J. Cole", "Post Malone", "Doja Cat", "Future", "Megan Thee Stallion"
    ],
    "electronic": [
        "Calvin Harris", "Zedd", "David Guetta", "Marshmello", "Deadmau5", 
        "Martin Garrix", "Avicii", "Tiesto", "Alesso", "Steve Aoki"
    ]
}

def generate_random_event(performers_list):
    locations = ["Zagreb", "Split", "Rijeka", "Osijek", "Pula"]
    
    performer = choice(performers_list)
    performers_list.remove(performer)   

    ticket_price = randint(50, 150)  
    location = choice(locations)  
    
    event_date = datetime.now() + timedelta(days=randint(1, 180))  
    formatted_date = event_date.strftime("%Y-%m-%d %H:%M:%S")
    
    prompt = f"Write a short description of {performer} for a concert event."
    response = model.generate_content(prompt)
    description = response.text.strip()  
    
    return {
        "performer": performer,
        "ticket_price": ticket_price,
        "location": location,
        "event_date": formatted_date,
        "description": description  
    }

genre = input("Unesite žanr (pop, rock, hip-hop, electronic): ").lower()

if genre not in performers_by_genre:
    print("Nepoznat žanr! Molimo odaberite jedan od sljedećih: pop, rock, hip-hop, electronic.")
else:
    performers_list = performers_by_genre[genre]

    events = [generate_random_event(performers_list) for _ in range(10)]  # Generiraj 10 izvođača

    events_json = json.dumps(events, indent=4)

    print(events_json)

    with open("events.json", "w") as json_file:
        json_file.write(events_json)

    print("\nPodaci o izvođačima su spremljeni u 'events.json'.")
