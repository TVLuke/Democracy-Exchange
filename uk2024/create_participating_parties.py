#!/usr/bin/env python3
import csv
import json
import os

# Party information
PARTY_INFO = {
    "Con": {
        "name": "Conservative Party",
        "color": "#0087dc",
        "left_to_right": 7
    },
    "Lab": {
        "name": "Labour Party",
        "color": "#dc241f",
        "left_to_right": 3
    },
    "LD": {
        "name": "Liberal Democrats",
        "color": "#faa61a",
        "left_to_right": 4
    },
    "RUK": {
        "name": "Reform UK",
        "color": "#12b6cf",
        "left_to_right": 8
    },
    "Green": {
        "name": "Green Party",
        "color": "#6ab023",
        "left_to_right": 2
    },
    "SNP": {
        "name": "Scottish National Party",
        "color": "#fdf38e",
        "left_to_right": 3
    },
    "PC": {
        "name": "Plaid Cymru",
        "color": "#008142",
        "left_to_right": 3
    },
    "DUP": {
        "name": "Democratic Unionist Party",
        "color": "#d46a4c",
        "left_to_right": 7
    },
    "SF": {
        "name": "Sinn Féin",
        "color": "#326760",
        "left_to_right": 1
    },
    "SDLP": {
        "name": "Social Democratic and Labour Party",
        "color": "#2aa82c",
        "left_to_right": 3
    },
    "UUP": {
        "name": "Ulster Unionist Party",
        "color": "#48a5ee",
        "left_to_right": 6
    },
    "APNI": {
        "name": "Alliance Party of Northern Ireland",
        "color": "#f6cb2f",
        "left_to_right": 4
    }
}

def extract_party_columns(csv_file):
    """Extract party columns from the CSV header."""
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        # Find indices of 'Majority' and 'Of which other winner'
        majority_idx = header.index('Majority')
        other_winner_idx = header.index('Of which other winner')
        
        # Extract party columns between these indices
        party_columns = header[majority_idx + 1:other_winner_idx]
        return party_columns

def create_participating_parties(csv_file, output_file):
    """Create participating_parties.json from CSV and party information."""
    # Get party columns from CSV
    party_columns = extract_party_columns(csv_file)
    
    # Create party objects
    participating_parties = []
    for party in party_columns:
        if party in PARTY_INFO:
            party_obj = {
                "short_name": party,
                "name": PARTY_INFO[party]["name"],
                "color": PARTY_INFO[party]["color"],
                "left_to_right": PARTY_INFO[party]["left_to_right"]
            }
            participating_parties.append(party_obj)
        else:
            print(f"Warning: No information found for party {party}")
            party_obj = {
                "short_name": party,
                "name": party,
                "color": "#CCCCCC",  # Default gray color
                "left_to_right": 0    # Default center position
            }
            participating_parties.append(party_obj)
    
    # Write to JSON file
    with open(output_file, 'w') as f:
        json.dump(participating_parties, f, indent=2)
    print(f"Created {output_file} with {len(participating_parties)} parties")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(script_dir, "HoC-GE2024-results-by-constituency.csv")
    output_file = os.path.join(script_dir, "participating_parties.json")
    
    create_participating_parties(csv_file, output_file)
