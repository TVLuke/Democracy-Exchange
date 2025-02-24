TITLE = "nach italienischem Wahlrecht (Rosatellum)."

DESCRIPTION = """
Das italienische Wahlsystem 'Rosatellum' für die Abgeordnetenkammer (Camera dei deputati):

Grundsätze:
- Gemischtes Wahlsystem mit zwei Komponenten:
  * 36% der Sitze durch Mehrheitswahl in Einerwahlkreisen (FPTP)
  * 64% der Sitze durch Verhältniswahl mit Parteilisten (PR)

Sperrklauseln:
- Einzelne Parteien: 3% der Gesamtstimmen
- Wahlbündnisse (Koalitionen): 10% der Gesamtstimmen
  * Mindestens eine Partei im Bündnis muss 3% erreichen

Besonderheiten:
- Eine Stimme zählt sowohl für Direkt- als auch Listenmandat
- Stimmen von Parteien zwischen 1-3% werden auf Koalitionspartner über 3% verteilt
- Parteien müssen Koalitionszugehörigkeit vor der Wahl erklären
- Verteilung der Verhältniswahlsitze nach dem Hare-Niemeyer-Verfahren
- Insgesamt 630 Sitze in der Abgeordnetenkammer

Ablauf der Sitzverteilung:
1. Direktmandate (36%):
   - In jedem Wahlkreis gewinnt der Kandidat mit den meisten Stimmen
   - 36% der Sitze werden durch Direktmandate vergeben (bei 630 Sitzen: 226 Sitze)

2. Verhältniswahlmandate (64%):
   - Nur Parteien über der Sperrklausel werden berücksichtigt
   - 404 Sitze nach Verhältniswahl mit Hare-Niemeyer
   - Restmandate nach größten Dezimalstellen

Dieses System wurde 2017 eingeführt und nach seinem Autor Ettore Rosato benannt.
"""

from typing import List, Dict, Any
from collections import defaultdict
import math
import json
import random
from party import Party

def calculate_seats(results: list, states: list, total_seats: int, participating_parties: list, process: dict = None) -> List[Party]:
    """
    Calculate seat distribution for Italian Chamber of Deputies using the Rosatellum system.
    
    Assumptions for mapping other election data:
    1. If both member and list votes exist:
       - member_votes used for FPTP seats (36%)
       - list_votes used for proportional seats (64%)
    2. If only list votes exist:
       - Use list_votes for both FPTP and proportional
    3. If only member votes exist:
       - Use member_votes for both FPTP and proportional
    4. For coalitions:
       - Parties marked as in_coalition=True are treated as coalition members
       - Coalition thresholds and vote sharing applied accordingly
    
    Args:
        results: List of district results with voting data
        states: List of states (used for district grouping)
        total_seats: Total number of seats (630 for Chamber of Deputies)
        participating_parties: List of parties with coalition information
        process: Dictionary to store calculation steps
    """
    if process is None:
        process = {}
    if 'seat_calculation' not in process:
        process['seat_calculation'] = []
    
    # Add description to process
    process['seat_calculation'].append("## Electoral System Description")
    process['seat_calculation'].append(DESCRIPTION)
    process['seat_calculation'].append("")
    
    print("\n=== STARTING ITALIAN SEAT CALCULATION ===")
    print(f"Total seats to allocate: {total_seats}")
    print(f"Number of participating parties: {len(participating_parties)}")
    
    # Initialize vote counting
    party_votes = defaultdict(int)
    coalition_votes = defaultdict(int)
    coalition_members = defaultdict(list)
    
    # Calculate direct allocation seats (36% of total)
    fptp_seats = int(total_seats * 0.36)
    proportional_seats = total_seats - fptp_seats
    
    process['seat_calculation'].append(f"\nSeat allocation:")
    process['seat_calculation'].append(f"Direct allocation seats (36%): {fptp_seats}")
    process['seat_calculation'].append(f"Proportional seats (64%): {proportional_seats}")
    
    # Count votes for each party
    direct_votes = defaultdict(int)
    proportional_votes = defaultdict(int)
    total_direct_votes = 0
    total_proportional_votes = 0
    
    print("\nCounting votes...")
    
    # Randomly select 3 districts to document in detail
    example_districts = random.sample(results, min(3, len(results)))
    process['seat_calculation'].append("""
=== Example Districts ===
Here are three randomly selected districts showing how votes are counted and allocated:""")
    
    # First count votes from results
    for district in results:
        if 'party_results' in district:
            district_votes = {}
            district_total_votes = 0
            
            for party_name, party_results in district['party_results'].items():
                if 'list' in party_results:
                    votes = party_results['list']
                    proportional_votes[party_name] += int(votes * 0.64)
                    direct_votes[party_name] += int(votes * 0.36)
                    party_votes[party_name] += votes
                    district_votes[party_name] = votes
                    district_total_votes += votes
                elif 'member' in party_results:
                    votes = party_results['member']
                    proportional_votes[party_name] += int(votes * 0.64)
                    direct_votes[party_name] += int(votes * 0.36)
                    party_votes[party_name] += votes
                    district_votes[party_name] = votes
                    district_total_votes += votes
            
            # Document example districts with detailed vote calculations
            if district in example_districts:
                # Find winner of direct mandate
                winner = max(district_votes.items(), key=lambda x: x[1])
                
                vote_details = "\n".join([f"- {party}: {votes:,} votes ({votes/district_total_votes*100:.1f}%)" 
                                        for party, votes in sorted(district_votes.items(), key=lambda x: x[1], reverse=True)])
                
                process['seat_calculation'].append(f"""

## District: {district['name']}
This district demonstrates how votes are split between direct mandate (36%) and proportional representation (64%):

Total votes cast: {district_total_votes:,}
{vote_details}

Direct mandate winner:
- {winner[0]}: {winner[1]:,} votes ({winner[1]/district_total_votes*100:.1f}%)

Vote allocation:
- Direct votes (36%): {int(district_total_votes * 0.36):,} votes for FPTP allocation
- Proportional votes (64%): {int(district_total_votes * 0.64):,} votes for PR allocation
""")
            
            # Update total vote counts
            total_proportional_votes += int(district_total_votes * 0.64)
            total_direct_votes += int(district_total_votes * 0.36)
    
    # Print and log vote totals
    print("\nParty vote totals:")
    process['seat_calculation'].append("\n=== Party Vote Totals ===")
    for party_name, votes in party_votes.items():
        vote_details = f"""
{party_name}: {votes:,} total votes
  - Direct votes (36%): {direct_votes[party_name]:,}
  - Proportional votes (64%): {proportional_votes[party_name]:,}"""
        print(vote_details)
        process['seat_calculation'].append(vote_details)
    
    # Log direct vote counts
    process['seat_calculation'].append(f"\nDirect vote counts (36% of total votes):")
    if total_direct_votes > 0:
        for party_name, votes in sorted(direct_votes.items(), key=lambda x: x[1], reverse=True):
            vote_share = votes / total_direct_votes * 100
            process['seat_calculation'].append(f"{party_name}: {votes:,} votes ({vote_share:.1f}%)")
    else:
        process['seat_calculation'].append(f"WARNING: No valid direct votes found!")
        return []  # Return empty list if no valid votes

    # Allocate direct seats based on direct votes
    fptp_allocation = defaultdict(int)
    
    header = f"\n=== DIRECT SEAT ALLOCATION (36% = {fptp_seats} seats) ==="
    print(header)
    process['seat_calculation'].append(header)
    
    subheader = f"Using 36% of member votes (if available) or list votes"
    print(subheader)
    process['seat_calculation'].append(subheader)
    
    if total_direct_votes > 0:
        # Show all direct votes first
        vote_header = f"\nDirect votes (36% of total votes):"
        print(vote_header)
        process['seat_calculation'].append(vote_header)
        
        for party_name, votes in sorted(direct_votes.items(), key=lambda x: x[1], reverse=True):
            vote_share = votes / total_direct_votes * 100
            vote_line = f"{party_name}: {votes:,} votes ({vote_share:.2f}%)"
            print(vote_line)
            process['seat_calculation'].append(vote_line)
        
        # Calculate direct seat shares
        direct_shares = {party: votes/total_direct_votes for party, votes in direct_votes.items()}
        allocated_seats = 0
        remainders = {}
        
        alloc_header = f"\nInitial direct seat allocation:"
        print(alloc_header)
        process['seat_calculation'].append(alloc_header)
        
        # First allocation - give each party their fair share
        for party, share in sorted(direct_shares.items(), key=lambda x: x[1], reverse=True):
            fair_share = share * fptp_seats
            seats = int(fair_share)
            fptp_allocation[party] = seats
            remainders[party] = fair_share - seats
            allocated_seats += seats
            
            alloc_line = f"{party}: {seats} seats (fair share: {fair_share:.3f}, remainder: {fair_share - seats:.3f})"
            print(alloc_line)
            process['seat_calculation'].append(alloc_line)
        
        # Distribute remaining seats by largest remainder
        remaining_seats = fptp_seats - allocated_seats
        if remaining_seats > 0:
            remain_header = f"\nDistributing {remaining_seats} remaining direct seats by largest remainder:"
            print(remain_header)
            process['seat_calculation'].append(remain_header)
            
            sorted_remainders = sorted(remainders.items(), key=lambda x: x[1], reverse=True)
            
            for i in range(remaining_seats):
                if i < len(sorted_remainders):
                    party = sorted_remainders[i][0]
                    fptp_allocation[party] += 1
                    remain_line = f"{party}: +1 seat (remainder was {sorted_remainders[i][1]:.3f})"
                    print(remain_line)
                    process['seat_calculation'].append(remain_line)
        
        # Show final direct allocation
        final_header = f"\nFinal direct seat allocation:"
        print(final_header)
        process['seat_calculation'].append(final_header)
        
        for party, seats in sorted(fptp_allocation.items(), key=lambda x: x[1], reverse=True):
            if seats > 0:
                vote_share = direct_votes[party] / total_direct_votes * 100
                seat_share = seats / fptp_seats * 100
                final_line = f"{party}: {seats} seats ({seat_share:.2f}% of seats, {vote_share:.2f}% of direct votes)"
                print(final_line)
                process['seat_calculation'].append(final_line)
    else:
        # If no direct votes, give all direct seats to party with most list votes
        top_party = max(party_votes.items(), key=lambda x: x[1])[0]
        fptp_allocation[top_party] = fptp_seats
        process['seat_calculation'].append(f"No valid direct votes. Allocating all direct seats to party with most list votes: {top_party}")
    
    # Log proportional vote counts
    process['seat_calculation'].append(f"\nProportional vote counts (64% of total votes):")
    for party_name, votes in sorted(proportional_votes.items(), key=lambda x: x[1], reverse=True):
        vote_share = votes / total_proportional_votes * 100
        process['seat_calculation'].append(f"{party_name}: {votes:,} votes ({vote_share:.1f}%)")
    
    # Apply thresholds and calculate eligible parties
    eligible_parties = {}
    process['seat_calculation'].append(f"\nVote shares and thresholds:")
    process['seat_calculation'].append(f"Total proportional votes: {total_proportional_votes:,}")
    
    # Check if any parties have coalition information
    coalitions = defaultdict(list)
    coalition_votes = defaultdict(int)
    coalition_party_votes = defaultdict(dict)
    has_coalitions = False
    
    for party in participating_parties:
        party_name = party['short_name']
        if 'coalition' in party and party['coalition']:
            has_coalitions = True
            coalition_name = party['coalition']
            coalitions[coalition_name].append(party_name)
            if party_name in party_votes:
                coalition_votes[coalition_name] += party_votes[party_name]
                coalition_party_votes[coalition_name][party_name] = party_votes[party_name]
    
    if has_coalitions:
        process['seat_calculation'].append("\n=== COALITION INFORMATION ===")
        for coalition_name, parties in coalitions.items():
            total_votes = coalition_votes[coalition_name]
            vote_share = total_votes / total_proportional_votes * 100
            coalition_info = f"\n{coalition_name} Coalition:\n"
            coalition_info += f"Total votes: {total_votes:,} ({vote_share:.2f}% of all votes)\n"
            coalition_info += "Member parties:\n"
            
            # Sort parties by votes
            sorted_parties = sorted(
                [(p, coalition_party_votes[coalition_name].get(p, 0)) for p in parties],
                key=lambda x: x[1],
                reverse=True
            )
            
            for party_name, party_votes_count in sorted_parties:
                if party_votes_count > 0:
                    party_share = party_votes_count / total_proportional_votes * 100
                    coalition_share = party_votes_count / total_votes * 100
                    coalition_info += f"- {party_name}: {party_votes_count:,} votes "
                    coalition_info += f"({party_share:.2f}% of all votes, {coalition_share:.2f}% of coalition votes)\n"
                else:
                    coalition_info += f"- {party_name}: No votes recorded\n"
            
            coalition_info += f"Threshold status: {'Above' if vote_share >= 10 else 'Below'} 10% coalition threshold"
            process['seat_calculation'].append(coalition_info)
    
    print("\n=== APPLYING THRESHOLDS ===\n")
    print(f"Total proportional votes: {total_proportional_votes:,}")
    if has_coalitions:
        print("Coalition vote shares:")
        for coalition, votes in coalition_votes.items():
            share = votes / total_proportional_votes * 100
            print(f"{coalition}: {votes:,} votes ({share:.2f}%)")
    
    # Process parties and apply thresholds
    print("\nChecking party eligibility:")
    for party_name, votes in proportional_votes.items():
        vote_share = votes / total_proportional_votes
        print(f"\n{party_name}:")
        print(f"  Proportional votes: {votes:,} ({vote_share*100:.2f}%)")
        process['seat_calculation'].append(f"\n{party_name}:")
        process['seat_calculation'].append(f"  Proportional votes: {votes:,} ({vote_share*100:.2f}%)")
        
        if has_coalitions:
            # Find party's coalition
            party_info = next((p for p in participating_parties if p['short_name'] == party_name), None)
            coalition_name = party_info.get('coalition') if party_info else None
            
            coalition_share = coalition_votes[coalition_name] / total_proportional_votes if coalition_name else 0
            if coalition_name:
                print(f"  Part of coalition: {coalition_name} ({coalition_share*100:.2f}% total)")
            
            if coalition_name and coalition_share >= 0.10:
                # Party in coalition above 10%
                if vote_share >= 0.03:
                    # Party gets its own seats
                    eligible_parties[party_name] = votes
                    msg = f"  ELIGIBLE: Above 3% threshold in coalition above 10%"
                    print(msg)
                    process['seat_calculation'].append(msg)
                elif vote_share >= 0.01:
                    # Votes get redistributed to coalition partners above 3%
                    msg = f"  NOT ELIGIBLE: Between 1-3%, votes will be redistributed to coalition partners above 3%"
                    print(msg)
                    process['seat_calculation'].append(msg)
                    
                    # Find coalition partners above 3%
                    coalition_partners = []
                    total_partner_votes = 0
                    for p in participating_parties:
                        if p.get('coalition') == coalition_name and p['short_name'] != party_name:
                            p_votes = proportional_votes.get(p['short_name'], 0)
                            p_share = p_votes / total_proportional_votes
                            if p_share >= 0.03:
                                coalition_partners.append(p['short_name'])
                                total_partner_votes += p_votes
                    
                    # Redistribute votes proportionally
                    if coalition_partners and total_partner_votes > 0:
                        for partner in coalition_partners:
                            partner_share = proportional_votes[partner] / total_partner_votes
                            additional_votes = votes * partner_share
                            proportional_votes[partner] += additional_votes
                            msg = f"    Redistributing {additional_votes:,.0f} votes to {partner}"
                            print(msg)
                            process['seat_calculation'].append(msg)
                else:
                    msg = f"  NOT ELIGIBLE: Below 1% threshold"
                    print(msg)
                    process['seat_calculation'].append(msg)
            else:
                # Independent party or coalition below 10%
                if vote_share >= 0.03:
                    eligible_parties[party_name] = votes
                    msg = f"  ELIGIBLE: Above 3% threshold"
                    print(msg)
                    process['seat_calculation'].append(msg)
                else:
                    msg = f"  NOT ELIGIBLE: Below 3% threshold"
                    print(msg)
                    process['seat_calculation'].append(msg)
        else:
            # No coalitions, simple 3% threshold
            if vote_share >= 0.03:
                eligible_parties[party_name] = votes
                msg = f"  ELIGIBLE: Above 3% threshold"
                print(msg)
                process['seat_calculation'].append(msg)
            else:
                msg = f"  NOT ELIGIBLE: Below 3% threshold"
                print(msg)
                process['seat_calculation'].append(msg)
    
    print(f"\nEligible parties: {list(eligible_parties.keys())}")

    
    process['seat_calculation'].append(f"\nEligible parties: {list(eligible_parties.keys())}")

    # Calculate FPTP seats (36% of total)
    fptp_seats = int(total_seats * 0.36)
    proportional_seats = total_seats - fptp_seats
    
    process['seat_calculation'].append(f"""
FPTP Seats (36%): {fptp_seats}
Proportional Seats (64%): {proportional_seats}
""")

    # Initialize seat allocations
    fptp_allocation = defaultdict(int)
    proportional_allocation = defaultdict(int)
    
    # Check if we have any eligible parties
    if not eligible_parties:
        # If no parties meet the threshold, make all parties eligible
        print("\nNo parties met the threshold. Making all parties eligible.")
        process['seat_calculation'].append("\nNo parties met the threshold. Making all parties eligible.")
        for party_name, votes in proportional_votes.items():
            eligible_parties[party_name] = votes
    
    # Calculate vote shares for eligible parties
    total_eligible_votes = sum(eligible_parties.values())
    vote_shares = {party: votes/total_eligible_votes for party, votes in eligible_parties.items()}
    
    # Allocate FPTP seats
    process['seat_calculation'].append(f"\nFPTP allocation ({fptp_seats} seats):")
    process['seat_calculation'].append(f"Total eligible votes: {total_eligible_votes:,}")
    
    # First allocation - give each party their fair share
    remainders = {}
    allocated_seats = 0
    
    for party, share in vote_shares.items():
        # Calculate fair share of seats
        fair_share = share * fptp_seats
        # Allocate whole number of seats
        seats = int(fair_share)
        fptp_allocation[party] = seats
        remainders[party] = fair_share - seats
        allocated_seats += seats
        
        if seats > 0:
            msg = f"{party}: {seats} seats ({share*100:.1f}% of votes)"
            print(msg)
            process['seat_calculation'].append(msg)
    
    # Distribute remaining seats by largest remainder
    remaining_seats = fptp_seats - allocated_seats
    if remaining_seats > 0:
        msg = f"\nDistributing {remaining_seats} remaining FPTP seats:"
        print(msg)
        process['seat_calculation'].append(msg)
        sorted_remainders = sorted(remainders.items(), key=lambda x: x[1], reverse=True)
        
        for i in range(remaining_seats):
            party = sorted_remainders[i][0]
            fptp_allocation[party] += 1
            msg = f"{party}: +1 seat (remainder was {sorted_remainders[i][1]:.3f})"
            print(msg)
            process['seat_calculation'].append(msg)
    
    # Final summary
    process['seat_calculation'].append(f"\nFinal FPTP allocation:")
    total_fptp_allocated = 0
    total_eligible_votes = sum(eligible_parties.values())
    
    for party, seats in sorted(fptp_allocation.items(), key=lambda x: x[1], reverse=True):
        if seats > 0:
            total_fptp_allocated += seats
            vote_share = eligible_parties[party] / total_eligible_votes * 100
            seat_share = seats / fptp_seats * 100
            process['seat_calculation'].append(
                f"{party}: {seats} seats ({seat_share:.1f}% of seats, {vote_share:.1f}% of votes)")
    
    process['seat_calculation'].append(f"Total FPTP seats allocated: {total_fptp_allocated} of {fptp_seats}")

    # Allocate proportional seats using largest remainder method
    proportional_allocation = defaultdict(int)
    
    header = f"\n=== PROPORTIONAL ALLOCATION (64% = {proportional_seats} seats) ==="
    print(header)
    process['seat_calculation'].append(header)
    
    if eligible_parties:  # Only proceed if we have eligible parties
        total_eligible_votes = sum(eligible_parties.values())
        
        votes_header = f"\nProportional votes (64% of total votes):"
        print(votes_header)
        process['seat_calculation'].append(votes_header)
        
        for party_name, votes in sorted(proportional_votes.items(), key=lambda x: x[1], reverse=True):
            if party_name in eligible_parties:
                vote_share = votes / total_proportional_votes * 100
                vote_line = f"{party_name}: {votes:,} votes ({vote_share:.2f}%)"
                print(vote_line)
                process['seat_calculation'].append(vote_line)
        
        # Calculate vote shares and initial allocation using proportional votes
        vote_shares = {party: proportional_votes[party]/total_proportional_votes 
                      for party in eligible_parties.keys() 
                      if party in proportional_votes}
        remainders = {}
        allocated_seats = 0
        
        alloc_header = f"\nInitial proportional seat allocation:"
        print(alloc_header)
        process['seat_calculation'].append(alloc_header)
        
        for party, share in sorted(vote_shares.items(), key=lambda x: x[1], reverse=True):
            # Calculate fair share of seats
            fair_share = share * proportional_seats
            # Allocate whole number of seats
            seats = int(fair_share)
            proportional_allocation[party] = seats
            remainders[party] = fair_share - seats
            allocated_seats += seats
            
            alloc_line = f"{party}: {seats} seats (fair share: {fair_share:.3f}, remainder: {fair_share - seats:.3f})"
            print(alloc_line)
            process['seat_calculation'].append(alloc_line)
        
        # Distribute remaining seats by largest remainder
        remaining_seats = proportional_seats - allocated_seats
        if remaining_seats > 0:
            remain_header = f"\nDistributing {remaining_seats} remaining proportional seats:"
            print(remain_header)
            process['seat_calculation'].append(remain_header)
            
            sorted_remainders = sorted(remainders.items(), key=lambda x: x[1], reverse=True)
            
            # Keep distributing seats until all are allocated
            while remaining_seats > 0:
                # If we've gone through all parties, start over
                if len(sorted_remainders) == 0:
                    sorted_remainders = sorted(remainders.items(), key=lambda x: x[1], reverse=True)
                
                party = sorted_remainders[0][0]
                proportional_allocation[party] += 1
                remain_line = f"{party}: +1 seat (remainder was {sorted_remainders[0][1]:.3f})"
                print(remain_line)
                process['seat_calculation'].append(remain_line)
                
                # Remove this party from the list and decrement remaining seats
                sorted_remainders = sorted_remainders[1:]
                remaining_seats -= 1
        
        # Final summary
        final_header = f"\nFinal proportional allocation:"
        print(final_header)
        process['seat_calculation'].append(final_header)
        
        total_prop_allocated = 0
        for party, seats in sorted(proportional_allocation.items(), key=lambda x: x[1], reverse=True):
            if seats > 0:
                total_prop_allocated += seats
                vote_share = proportional_votes[party] / total_proportional_votes * 100
                seat_share = seats / proportional_seats * 100
                final_line = f"{party}: {seats} seats ({seat_share:.1f}% of seats, {vote_share:.1f}% of proportional votes)"
                print(final_line)
                process['seat_calculation'].append(final_line)
        
        summary = f"Total proportional seats allocated: {total_prop_allocated} of {proportional_seats}"
        print(summary)
        process['seat_calculation'].append(summary)
    else:
        # If no eligible parties, give all proportional seats to party with most votes
        top_party = max(party_votes.items(), key=lambda x: x[1])[0]
        proportional_allocation[top_party] = proportional_seats
        process['seat_calculation'].append(f"No eligible parties for proportional seats. Allocating all to party with most votes: {top_party}")

    # Create final Party objects with total seats
    final_parties = []
    total_allocated_seats = 0
    process['seat_calculation'].append(f"\nFinal party allocations:")
    
    # Get all parties that got any seats
    parties_with_seats = set(fptp_allocation.keys()) | set(proportional_allocation.keys())
    
    for party_name in parties_with_seats:
        # Find party info
        party_info = next((p for p in participating_parties if p['short_name'] == party_name), None)
        if not party_info:
            continue
            
        # Get total seats for this party
        party_seats = fptp_allocation.get(party_name, 0) + proportional_allocation.get(party_name, 0)
        
        # Only include parties that got seats
        if party_seats > 0:
            # Use proportional votes for vote share if available, otherwise direct votes
            if party_name in proportional_votes:
                votes = proportional_votes[party_name]
                total_votes = total_proportional_votes
            else:
                votes = direct_votes.get(party_name, 0)
                total_votes = total_direct_votes
            
            final_parties.append(Party(
                name=party_name,
                color=party_info.get('color', '#808080'),
                size=party_seats,
                left_to_right=party_info.get('left_to_right', 0),
                votes=party_votes[party_name]
            ))
            total_allocated_seats += party_seats
            vote_share = votes / total_votes * 100 if total_votes > 0 else 0
            seat_share = party_seats / total_seats * 100
            process['seat_calculation'].append(
                f"{party_name}: {party_seats} seats ({seat_share:.1f}% of seats, {vote_share:.1f}% of votes)")
    
    # If no parties got seats through normal allocation, give all seats to party with most votes
    if not final_parties:
        # Use proportional votes to determine top party
        top_party_name = max(proportional_votes.items(), key=lambda x: x[1])[0]
        top_party_votes = proportional_votes[top_party_name]
        party_info = next((p for p in participating_parties if p['short_name'] == top_party_name), None)
        
        if party_info:
            final_parties.append(Party(
                name=top_party_name,
                color=party_info.get('color', '#808080'),
                size=total_seats,
                left_to_right=party_info.get('left_to_right', 0),
                votes=top_party_votes
            ))
            total_allocated_seats = total_seats
            process['seat_calculation'].append(f"No parties received seats through normal allocation.")
            process['seat_calculation'].append(f"Allocating all seats to party with most votes: {top_party_name}")
    
    process['seat_calculation'].append(f"\nTotal allocated seats: {total_allocated_seats} of {total_seats}")
    
    # Ensure we have at least one party with seats
    if not final_parties:
        # If no parties got seats through normal allocation, give all seats to the party with most votes
        top_party_name = max(party_votes.items(), key=lambda x: x[1])[0]
        party_info = next((p for p in participating_parties if p['short_name'] == top_party_name), None)
        
        if party_info:
            votes = party_votes[top_party_name]
            final_parties.append(Party(
                name=top_party_name,
                color=party_info.get('color', '#808080'),
                size=total_seats,
                left_to_right=party_info.get('left_to_right', 0),
                votes=votes
            ))
            process['seat_calculation'].append(f"\nNo parties received seats through normal allocation.")
            process['seat_calculation'].append(f"Allocating all seats to party with most votes: {top_party_name}")
    
    # Sort parties by number of seats
    final_parties.sort(key=lambda x: (-x.size, -x.votes))
    
    # Document final distribution
    # Get coalition info for each party
    party_coalitions = {p['short_name']: p.get('coalition', '') for p in participating_parties}
    
    process['seat_calculation'].append(f"""
=== FINAL SEAT DISTRIBUTION SUMMARY ===
- Total seats allocated: {total_allocated_seats} of {total_seats} ({total_allocated_seats/total_seats*100:.1f}%)
- FPTP seats: {sum(fptp_allocation.values())} of {fptp_seats} ({sum(fptp_allocation.values())/fptp_seats*100:.1f}%)
- Proportional seats: {sum(proportional_allocation.values())} of {proportional_seats} ({sum(proportional_allocation.values())/proportional_seats*100:.1f}%)
- Number of parties represented: {len(final_parties)}

Party-by-Party Breakdown:
{chr(10).join(f'- {party.name} {f"({party_coalitions[party.name]})" if party_coalitions.get(party.name) else ""}: {party.size} seats ({party.size/total_seats*100:.1f}%)' for party in final_parties)}

Threshold Effects:
- Independent parties needed 3% of total votes
- Coalitions needed 10% of total votes collectively
- Parties in coalitions above 10% needed only 1% individually
- Parties in coalitions below 10% needed 3% individually

System Details:
- Direct mandate seats: 36% of total seats
- Proportional seats: 64% of total seats
- Threshold for representation: 3% of total votes (or 1% if in coalition above 10%)
- Coalition threshold: 10% of total votes
""")
    
    # Add a separator line for readability
    process['seat_calculation'].append("\n" + "=" * 50 + "\n")
    
    return final_parties
