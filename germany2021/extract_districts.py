import xml.etree.ElementTree as ET
import json
import pandas as pd

# Read population data from CSV
def read_population_data():
    # Read the CSV file line by line to handle the special format
    print("Reading CSV file...")
    with open('1000A-1W19_de.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    district_data = {}
    
    # Find both the Deutschland (citizens) and Insgesamt (total population) lines
    for line in lines:
        parts = line.strip().split(';')
        if len(parts) < 2:
            continue
            
        if parts[1] == 'Deutschland' or parts[1] == 'Insgesamt':
            # Get the date from the first field if it exists
            date = parts[0].strip() if parts[0] else ''
            
            # Process data - values appear every 4 positions starting at index 2
            values = []
            for i in range(2, len(parts), 4):
                if i < len(parts):
                    val = parts[i].strip()
                    if val and val != 'e':
                        try:
                            # Remove dots (thousand separators) and convert to int
                            values.append(int(val.replace('.', '')))
                        except ValueError:
                            values.append(0)
                    else:
                        values.append(0)
            
            # Store values in district_data
            for i, value in enumerate(values, start=1):
                if i not in district_data:
                    district_data[i] = {'citizens': 0, 'population': 0}
                
                if parts[1] == 'Deutschland':
                    district_data[i]['citizens'] = value
                else:  # Insgesamt
                    district_data[i]['population'] = value
                    # Print the data for each district
                    print(f"District {i}: {value:,} total population, {district_data[i]['citizens']:,} citizens")
    
    print(f"Total districts with data: {len(district_data)}")
    return district_data

# Get population data
district_populations = read_population_data()

# Path to the XML file
xml_file = 'gesamtergebnis_01.xml'

# Parse the XML file
tree = ET.parse(xml_file)
root = tree.getroot()

# Create mapping of state numbers to state names
def get_state_mapping():
    state_mapping = {}
    for gebiet in root.findall('Gebietsergebnis'):
        if gebiet.get('Gebietsart') == 'LAND':
            state_number = gebiet.get('Gebietsnummer')
            state_name = gebiet.find('GebietText').text
            state_mapping[state_number] = state_name
    return state_mapping

# Get state mapping
state_mapping = get_state_mapping()

# List to store district information
voting_districts = []

# Dictionary to store district results
district_results = {}

# Find all Gebietsergebnis elements for WAHLKREIS
for gebiet in root.findall('Gebietsergebnis'):
    if gebiet.get('Gebietsart') == 'WAHLKREIS':
        district_number = int(gebiet.get('Gebietsnummer'))
        district_name = gebiet.find('GebietText').text
        
        # Add to districts list
        voting_districts.append({
            "name": district_name,
            "number": district_number
        })
        
        # Initialize results for this district
        # Get the state number from UegGebietsnummer attribute
        state_number = gebiet.get('UegGebietsnummer')
        state_name = state_mapping.get(state_number, 'Unknown')
        
        # Get electorate from Wahlberechtigte group
        electorate = 0
        for gruppe in gebiet.findall('.//Gruppenergebnis'):
            name = gruppe.get('Name')
            if name == 'Wahlberechtigte':
                stimme = gruppe.find('Stimmergebnis')
                if stimme is not None:
                    anzahl = stimme.get('Anzahl')
                    if anzahl is not None:
                        electorate = int(anzahl)
                        print(f"Found electorate for district {district_number}: {electorate}")
                break

        district_results[district_number] = {
            "district": district_number,
            "name": district_name,
            "state": state_name,
            "population": district_populations.get(district_number, {}).get('population', 0),
            "citizens": district_populations.get(district_number, {}).get('citizens', 0),
            "electorate": electorate,
            "party_results": {}
        }
        
        # Get party results
        for gruppe in gebiet.findall('Gruppenergebnis'):
            if gruppe.get('Gruppenart') == 'PARTEI':
                party_name = gruppe.get('Name')
                party_result = {"member": 0, "list": 0}
                
                # Get vote counts
                for stimme in gruppe.findall('Stimmergebnis'):
                    vote_type = stimme.get('Stimmart')
                    votes = int(stimme.get('Anzahl'))
                    
                    if vote_type == 'DIREKT':
                        party_result["member"] = votes
                    elif vote_type == 'LISTE':
                        party_result["list"] = votes
                
                district_results[district_number]["party_results"][party_name] = party_result

# Sort districts by number
voting_districts.sort(key=lambda x: x['number'])

# Convert district_results to list and sort by district number
results_list = list(district_results.values())
results_list.sort(key=lambda x: x['district'])

# Calculate state populations by summing district populations
state_results = {}
for district in results_list:
    state_name = district['state']
    if state_name not in state_results:
        state_results[state_name] = {
            'name': state_name,
            'population': 0,
            'citizens': 0,
            'electorate': 0
        }
    state_results[state_name]['population'] += district['population']
    state_results[state_name]['citizens'] += district['citizens']
    state_results[state_name]['electorate'] += district['electorate']

# Write districts to JSON file
with open('voting_districts.json', 'w', encoding='utf-8') as f:
    json.dump(voting_districts, f, ensure_ascii=False, indent=2)

# Write results to JSON file
with open('voting_district_results.json', 'w', encoding='utf-8') as f:
    json.dump(results_list, f, ensure_ascii=False, indent=2)

# Write state results to JSON file
with open('states.json', 'w', encoding='utf-8') as f:
    json.dump(state_results, f, ensure_ascii=False, indent=2)

print(f"Found {len(voting_districts)} voting districts")
print(f"Found {len(state_results)} states")
print("\nState populations:")
for state_name, state_data in sorted(state_results.items()):
    print(f"{state_name}: {state_data['population']:,} total population, {state_data['citizens']:,} citizens, {state_data['electorate']:,} voters")

print("\nSample of district results:")
first_district = results_list[0]
print(f"\nDistrict {first_district['district']}: {first_district['name']}")
for party, results in list(first_district['party_results'].items())[:3]:
    print(f"- {party}: Member votes: {results['member']:,}, List votes: {results['list']:,}")
print("...")
