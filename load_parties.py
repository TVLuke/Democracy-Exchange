import os
import json
import hashlib
from typing import Optional

def generate_color_from_name(name: str) -> str:
    """Generate a deterministic hex color code from a name using its hash."""
    # Get the hash of the name
    hash_object = hashlib.sha256(name.encode())
    hex_hash = hash_object.hexdigest()
    
    # Take the first 6 characters of the hash for the color
    return f'#{hex_hash[:6]}'

def load_parties(folder_path: str) -> Optional[list]:
    """
    Load parties from a participating_parties.json file in the specified folder.
    For parties without colors, generates and adds random colors.
    
    Args:
        folder_path: Path to the folder containing participating_parties.json
        
    Returns:
        List of party data dictionaries if successful, None if file not found
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
    
    # Add hash-based colors for parties that don't have one
    for party in party_data:
        if not party.get('color'):
            party['color'] = generate_color_from_name(party['name'])
    
    return party_data

def load_basic_information(folder_path: str) -> dict:
    """Load basic information from a folder.
    
    Args:
        folder_path: Path to the election folder
        
    Returns:
        Dictionary containing all basic information including seats, name, and data sources
    """
    basic_info_file = os.path.join(folder_path, 'basic_information.json')
    if not os.path.exists(basic_info_file):
        return {'seats': 0, 'name': ''}  # Or handle the error as needed
    
    with open(basic_info_file, 'r', encoding='utf-8') as file:
        basic_info = json.load(file)
    
    return basic_info

if __name__ == '__main__':
    # Example usage
    import sys
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        parties = load_parties(folder_path)
        if parties:
            print(f"Loaded {len(parties)} parties:")
            for party in parties:
                print(f"- {party['short_name']}: {party['color']}")
    else:
        print("Please provide a folder path")
