#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import json
import os
from typing import Dict, List

# Mapping from EML names to our standardized short names
PARTY_NAME_MAPPING = {
    'VVD': 'VVD',
    'Volkspartij voor Vrijheid en Democratie': 'VVD',
    'NSC': 'NSC',
    'Nieuw Sociaal Contract': 'NSC',
    'PVV': 'PVV',
    'PVV (Partij voor de Vrijheid)': 'PVV',
    'Partij voor de Vrijheid': 'PVV',
    'GroenLinks-PvdA': 'GL-PvdA',
    'GROENLINKS-PVDA': 'GL-PvdA',
    'GROENLINKS / Partij van de Arbeid (PvdA)': 'GL-PvdA',
    'D66': 'D66',
    'Democraten 66': 'D66',
    'BBB': 'BBB',
    'BoerBurgerBeweging': 'BBB',
    'CDA': 'CDA',
    'Christen-Democratisch Appèl': 'CDA',
    'SP': 'SP',
    'SP (Socialistische Partij)': 'SP',
    'Socialistische Partij': 'SP',
    'ChristenUnie': 'CU',
    'Partij voor de Dieren': 'PvdD',
    'PvdD': 'PvdD',
    'SGP': 'SGP',
    'Staatkundig Gereformeerde Partij': 'SGP',
    'Staatkundig Gereformeerde Partij (SGP)': 'SGP',
    'DENK': 'DENK',
    'Forum voor Democratie': 'FVD',
    'FVD': 'FVD',
    'Volt': 'Volt',
    'Volt Nederland': 'Volt',
    'JA21': 'JA21',
    'BIJ1': 'Bij1',
    'Bij1': 'Bij1',
    '50PLUS': '50PLUS',
    'BVNL': 'BVNL',
    'BVNL / Groep Van Haga': 'BVNL',
    'Belang van Nederland': 'BVNL',
    'Piratenpartij': 'Piratenpartij',
    'Piratenpartij - De Groenen': 'Piratenpartij',
    'Splinter': 'Splinter',
    'LEF': 'LEF',
    'LEF - Voor de Nieuwe Generatie': 'LEF',
    'LP': 'LP',
    'LP (Libertaire Partij)': 'LP',
    'Libertaire Partij': 'LP',
    'Nederland met een PLAN': 'PLAN',
    'PLAN': 'PLAN',
    'PartijvdSport': 'PvdS',
    'Partij van de Sport': 'PvdS',
    'Politieke Partij voor Basisinkomen': 'PPB',
    'PPB': 'PPB'
}

# Left to right scale: 1 (far left) to 8 (far right)
PARTY_LEFT_RIGHT = {
    'GL-PvdA': 2,    # Left-wing progressive
    'SP': 2,         # Left-wing socialist
    'Bij1': 1,       # Far left
    'PvdD': 3,       # Left-wing environmentalist
    'D66': 4,        # Center progressive
    'Volt': 4,       # Center progressive
    'CDA': 5,        # Center-right Christian democratic
    'CU': 5,         # Center-right Christian
    'VVD': 6,        # Right-wing liberal
    'NSC': 5,        # Center-right
    'BBB': 6,        # Right-wing
    'SGP': 7,        # Conservative right
    'JA21': 7,       # Conservative right
    'PVV': 8,        # Far right
    'FVD': 8,        # Far right
    'BVNL': 7,       # Conservative right
    'DENK': 4,       # Center
    '50PLUS': 5,     # Center
    'Piratenpartij': 4,  # Center progressive
    'Splinter': 4,   # Center
    'LEF': 4,        # Center
    'LP': 6,         # Right-wing libertarian
    'PLAN': 4,       # Center
    'PvdS': 4,       # Center
    'PPB': 3         # Left-leaning
}

# Default party colors - can be extended
PARTY_COLORS = {
    'VVD': '#0000FF',      # Blue
    'NSC': '#00B0F0',      # Light Blue
    'PVV': '#000000',      # Black
    'GL-PvdA': '#FF0000',  # Red
    'D66': '#00FF00',      # Green
    'BBB': '#92D050',      # Light Green
    'CDA': '#008000',      # Dark Green
    'SP': '#FF0000',       # Red
    'CU': '#00B050',       # Green
    'PvdD': '#7030A0',     # Purple
    'SGP': '#FFC000',      # Gold
    'DENK': '#00B0F0',     # Light Blue
    'FVD': '#7030A0',      # Purple
    'Volt': '#7030A0',     # Purple
    'JA21': '#0070C0',     # Blue
    'Bij1': '#7030A0',     # Purple
    '50PLUS': '#FFC000',   # Gold
    'BVNL': '#FF0000',     # Red
    'Piratenpartij': '#7030A0',  # Purple
    'Splinter': '#7030A0',  # Purple
    'LEF': '#A5A5A5',      # Light Gray
    'LP': '#A5A5A5',       # Light Gray
    'PLAN': '#A5A5A5',     # Light Gray
    'PvdS': '#A5A5A5',     # Light Gray
    'PPB': '#A5A5A5'       # Light Gray
}

# Full names of parties - can be extended
PARTY_FULL_NAMES = {
    'VVD': 'Volkspartij voor Vrijheid en Democratie',
    'NSC': 'Nieuw Sociaal Contract',
    'PVV': 'Partij voor de Vrijheid',
    'GL-PvdA': 'GroenLinks-PvdA',
    'D66': 'Democraten 66',
    'BBB': 'BoerBurgerBeweging',
    'CDA': 'Christen-Democratisch Appèl',
    'SP': 'Socialistische Partij',
    'CU': 'ChristenUnie',
    'PvdD': 'Partij voor de Dieren',
    'SGP': 'Staatkundig Gereformeerde Partij',
    'DENK': 'DENK',
    'FVD': 'Forum voor Democratie',
    'Volt': 'Volt Nederland',
    'JA21': 'JA21',
    'Bij1': 'Bij1',
    '50PLUS': '50PLUS',
    'BVNL': 'Belang van Nederland',
    'Piratenpartij': 'Piratenpartij - De Groenen',
    'Splinter': 'Splinter',
    'LEF': 'LEF - Voor de Nieuwe Generatie',
    'LP': 'Libertaire Partij',
    'PLAN': 'Nederland met een PLAN',
    'PvdS': 'Partij van de Sport',
    'PPB': 'Politieke Partij voor Basisinkomen'
}

def parse_eml_file(file_path: str) -> List[str]:
    """Parse EML file and extract party names, using standard names when available."""
    ns = {
        'eml': 'urn:oasis:names:tc:evs:schema:eml',
        'kr': 'http://www.kiesraad.nl/extensions'
    }
    
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    parties = set()
    
    # Look for party names in different possible locations
    # First try RegisteredParties section
    registered_parties = root.findall('.//kr:RegisteredParties/kr:RegisteredParty/kr:RegisteredAppellation', ns)
    for party in registered_parties:
        if party.text:
            party_name = party.text.strip()
            # Use mapped name if available, otherwise use original
            parties.add(PARTY_NAME_MAPPING.get(party_name, party_name))
    
    # Also look in AffiliationIdentifier sections which might contain party names
    affiliations = root.findall('.//eml:AffiliationIdentifier/eml:RegisteredName', ns)
    for affiliation in affiliations:
        if affiliation.text:
            party_name = affiliation.text.strip()
            # Use mapped name if available, otherwise use original
            parties.add(PARTY_NAME_MAPPING.get(party_name, party_name))
    
    return sorted(list(parties))

def create_participating_parties_json(parties: List[str], output_file: str):
    """Create the participating_parties.json file."""
    party_data = [
        {
            "short_name": party,
            "name": PARTY_FULL_NAMES.get(party, party),  # Use party name if full name not found
            "color": PARTY_COLORS.get(party, "#808080"),  # Use gray if color not found
            "left_to_right": PARTY_LEFT_RIGHT.get(party, 4)  # Default to center (4) if not specified
        }
        for party in parties
        if party.strip()  # Only include non-empty party names
    ]
    
    # Sort parties by name
    party_data = sorted(party_data, key=lambda x: x["short_name"])
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(party_data, f, ensure_ascii=False, indent=4)

def main():
    # Directory containing the EML files
    election_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(election_dir, 'verkiezingsuitslag-tweede-kamer-2023-4')
    
    # Files to check for party information
    files_to_check = [
        'Verkiezingsdefinitie_TK2023.eml.xml',
        'Totaaltelling_TK2023.eml.xml',
        'Resultaat_TK2023.eml.xml'
    ]
    
    all_parties = set()
    for filename in files_to_check:
        file_path = os.path.join(results_dir, filename)
        if os.path.exists(file_path):
            parties = parse_eml_file(file_path)
            all_parties.update(parties)
    
    # Create the output file
    output_file = os.path.join(election_dir, 'participating_parties.json')
    create_participating_parties_json(sorted(list(all_parties)), output_file)
    print(f"Created participating_parties.json with {len(all_parties)} parties")

if __name__ == "__main__":
    main()
