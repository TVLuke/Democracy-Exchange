import json

# Read the input JSON file
with open('wahl_20241003_214746.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get the first district (G00000) which contains all parties
first_district = data['G00000']

# List of fields to exclude as they are not parties
exclude_fields = ['gebietsname', 'wahlberechtigt', 'abgegeben', 'ungueltig', 'gueltig']

# Extract party names (all fields that are not in exclude_fields)
parties = []
for field in first_district:
    if field not in exclude_fields:
        parties.append({
            "short_name": field,
            "name": "",  # Initialize with empty string
            "color": "",  # Initialize with empty string
            "left_to_right": 0  # Initialize with 0
        })

# Write the output JSON file
with open('participating_parties.json', 'w', encoding='utf-8') as f:
    json.dump(parties, f, indent=2, ensure_ascii=False)

print(f"Created participating_parties.json with {len(parties)} parties")
