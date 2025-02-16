import os
import json
import random
from collections import namedtuple
from typing import List, Optional
from party import Party

def generate_random_color() -> str:
    """Generate a random hex color code."""
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f'#{r:02x}{g:02x}{b:02x}'

def load_parties(folder_path: str) -> Optional[List[Party]]:
    """
    Load parties from a participating_parties.json file in the specified folder.
    
    Args:
        folder_path: Path to the folder containing participating_parties.json
        
    Returns:
        List of Party tuples if successful, None if file not found
    """
    json_path = os.path.join(folder_path, 'participating_parties.json')
    
    # Check if file exists
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found")
        return None
    
    # Read and parse JSON file
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            party_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    # Process parties
    parties = []
    for party in party_data:
        # Get party name (use short_name if available, otherwise name)
        party_name = party.get('short_name') or party.get('name')
        if not party_name:
            continue
            
        # Get color or generate random one
        color = party.get('color') or generate_random_color()
        
        # Get left_to_right value
        left_to_right = party.get('left_to_right', 0)
        
        # Create Party tuple
        parties.append(Party(name=party_name, color=color, size=0, left_to_right=left_to_right, votes=0))
    
    return parties

def load_basic_information(folder_path: str) -> int:
    basic_info_file = os.path.join(folder_path, 'basic_information.json')
    if not os.path.exists(basic_info_file):
        return 0  # Or handle the error as needed
    
    with open(basic_info_file, 'r') as file:
        basic_info = json.load(file)
    
    return basic_info.get('seats', 0)

if __name__ == '__main__':
    # Example usage
    import sys
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        parties = load_parties(folder_path)
        if parties:
            print(f"Loaded {len(parties)} parties:")
            for party in parties:
                print(f"- {party.name}: {party.color}")
    else:
        print("Please provide a folder path")
