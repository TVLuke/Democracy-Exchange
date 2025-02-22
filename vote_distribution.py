import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def plot_vote_distribution(all_parties, calculated_parties, timestamp, vote_title, seat_title, output_dir, relevant_vote='list', voting_data=None):
    """Create bar graphs showing vote and seat percentages for parties.
    
    Args:
        all_parties: Dictionary of party data from participating_parties.json
        calculated_parties: List of Party objects that made it into parliament
        vote_title: Title for the vote percentage plot
        seat_title: Title for the vote vs seat percentage plot
        output_dir: Directory to save the plots
        relevant_vote: Type of vote to display ('list' or 'member')
        voting_data: List of voting district results containing vote type information
    """
    
    # Get total votes and seats
    total_votes_all = sum(party.votes for party in calculated_parties)
    total_seats = sum(party.size for party in calculated_parties)
    
    # First plot: Vote distribution including 'Other'
    vote_parties = []
    vote_percentages = []
    vote_colors = []
    
    # Add parties with seats first
    parliament_votes = 0
    for party in sorted(calculated_parties, key=lambda x: x.votes, reverse=True):
        if party.size > 0:  # If party has seats
            parliament_votes += party.votes
            vote_percentage = (party.votes / total_votes_all) * 100
            vote_parties.append(party.name)
            vote_percentages.append(vote_percentage)
            # Get color from all_parties dictionary
            party_data = next((p for p in all_parties if p['short_name'] == party.name), None)
            vote_colors.append(party_data['color'] if party_data else '#CCCCCC')
    
    # Calculate 'Other' as sum of votes from parties without seats
    other_votes = sum(party.votes for party in calculated_parties if party.size == 0)
    if other_votes > 0:
        other_percentage = (other_votes / total_votes_all) * 100
        vote_parties.append('Sonstige')
        vote_percentages.append(other_percentage)
        vote_colors.append('#CCCCCC')
    
    # Second plot: Vote vs Seat distribution (showing all parties with seats and parties > 1% votes)
    vs_parties = []
    vs_vote_percentages = []
    vs_seat_percentages = []
    vs_colors = []
    differences = []
    total_difference = 0  # Track total difference including parties not shown
    
    # Process each party
    for party in sorted(calculated_parties, key=lambda x: x.votes, reverse=True):
        vote_percentage = (party.votes / total_votes_all) * 100
        seat_percentage = (party.size / total_seats) * 100 if total_seats > 0 else 0
        difference = abs(vote_percentage - seat_percentage)
        total_difference += difference
        
        # Show parties that either have seats or have > 1% votes
        if party.size > 0 or vote_percentage > 1:
            vs_parties.append(party.name)
            vs_vote_percentages.append(vote_percentage)
            vs_seat_percentages.append(seat_percentage)
            differences.append(difference)
            # Get color from all_parties dictionary
            party_data = next((p for p in all_parties if p['short_name'] == party.name), None)
            vs_colors.append(party_data['color'] if party_data else '#CCCCCC')
    
    # Create the vote percentage plot
    plt.figure(figsize=(15, 8))
    bars = plt.bar(range(len(vote_parties)), vote_percentages, color=vote_colors)
    
    # Customize the plot
    plt.title(vote_title, pad=20, fontsize=14, fontweight='bold')
    plt.xlabel("Politische Parteien", fontsize=12)
    # Check for vote types in data
    has_member_votes = False
    has_list_votes = False
    if voting_data:
        for district in voting_data:
            if 'party_results' in district:
                for party_results in district['party_results'].values():
                    if 'member' in party_results:
                        has_member_votes = True
                    if 'list' in party_results:
                        has_list_votes = True
                    if has_member_votes and has_list_votes:
                        break
            if has_member_votes and has_list_votes:
                break
    
    # Simple vote type logic for first plot
    if relevant_vote == 'list':
        first_plot_type = "(Listenstimmen)" if has_list_votes else "(Mandatsstimmen)"
    else:  # relevant_vote == 'member'
        first_plot_type = "(Mandatsstimmen)" if has_member_votes else "(Listenstimmen)"
    
    # Detailed vote type logic for second plot
    if relevant_vote == 'list':
        if has_list_votes:
            second_plot_type = "(Listenstimmen)"
        elif has_member_votes:
            second_plot_type = "(Mandatsstimmen werden wie Listenstimmen gewertet)"
        else:
            second_plot_type = ""
    else:  # relevant_vote == 'member'
        if has_member_votes:
            second_plot_type = "(Mandatsstimmen)"
        elif has_list_votes:
            second_plot_type = "(Listenstimmen werden wie Mandatsstimmen gewertet)"
        else:
            second_plot_type = ""
    
    plt.ylabel(f"Stimmenanteil in Prozent {first_plot_type}", fontsize=12)
    
    # Set x-axis labels with better spacing
    plt.xticks(range(len(vote_parties)), vote_parties, rotation=45, ha='right', fontsize=10)
    
    # Add percentage labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom',
                fontsize=10,
                fontweight='bold')
    
    # Add grid for better readability
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Set y-axis to go from 0 to max percentage + some padding
    max_percentage = max(vote_percentages)
    plt.ylim(0, max_percentage * 1.1)  # Add 10% padding
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout(rect=[0, 0, 1, 1])
    
    # Save the plot
    vote_dist_file = os.path.join(output_dir, f'{timestamp}_vote_distribution.png')
    plt.savefig(vote_dist_file, bbox_inches='tight', dpi=300)
    plt.close()
    
    # Create the vote vs seat percentage plot
    plt.figure(figsize=(15, 8))
    
    # Plot vote percentages slightly behind and to the right
    bar_width = 0.35
    vote_bars = plt.bar([i + bar_width/3 for i in range(len(vs_parties))], 
                       vs_vote_percentages, 
                       bar_width, 
                       color=[adjust_color_alpha(c, 0.6) for c in vs_colors],
                       label='Stimmen')
    
    # Plot seat percentages
    seat_bars = plt.bar(range(len(vs_parties)), 
                       vs_seat_percentages, 
                       bar_width, 
                       color=vs_colors,
                       label='Sitze')
    
    # Customize the plot
    plt.title(seat_title, pad=20, fontsize=14, fontweight='bold')
    plt.xlabel("Politische Parteien", fontsize=12)
    plt.ylabel(f"Prozent {second_plot_type}", fontsize=12)
    
    # Set x-axis labels
    plt.xticks(range(len(vs_parties)), vs_parties, rotation=45, ha='right', fontsize=10)
    
    # Add difference labels above bars
    for i, (vote_bar, seat_bar, diff) in enumerate(zip(vote_bars, seat_bars, differences)):
        height = max(vote_bar.get_height(), seat_bar.get_height())
        plt.text(i + bar_width/2, height,
                f'Δ{diff:.1f}%',
                ha='center', va='bottom',
                fontsize=10,
                fontweight='bold')
    
    # Add total difference and footnote at the bottom
    plt.figtext(0.5, -0.08,
                f'Gesamte Stimmen-Sitze-Differenz: {total_difference:.1f}%',
                ha='center', va='bottom',
                fontsize=12,
                fontweight='bold')
    
    # Find party with biggest difference among shown parties
    max_diff_idx = np.argmax(differences)
    max_diff_party = vs_parties[max_diff_idx]
    vote_pct = vs_vote_percentages[max_diff_idx]
    seat_pct = vs_seat_percentages[max_diff_idx]
    
    # Fußnote mit Beispiel zur Gesamtdifferenz hinzufügen
    example_text = f"Zum Beispiel erhielt {max_diff_party} {vote_pct:.1f}% der Stimmen, aber {seat_pct:.1f}% der Sitze, "
    example_text += f"eine Differenz von {differences[max_diff_idx]:.1f}%."
    
    plt.figtext(0.5, -0.12,
                f'Hinweis: Dieser Wert stellt die Summe der absoluten Differenzen zwischen Stimmen- und Sitzanteilen aller Parteien dar.\n'
                f'Der Übersichtlichkeit halber werden nur Parteien mit mehr als 1% der Stimmen in der Grafik gezeigt. {example_text}',
                ha='center', va='bottom',
                fontsize=9,
                style='italic')
    
    # Add legend
    plt.legend()
    
    # Add grid for better readability
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Set y-axis to go from 0 to max percentage + some padding
    max_percentage = max(max(vs_vote_percentages), max(vs_seat_percentages))
    plt.ylim(0, max_percentage * 1.1)  # Add 10% padding
    
    # Adjust layout to prevent label cutoff and make room for footnote
    plt.tight_layout(rect=[0, 0.1, 1, 1])
    
    # Save the plot
    vote_seat_file = os.path.join(output_dir, f'{timestamp}_vote_seat_distribution.png')
    plt.savefig(vote_seat_file, bbox_inches='tight', dpi=300)
    plt.close()

def adjust_color_alpha(hex_color, alpha):
    """Passt den Alpha-Wert (Transparenz) einer Hex-Farbe an.
    
    Args:
        hex_color: Hex-Farbstring (z.B. '#FF0000')
        alpha: Alpha-Wert zwischen 0 und 1
        
    Returns:
        RGBA-Farbtupel
    """
    # Convert hex to RGB
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))
    # Return with alpha
    return (*rgb, alpha)
