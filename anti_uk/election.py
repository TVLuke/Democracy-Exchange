import math
import json
import sys
import os
from typing import Dict, List

TITLE = "nach britischem Wahlrecht."

# Add parent directory to path to import party.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from party import Party

def calculate_sainte_lague_seats(party_votes: Dict[str, int], total_seats: int) -> Dict[str, int]:
    """Calculate seats using Sainte-Laguë/Schepers method.
    
    Args:
        party_votes: Dictionary mapping party names to their vote counts
        total_seats: Total number of seats to distribute
        
    Returns:
        Dictionary mapping party names to their allocated seats
    """
    seats = {party: 0 for party in party_votes.keys()}
    divisors = {party: 1 for party in party_votes.keys()}
    
    # Distribute seats one by one
    for _ in range(total_seats):
        # Find party with highest quotient
        max_quotient = 0
        max_party = None
        for party in party_votes:
            quotient = party_votes[party] / divisors[party]
            if quotient > max_quotient:
                max_quotient = quotient
                max_party = party
        
        # Allocate seat and update divisor
        seats[max_party] += 1
        divisors[max_party] = 2 * seats[max_party] + 1
    
    return seats

def calculate_seats(results: list, states: list, total_seats: int, participating_parties: list) -> List[Party]:
    """Calculate seat distribution for Anti-UK elections using last-past-the-post system.
    
    In the Anti-UK system, each constituency (district) elects one MP using last-past-the-post.
    The party with the LEAST votes in each district wins that seat. This is the opposite of
    the UK's first-past-the-post system. If total_seats parameter is provided and different
    from the number of constituencies, the seats are scaled proportionally.
    
    Args:
        results: List of district results with voting data
        states: List of states (not used in Anti-UK system)
        total_seats: Total number of seats to distribute (0 means use district count)
        participating_parties: List of parties participating in the election
        
    Returns:
        List of Party objects with their allocated seats
    """

    # Initialize tracking dictionaries
    party_votes = {}
    party_seats = {}
    parties_with_seats = set()  # Track parties that won at least one district
    
    # Initialize vote and seat counts for all participating parties
    for party in participating_parties:
        party_votes[party['short_name']] = 0
        party_seats[party['short_name']] = 0
    
    # Count district winners and total votes
    district_count = len(results)
    for district in results:
        # Find party with least votes in district
        min_votes = float('inf')
        winner = None
        
        for party_name, results in district['party_results'].items():
            # Try member votes first, fall back to list votes if not available
            votes = results.get('member', results.get('list', 0))
            
            # Update total votes for the party if it's participating
            if party_name in party_votes:
                party_votes[party_name] += votes
            
            # Check if this party has the least votes in the district
            # Only consider parties with at least 1 vote
            if votes > 0 and votes < min_votes:
                min_votes = votes
                winner = party_name
        
        # Allocate seat to winning party if it's participating
        if winner and winner in party_seats:
            party_seats[winner] += 1
            parties_with_seats.add(winner)
    
    # If total_seats is specified and different from district count,
    # scale up the district-based seat distribution proportionally
    if total_seats > 0 and total_seats != district_count:
        # Calculate scaling factor
        scale_factor = total_seats / district_count
        
        # Scale each party's seats while maintaining proportions
        new_seats = {}
        remaining_seats = total_seats
        
        # First pass: allocate floor of scaled seats
        for party in party_seats:
            scaled_seats = int(party_seats[party] * scale_factor)
            new_seats[party] = scaled_seats
            remaining_seats -= scaled_seats
        
        # Second pass: distribute remaining seats by decimal remainder
        if remaining_seats > 0:
            # Calculate decimal remainders
            remainders = {party: (party_seats[party] * scale_factor) % 1
                        for party in party_seats}
            
            # Sort parties by decimal remainder (highest first)
            sorted_parties = sorted(remainders.items(), 
                                  key=lambda x: x[1],
                                  reverse=True)
            
            # Distribute remaining seats
            for i in range(remaining_seats):
                party = sorted_parties[i][0]
                new_seats[party] += 1
        
        # Update seats with new scaled distribution
        party_seats = new_seats
    
    # Create Party objects with final vote and seat counts
    parties = []
    for party_data in participating_parties:
        short_name = party_data['short_name']
        # Only include parties that won at least one district
        if short_name in parties_with_seats:
            parties.append(Party(
                name=short_name,
                color=party_data.get('color', '#CCCCCC'),
                size=party_seats[short_name],
                left_to_right=party_data.get('left_to_right', 0),
                votes=party_votes[short_name]
            ))
    
    return parties

if __name__ == "__main__":
    # Test code
    with open(os.path.join('uk2024', 'voting_district_results.json'), 'r') as f:
        results = json.load(f)
    
    with open(os.path.join('uk2024', 'participating_parties.json'), 'r') as f:
        participating_parties = json.load(f)
    
    parties = calculate_seats(results, [], 650, participating_parties)
    
    print("\nSeat Distribution:")
    for party in parties:
        if party.size > 0:
            print(f"{party.short_name}: {party.size} seats")