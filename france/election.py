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

def calculate_seats(results: list, states: list, total_seats: int, participating_parties: list) -> List[Party]:
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
    # Initialize tracking dictionaries
    party_votes = defaultdict(int)
    party_seats = defaultdict(int)
    parties_with_seats = set()
    cumulative_transfers = defaultdict(int)  # Track total vote transfers
    total_lost_votes = defaultdict(int)      # Track total lost votes
    
    # Create mapping of party positions
    party_positions = {p['short_name']: p.get('left_to_right', 0) 
                      for p in participating_parties}
    
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
                continue
            
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
