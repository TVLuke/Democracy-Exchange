import math
import json
import sys
import os
import random
from typing import Dict, List

TITLE = "nach US-amerikanischem Wahlrecht."

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

def calculate_seats(results: list, states: list, total_seats: int, participating_parties: list, process: dict) -> List[Party]:
    """Calculate seat distribution for US House of Representatives elections using first-past-the-post system.
    
    In the US system:
    - Each congressional district elects one Representative using first-past-the-post
    - The candidate with the most votes (plurality) wins the seat
    - No minimum threshold is required
    - Districts are redrawn every 10 years based on census data
    - Each state is guaranteed at least one Representative
    
    Args:
        results: List of district results with voting data
        states: List of states (not used in US system)
        total_seats: Total number of seats to distribute (0 means use district count)
        participating_parties: List of parties participating in the election
        
    Returns:
        List of Party objects with their allocated seats
    """
    # Initialize tracking dictionaries
    party_votes = {}
    party_seats = {}
    parties_with_seats = set()
    district_count = len(results)
        
    # Add system explanation to process
    process['seat_calculation'] = []
    process['seat_calculation'].append(f"""
# United States House of Representatives Electoral System
The US uses First-Past-The-Post (FPTP) voting where:
- Each congressional district elects one Representative
- The candidate with the most votes (plurality) in each district wins that seat
- No minimum vote threshold is required
- Districts are redrawn every 10 years following the census
- Each state is guaranteed at least one Representative

In this calculation:
- Number of districts: {district_count}
- Target number of seats: {total_seats}
""")
    
    # Initialize vote and seat counts for all participating parties
    for party in participating_parties:
        party_votes[party['short_name']] = 0
        party_seats[party['short_name']] = 0
    
    # Randomly select 3 districts to document in detail
    example_districts = random.sample(results, min(3, len(results)))
    
    # Process each district
    for district in results:
        # Find party with most votes in district
        max_votes = 0
        second_max_votes = 0
        winner = None
        second_place = None
        all_votes = {}
        
        # Document example districts
        if district in example_districts:
            process['seat_calculation'].append(f"""
## Congressional District: {district['name']}
This district demonstrates how First-Past-The-Post works in US House elections:""")
        
        for party_name, results in district['party_results'].items():
            # Try member votes first, fall back to list votes if not available
            votes = results.get('member', results.get('list', 0))
            all_votes[party_name] = votes
            
            # Update total votes for the party if it's participating
            if party_name in party_votes:
                party_votes[party_name] += votes
            
            # Check if this party won the district
            if votes > max_votes:
                second_max_votes = max_votes
                second_place = winner
                max_votes = votes
                winner = party_name
            elif votes > second_max_votes:
                second_max_votes = votes
                second_place = party_name
        
        # Document example districts with detailed vote calculations
        if district in example_districts:
            margin = max_votes - second_max_votes
            total_district_votes = sum(all_votes.values())
            vote_details = "\n".join([f"- {party}: {votes:,} votes ({votes/total_district_votes*100:.1f}%)" 
                                    for party, votes in sorted(all_votes.items(), key=lambda x: x[1], reverse=True)])
            
            process['seat_calculation'].append(f"""
## Example Congressional District: {district['name']}
This example shows how the Representative is determined:

Total votes cast: {total_district_votes:,}
{vote_details}

Winner determination:
- Highest vote count: {winner} with {max_votes:,} votes ({max_votes/total_district_votes*100:.1f}%)
- Second place: {second_place} with {second_max_votes:,} votes ({second_max_votes/total_district_votes*100:.1f}%)
- Margin of victory: {margin:,} votes ({(margin/total_district_votes*100):.1f}% of total votes)

Result: {winner} wins this district's seat in the House of Representatives.
""")
        
        # Allocate seat to winning party if it's participating
        if winner and winner in party_seats:
            party_seats[winner] += 1
            parties_with_seats.add(winner)
    
    # If total_seats is specified and different from district count,
    # scale up the district-based seat distribution proportionally
    if total_seats > 0 and total_seats != district_count:
        # Calculate scaling factor
        scale_factor = total_seats / district_count
        
        # Calculate original percentages
        original_total = sum(party_seats.values())
        original_with_pct = {party: {'seats': seats, 
                                    'percentage': (seats/original_total*100 if original_total > 0 else 0)} 
                           for party, seats in party_seats.items() if seats > 0}
        
        process['seat_calculation'].append(f"""
## Scaling Process Explanation
The US House system needs to scale from {district_count} districts to {total_seats} total seats.

This scaling maintains proportionality through these steps:
1. Calculate scaling factor: {total_seats} seats ÷ {district_count} districts = {scale_factor:.4f}
2. Multiply each party's district seats by this factor
3. Take the integer part first (floor)
4. Distribute remaining seats by highest decimal remainder

This preserves the proportional relationship between parties while reaching the target seat count.

Original seat distribution (showing only parties that won seats):
{json.dumps({party: f"{data['seats']} seats ({data['percentage']:.1f}%)" 
            for party, data in original_with_pct.items()}, indent=2)}""")
        
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
                party = sorted_parties[i % len(sorted_parties)][0]
                new_seats[party] += 1
            
            # Document final distribution
            process['seat_calculation'].append(f"""
Final seat distribution after scaling:
{json.dumps({party: seats for party, seats in new_seats.items() if seats > 0}, indent=2)}
""")
        
        # Update party seats with scaled values
        party_seats = new_seats
    
    # Create Party objects with final seat counts
    final_parties = []
    for party in participating_parties:
        party_name = party['short_name']
        if party_name in party_votes:
            final_parties.append(Party(
                name=party_name,
                color=party.get('color', '#808080'),
                size=party_seats[party_name],  # size is used for seats
                left_to_right=party.get('left_to_right', 0),
                votes=party_votes[party_name]
            ))
    
    return final_parties
