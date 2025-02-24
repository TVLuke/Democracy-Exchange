import math
import json
import sys
import os
from typing import List, Dict, Set, Tuple
from collections import defaultdict

TITLE = "nach französischem Wahlrecht."

# Add parent directory to path to import party.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from party import Party

def get_votes_for_round(party_results: dict, use_member_votes: bool = True) -> Dict[str, int]:
    """Get votes for each party, preferring member votes over list votes.
    
    Args:
        party_results: Dictionary of party results
        use_member_votes: Whether to prefer member votes over list votes
        
    Returns:
        Dictionary mapping party names to their vote counts
    """
    votes = {}
    for party_name, results in party_results.items():
        if use_member_votes:
            votes[party_name] = results.get('member', results.get('list', 0))
        else:
            votes[party_name] = results.get('list', results.get('member', 0))
    return votes

def redistribute_votes(eliminated_votes: Dict[str, int], 
                      party_positions: Dict[str, int],
                      eliminated_party: str,
                      party_position: int) -> Dict[str, int]:
    """Redistribute votes from eliminated parties based on left-right positions.
    
    Args:
        eliminated_votes: Votes to redistribute
        party_positions: Left-to-right positions of parties
        eliminated_party: Party whose votes are being redistributed
        party_position: Left-to-right position of the eliminated party
        
    Returns:
        Dictionary of redistributed votes
    """
    redistributed = {}
    votes_to_distribute = eliminated_votes[eliminated_party]
    
    # If eliminated party has no position (0), all votes are lost
    if party_position == 0:
        return redistributed
    
    # Find parties with same position (80% of votes)
    same_position_parties = [p for p, pos in party_positions.items() 
                           if pos == party_position and p != eliminated_party 
                           and pos != 0]  # Only redistribute to positioned parties
    if same_position_parties:
        votes_per_party = (votes_to_distribute * 80 // 100) // len(same_position_parties)
        for party in same_position_parties:
            redistributed[party] = votes_per_party
    
    # Find parties with distance of 1 (30% of remaining votes)
    close_parties = [p for p, pos in party_positions.items()
                    if abs(pos - party_position) == 1 and p != eliminated_party 
                    and pos != 0]  # Only redistribute to positioned parties
    if close_parties:
        remaining_votes = votes_to_distribute - sum(redistributed.values())
        votes_per_party = (remaining_votes * 30 // 100) // len(close_parties)
        for party in close_parties:
            redistributed[party] = votes_per_party
    
    return redistributed

def simulate_second_round(first_round_votes: Dict[str, int],
                         party_positions: Dict[str, int],
                         top_three: Set[str]) -> Tuple[Dict[str, int], Dict[Tuple[str, str], int]]:
    """Simulate second round by redistributing votes from eliminated parties.
    
    Args:
        first_round_votes: Votes from first round
        party_positions: Left-to-right positions of parties
        top_three: Set of parties that made it to second round
        
    Returns:
        Tuple of (second round votes dict, vote transfers dict)
        Vote transfers dict maps (from_party, to_party) to number of votes transferred
    """
    second_round = first_round_votes.copy()
    vote_transfers = {}  # Maps (from_party, to_party) to number of votes transferred
    
    # Redistribute votes from eliminated parties
    for party, votes in first_round_votes.items():
        if party not in top_three:
            redistributed = redistribute_votes(
                first_round_votes, party_positions, party, party_positions[party])
            
            # Add redistributed votes to second round totals and track transfers
            for target_party, additional_votes in redistributed.items():
                if target_party in top_three:
                    second_round[target_party] += additional_votes
                    vote_transfers[(party, target_party)] = additional_votes
            
            # Track lost votes as transfer to None
            lost_votes = votes - sum(additional_votes 
                                   for target_party, additional_votes in redistributed.items() 
                                   if target_party in top_three)
            if lost_votes > 0:
                vote_transfers[(party, None)] = lost_votes
            
            # Remove eliminated party's original votes
            second_round[party] = 0
    
    return second_round, vote_transfers

def calculate_seats(results: list, states: list, total_seats: int, participating_parties: list, process: dict = None) -> List[Party]:
    """Calculate seat distribution for French elections using two-round system.
    
    In the French system:
    - Parties with ≥12.5% in first round continue to second round
    - If a party gets >50% and ≥25% of registered voters in first round, they win immediately
    - Otherwise, votes from eliminated parties are redistributed based on left-right position
    
    Args:
        results: List of district results with voting data
        states: List of states (not used in French system)
        total_seats: Total number of seats to distribute (0 means use district count)
        participating_parties: List of parties participating in the election
        
    Returns:
        List of Party objects with their allocated seats
    """
    if process is None:
        process = {}
    
    process['seat_calculation'] = []
    
    # Add system explanation
    process['seat_calculation'].append(f"""
## French Electoral System Explanation

This election uses the French two-round voting system (scrutin uninominal majoritaire à deux tours):

1. **First Round**
   - All candidates can participate
   - If a candidate receives >50% of votes AND ≥25% of registered voters, they win immediately
   - Otherwise, qualified candidates proceed to second round

2. **Second Round Qualification**
   - Candidates need ≥12.5% of votes to qualify
   - If no candidates reach 12.5%, top two advance
   - When no second round data is provided, votes are simulated:
     * 80% of votes from eliminated parties go to parties with same left-right position
     * 30% of remaining votes go to parties within 1 position on left-right scale
     * Other votes are considered lost/abstentions

Key Features:
- {total_seats if total_seats > 0 else len(results)} total seats to be distributed
- Single-member constituencies
- Two rounds if no absolute majority in first round

3. **Seat Scaling**
   When the required number of seats ({total_seats}) differs from the number of districts ({len(results)}),
   we use proportional scaling to maintain fair representation:
   - First calculate results for all districts
   - Then multiply each party's seats by (total_seats / number_of_districts)
   - Round to nearest whole number while preserving total seats
   - This maintains the proportional representation from the district results
   
   Example: If we have 100 districts but need 200 seats:
   - Party A wins 60 districts → scaled to 120 seats (60 * 200/100)
   - Party B wins 40 districts → scaled to 80 seats (40 * 200/100)
   The relative strength of each party remains the same.
""")

    # Initialize tracking dictionaries
    party_votes = defaultdict(int)
    party_seats = defaultdict(int)
    parties_with_seats = set()
    cumulative_transfers = defaultdict(int)  # Track total vote transfers
    total_lost_votes = defaultdict(int)      # Track total lost votes
    
    # Create mapping of party positions
    party_positions = {p['short_name']: p.get('left_to_right', 0) 
                      for p in participating_parties}
    
    # Select example districts to demonstrate the process
    example_districts = []
    first_round_winners = []
    multiple_qualifiers = []
    top_two_only = []
    
    # First pass: categorize districts by type
    for district in results[:20]:  # Look in first 20 districts for interesting examples
        first_round_votes = get_votes_for_round(district['party_results'])
        total_votes = sum(first_round_votes.values())
        registered_voters = district.get('registered_voters', total_votes * 2)
        
        top_party = max(first_round_votes.items(), key=lambda x: x[1])
        qualifying_parties = {party for party, votes in first_round_votes.items()
                            if votes >= total_votes * 0.125}
        
        if top_party[1] > total_votes * 0.5 and top_party[1] >= registered_voters * 0.25:
            first_round_winners.append(district)
        elif len(qualifying_parties) >= 3:
            multiple_qualifiers.append(district)
        elif len(qualifying_parties) <= 2:
            top_two_only.append(district)
    
    # Add one example of each type if available
    if first_round_winners:
        example_districts.append(first_round_winners[0])
    if multiple_qualifiers:
        example_districts.append(multiple_qualifiers[0])
    if top_two_only:
        example_districts.append(top_two_only[0])
        
    # If we don't have enough examples, add more of whatever type we have
    while len(example_districts) < 3:
        if multiple_qualifiers and len(multiple_qualifiers) > 1:
            example_districts.append(multiple_qualifiers[1])
            multiple_qualifiers.pop(1)
        elif top_two_only and len(top_two_only) > 1:
            example_districts.append(top_two_only[1])
            top_two_only.pop(1)
        elif first_round_winners and len(first_round_winners) > 1:
            example_districts.append(first_round_winners[1])
            first_round_winners.pop(1)
        else:
            # If we can't find any more examples, just break
            break
    
    # Document example districts
    process['seat_calculation'].append("""

## Example Districts

To illustrate how the French two-round system works in practice, here are three example districts:
""")
    
    for i, district in enumerate(example_districts, 1):
        first_round_votes = get_votes_for_round(district['party_results'])
        total_votes = sum(first_round_votes.values())
        registered_voters = district.get('registered_voters', total_votes * 2)
        
        example_text = f"""
### Example {i}: {district.get('name', f'District {i}')}

**First Round Results:**
- Total votes cast: {total_votes:,}
- Registered voters: {registered_voters:,}

**Party Results:**
"""        
        # Add first round results
        for party, votes in sorted(first_round_votes.items(), key=lambda x: x[1], reverse=True):
            percentage = (votes / total_votes) * 100
            threshold_pct = (votes / registered_voters) * 100
            example_text += f"- {party}: {votes:,} votes ({percentage:.1f}% of votes, {threshold_pct:.1f}% of registered)\n"
        
        # Check for first round winner
        top_party = max(first_round_votes.items(), key=lambda x: x[1])
        if top_party[1] > total_votes * 0.5 and top_party[1] >= registered_voters * 0.25:
            example_text += f"\n**Result:** {top_party[0]} wins in first round with absolute majority and ≥25% of registered voters"
        else:
            # Show second round qualification and simulation
            qualifying_parties = {party for party, votes in first_round_votes.items()
                                if votes >= total_votes * 0.125}
            
            if not qualifying_parties:
                qualifying_parties = {p[0] for p in 
                                    sorted(first_round_votes.items(), 
                                          key=lambda x: x[1], 
                                          reverse=True)[:2]}
                example_text += "\n**Second Round:** No parties reached 12.5% threshold - top two advance:\n"
            else:
                example_text += "\n**Second Round:** Parties qualifying (≥12.5%):\n"
            
            for party in qualifying_parties:
                votes = first_round_votes[party]
                example_text += f"- {party}: {votes:,} votes ({(votes/total_votes)*100:.1f}%)\n"
            
            # If no second round data, show vote redistribution simulation
            if 'party_results_round_2' not in district:
                example_text += "\n**Vote Redistribution Simulation:**\n"
                second_round_votes, transfers = simulate_second_round(
                    first_round_votes, party_positions, qualifying_parties)
                
                # Show transfers
                example_text += "Vote Transfers:\n"
                for (from_party, to_party), votes in transfers.items():
                    if to_party is None:
                        example_text += f"- {from_party}: {votes:,} votes lost/abstained\n"
                    else:
                        example_text += f"- {from_party} → {to_party}: {votes:,} votes\n"
                
                # Show final result
                example_text += "\n**Final Second Round Result:**\n"
                for party, votes in sorted(second_round_votes.items(), key=lambda x: x[1], reverse=True):
                    if votes > 0:
                        example_text += f"- {party}: {votes:,} votes ({(votes/total_votes)*100:.1f}%)\n"
                
                winner = max(second_round_votes.items(), key=lambda x: x[1])[0]
                example_text += f"\n**Result:** {winner} wins the simulated second round"
            
        process['seat_calculation'].append(example_text + "\n")
    
    # Process each district
    district_count = len(results)
    for district in results:
        if 'party_results_round_2' in district:
            # Use actual second round results
            second_round_votes = get_votes_for_round(district['party_results_round_2'])
            winner = max(second_round_votes.items(), key=lambda x: x[1])[0]
        else:
            # Get first round votes
            first_round_votes = get_votes_for_round(district['party_results'])
            total_votes = sum(first_round_votes.values())
            registered_voters = district.get('registered_voters', total_votes * 2)  # Estimate if not provided
            
            # Check for first round winner (>50% and ≥25% of registered voters)
            top_party = max(first_round_votes.items(), key=lambda x: x[1])
            if (top_party[1] > total_votes * 0.5 and 
                top_party[1] >= registered_voters * 0.25):
                winner = top_party[0]
            else:
            
                # Find parties that qualify for second round (≥12.5%)
                qualifying_parties = {party for party, votes in first_round_votes.items()
                                    if votes >= total_votes * 0.125}
                
                # If no parties qualify, use top two
                if not qualifying_parties:
                    qualifying_parties = {p[0] for p in 
                                        sorted(first_round_votes.items(), 
                                              key=lambda x: x[1], 
                                              reverse=True)[:2]}
                
                # Simulate second round
                second_round_votes, transfers = simulate_second_round(
                    first_round_votes, party_positions, qualifying_parties)
                
                # Accumulate transfers
                for (from_party, to_party), votes in transfers.items():
                    if to_party is None:
                        total_lost_votes[from_party] += votes
                    else:
                        cumulative_transfers[(from_party, to_party)] += votes
                
                winner = max(second_round_votes.items(), key=lambda x: x[1])[0]
        
        # Update vote totals and allocate seat
        for party, votes in get_votes_for_round(district['party_results']).items():
            party_votes[party] += votes
        
        party_seats[winner] += 1
        parties_with_seats.add(winner)
    
    # If total_seats is specified and different from district count,
    # scale up the district-based seat distribution proportionally
    if total_seats > 0 and total_seats != district_count:
        # Calculate scaling factor first
        scale_factor = total_seats / district_count
        
        # Add scaling explanation to process with before/after comparison
        scaling_text = f"""
## Seat Scaling Applied

Scaling from {district_count} districts to {total_seats} total seats:

### Before Scaling ({district_count} seats)
| Party | Seats | Percentage |
|-------|--------|------------|
"""
        
        # Add original seat distribution
        for party, seats in sorted(party_seats.items(), key=lambda x: x[1], reverse=True):
            if seats > 0:
                pct = (seats / district_count) * 100
                scaling_text += f"| {party} | {seats:,} | {pct:.1f}% |\n"
        
        scaled_seats = {}
        total_scaled = 0
        
        for party, seats in party_seats.items():
            scaled = round(seats * scale_factor)
            scaled_seats[party] = scaled
            total_scaled += scaled
        
        # Adjust for rounding errors
        if total_scaled != total_seats:
            max_party = max(scaled_seats.items(), key=lambda x: x[1])[0]
            scaled_seats[max_party] += total_seats - total_scaled
        
        # Add scaled seat distribution
        scaling_text += f"""

### After Scaling ({total_seats} seats)
| Party | Seats | Percentage | Change |
|-------|--------|------------|---------|\n"""
        
        for party, seats in sorted(scaled_seats.items(), key=lambda x: x[1], reverse=True):
            if seats > 0:
                orig_pct = (party_seats[party] / district_count) * 100
                new_pct = (seats / total_seats) * 100
                pct_change = new_pct - orig_pct
                scaling_text += f"| {party} | {seats:,} | {new_pct:.1f}% | {pct_change:+.1f}% |\n"
        
        scaling_text += f"""

Scaling Details:
- Scaling factor: {scale_factor:.3f}
- Each party's seats multiplied by this factor and rounded
- Total seats preserved through rounding adjustments
- Percentages of total seats remain nearly identical"""
        
        process['seat_calculation'].append(scaling_text)
        
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
    
    # Print cumulative vote transfer statistics
    print("\nCumulative Vote Transfers:")
    print("------------------------")
    
    # Sort transfers by number of votes
    sorted_transfers = sorted(cumulative_transfers.items(), 
                            key=lambda x: x[1], 
                            reverse=True)
    
    for (from_party, to_party), votes in sorted_transfers:
        print(f"{from_party} -> {to_party}: {votes:,} votes")
    
    print("\nTotal Lost Votes:")
    print("----------------")
    sorted_lost = sorted(total_lost_votes.items(),
                        key=lambda x: x[1],
                        reverse=True)
    for party, votes in sorted_lost:
        print(f"{party}: {votes:,} votes")
    
    # Create Party objects with final vote and seat counts
    parties = []
    for party_data in participating_parties:
        short_name = party_data['short_name']
        votes = party_votes.get(short_name, 0)
        if votes > 0:  # Include all parties that got votes
            parties.append(Party(
                name=short_name,
                color=party_data.get('color', '#CCCCCC'),
                size=party_seats.get(short_name, 0),  # 0 seats if party didn't win any
                left_to_right=party_data.get('left_to_right', 0),
                votes=votes
            ))
    
    return parties
