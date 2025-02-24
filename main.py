import json
import os
import importlib.util
from datetime import datetime
import matplotlib.pyplot as plt
from load_parties import load_parties, load_basic_information
from plotparlament import main as plot_main, plot_deputies
from vote_distribution import plot_vote_distribution
from election_report import create_election_report

# Set up election parameters
country = 'germany'
year = '2025'
election = country + year

appointments = ['italy', 'netherlands']

# Visualization
POINT_SIZE = 100  # Doubled point size
INITIAL_RADIUS = 3.0  # Reduced from 4.0
RADIUS_INCREMENT = 0.8  # Reduced from 1.11

# Initialize process dictionary to collect data about the election calculation
process = {}


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
election_basic_info = load_basic_information(election)
TOTAL_SEATS = election_basic_info.get('seats', 0)
election_name = election_basic_info.get('name', '')

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

def generate_vote_summary(party_totals: dict, electorate_size: int) -> str:
    """Generate a markdown summary of voting data including party vote totals and percentages.
    
    Args:
        party_totals: Dictionary mapping party names to their total votes
        electorate_size: Total size of the electorate
        
    Returns:
        Markdown formatted string containing vote summary
    """
    total_votes = sum(party_totals.values())
    turnout_percentage = (total_votes / electorate_size) * 100 if electorate_size > 0 else 0
    
    # Start building the markdown text
    markdown = []
    
    # Overview section
    markdown.append(f"### Vote Summary")
    markdown.append(f"")
    markdown.append(f"A total of {total_votes:,} votes were cast, representing a turnout of {turnout_percentage:.1f}% of the electorate.")
    markdown.append(f"")
    
    # Party results table
    markdown.append("| Party | Votes | Percentage |")
    markdown.append("|-------|--------|------------|")
    
    # Add rows for each party
    for party_name, votes in sorted(party_totals.items(), key=lambda x: x[1], reverse=True):
        percentage = (votes / total_votes) * 100 if total_votes > 0 else 0
        markdown.append(f"| {party_name} | {votes:,} | {percentage:.1f}% |")
    
    # Add winning party statement
    markdown.append(f"")
    winning_party = max(party_totals.items(), key=lambda x: x[1])
    markdown.append(f"**{winning_party[0]}** received the most votes with {winning_party[1]:,} votes "
                   f"({(winning_party[1]/total_votes*100):.1f}% of total votes).")
    
    return '\n'.join(markdown)

def calculate_election_results(election_id: str, appointments: list) -> dict:
    """Calculate election results for given election and appointments.
    
    Args:
        election_id: String identifier for the election (e.g. 'germany2021')
        appointments: List of appointment identifiers to calculate results for
        
    Returns:
        Dictionary mapping appointment names to their calculated party results
    """
    # Load voting results
    voting_data = load_results(election_id)
    if not voting_data:
        raise ValueError("Could not load voting district results")

    # Load parties and basic information
    parties = load_parties(election_id)
    if not parties:
        raise ValueError("Could not load parties from participating_parties.json")

    # Load basic information
    election_basic_info = load_basic_information(election_id)
    TOTAL_SEATS = election_basic_info.get('seats', 0)
    election_name = election_basic_info.get('name', '')
    
    # Apply country-specific changes
    voting_data, parties = apply_country_changes(election_id, voting_data, parties)

    if not isinstance(voting_data, list) or not voting_data or not isinstance(voting_data[0], dict):
        raise ValueError("Voting data is not in the expected format")

    # Load appointment basic info
    appointment_info = {}
    for appointment in appointments:
        info_file = os.path.join(appointment, 'basic_information.json')
        if os.path.exists(info_file):
            with open(info_file, 'r', encoding='utf-8') as f:
                appointment_info[appointment] = json.load(f)
    
    # Get total votes per party across all districts
    party_totals = {}
    for district in voting_data:
        if 'party_results' in district:
            for party_name, results in district['party_results'].items():
                if party_name not in party_totals:
                    party_totals[party_name] = 0
                # Use the correct vote type based on appointment's basic_information
                for appointment in appointments:
                    if appointment in appointment_info:
                        vote_type = appointment_info[appointment].get('relevant_vote', 'list')
                        votes = results.get(vote_type, 0)
                        party_totals[party_name] += votes

    # Print totals sorted by votes
    for party_name, total_votes in sorted(party_totals.items(), key=lambda x: x[1], reverse=True):
        print(f"{party_name}: {total_votes:,} list votes")

    # Load states data
    states_file = os.path.join(election_id, 'states.json')
    with open(states_file, 'r', encoding='utf-8') as f:
        states = json.load(f)

    results = {}
    
    # Get total population, citizens and electorate size
    def get_total_from_states_or_districts(key):
        # Try to get from states first
        if states:
            state_total = sum((state.get(key) or 0) for state in states.values() if state.get(key) not in [None, 0])
            if state_total > 0:
                return state_total
        # Fall back to districts if state data not available
        return sum((district.get(key) or 0) for district in voting_data if district.get(key) not in [None, 0])
    
    total_population = get_total_from_states_or_districts('population')
    total_citizens = get_total_from_states_or_districts('citizens')
    electorate_size = get_total_from_states_or_districts('electorate')
    
    # Validate appointments first
    for appointment in appointments:
        appointment_path = os.path.join(appointment)
        if not os.path.exists(appointment_path):
            raise ValueError(f"Invalid appointment method: {appointment}")
    
    # Generate vote summary and add to process dictionary
    process['vote_summary'] = generate_vote_summary(party_totals, electorate_size)
    
    # Calculate results for each appointment (now validated)
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
        calculated_parties = election_module.calculate_seats(voting_data, states, TOTAL_SEATS, parties, process)
        
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
        
        # Load basic information from the appointment directory
        appointment_basic_info = load_basic_information(appointment)
        if not appointment_basic_info:
            appointment_basic_info = {'relevant_vote': 'list'}
            


        # Store results
        results[appointment] = {
            'basic_info': election_basic_info,
            'appointment_basic_info': appointment_basic_info,
            'voting_data': voting_data,
            'calculated_parties': calculated_parties,
            'all_parties': parties,
            'election_title': election_title,
            'election_name': election_name,
            'states': states
        }
    
    return results, process


def main():
    # Initialize process dictionary to collect data about the election calculation
    process = {}
    
    # Calculate results
    results, process = calculate_election_results(election, appointments)
    
    # Create plots directory if it doesn't exist
    plots_dir = "plots"
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)
        
    # Create timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create plots for each appointment
    for appointment, result in results.items():
        basic_info = result['basic_info']
        voting_data = result['voting_data']
        calculated_parties = result['calculated_parties']
        all_parties = result['all_parties']
        election_title = result['election_title']
        election_name = result['election_name']
        states = result['states']
        
        # Load basic information from appointment folder
        appointment_basic_info = load_basic_information(appointment)
        
        # Get relevant vote type
        relevant_vote = appointment_basic_info.get('relevant_vote', 'list')  # default to list if not specified
        
        # Create plot for this appointment's seat distribution
        deputies = plot_main(NUM_ROWS, INITIAL_RADIUS, RADIUS_INCREMENT, TOTAL_SEATS)
        parliament_alt_text, coalitions_alt_text = plot_deputies(deputies, calculated_parties, 200, 
                     plots_dir, f"{election}_{appointment}", title=f"{election_name} {election_title}",
                     relevant_vote=relevant_vote,
                     voting_data=voting_data)
        
        # Create vote distribution plots
        vote_dist_alt_text, vote_seat_alt_text = plot_vote_distribution(
                             all_parties, calculated_parties, f"{election}_{appointment}",
                             f"{election_name}",  # Title for vote percentage plot
                             f"{election_name} {election_title}",  # Title for vote vs seat percentage plot
                             output_dir=plots_dir,
                             relevant_vote=relevant_vote,
                             voting_data=voting_data)
        
        # Calculate total population, citizens and electorate from voting data
        def get_total_from_states_or_districts(key):
            # Try to get from states first
            if states:
                state_total = sum((state.get(key) or 0) for state in states.values() if state.get(key) not in [None, 0])
                if state_total > 0:
                    return state_total
            # Fall back to districts if state data not available
            return sum((district.get(key) or 0) for district in voting_data if district.get(key) not in [None, 0])
        
        total_population = get_total_from_states_or_districts('population')
        total_citizens = get_total_from_states_or_districts('citizens')
        electorate_size = get_total_from_states_or_districts('electorate')
        
        # Get total votes from calculated parties
        total_votes = sum(party.votes for party in calculated_parties if hasattr(party, 'votes'))
        
        # Prepare party results for the report using calculated_parties
        party_results = [{
            'name': party.name,
            'votes': party.votes if hasattr(party, 'votes') else 0,
            'seats': party.size
        } for party in calculated_parties]

        # Generate the report
        report_data = {
            'election_name': f"{election_name} {election_title}",
            'election_date': year,  # Using the year from election data
            'total_population': total_population,
            'total_citizens': total_citizens,
            'electorate_size': electorate_size,
            'total_votes': total_votes,
            'party_results': party_results,
            'total_seats': TOTAL_SEATS,
            'image_paths': {
                'parliament': f"../plots/{election}_{appointment}_parliament.png",
                'vote_distribution': f"../plots/{election}_{appointment}_vote_distribution.png",
                'vote_seat_distribution': f"../plots/{election}_{appointment}_vote_seat_distribution.png",
                'coalitions': f"../plots/{election}_{appointment}_coalitions.png"
            },
            'alt_texts': {
                'parliament': parliament_alt_text,
                'coalitions': coalitions_alt_text if coalitions_alt_text else 'No possible coalitions found.',
                'vote_distribution': vote_dist_alt_text,
                'vote_seat_distribution': vote_seat_alt_text
            },
            'process': process,
            'data_sources': results[appointment]['basic_info'].get('data-sources', []),
            'appointment_data_sources': results[appointment]['appointment_basic_info'].get('data-sources', [])
        }
        
        # Store report data in results
        results[appointment]['report_data'] = report_data

        # Create and save the report
        report = create_election_report(**report_data)
        os.makedirs('reports', exist_ok=True)
        report_file = os.path.join('reports', f'{election}_{appointment}_report.md')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)


if __name__ == "__main__":
    main()
