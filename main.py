from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(title="Futbol 3-2-1 Oyun API'si")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WIKIDATA_URL = "https://query.wikidata.org/sparql"

def query_wikidata(sparql_query: str):
    headers = {
        "User-Agent": "FootballQuizApp/1.0 (contact@example.com)",
        "Accept": "application/json"
    }
    response = requests.get(WIKIDATA_URL, params={'query': sparql_query, 'format': 'json'}, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

@app.get("/")
def home():
    return {"status": "API çalışıyor", "endpoint": "/player/{player_name}"}

@app.get("/player/{player_name}")
def get_player_info(player_name: str):
    sparql_query = f"""
    SELECT ?player ?playerLabel ?countryLabel ?clubLabel WHERE {{
      ?player rdfs:label "{player_name}"@en.
      ?player wdt:P106 wd:Q937857.
      
      OPTIONAL {{ ?player wdt:P27 ?country. }}
      OPTIONAL {{ ?player wdt:P54 ?club. }}
      
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,tr". }}
    }}
    """
    
    data = query_wikidata(sparql_query)
    
    if not data or not data['results']['bindings']:
        raise HTTPException(status_code=404, detail="Oyuncu bulunamadı.")

    bindings = data['results']['bindings']
    
    full_name = bindings[0]['playerLabel']['value']
    country = bindings[0].get('countryLabel', {}).get('value', 'Bilinmiyor')
    
    clubs = set()
    for item in bindings:
        if 'clubLabel' in item:
            clubs.add(item['clubLabel']['value'])

    return {
        "search_term": player_name,
        "name": full_name,
        "country": country,
        "clubs": list(clubs)
    }