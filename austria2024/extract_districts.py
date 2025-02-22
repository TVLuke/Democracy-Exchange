import json
import csv

# Read the population data from CSV
def read_population_data():
    state_populations = {}
    with open('bevoelkerungbl2022.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['YEAR'] == '2021':
                # Remove thousand separators and decimal part
                population = int(float(row['POPULATION'].replace(' ', '').replace(',', '.')))
                state_populations[row['FEDERAL_STATE']] = population
    return state_populations

# Read the election data
with open('wahl_20241003_214746.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Read the participating parties
with open('participating_parties.json', 'r', encoding='utf-8') as f:
    parties = json.load(f)
    party_names = [party['short_name'] for party in parties]

# Map of district codes to names
district_names = {
    "1A": "Burgenland Nord",
    "1B": "Burgenland Süd",
    "2A": "Klagenfurt",
    "2B": "Villach",
    "2C": "Kärnten West",
    "2D": "Kärnten Ost",
    "3A": "Weinviertel",
    "3B": "Waldviertel",
    "3C": "Mostviertel",
    "3D": "Niederösterreich Mitte",
    "3E": "Niederösterreich Süd",
    "3F": "Thermenregion",
    "3G": "Niederösterreich Ost",
    "4A": "Linz und Umgebung",
    "4B": "Innviertel",
    "4C": "Hausruckviertel",
    "4D": "Traunviertel",
    "4E": "Mühlviertel",
    "5A": "Salzburg Stadt",
    "5B": "Flachgau/Tennengau",
    "5C": "Lungau/Pinzgau/Pongau",
    "6A": "Graz und Umgebung",
    "6B": "Oststeiermark",
    "6C": "Weststeiermark",
    "6D": "Obersteiermark",
    "7A": "Innsbruck",
    "7B": "Innsbruck-Land",
    "7C": "Unterland",
    "7D": "Oberland",
    "7E": "Osttirol",
    "8A": "Vorarlberg Nord",
    "8B": "Vorarlberg Süd",
    "9A": "Wien Innen-Süd",
    "9B": "Wien Innen-West",
    "9C": "Wien Innen-Ost",
    "9D": "Wien Süd",
    "9E": "Wien Süd-West",
    "9F": "Wien Nord-West",
    "9G": "Wien Nord"
}

# Map state numbers to names
state_names = {
    "1": "Burgenland",
    "2": "Kärnten",
    "3": "Niederösterreich",
    "4": "Oberösterreich",
    "5": "Salzburg",
    "6": "Steiermark",
    "7": "Tirol",
    "8": "Vorarlberg",
    "9": "Wien"
}

# Dictionary to store combined districts
combined_districts = {}

# Process each region in the data
for region_id, region_data in data.items():
    # Skip the national total
    if region_id == 'G00000':
        continue
        
    # Skip state totals (ending in 0000)
    if region_id.endswith('0000'):
        continue
        
    # Get the district code (first digit and letter after G)
    district_code = region_id[1:3]
    
    # Skip if not a valid district code
    if district_code not in district_names:
        continue
        
    # Initialize district if not exists
    if district_code not in combined_districts:
        combined_districts[district_code] = {
            "district": f"G{district_code}",
            "name": district_names[district_code],
            "state": state_names[district_code[0]],
            "population": 0,  # Placeholder for actual population
            "electorate": 0,  # Number of eligible voters
            "party_results": {party: {"list": 0} for party in party_names}
        }
    
    # Add electorate size
    if 'wahlberechtigt' in region_data:
        combined_districts[district_code]["electorate"] += int(region_data['wahlberechtigt'])
    
    # Add votes for each party
    for party in party_names:
        if party in region_data:
            combined_districts[district_code]["party_results"][party]["list"] += int(region_data[party])

# Convert to list and sort by district ID
district_list = list(combined_districts.values())
district_list.sort(key=lambda x: x["district"])

# Write the output JSON file
with open('voting_district_results.json', 'w', encoding='utf-8') as f:
    json.dump(district_list, f, indent=2, ensure_ascii=False)

# Calculate state totals
state_results = {}
population_data = read_population_data()

for district in district_list:
    state_name = district['state']
    if state_name not in state_results:
        state_results[state_name] = {
            'name': state_name,
            'population': population_data.get(state_name, 0),
            'electorate': 0
        }
    state_results[state_name]['electorate'] += district['electorate']

# Write the state results to a JSON file
with open('states.json', 'w', encoding='utf-8') as f:
    json.dump(state_results, f, indent=2, ensure_ascii=False)

print(f"Created voting_district_results.json with {len(district_list)} districts")
print(f"Created states.json with {len(state_results)} states")
print("\nState populations and electorates:")
for state_name, state_data in sorted(state_results.items()):
    print(f"{state_name}: {state_data['population']:,} people, {state_data['electorate']:,} voters")
