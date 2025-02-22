import json
import os
import importlib.util
from datetime import datetime
import matplotlib.pyplot as plt
from load_parties import load_parties, load_basic_information
from plotparlament import main as plot_main, plot_deputies
from vote_distribution import plot_vote_distribution

# Set up election parameters
country = 'germany'
year = '2021'
election = country + year

appointments = ['germany']

# Visualization


POINT_SIZE = 50


def load_results(folder_path: str) -> list:
    """Load voting district results from a folder.
    
    Args:
        folder_path: Path to the election folder
        
    Returns:
        List of voting district results
    """
    results_file = os.path.join(folder_path, 'voting_district_results.json')
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading voting results: {e}")
        return None

def apply_country_changes(folder_path: str, voting_data: list, parties: list) -> list:
    """Apply country-specific changes to voting data.
    
    Args:
        folder_path: Path to the election folder
        voting_data: List of voting district results
        parties: List of participating parties
        
    Returns:
        Modified voting data
    """
    try:
        # Import the country-specific changes module
        module_path = os.path.join(folder_path, 'country_specific_voting_data_changes.py')
        if os.path.exists(module_path):
            spec = importlib.util.spec_from_file_location('country_specific_changes', module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Apply country-specific changes
            if hasattr(module, 'changes_for_country'):
                return module.changes_for_country(voting_data, parties)
    except Exception as e:
        print(f"Warning: Could not apply country-specific changes: {e}")
    
    return voting_data

# Load parties and basic information
parties = load_parties(election)
if not parties:
    print("Error: Could not load parties from participating_parties.json")
    exit(1)

# Load basic information
TOTAL_SEATS, election_name = load_basic_information(election)

# Calculate optimal visualization parameters based on total seats
# For larger parliaments (>400 seats), use more rows to maintain density
NUM_ROWS = max(3, min(15, TOTAL_SEATS // 65))  # Between 3 and 15 rows

# Scale initial radius based on total seats
# Start with a larger base radius for better spread
INITIAL_RADIUS = max(2.0, min(4.0, TOTAL_SEATS / 150))

# Make increment smaller for more rows to maintain density
# This creates a denser, more filled appearance
RADIUS_INCREMENT = INITIAL_RADIUS * (2.5 / max(NUM_ROWS - 2, 1))

print(f"Total seats: {TOTAL_SEATS}, rows: {NUM_ROWS}")
print(f"Initial radius: {INITIAL_RADIUS:.2f}, increment: {RADIUS_INCREMENT:.2f}")

# Load voting results
voting_data = load_results(election)
if not voting_data:
    print("Error: Could not load voting district results")
    exit(1)

# Apply country-specific changes
voting_data, parties = apply_country_changes(election, voting_data, parties)

# Print voting data summary
print("\nVoting Data Summary:")
print("-" * 20)

if not isinstance(voting_data, list) or not voting_data or not isinstance(voting_data[0], dict):
    print("Error: Voting data is not in the expected format (list of district dictionaries)")
    exit(1)

# Get total votes per party across all districts
party_totals = {}
for district in voting_data:
    if 'party_results' in district:
        for party_name, results in district['party_results'].items():
            if party_name not in party_totals:
                party_totals[party_name] = 0
            party_totals[party_name] += results.get('list', 0)

# Print totals sorted by votes
for party_name, total_votes in sorted(party_totals.items(), key=lambda x: x[1], reverse=True):
    print(f"{party_name}: {total_votes:,} list votes")

# Load states data
states_file = os.path.join(election, 'states.json')
with open(states_file, 'r', encoding='utf-8') as f:
    states = json.load(f)

# Try different seat distribution methods
for appointment in appointments:
    print(f"\nCalculating seats using {appointment} method...")
    print("=" * 50)
    
    # Load election calculation module
    election_module_path = os.path.join(appointment, 'election.py')
    if not os.path.exists(election_module_path):
        print(f"Error: Could not find election calculation module at {election_module_path}")
        continue

    spec = importlib.util.spec_from_file_location('election_module', election_module_path)
    election_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(election_module)
    
    # Calculate seats
    calculated_parties = election_module.calculate_seats(voting_data, states, TOTAL_SEATS, parties)
    
    # Sort parties from left to right
    calculated_parties.sort(key=lambda p: p.left_to_right)
    
    # Print seat distribution
    print("\nSeat Distribution in Parliament:")
    print("-" * 30)
    total_seats = 0
    for party in calculated_parties:
        if party.size > 0:  # Only show parties that got seats
            print(f"{party.name}: {party.size:,} seats")
            total_seats += party.size
    print(f"\nTotal Seats: {total_seats:,}")
    
    print("\nParties before plotting:")
    print("-" * 20)
    for party in calculated_parties:
        if party.size > 0:  # Only show parties that got seats
            print(f"{party.name}:")
            print(f"  Votes: {party.votes:,}")
            print(f"  Color: {party.color}")
            print(f"  Seats: {party.size}")
            print(f"  Left-Right Position: {party.left_to_right}")

    # Get the election title from the module
    election_title = getattr(election_module, 'TITLE', '')
    
    # Create plots directory if it doesn't exist
    plots_dir = "plots"
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)
        
    # Create timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Read relevant_vote type from the appointment's basic information
    with open(f'{appointment}/basic_information.json', 'r') as f:
        basic_info = json.load(f)
        relevant_vote = basic_info.get('relevant_vote', 'list')  # default to list if not specified
    
    # Create plot for this appointment's seat distribution
    deputies = plot_main(NUM_ROWS, INITIAL_RADIUS, RADIUS_INCREMENT, TOTAL_SEATS)
    plot_deputies(deputies, calculated_parties, POINT_SIZE, 
                 plots_dir, timestamp, title=f"{election_name} {election_title}",
                 relevant_vote=relevant_vote,
                 voting_data=voting_data)
    
    # Create vote distribution plots - one for votes only, one for votes vs seats
    plot_vote_distribution(parties, calculated_parties, timestamp,
                         f"{election_name}",  # Title for vote percentage plot
                         f"{election_name} {election_title}",  # Title for vote vs seat percentage plot
                         plots_dir,
                         relevant_vote=relevant_vote,
                         voting_data=voting_data)
