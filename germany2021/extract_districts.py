import xml.etree.ElementTree as ET
import json

# Path to the XML file
xml_file = 'gesamtergebnis_01.xml'

# Parse the XML file
tree = ET.parse(xml_file)
root = tree.getroot()

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
        district_results[district_number] = {
            "district": district_number,
            "name": district_name,
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

# Write districts to JSON file
with open('voting_districts.json', 'w', encoding='utf-8') as f:
    json.dump(voting_districts, f, ensure_ascii=False, indent=2)

# Write results to JSON file
with open('voting_district_results.json', 'w', encoding='utf-8') as f:
    json.dump(results_list, f, ensure_ascii=False, indent=2)

print(f"Found {len(voting_districts)} voting districts")
print("Sample of district results:")
first_district = results_list[0]
print(f"\nDistrict {first_district['district']}: {first_district['name']}")
for party, results in list(first_district['party_results'].items())[:3]:
    print(f"- {party}: Member votes: {results['member']:,}, List votes: {results['list']:,}")
print("...")
