#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import json
import csv
import os
from typing import Dict, List, Set

# Mapping of electoral districts to provinces
DISTRICT_TO_PROVINCE = {
    'Groningen': 'Groningen',
    'Leeuwarden': 'Friesland',
    'Assen': 'Drenthe',
    'Zwolle': 'Overijssel',
    'Lelystad': 'Flevoland',
    'Nijmegen': 'Gelderland',
    'Arnhem': 'Gelderland',
    'Utrecht': 'Utrecht',
    'Amsterdam': 'Amsterdam',  # Special case as it's a municipality
    'Haarlem': 'Noord-Holland',
    'Den Helder': 'Noord-Holland',
    "'s-Gravenhage": 'Zuid-Holland',
    'Rotterdam': 'Rotterdam',  # Special case as it's a municipality
    'Dordrecht': 'Zuid-Holland',
    'Leiden': 'Zuid-Holland',
    'Middelburg': 'Zeeland',
    'Tilburg': 'Noord-Brabant',
    "'s-Hertogenbosch": 'Noord-Brabant',
    'Maastricht': 'Limburg',
    'Bonaire': None  # Special case, not a province
}

# Mapping from provinces to their population (2023)
PROVINCE_POPULATIONS = {}

def load_population_data(csv_file: str):
    """Load population data from CSV file."""
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['Periods'] == '2023':
                region = row['Regions']
                if region.endswith(' (PV)'):  # Province
                    province = region[:-5]  # Remove ' (PV)'
                    population = int(row['Population on 1 January (number)'])
                    PROVINCE_POPULATIONS[province] = population
                elif region in ['Amsterdam', 'Rotterdam']:  # Special municipalities
                    PROVINCE_POPULATIONS[region] = int(row['Population on 1 January (number)'])

def load_party_mapping(json_file: str) -> Dict[str, str]:
    """Load party name to short name mapping from participating_parties.json."""
    with open(json_file, 'r', encoding='utf-8') as f:
        parties = json.load(f)
    
    # Create base mapping from participating_parties.json
    mapping = {party['name']: party['short_name'] for party in parties}
    
    # Add manual mappings for variations in names
    manual_mappings = {
        'VVD': 'VVD',  # Direct match
        'PVV (Partij voor de Vrijheid)': 'PVV',
        'GROENLINKS / Partij van de Arbeid (PvdA)': 'GL-PvdA',
        'SP (Socialistische Partij)': 'SP',
        'ChristenUnie': 'CU',
        'Staatkundig Gereformeerde Partij (SGP)': 'SGP',
        'Volt Nederland': 'Volt',
        'Volt': 'Volt',
        'BIJ1': 'Bij1',
        'BVNL / Groep Van Haga': 'BVNL',
        'BoerBurgerBeweging': 'BBB',
        'Democraten 66': 'D66',
        'D66': 'D66',
        'Christen-Democratisch Appèl': 'CDA',
        'CDA': 'CDA',
        'Partij voor de Dieren': 'PvdD',
        'Forum voor Democratie': 'FVD',
        'Nieuw Sociaal Contract': 'NSC',
        'JA21': 'JA21',
        'DENK': 'DENK',
        '50PLUS': '50PLUS',
        'LEF - Voor de Nieuwe Generatie': 'LEF',
        'Nederland met een PLAN': 'PLAN',
        'Piratenpartij - De Groenen': 'Piratenpartij',
        'PartijvdSport': 'PvdS',
        'Libertaire Partij': 'LP',
        'Samen voor Nederland': 'Samen voor Nederland',
        'Splinter': 'Splinter',
        'Politieke Partij voor Basisinkomen': 'PPB',
        'BBB': 'BBB',
        'SGP': 'SGP'
    }
    
    mapping.update(manual_mappings)
    return mapping

def parse_district_results(definition_file: str, results_file: str, population_file: str, party_mapping: Dict[str, str]) -> List[Dict]:
    """Parse district results from the Dutch election files."""
    ns = {
        'eml': 'urn:oasis:names:tc:evs:schema:eml',
        'kr': 'http://www.kiesraad.nl/extensions'
    }
    
    # Parse definition file for district information
    def_tree = ET.parse(definition_file)
    def_root = def_tree.getroot()
    
    # Parse results file for total votes (for verification)
    res_tree = ET.parse(results_file)
    res_root = res_tree.getroot()
    
    # Get total votes per party from the results file
    party_votes = {}
    total_selections = res_root.findall('.//eml:Count//eml:Selection', ns)
    for selection in total_selections:
        party = selection.find('.//eml:AffiliationIdentifier/eml:RegisteredName', ns)
        if party is not None:
            party_name = party.text
            if party_name in party_mapping:
                short_name = party_mapping[party_name]
                votes = int(selection.find('eml:ValidVotes', ns).text)
                party_votes[short_name] = votes
    
    districts = []
    script_dir = os.path.dirname(results_file)
    
    # Get all kieskring regions
    kieskringen = def_root.findall('.//kr:Region[@RegionCategory="KIESKRING"]', ns)
    
    for kieskring in kieskringen:
        district_num = kieskring.get('RegionNumber')
        district_name = kieskring.find('kr:RegionName', ns).text
        
        # Skip Bonaire as it's not part of the main Netherlands
        if district_name == 'Bonaire':
            continue
        
        # Find the district results file
        district_file = None
        district_name_normalized = district_name.replace("'", "").replace(" ", "_")
        for filename in os.listdir(script_dir):
            if filename.startswith('Telling_TK2023_kieskring_') and filename.endswith('.eml.xml'):
                if district_name_normalized in filename:
                    district_file = os.path.join(script_dir, filename)
                    break
        
        if not district_file:
            print(f"Warning: Could not find results file for district {district_name}")
            continue
        
        # Parse district results
        district_tree = ET.parse(district_file)
        district_root = district_tree.getroot()
        
        # Get district results
        district_results = {}
        for party_name in party_votes.keys():
            district_results[party_name] = {
                "list": 0  # Initialize with 0 votes
            }
        
        # Get total votes from TotalVotes section
        total_votes = district_root.find('.//eml:TotalVotes', ns)
        if total_votes is not None:
            for selection in total_votes.findall('eml:Selection', ns):
                party = selection.find('.//eml:AffiliationIdentifier/eml:RegisteredName', ns)
                if party is not None:
                    party_name = party.text
                    if party_name in party_mapping:
                        short_name = party_mapping[party_name]
                        votes = int(selection.find('eml:ValidVotes', ns).text)
                        district_results[short_name] = {
                            "list": votes
                        }
        
        # Get district population and electorate
        province = DISTRICT_TO_PROVINCE[district_name]
        if province in PROVINCE_POPULATIONS:
            if province in ['Gelderland', 'Noord-Holland', 'Zuid-Holland', 'Noord-Brabant']:
                # For provinces with multiple districts, divide population
                num_districts = sum(1 for d in DISTRICT_TO_PROVINCE.values() if d == province)
                population = PROVINCE_POPULATIONS[province] // num_districts
            else:
                population = PROVINCE_POPULATIONS[province]
        else:
            # Fallback to rough estimate
            population = int(17400000 / 19)
        
        # Estimate electorate as 80% of population
        electorate = population * 80 // 100
        
        district_data = {
            "district": int(district_num),
            "name": district_name,
            "state": DISTRICT_TO_PROVINCE[district_name],
            "population": population,
            "electorate": electorate,
            "party_results": district_results
        }
        
        districts.append(district_data)
    
    return sorted(districts, key=lambda x: x['district'])

def create_district_results_json(districts: List[Dict], output_file: str):
    """Create the voting_district_results.json file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(districts, f, ensure_ascii=False, indent=2)

def main():
    # Directory containing the EML files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    definition_file = os.path.join(script_dir, 'verkiezingsuitslag-tweede-kamer-2023-4', 'Verkiezingsdefinitie_TK2023.eml.xml')
    results_file = os.path.join(script_dir, 'verkiezingsuitslag-tweede-kamer-2023-4', 'Totaaltelling_TK2023.eml.xml')
    population_file = os.path.join(script_dir, 'Population_dynamics__region_24022025_135422.csv')
    participating_parties_file = os.path.join(script_dir, 'participating_parties.json')
    
    # Load population data
    load_population_data(population_file)
    
    # Load party mapping and parse districts and results
    party_mapping = load_party_mapping(participating_parties_file)
    districts = parse_district_results(definition_file, results_file, population_file, party_mapping)
    
    # Verify vote totals
    party_totals = {}
    for district in districts:
        for party, result in district['party_results'].items():
            party_totals[party] = party_totals.get(party, 0) + result['list']
    
    print("\nVote totals per party:")
    for party, total in sorted(party_totals.items()):
        print(f"{party}: {total:,}")
    
    # Create the output file
    output_file = os.path.join(script_dir, 'voting_district_results.json')
    create_district_results_json(districts, output_file)
    print(f"\nCreated voting_district_results.json with {len(districts)} districts")

if __name__ == "__main__":
    main()
