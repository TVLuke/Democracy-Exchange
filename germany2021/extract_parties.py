import xml.etree.ElementTree as ET
import json

# Path to the XML file
xml_file = './germany2021/gesamtergebnis_01.xml'

# Parse the XML file
tree = ET.parse(xml_file)
root = tree.getroot()

# Set to store unique party names
unique_parties = set()

# Find all Gruppenergebnis elements
for gruppe in root.findall('.//Gruppenergebnis'):
    if gruppe.get('Gruppenart') == 'PARTEI':
        party_name = gruppe.get('Name')
        unique_parties.add(party_name)

# Create the party data structure
participating_parties = []
for party_name in sorted(unique_parties):
    party = {
        "short_name": party_name,
        "name": "",  # Left empty as requested
        "color": "",  # Left empty as requested
        "left_to_right": 0
    }
    participating_parties.append(party)

# Write to JSON file
output_file = './germany2021/participating_parties.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(participating_parties, f, ensure_ascii=False, indent=2)

print(f"Found {len(participating_parties)} unique parties:")
for party in participating_parties:
    print(f"- {party['short_name']}")
