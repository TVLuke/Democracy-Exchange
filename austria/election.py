import math
import json
import sys
import os

TITLE = "nach Österreichischem Wahlrecht."

# Add parent directory to path to import party.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from party import Party

def calculate_district_seats(districts, state_seats, verhaeltniszahl, state_name):
    # Group districts by state and calculate their mandates
    state_districts = [d for d in districts if d['state'] == state_name]
    district_calculations = []
    total_value = 0  # Sum of all population/electorate values
    
    # First determine which value to use (population or electorate) and get total
    use_electorate = all(d['population'] == 0 for d in state_districts)
    
    for district in state_districts:
        value = district['electorate'] if use_electorate else district['population']
        if value == 0:
            print(f"Error: No valid population or electorate data for district {district['district']}")
            return None
        total_value += value
    
    # Calculate exact mandates for each district
    initial_total = 0
    for district in state_districts:
        value = district['electorate'] if use_electorate else district['population']
        exact_mandate = value / verhaeltniszahl
        decimal_part = exact_mandate - int(exact_mandate)
        initial_seats = round(exact_mandate)
        initial_total += initial_seats
        
        district_calculations.append({
            'district': district['district'],
            'name': district['name'],
            'exact': exact_mandate,
            'decimal': decimal_part,
            'seats': initial_seats,
            'value': value
        })
    
    # Adjust seats to match state total
    while initial_total != state_seats:
        if initial_total < state_seats:
            # Need to add seats - sort by decimal part descending
            candidates = sorted(district_calculations, key=lambda x: x['decimal'], reverse=True)
            for calc in candidates:
                if calc['seats'] < math.ceil(calc['exact']):
                    calc['seats'] += 1
                    initial_total += 1
                    break
        else:
            # Need to remove seats - sort by decimal part ascending
            candidates = sorted(district_calculations, key=lambda x: x['decimal'])
            for calc in candidates:
                if calc['seats'] > math.floor(calc['exact']):
                    calc['seats'] -= 1
                    initial_total -= 1
                    break
        
        # Safety check to prevent infinite loop
        if not any(c['seats'] < math.ceil(c['exact']) for c in district_calculations) and initial_total < state_seats:
            # Force increment the one with highest decimal if we need more seats
            district_calculations[0]['seats'] += 1
            initial_total += 1
        elif not any(c['seats'] > math.floor(c['exact']) for c in district_calculations) and initial_total > state_seats:
            # Force decrement the one with lowest decimal if we need fewer seats
            district_calculations[-1]['seats'] -= 1
            initial_total -= 1
    
    return district_calculations

def calculate_state_wahlzahl(results, state_name, state_seats, vote_type):
    # Calculate total votes in state
    state_total_votes = 0
    for district in results:
        if district['state'] == state_name and 'party_results' in district:
            for party, result in district['party_results'].items():
                # Try list votes first, fall back to member votes if list doesn't exist
                votes = result.get(vote_type, 0)
                state_total_votes += votes
    
    # Calculate Wahlzahl
    return state_total_votes / state_seats if state_seats > 0 else 0

def calculate_seats(results, states, total_seats, participating_parties):
    print("\nAustrian National Council Election Calculation")
    print("==========================================\n")
    print("The Austrian National Council (Nationalrat) consists of 183 seats.")
    print("The election uses a three-level proportional representation system:")
    print("1. Regional constituency level (Regionalwahlkreise)")
    print("2. State level (Landeswahlkreise)")
    print("3. Federal level (Bundesebene)\n")
    
    # Determine whether to use list or member votes
    use_list_votes = False
    for district in results:
        if 'party_results' in district:
            for result in district['party_results'].values():
                if 'list' in result:
                    use_list_votes = True
                    break
            if use_list_votes:
                break
    
    vote_type = 'list' if use_list_votes else 'member'
    print(f"Using {vote_type} votes for calculations\n")
    
    # Step 0: Calculate total votes and which parties are over 4%
    party_total_votes = {}
    total_votes = 0
    
    for district in results:
        if 'party_results' not in district:
            continue
        for party, result in district['party_results'].items():
            # Try list votes first, fall back to member votes if list doesn't exist
            votes = result.get(vote_type, 0)
            if party not in party_total_votes:
                party_total_votes[party] = 0
            party_total_votes[party] += votes
            total_votes += votes
    
    threshold = total_votes * 0.04
    qualified_parties = {party: votes for party, votes in party_total_votes.items() 
                       if votes >= threshold}
    
    print("Initial Vote Count and 4% Threshold Check")
    print("---------------------------------------")
    print(f"Total valid votes cast: {total_votes:,}")
    print(f"4% threshold: {threshold:,.0f} votes")
    print("\nParty Results:")
    for party, votes in sorted(party_total_votes.items(), key=lambda x: x[1], reverse=True):
        percentage = (votes / total_votes) * 100
        status = "qualified" if votes >= threshold else "did not qualify"
        print(f"{party}: {votes:,} votes ({percentage:.2f}%) - {status}")
        if votes >= threshold:
            print("   → Qualifies for mandate distribution at all levels")
        else:
            print("   → Can only receive direct mandates in regional constituencies")
    
    print("\nState Mandate Distribution")
    print("------------------------")
    print("According to §1 of the Nationalrats-Wahlordnung, the 183 seats")
    print("are distributed among the states based on their citizen population.")
    
    total_population = sum(state['population'] for state in states.values())
    verhaeltniszahl = total_population / total_seats
    print(f"\nTotal citizen population: {total_population:,}")
    print(f"Verhältniszahl (citizens per mandate): {verhaeltniszahl:,.2f}")
    
    state_seats = {}
    total_predefined_seats = 0
    states_needing_calculation = []
    
    # First, handle states with predefined mandates
    for state_name, state_data in states.items():
        if 'mandates' in state_data:
            state_seats[state_name] = state_data['mandates']
            total_predefined_seats += state_data['mandates']
        else:
            states_needing_calculation.append(state_name)
    
    # Then calculate remaining seats for states without predefined mandates
    if states_needing_calculation:
        remaining_seats = total_seats - total_predefined_seats
        remaining_population = sum(states[state]['population'] for state in states_needing_calculation)
        remaining_verhaeltniszahl = remaining_population / remaining_seats
        
        print("\nCalculating state mandates using Hare quota method:")
        # Calculate seats for remaining states
        for state_name in states_needing_calculation:
            population = states[state_name]['population']
            exact_seats = population / remaining_verhaeltniszahl
            seats = round(exact_seats)
            state_seats[state_name] = seats
            print(f"{state_name}:")
            print(f"  Population: {population:,}")
            print(f"  Exact quota: {exact_seats:.3f}")
            print(f"  Allocated seats: {seats}")
    
    print("\nFinal State Mandate Distribution:")
    print("--------------------------------")
    for state_name, seats in sorted(state_seats.items()):
        source = "predefined" if 'mandates' in states[state_name] else "calculated by population"
        print(f"{state_name}: {seats} seats ({source})")
    
    # Step 1: First Ermittlungsverfahren - Regional Level
    party_seats = {party: 0 for party in party_total_votes.keys()}
    direct_mandate_parties = set()
    
    print("\nFirst Ermittlungsverfahren - Regional Level")
    print("----------------------------------------")
    print("In the first phase, mandates are distributed in the regional constituencies.")
    print("A party can receive a 'Grundmandat' (basic mandate) if it reaches the")
    print("Wahlzahl (electoral quotient) in a regional constituency.")
    print("The Wahlzahl is calculated by dividing total valid votes by available seats.")
    
    for district in results:
        state = district['state']
        state_wahlzahl = calculate_state_wahlzahl(results, state, state_seats[state], vote_type)
        
        if 'party_results' in district:
            print(f"\nAnalyzing {district['name']} ({state})")
            print(f"Wahlzahl: {state_wahlzahl:,.2f}")
            
            for party, result in district['party_results'].items():
                # Try list votes first, fall back to member votes if list doesn't exist
                votes = result.get(vote_type, 0)
                if votes > 0:
                    print(f"{party}: {votes:,} votes")
                    if votes >= state_wahlzahl:
                        seats = int(votes / state_wahlzahl)
                        if seats > 0:
                            party_seats[party] += seats
                            direct_mandate_parties.add(party)
                            print(f"  → Receives {seats} direct mandate(s)")
                            if party not in qualified_parties:
                                print(f"  → This allows {party} to participate in further distributions")
                                print(f"     despite being below the 4% threshold")
                    else:
                        print(f"  → Below Wahlzahl, no direct mandate")
    
    # Step 2: Second Ermittlungsverfahren - State Level
    print("\nSecond Ermittlungsverfahren - State Level")
    print("---------------------------------------")
    print("In the second phase, remaining mandates are distributed at the state level")
    print("using the same Wahlzahl as in the first phase. Only parties that either:")
    print("  a) Received at least one Grundmandat, or")
    print("  b) Reached the 4% threshold nationally")
    print("participate in this distribution.")
    
    for state_name in state_seats:
        state_wahlzahl = calculate_state_wahlzahl(results, state_name, state_seats[state_name], vote_type)
        state_party_votes = {}
        
        # Sum up votes for each party in this state
        for district in results:
            if district['state'] == state_name and 'party_results' in district:
                for party, result in district['party_results'].items():
                    if party in qualified_parties or party in direct_mandate_parties:
                        if party not in state_party_votes:
                            state_party_votes[party] = 0
                        # Try list votes first, fall back to member votes if list doesn't exist
                        votes = result.get(vote_type, 0)
                        state_party_votes[party] += votes
        
        # Calculate seats for each party
        print(f"\n{state_name}:")
        print(f"State Wahlzahl: {state_wahlzahl:,.2f}")
        for party, votes in state_party_votes.items():
            total_possible_seats = int(votes / state_wahlzahl)
            current_seats = party_seats[party]
            new_seats = total_possible_seats - current_seats
            if new_seats > 0:
                print(f"{party}:")
                print(f"  Total votes: {votes:,}")
                print(f"  Total possible seats: {total_possible_seats}")
                print(f"  Already has {current_seats} seats from first phase")
                print(f"  Receives {new_seats} additional seats")
                party_seats[party] += new_seats
            elif votes > 0:
                print(f"{party}:")
                print(f"  Total votes: {votes:,}")
                print(f"  No additional seats (already has {current_seats} seats)")
    
    # Step 3: Third Ermittlungsverfahren - Federal Level using D'Hondt method
    used_seats = sum(party_seats.values())
    remaining_seats = total_seats - used_seats
    
    print(f"\nThird Ermittlungsverfahren - Federal Level")
    print(f"----------------------------------------")
    print("The third and final phase uses the D'Hondt method to distribute")
    print("all 183 mandates at the federal level. This ensures proportional")
    print("representation according to the nationwide vote totals.")
    
    print(f"\nCurrent status:")
    print(f"- Mandates distributed in first two phases: {used_seats}")
    print(f"- Remaining mandates to distribute: {remaining_seats}")
    
    eligible_parties = set(qualified_parties.keys()) | direct_mandate_parties
    
    print("\nEligible parties for federal distribution:")
    for party in sorted(eligible_parties):
        print(f"- {party}: {party_total_votes[party]:,} total votes")
        if party in direct_mandate_parties and party not in qualified_parties:
            print("  → Qualified through direct mandate")
        else:
            print("  → Qualified through 4% threshold")
    
    print("\nD'Hondt distribution sequence:")
    print("Each mandate is assigned to the party with the highest quotient,")
    print("calculated as: total votes ÷ (current seats + 1)")
    
    while remaining_seats > 0:
        # Calculate quotients for each party
        quotients = {party: party_total_votes[party] / (party_seats[party] + 1)
                    for party in eligible_parties}
        
        # Find party with highest quotient
        winner = max(quotients.items(), key=lambda x: x[1])[0]
        winning_quotient = quotients[winner]
        
        # Show calculation details
        print(f"\nMandate {total_seats - remaining_seats + 1}:")
        print(f"  Goes to: {winner}")
        print(f"  Calculation: {party_total_votes[winner]:,} ÷ {party_seats[winner] + 1}")
        print(f"  Quotient: {winning_quotient:,.2f}")
        
        # Show next highest quotients for context
        sorted_quotients = sorted([(p, q) for p, q in quotients.items() if p != winner],
                                 key=lambda x: x[1], reverse=True)[:2]
        print("  Next highest quotients:")
        for party, quotient in sorted_quotients:
            print(f"    {party}: {quotient:,.2f}")
        
        # Assign the mandate
        party_seats[winner] += 1
        remaining_seats -= 1
    
    print("\nFinal Mandate Distribution")
    print("------------------------")
    print("The final distribution reflects both direct mandates and proportional")
    print("representation across all three levels of the electoral system.\n")
    
    for party, seats in sorted(party_seats.items(), key=lambda x: x[1], reverse=True):
        if seats > 0:  # Only show parties that got seats
            vote_share = (party_total_votes[party] / total_votes) * 100
            seat_share = (seats / total_seats) * 100
            print(f"{party}:")
            print(f"  Mandates: {seats} ({seat_share:.2f}% of seats)")
            print(f"  Votes: {party_total_votes[party]:,} ({vote_share:.2f}% of votes)")
            if party in direct_mandate_parties and party not in qualified_parties:
                print(f"  Note: Qualified through direct mandate")
            elif party in qualified_parties:
                print(f"  Note: Qualified through 4% threshold")
    
    # Create Party objects for all parties that received votes
    party_metadata = {p['short_name']: p for p in participating_parties}
    
    parties = []
    for party, votes in party_total_votes.items():
        metadata = party_metadata.get(party, {'color': '', 'left_to_right': 0})
        parties.append(Party(
            name=party,
            color=metadata['color'],
            size=party_seats.get(party, 0),  # 0 seats if party didn't get any
            left_to_right=metadata['left_to_right'],
            votes=votes
        ))
    
    return parties

if __name__ == "__main__":
    import json
    
    # Load the data from austria2024 folder
    with open(os.path.join('austria2024', 'participating_parties.json'), 'r', encoding='utf-8') as f:
        participating_parties = json.load(f)
        
    with open(os.path.join('austria2024', 'voting_district_results.json'), 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    with open(os.path.join('austria2024', 'states.json'), 'r', encoding='utf-8') as f:
        states = json.load(f)
    
    # Calculate seats distribution (183 seats total)
    total_seats = 183
    parties = calculate_seats(results, states, total_seats, participating_parties)
    
    print("\nParties in Parliament:")
    print("--------------------")
    for party in sorted(parties, key=lambda p: p.votes, reverse=True):
        if party.size > 0:  # Only show parties that got seats
            print(f"{party.name}:")
            print(f"  Votes: {party.votes:,}")
            print(f"  Color: {party.color}")
            print(f"  Seats: {party.size}")
            print(f"  Left-Right Position: {party.left_to_right}")
