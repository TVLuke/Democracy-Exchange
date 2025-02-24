import math
import json
import sys
import os
from typing import Dict, List, Set

TITLE = "nach deutschem Wahlrecht von 2023."

# Add parent directory to path to import party.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from party import Party

def get_qualifying_parties(results: list, participating_parties: list) -> Set[str]:
    """Determine which parties qualify for seats based on the 5% threshold and direct mandates."""
    qualifying_parties = set()
    total_votes = 0
    party_votes = {}
    party_direct_mandates = {}

    # Count total votes and direct mandates per party
    for district in results:
        # Find party with most member votes in district
        max_votes = 0
        winner = None
        for party_name, results in district['party_results'].items():
            member_votes = results.get('member', 0)
            if member_votes > max_votes:
                max_votes = member_votes
                winner = party_name
            
            # Sum up list votes (or member votes if list votes don't exist) for 5% calculation
            list_votes = results.get('list', None)
            if list_votes is None:
                list_votes = member_votes  # Use member votes if list votes don't exist
            party_votes[party_name] = party_votes.get(party_name, 0) + list_votes
            total_votes += list_votes
        
        # Count direct mandate
        if winner:
            party_direct_mandates[winner] = party_direct_mandates.get(winner, 0) + 1
    
    # Check which parties qualify
    threshold = total_votes * 0.05  # 5% threshold
    for party in participating_parties:
        name = party['short_name']
        # Qualify if:
        # 1. Over 5% threshold
        # 2. At least 3 direct mandates
        # 3. Minority party
        if (party_votes.get(name, 0) >= threshold or
            party_direct_mandates.get(name, 0) >= 3 or
            party.get('minority', False)):
            qualifying_parties.add(name)
    
    return qualifying_parties

def calculate_sainte_lague_seats(party_votes: Dict[str, int], total_seats: int) -> Dict[str, int]:
    """Calculate seats using Sainte-Laguë/Schepers method."""
    total_votes = sum(party_votes.values())
    
    # Initial divisor
    divisor = total_votes / total_seats
    
    while True:
        # Calculate seats with current divisor
        seats = {}
        total_allocated = 0
        
        for party, votes in party_votes.items():
            quotient = votes / divisor
            # Standard rounding
            allocated = round(quotient)
            seats[party] = allocated
            total_allocated += allocated
        
        # Check if we've allocated the correct number of seats
        if total_allocated == total_seats:
            return seats
        elif total_allocated > total_seats:
            # Too many seats, increase divisor
            divisor *= 1.001
        else:
            # Too few seats, decrease divisor
            divisor *= 0.999

def calculate_seats(results: list, states: list, total_seats: int, participating_parties: list, process: dict = None) -> List[Party]:
    """
    Calculate seat distribution for German elections using Sainte-Laguë method.

    Args:
        results (list): List of district results with voting data
        states (list): List of states and their basic seat allocations
        total_seats (int): Total number of seats to distribute
        participating_parties (list): List of parties participating in the election

    Returns:
        List[Party]: List of Party objects with their allocated seats
    """
    # Get qualifying parties
    qualifying_parties = get_qualifying_parties(results, participating_parties)
    
    # Calculate total list votes (or member votes if list votes don't exist) for all parties
    all_party_votes = {}
    qualifying_party_votes = {}
    for district in results:
        for party_name, results in district['party_results'].items():
            list_votes = results.get('list', None)
            if list_votes is None:
                list_votes = results.get('member', 0)  # Use member votes if list votes don't exist
            all_party_votes[party_name] = all_party_votes.get(party_name, 0) + list_votes
            if party_name in qualifying_parties:
                qualifying_party_votes[party_name] = qualifying_party_votes.get(party_name, 0) + list_votes
    
    # Calculate seats using Sainte-Laguë method for qualifying parties only
    seat_distribution = calculate_sainte_lague_seats(qualifying_party_votes, total_seats)
    
    # Create final Party tuples with all calculated information
    parties = []
    for party_data in participating_parties:
        party_name = party_data['short_name']
        votes = all_party_votes.get(party_name, 0)
        if votes > 0:  # Include all parties that got votes
            parties.append(Party(
                name=party_name,  # Use short_name since name is empty
                color=party_data.get('color', '#000000'),
                size=seat_distribution.get(party_name, 0) if party_name in qualifying_parties else 0,
                left_to_right=party_data.get('left_to_right', 0),
                votes=votes
            ))
    
    return parties

if __name__ == "__main__":
    # Test code
    with open(os.path.join('germany2021', 'voting_district_results.json'), 'r') as f:
        results = json.load(f)
    
    with open(os.path.join('germany2021', 'states.json'), 'r') as f:
        states = json.load(f)
    
    with open(os.path.join('germany2021', 'participating_parties.json'), 'r') as f:
        participating_parties = json.load(f)
    
    total_seats = 736  # Current Bundestag size
    
    parties = calculate_seats(results, states, total_seats, participating_parties)
    
    # Print results
    print("\nParty Results:")
    print("-" * 40)
    for party in sorted(parties, key=lambda p: (-p.size, p.left_to_right)):
        print(f"{party.name or 'Unknown'}:")
        print(f"  Seats: {party.size:,}")
        print(f"  Votes: {party.votes:,}")
        print(f"  Left-Right Position: {party.left_to_right}")
        print()