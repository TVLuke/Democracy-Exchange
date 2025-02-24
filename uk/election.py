import math
import json
import sys
import os
import random
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

def calculate_seats(results: list, states: list, total_seats: int, participating_parties: list, process: dict) -> List[Party]:
    """Calculate seat distribution for UK elections using first-past-the-post system.
    
    In the UK system, each constituency (district) elects one MP using first-past-the-post.
    Only parties that win at least one district get seats. If total_seats parameter is
    provided and different from the number of constituencies, only the seats of parties
    that won districts are scaled using the Sainte-Laguë method.
    
    Args:
        results: List of district results with voting data
        states: List of states (not used in UK system)
        total_seats: Total number of seats to distribute (0 means use district count)
        participating_parties: List of parties participating in the election
        
    Returns:
        List of Party objects with their allocated seats
    """

    # Initialize tracking dictionaries
    party_votes = {}
    party_seats = {}
    parties_with_seats = set()
    total_votes = 0  # Track total votes for vote summary
    # Count district winners and total votes
    district_count = len(results)
        
    # Add system explanation to process
    process['seat_calculation'] = []
    process['seat_calculation'].append(f"""
# United Kingdom Electoral System
The UK uses First-Past-The-Post (FPTP) voting where:
- Each constituency (district) elects one Member of Parliament (MP)
- The candidate with the most votes in each constituency wins that seat
- No minimum threshold is required
- Normally, the total number of seats equals the number of constituencies ({district_count} in this dataset)

In this calculation, the target number of seats is {total_seats}, which differs from the number of constituencies. This means we will need to scale the results proportionally after determining constituency winners.
""")  # Track parties that won at least one district
    
    # Initialize vote and seat counts for all participating parties
    for party in participating_parties:
        party_votes[party['short_name']] = 0
        party_seats[party['short_name']] = 0
    

    
    # Randomly select 3 districts to document in detail
    example_districts = random.sample(results, min(3, len(results)))
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
## Constituency: {district['name']}
This constituency demonstrates how First-Past-The-Post works:""")
        
        
        for party_name, results in district['party_results'].items():
            # Try member votes first, fall back to list votes if not available
            member_votes = results.get('member', 0)
            list_votes = results.get('list', 0)
            votes = member_votes if member_votes > 0 else list_votes
            all_votes[party_name] = votes
            
            # Update total votes for the party if it's participating
            if party_name in party_votes:
                party_votes[party_name] += votes
                print(f"District {district['name']}: {party_name} got {member_votes} member votes, {list_votes} list votes, using {votes} votes")
            
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
## Example Constituency: {district['name']}
This example shows how First-Past-The-Post determines the winner:

Total votes cast: {total_district_votes:,}
{vote_details}

Winner determination:
- Highest vote count: {winner} with {max_votes:,} votes ({max_votes/total_district_votes*100:.1f}%)
- Second place: {second_place} with {second_max_votes:,} votes ({second_max_votes/total_district_votes*100:.1f}%)
- Margin of victory: {margin:,} votes ({(margin/total_district_votes*100):.1f}% of total votes)

Result: {winner} wins this constituency's single seat, regardless of the margin of victory.
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
The UK system needs to scale from {district_count} constituencies to {total_seats} total seats.

This scaling maintains proportionality through these steps:
1. Calculate scaling factor: {total_seats} seats ÷ {district_count} constituencies = {scale_factor:.4f}
2. Multiply each party's constituency seats by this factor
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
                party = sorted_parties[i][0]
                new_seats[party] += 1
        
        # Update seats with new scaled distribution
        party_seats = new_seats
        
        # Calculate final percentages
        final_total = sum(party_seats.values())
        final_with_pct = {party: {'seats': seats, 
                                 'percentage': (seats/final_total*100 if final_total > 0 else 0)} 
                        for party, seats in party_seats.items() if seats > 0}
        
        process['seat_calculation'].append(f"""
Final seat distribution after scaling (showing only parties that won seats):
{json.dumps({party: f"{data['seats']} seats ({data['percentage']:.1f}%)" 
            for party, data in final_with_pct.items()}, indent=2)}

Note how the percentage of seats for each party remains nearly identical after scaling,
demonstrating that the proportional relationships are preserved.""")
    
    # Create Party objects with final vote and seat counts
    parties = []
    for party_data in participating_parties:
        short_name = party_data['short_name']
        # Include all parties that got votes
        if party_votes[short_name] > 0:
            parties.append(Party(
                name=short_name,
                color=party_data.get('color', '#CCCCCC'),
                size=party_seats.get(short_name, 0),  # 0 seats if party didn't win any districts
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
    # Sort parties by size in descending order
    sorted_parties = sorted(parties, key=lambda x: x.size, reverse=True)
    for party in sorted_parties:
        if party.size > 0:
            print(f"{party.name}: {party.size} seats")