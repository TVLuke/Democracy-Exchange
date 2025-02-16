import json
import os
import importlib.util
from collections import namedtuple
from party import Party

folder_path = 'germany2021'
voting_results_file = os.path.join(folder_path, 'voting_district_results.json')

# Dynamically load the changes_for_list function
module_name = 'election_specific_result_changes'
module_path = os.path.join(folder_path, f'{module_name}.py')

spec = importlib.util.spec_from_file_location(module_name, module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
changes_for_list = module.changes_for_list

def get_results_for_list(folder_path: str, type: str, parties: list) -> list:
    print("lets go");
    if not os.path.exists(voting_results_file):
        return []

    with open(voting_results_file, 'r') as file:
        voting_data = json.load(file)

    # Initialize votes for each party
    for party in parties:
        votes = 0
        current_party_name = party.name  # Store the current party name
        # Assuming voting_data is structured with districts
        for district in voting_data:
            # Add votes for the current party
            votes += district.get('party_results', {}).get(current_party_name, {}).get('list', 0)
        # Update party votes
        parties = [party._replace(votes=votes) if party.name == current_party_name else party for party in parties]

    print("Final party results:")
    for party in parties:
        print(f"{party.name}: {party.votes} votes")

    return changes_for_list(parties)

def get_results(folder_path: str, type: str, parties: list) -> list:
    if type == 'member':
        return []

    if type == 'list':
        print("LIST!")
        return get_results_for_list(folder_path, type, parties)
    
    return []
