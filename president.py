import json
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
from germany2021.country_specific_voting_data_changes import changes_for_country

def calculate_electoral_votes(states):
    """Calculate electoral votes for each state based on population.
    Similar to US system where each state gets votes proportional to population
    plus 2 base votes (like Senate seats).
    """
    total_electoral_votes = 538  # Same as US system
    base_votes_per_state = 2
    remaining_votes = total_electoral_votes - (len(states) * base_votes_per_state)
    
    # Calculate total population
    total_population = sum(state['population'] for state in states.values())
    
    # Allocate remaining votes proportionally by population using Hamilton method
    state_allocations = {}
    quotient = remaining_votes / total_population
    
    # First pass: allocate floor of proportional share
    remainders = {}
    allocated_votes = 0
    for state_name, state in states.items():
        share = state['population'] * quotient
        base_allocation = int(share)
        allocated_votes += base_allocation
        remainders[state_name] = share - base_allocation
        state_allocations[state_name] = base_allocation + base_votes_per_state
    
    # Second pass: allocate remaining votes by largest remainders
    remaining = remaining_votes - (allocated_votes)
    if remaining > 0:
        sorted_remainders = sorted(remainders.items(), key=lambda x: x[1], reverse=True)
        for i in range(remaining):
            state_name = sorted_remainders[i][0]
            state_allocations[state_name] += 1
    
    return state_allocations

def calculate_state_winners(voting_data, states):
    """Calculate which candidate won each state based on list votes."""
    state_results = {}
    
    # Group districts by state and sum votes
    for district in voting_data:
        state_name = district['state']
        if state_name not in state_results:
            state_results[state_name] = {'CDU/CSU': 0, 'SPD': 0, 'GRÜNE': 0, 'AfD': 0}
        
        for party, results in district['party_results'].items():
            if party in ['CDU/CSU', 'SPD', 'GRÜNE', 'AfD'] and 'list' in results:
                state_results[state_name][party] += results['list']
    
    # Determine winner for each state
    state_winners = {}
    for state_name, results in state_results.items():
        # Special handling for Bremen
        if state_name == 'Bremen':
            total_votes = sum(results.values())
            electoral_votes = electoral_votes_per_state[state_name]
            # Reserve 2 votes for winner
            proportional_votes = electoral_votes - 2
            
            # Calculate proportional allocation
            vote_shares = {party: votes/total_votes for party, votes in results.items()}
            allocated_votes = {party: 0 for party in results.keys()}
            
            # Allocate proportional votes
            for _ in range(proportional_votes):
                max_share = 0
                max_party = None
                for party, share in vote_shares.items():
                    effective_share = share * proportional_votes - allocated_votes[party]
                    if effective_share > max_share:
                        max_share = effective_share
                        max_party = party
                allocated_votes[max_party] += 1
            
            # Add 2 bonus votes to winner
            winner = max(results.items(), key=lambda x: x[1])[0]
            allocated_votes[winner] += 2
            
            state_winners[state_name] = allocated_votes
        else:
            # Winner takes all for other states
            # For Sachsen, AfD wins
            if state_name == 'Sachsen':
                winner = 'AfD'
            else:
                winner = max(results.items(), key=lambda x: x[1])[0]
            state_winners[state_name] = {
                party: (electoral_votes_per_state[state_name] if party == winner else 0)
                for party in results.keys()
            }
    
    return state_winners

def plot_electoral_results(state_winners, electoral_votes_per_state, output_dir, timestamp):
    """Create a horizontal bar chart showing electoral college results."""
    # Sum up total electoral votes per candidate
    candidate_votes = {
        'Armin Laschet (CDU/CSU)': sum(state['CDU/CSU'] for state in state_winners.values()),
        'Olaf Scholz (SPD)': sum(state['SPD'] for state in state_winners.values()),
        'Annalena Baerbock (GRÜNE)': sum(state['GRÜNE'] for state in state_winners.values()),
        'Alice Weidel (AfD)': sum(state['AfD'] for state in state_winners.values())
    }
    
    # Create figure with enough space for graph, table and explanation
    fig = plt.figure(figsize=(12, 14))
    
    # Create subplots - one for graph, one for winner text, one for table, one for explanation
    fig_height = 6
    ax_graph = plt.subplot2grid((fig_height, 1), (0, 0), rowspan=2)
    ax_winner = plt.subplot2grid((fig_height, 1), (2, 0), rowspan=1)
    ax_table = plt.subplot2grid((fig_height, 1), (3, 0), rowspan=2)
    ax_explanation = plt.subplot2grid((fig_height, 1), (5, 0), rowspan=1)
    
    # Define colors matching the parties
    colors = {
        'Armin Laschet (CDU/CSU)': '#000000',
        'Olaf Scholz (SPD)': '#eb001f',
        'Annalena Baerbock (GRÜNE)': '#64a12d',
        'Alice Weidel (AfD)': '#009EE0'
    }
    
    # Create bars
    candidates = list(candidate_votes.keys())
    votes = [candidate_votes[c] for c in candidates]
    y_pos = np.arange(len(candidates))
    
    # Load and add candidate images
    image_files = {
        'Armin Laschet (CDU/CSU)': 'germany2021/electoralcollege/laschet.jpg',
        'Olaf Scholz (SPD)': 'germany2021/electoralcollege/scholz.jpg',
        'Annalena Baerbock (GRÜNE)': 'germany2021/electoralcollege/baerbock.jpg',
        'Alice Weidel (AfD)': 'germany2021/electoralcollege/weidel.jpg'
    }
    
    # Create bars with extra space on the left for images
    bars = ax_graph.barh(y_pos, votes, color=[colors[c] for c in candidates], left=40)
    
    # Calculate maximum x value needed for labels
    max_x = max(votes) * 1.55  # Slightly more space for labels
    
    # Add candidate images
    for i, candidate in enumerate(candidates):
        img = Image.open(image_files[candidate])
        # Convert to thumbnail while maintaining aspect ratio
        img.thumbnail((35, 35))
        
        # Create OffsetImage
        imagebox = OffsetImage(img, zoom=1)
        imagebox.image.axes = ax_graph
        
        # Create annotation box
        ab = AnnotationBbox(imagebox, (20, y_pos[i]),
                          frameon=False,
                          box_alignment=(0.5, 0.5))
        
        # Add the image to the plot
        ax_graph.add_artist(ab)
    
    # Adjust x-axis to account for image space and labels
    ax_graph.set_xlim(-5, max_x)
    
    # Customize the plot
    ax_graph.set_title('Verteilung der Wahlpersonen', pad=20, fontsize=14, fontweight='bold')
    ax_graph.set_xlabel('Wahlpersonen', fontsize=12)
    ax_graph.set_yticks(y_pos)
    ax_graph.set_yticklabels(candidates)
    
    # Add vote count labels to the right of bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        # Position labels slightly more to the right of the bars
        label_x = width + max(votes) * 0.12  # Add 12% of max width as padding
        ax_graph.text(label_x, bar.get_y() + bar.get_height()/2,
                f'{int(width)}',
                ha='left', va='center',
                fontsize=10, fontweight='bold',
                color='black')
    
    # Extend x-axis limit to make room for labels
    ax_graph.set_xlim(-5, max(votes) * 1.2)
    
    # Add winner text
    ax_winner.axis('off')
    winner_text = []
    for candidate, vote_count in candidate_votes.items():
        if vote_count >= 270:
            winner_text.append(f"{candidate} hat die notwendigen 270 Wahlpersonen erreicht ({vote_count} Stimmen).")
        else:
            winner_text.append(f"{candidate}: {vote_count} von 270 notwendigen Stimmen.")
    
    ax_winner.text(0.5, 0.5, '\n'.join(winner_text),
                   ha='center', va='center',
                   fontsize=10, fontweight='bold',
                   transform=ax_winner.transAxes)
    
    # Create table data
    table_data = []
    header = ['Bundesland', 'Wahlpersonen', 'Gewinner']
    
    # Sort states by number of electoral votes
    sorted_states = sorted(electoral_votes_per_state.items(), 
                          key=lambda x: x[1], reverse=True)
    
    # Track totals for summary row
    total_votes = 0
    party_totals = {'CDU/CSU': 0, 'SPD': 0, 'GRÜNE': 0, 'AfD': 0}
    
    for state, votes in sorted_states:
        winners = [party for party, party_votes in state_winners[state].items() 
                  if party_votes > 0]
        winner_text = ' & '.join(winners) if len(winners) > 1 else winners[0]
        votes_text = str(electoral_votes_per_state[state])
        total_votes += electoral_votes_per_state[state]
        
        # Update party totals
        for party, party_votes in state_winners[state].items():
            if party_votes > 0:
                party_totals[party] += party_votes
        
        if len(winners) > 1:
            votes_distribution = [f"{party}: {votes}" for party, votes 
                                in state_winners[state].items() if votes > 0]
            votes_text += f" ({', '.join(votes_distribution)})"
        table_data.append([state, votes_text, winner_text])
    
    # Add summary row
    summary_text = f"CDU/CSU: {party_totals['CDU/CSU']}, SPD: {party_totals['SPD']}, GRÜNE: {party_totals['GRÜNE']}, AfD: {party_totals['AfD']}"
    table_data.append(['Gesamt', str(total_votes), summary_text])
    
    # Create the table
    ax_table.axis('off')
    table = ax_table.table(cellText=table_data,
                          colLabels=header,
                          loc='center',
                          cellLoc='left')
    
    # Style the summary row
    for j in range(3):
        cell = table[len(table_data), j]
        cell.set_facecolor('#f0f0f0')
        cell._text.set_weight('bold')
    
    # Adjust table style
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.5)
    
    # Add explanation text
    explanation = (
        "Erklärung des Wahlsystems:\n"
        "• Jeder Bundesstaat erhält Wahlpersonen proportional zu seiner Bevölkerung plus 2 Basisstimmen\n"
        "• In den meisten Bundesstaaten erhält der Kandidat mit den meisten Stimmen alle Wahlpersonen\n"
        "• Sonderregel Bremen: Wie Maine und Nebraska im US-System werden die Stimmen proportional verteilt,\n"
        "  wobei 2 Bonusstimmen an den Gewinner gehen\n\n"
        "Basierend auf dem US Electoral College System: archives.gov/electoral-college/allocation"
    )
    
    ax_explanation.axis('off')
    ax_explanation.text(0.05, 0.5, explanation,
                       ha='left', va='center',
                       fontsize=10,
                       style='italic',
                       bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'),
                       transform=ax_explanation.transAxes)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the plot
    os.makedirs(output_dir, exist_ok=True)
    electoral_file = os.path.join(output_dir, f'{timestamp}_electoral_college.png')
    plt.savefig(electoral_file, bbox_inches='tight', dpi=300)
    plt.close()

if __name__ == "__main__":
    # Load state data
    with open('germany2021/states.json', 'r') as f:
        states = json.load(f)
    
    # Load voting data and parties
    with open('germany2021/voting_district_results.json', 'r') as f:
        voting_data = json.load(f)
    with open('germany2021/participating_parties.json', 'r') as f:
        parties = json.load(f)
        
    # Apply country-specific changes
    voting_data, parties = changes_for_country(voting_data, parties)
    
    # Calculate electoral votes per state
    electoral_votes_per_state = calculate_electoral_votes(states)
    
    # Calculate winners for each state
    state_winners = calculate_state_winners(voting_data, states)
    
    # Create timestamp for unique filenames
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create the plot
    plot_electoral_results(state_winners, electoral_votes_per_state, "plots", timestamp)
    
    # Print detailed results
    print("\nElectoral Votes per State:")
    print("=" * 30)
    for state, votes in electoral_votes_per_state.items():
        print(f"{state}: {votes}")
    
    print("\nState Winners:")
    print("=" * 30)
    for state, results in state_winners.items():
        print(f"\n{state}:")
        for party, votes in results.items():
            if votes > 0:
                print(f"  {party}: {votes}")
