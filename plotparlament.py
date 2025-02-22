import os
from datetime import datetime
from itertools import combinations
import numpy as np
import matplotlib.pyplot as plt
from collections import namedtuple, defaultdict
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

from footer_utils import add_footer_and_logo

def calculate_radius(num_rows, initial_radius, radius_increment):
    """Calculate the radius for each row."""
    return [initial_radius + i * radius_increment for i in range(num_rows)]

def calculate_arc_lengths(radius):
    """Calculate the arc lengths for each radius."""
    return [r * np.pi for r in radius]

def calculate_deputies_per_row(num_deputies, arc_lengths, total_arc_length):
    """Calculate the number of deputies per row."""
    deputies_per_row = [int(num_deputies * (arc_length / total_arc_length)) for arc_length in arc_lengths]

    # Distribute the remaining deputies
    diff = num_deputies - sum(deputies_per_row)
    deputies_per_row[-1] += diff
    return deputies_per_row

def generate_points(num_rows, radii, deputies_per_row):
    """Generate the points for each deputy."""
    points = []
    for row in range(num_rows):
        radius = radii[row]
        num_deputies_row = deputies_per_row[row]
        angles = np.linspace(0, np.pi, num_deputies_row)  # Spread deputies across the semicircle
        x = radius * np.cos(angles)
        y = radius * np.sin(angles)
        for i in range(num_deputies_row):
            points.append((radius, angles[i], x[i], y[i]))
    return sorted(points, key=lambda x: x[1], reverse=True)


def main(num_rows, initial_radius, radius_increment, NUM_DEPUTIES):
    """Main function to generate deputies' positions."""
    radius = calculate_radius(num_rows, initial_radius, radius_increment)
    arc_lengths = calculate_arc_lengths(radius)
    total_arc_length = sum(arc_lengths)
    deputies_per_row = calculate_deputies_per_row(NUM_DEPUTIES, arc_lengths, total_arc_length)
    points = generate_points(num_rows, radius, deputies_per_row)

    Deputy = namedtuple('Deputy', ['x', 'y', 'radius', 'angle'])
    return [Deputy(x, y, radius, angle) for (radius, angle, x, y) in points]

def calculate_coalition_distance(parties):
    """Calculate the sum of absolute differences between left_to_right values of parties."""
    if len(parties) == 1:
        return 0
    
    total_distance = 0
    for i in range(len(parties)):
        for j in range(i + 1, len(parties)):
            total_distance += abs(parties[i].left_to_right - parties[j].left_to_right)
    return total_distance

def has_majority_subgroup(parties_combo, total_seats):
    """Check if any subgroup of the coalition already has a majority."""
    majority = total_seats / 2
    n = len(parties_combo)
    
    # Check all possible subgroups (except the full group)
    for size in range(1, n):
        for subgroup in combinations(parties_combo, size):
            seats = sum(party.size for party in subgroup)
            if seats > majority:
                return True
    return False

def find_possible_coalitions(parties, total_seats):
    """Find all possible coalitions of up to 4 parties that have a majority.
    Sort them by ideological distance (smallest first).
    Only include coalitions where no subgroup already has a majority."""
    majority = total_seats / 2
    coalitions = []
    
    # Filter out parties with 0 seats
    valid_parties = [p for p in parties if p.size > 0]
    
    # Check single party majorities
    for i in range(len(valid_parties)):
        seats = valid_parties[i].size
        if seats > majority:
            distance = calculate_coalition_distance([valid_parties[i]])
            coalitions.append(([valid_parties[i]], seats, distance))
    
    # Check two party coalitions
    for i in range(len(valid_parties)):
        for j in range(i + 1, len(valid_parties)):
            seats = valid_parties[i].size + valid_parties[j].size
            if seats > majority:
                parties_combo = [valid_parties[i], valid_parties[j]]
                distance = calculate_coalition_distance(parties_combo)
                coalitions.append((parties_combo, seats, distance))
    
    # Check three party coalitions
    for i in range(len(valid_parties)):
        for j in range(i + 1, len(valid_parties)):
            for k in range(j + 1, len(valid_parties)):
                seats = valid_parties[i].size + valid_parties[j].size + valid_parties[k].size
                if seats > majority:
                    parties_combo = [valid_parties[i], valid_parties[j], valid_parties[k]]
                    if not has_majority_subgroup(parties_combo, total_seats):
                        distance = calculate_coalition_distance(parties_combo)
                        coalitions.append((parties_combo, seats, distance))
    
    # Check four party coalitions
    for i in range(len(valid_parties)):
        for j in range(i + 1, len(valid_parties)):
            for k in range(j + 1, len(valid_parties)):
                for l in range(k + 1, len(valid_parties)):
                    seats = valid_parties[i].size + valid_parties[j].size + valid_parties[k].size + valid_parties[l].size
                    if seats > majority:
                        parties_combo = [valid_parties[i], valid_parties[j], valid_parties[k], valid_parties[l]]
                        if not has_majority_subgroup(parties_combo, total_seats):
                            distance = calculate_coalition_distance(parties_combo)
                            coalitions.append((parties_combo, seats, distance))
    
    # Sort by ideological distance (ascending) and take top 10
    return sorted(coalitions, key=lambda x: x[2])[:10]

def plot_coalition_parliament(coalition_parties, total_seats, num_rows, initial_radius, radius_increment, ax, title=None):
    """Eine einzelne Koalition im Parlamentsstil visualisieren."""
    # Parteien nach Links-Rechts-Wert sortieren
    coalition_parties = sorted(coalition_parties, key=lambda x: x.left_to_right)
    
    # Gesamtzahl der Koalitionssitze und verbleibende Sitze berechnen
    coalition_seats = sum(party.size for party in coalition_parties)
    remaining_seats = total_seats - coalition_seats
    majority = total_seats / 2
    
    # Punkte für das Parlamentslayout für alle Sitze generieren
    all_deputies = main(num_rows, initial_radius, radius_increment, total_seats)
    
    # Zuerst die leeren Sitze als hohle Punkte darstellen
    for deputy in all_deputies[coalition_seats:]:
        ax.scatter(deputy.x, deputy.y, s=12, facecolors='none', 
                  edgecolors='gray', alpha=0.3, linewidth=0.5)
    
    # Dann die Koalitionssitze darüber darstellen
    current_index = 0
    for party in coalition_parties:
        party_deputies = all_deputies[current_index:current_index + party.size]
        for deputy in party_deputies:
            ax.scatter(deputy.x, deputy.y, s=12, alpha=1, color=party.color)
        current_index += party.size
    
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Create title with coalition info
    if title:
        majority_percentage = (coalition_seats / total_seats) * 100
        remaining_text = f' (+{remaining_seats} needed)' if coalition_seats < majority else ''
        full_title = f"{title}\n{coalition_seats} seats ({majority_percentage:.1f}%){remaining_text}"
        ax.set_title(full_title, pad=8, fontsize=8)

def plot_coalitions(coalitions, total_seats, output_dir, timestamp, title=None):
    """Mögliche Koalitionen im Parlamentsstil visualisieren und als Datei speichern.
    
    Args:
        coalitions: Liste möglicher Koalitionen
        total_seats: Gesamtzahl der Sitze im Parlament
        output_dir: Verzeichnis zum Speichern der Grafik
        timestamp: Zeitstempel für eindeutigen Dateinamen
    """
    if not coalitions:
        return
    
    num_coalitions = len(coalitions)
    num_cols = min(5, num_coalitions)  # Maximum 5 coalitions per row
    num_rows = (num_coalitions + num_cols - 1) // num_cols
    
    # Create figure at 1080p resolution
    dpi = 100  # Standard screen DPI
    fig = plt.figure(figsize=(1920/dpi, 1080/dpi))
    
    # Add title with more space between lines
    plt.suptitle('Wahrscheinlichste Mehrheitskoalitionen\n(nach ideologischer Distanz)\n\n\n' + (title if title else 'Sitzverteilung im Parlament'), y=0.98, fontsize=12)
    
    # Adjust bottom margin based on number of rows
    bottom_margin = 0.45 if num_rows == 1 else 0.30
    
    # Enger Abstand zwischen Teilgrafiken, but leave space at bottom for explanation
    # For single row, push graphs much lower to avoid subtitle overlap
    top_margin = 0.75 if num_rows == 1 else 0.82
    plt.subplots_adjust(hspace=0.35, top=top_margin, bottom=bottom_margin, left=0.05, right=0.95)
    
    # Find first coalition with three parties for the example
    example_coalition = None
    for coalition, seats, distance in coalitions:
        if len(coalition) == 3:
            example_coalition = (coalition, distance)
            break
    if not example_coalition:
        # Fallback to first coalition if no three-party coalition exists
        example_coalition = (coalitions[0][0], coalitions[0][2])

    # Add explanation of ideological distance calculation at the bottom
    base_explanation = (
        'Die "Ideologische Distanz":\n'
        'Für die Darstellung in korrekter Reihenfolge hat jede Partei einen left_to_right-Wert, mit 1 für die Partei, welche üblicherweise im Parlament ganz links sitzt, dann aufsteigend:\n'
        'Dieser Wert wird hier auch einfach als Distanzwert gewertet, um wahrscheinliche Koalitionen darzustellen.\n'
        'Diese Berechnung ist natürlich stark vereinfachend und in vielen Fällen einfach falsch.\n\n'
    )

    if len(example_coalition[0]) == 1:
        # Single party with majority
        p1 = example_coalition[0][0]
        explanation = base_explanation + (
            f'Beispiel für eine Einzelpartei-Mehrheit ({p1.name}):\n'
            f'{p1.name}: left_to_right = {p1.left_to_right}\n'
            f'Ideologische Distanz = 0 (Einzelpartei)'
        )
    elif len(example_coalition[0]) == 2:
        # Two-party coalition
        p1, p2 = example_coalition[0]
        explanation = base_explanation + (
            f'Beispiel für die Koalition {p1.name}-{p2.name}:\n'
            f'{p1.name}: left_to_right = {p1.left_to_right}\n'
            f'{p2.name}: left_to_right = {p2.left_to_right}\n'
            f'Ideologische Distanz = |{p1.left_to_right}-{p2.left_to_right}| = {example_coalition[1]}'
        )
    else:
        # Three-party coalition
        p1, p2, p3 = example_coalition[0]
        explanation = base_explanation + (
            f'Beispiel für die Koalition {p1.name}-{p2.name}-{p3.name}:\n'
            f'{p1.name}: left_to_right = {p1.left_to_right}\n'
            f'{p2.name}: left_to_right = {p2.left_to_right}\n'
            f'{p3.name}: left_to_right = {p3.left_to_right}\n'
            f'Ideologische Distanz = |{p1.left_to_right}-{p2.left_to_right}| + |{p1.left_to_right}-{p3.left_to_right}| + |{p2.left_to_right}-{p3.left_to_right}| = '
            f'{example_coalition[1]}'
        )
    # Position text based on number of rows
    text_y = 0.15 if num_rows == 1 else 0.08
    plt.figtext(0.05, text_y, explanation, fontsize=10, ha='left', va='bottom')
    
    for i, (parties, seats, distance) in enumerate(coalitions):
        ax = plt.subplot(num_rows, num_cols, i + 1)
        
        # Sort parties by left_to_right value
        parties = sorted(parties, key=lambda x: x.left_to_right)
        
        # Create title with party names, seats info, and distance
        party_names = ' + '.join(f"{p.name}" for p in parties)
        title = f"{party_names}\nIdeological Distance: {distance:.2f}"
        
        # Plot the parliament-style visualization for this coalition
        plot_coalition_parliament(parties, total_seats, 5, 5, 0.6, ax, title)
    
    # Save coalitions plot
    coalitions_file = os.path.join(output_dir, f'{timestamp}_coalitions.png')
    # Add total seats information
    plt.figtext(0.5, 0.02, f'Sitze gesamt: {total_seats}',
                ha='center', va='bottom',
                fontsize=10,
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
    
    plt.savefig(coalitions_file, bbox_inches='tight', dpi=300)
    plt.close()
    
    # Add footer and logo to saved image
    add_footer_and_logo(coalitions_file)

def plot_deputies(deputies, parties, POINT_SIZE=200, output_dir=None, timestamp=None, title=None, relevant_vote='list', voting_data=None):
    """Plot the deputies on a chart and possible coalitions in separate figures.
    Save the plots as PNG files with timestamps.
    
    Args:
        deputies: List of deputies with positions
        parties: List of parties with their properties
        POINT_SIZE: Size of the points representing deputies
        output_dir: Directory to save the plots
        timestamp: Timestamp string for unique filenames
        title: Optional title for the plot
        relevant_vote: Type of vote to display ('list' or 'member')
        voting_data: List of voting district results containing vote type information
    """
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    total_seats = sum(party.size for party in parties)
    
    # Full parliament plot at 1080p resolution
    dpi = 100  # Standard screen DPI
    plt.figure(figsize=(1920/dpi, 1080/dpi))
    current_index = 0
    point_size = 200  # Increased point size for main parliament
    
    for party in sorted(parties, key=lambda x: x.left_to_right):
        party_deputies = deputies[current_index:current_index + party.size]
        color = party.color
        label = f"{party.name} ({party.size})"
        
        for deputy in party_deputies:
            if color == 'unassigned':
                plt.scatter(deputy.x, deputy.y, s=point_size, facecolors='none', 
                           edgecolors='grey', linewidth=0.75, label=label)
            else:
                plt.scatter(deputy.x, deputy.y, s=point_size, alpha=1, 
                           color=color, label=label)
            label = ""  # Only show label once per party
        current_index += party.size
    
    ax = plt.gca()
    ax.set_aspect('equal')
    ax.axis('off')
    

    
    if title:
        plt.title(title, pad=20, fontsize=14)
    
    # Adjusted legend position and columns based on number of parties
    num_parties = sum(1 for p in parties if p.size > 0)
    ncols = min(6, num_parties)  # At most 6 columns, but fewer if fewer parties
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), 
               ncol=ncols, frameon=False)
    
    # Add vote type explanation
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
    
    if relevant_vote == 'list':
        if has_list_votes:
            vote_type = "Hinweis: Verteilung nutzt nur Listenstimmen (Zweitstimmen)."
        elif has_member_votes:
            vote_type = "Hinweis: Mandatsstimmen (Erststimmen) werden (auch) wie Listenstimmen (Zweitstimmen) gewertet"
        else:
            vote_type = ""
    else:  # relevant_vote == 'member'
        if has_member_votes:
            vote_type = "Hinweis: Verteilung nutzt nur Mandatsstimmen (Erststimmen) ."
        elif has_list_votes:
            vote_type = "Hinweis: Listenstimmen (Zweitstimmen) werden (auch) wie Mandatsstimmen (Erststimmen) gewertet"
        else:
            vote_type = ""
    
    if vote_type:
        plt.figtext(0.5, -0.02, vote_type,
                    ha='center', va='bottom',
                    fontsize=10,
                    style='italic')
    
    # Add total seats information
    plt.figtext(0.95, 0.95, f'Sitze gesamt: {total_seats}',
                ha='right', va='top',
                fontsize=10,
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
    
    # First adjust layout
    plt.tight_layout()

    # Save parliament plot
    parliament_file = os.path.join(output_dir, f'{timestamp}_parliament.png')
    plt.savefig(parliament_file, bbox_inches='tight', dpi=300)
    plt.close()
    
    # Add footer and logo to saved image
    add_footer_and_logo(parliament_file)
    
    # Generate and save coalition plots if any exist
    coalitions = find_possible_coalitions(parties, total_seats)
    if coalitions:
        plot_coalitions(coalitions, total_seats, output_dir, timestamp, title)