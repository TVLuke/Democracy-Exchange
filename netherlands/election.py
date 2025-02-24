from typing import List
import os
import sys

# Add parent directory to path to import party.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from party import Party
import math

def calculate_seats(results: list, states: list, total_seats: int, participating_parties: list, process: dict = None) -> List[Party]:
    """
    Calculate seats for the Dutch electoral system.
    Uses pure proportional representation with D'Hondt method.
    Electoral threshold is 1/150th of valid votes (kiesdeler).
    
    Args:
        results: List of election results
        states: List of states (not used in Dutch system as it's national)
        total_seats: Total number of seats to distribute (150 in Netherlands)
        participating_parties: List of party dictionaries
        process: Optional dictionary to store intermediate results
    
    Returns:
        List of Party objects with allocated seats
    """
    # Initialize vote counting
    party_votes = {}
    for party_dict in participating_parties:
        party_votes[party_dict['short_name']] = 0
    
    # Calculate total valid votes
    total_votes = 0
    for district in results:
        for party_name, result in district['party_results'].items():
            votes = result.get('list', 0)
            if party_name in party_votes:
                party_votes[party_name] += votes
                total_votes += votes

    # Calculate electoral threshold (kiesdeler)
    threshold = total_votes / total_seats  # 1/150th of total votes
    
    # Track seats for each party
    party_seats = {}
    for party_dict in participating_parties:
        party_seats[party_dict['short_name']] = 0
    
    # Filter parties that meet the threshold
    qualified_parties = []
    for party_dict in participating_parties:
        if party_votes[party_dict['short_name']] >= threshold:
            qualified_parties.append(party_dict['short_name'])
    
    # Store process information if requested
    if process is not None:
        process['qualified_parties'] = qualified_parties
        process['threshold'] = threshold
        process['total_votes'] = total_votes
        process['party_votes'] = party_votes
        
        # Add system explanation
        process['seat_calculation'] = []
        process['seat_calculation'].append(f"""
# Dutch Electoral System

The Netherlands uses a party-list proportional representation system with the following key features:

## Electoral Threshold (Kiesdeler)
- The electoral threshold is 1/{total_seats}th of the total valid votes ({threshold:,.0f} votes in this election)
- While the Dutch parliament normally has 150 seats, in this calculation we use {total_seats} seats
- Only parties that reach this threshold can receive seats
- With {total_seats} seats, parties need {(1/total_seats)*100:.2f}% of the total vote to enter parliament

## D'Hondt Method
- Seats are allocated using the D'Hondt method
- Each party's votes are divided by 1, 2, 3, etc. as they win seats
- The party with the highest quotient gets the next seat
- This process continues until all {total_seats} seats are allocated

## Qualified Parties
The following parties reached the electoral threshold:
{', '.join(qualified_parties)}

## Vote Totals
Total valid votes: {total_votes:,}

Party vote totals:
""")

        # Add vote totals for each party
        for party_name, votes in sorted(party_votes.items(), key=lambda x: x[1], reverse=True):
            if votes > 0:
                process['seat_calculation'].append(f"{party_name}: {votes:,} list votes")
    
    # Calculate seats using D'Hondt method
    seats_allocated = 0
    while seats_allocated < total_seats:
        max_quotient = 0
        max_party = None
        
        for party_name in qualified_parties:
            # Calculate quotient: votes / (seats + 1)
            quotient = party_votes[party_name] / (party_seats[party_name] + 1)
            
            if quotient > max_quotient:
                max_quotient = quotient
                max_party = party_name
        
        if max_party:
            party_seats[max_party] += 1
            seats_allocated += 1
            
            # Store allocation step if process tracking is enabled
            if process is not None:
                if 'seat_allocation_steps' not in process:
                    process['seat_allocation_steps'] = []
                process['seat_allocation_steps'].append({
                    'seat_number': seats_allocated,
                    'party': max_party,
                    'quotient': max_quotient
                })
    
    # Create Party objects with final results
    party_objects = []
    for party_dict in participating_parties:
        short_name = party_dict['short_name']
        party = Party(
            name=short_name,
            color=party_dict.get('color', '#808080'),
            size=party_seats[short_name],
            left_to_right=party_dict.get('left_to_right', 5),
            votes=party_votes[short_name]
        )
        party_objects.append(party)
    
    return party_objects
