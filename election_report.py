#!/usr/bin/env python3

"""
Generate a detailed markdown report for election results.
This script creates a comprehensive analysis of election results including:
- Basic election statistics (turnout, population, etc.)
- Seat distribution
- Vote share vs seat share analysis
- Visual representations (graphs and charts)
"""

import os
from typing import Dict, List, Any
from datetime import datetime

def format_percentage(value: float) -> str:
    """Format a value as a percentage with 2 decimal places."""
    return f"{value:.2f}%"

def format_number(value: int) -> str:
    """Format a number with thousands separators."""
    return f"{value:,}"

def calculate_vote_share(party_votes: int, total_votes: int) -> float:
    """Calculate vote share as a percentage."""
    return (party_votes / total_votes) * 100 if total_votes > 0 else 0

def calculate_seat_share(party_seats: int, total_seats: int) -> float:
    """Calculate seat share as a percentage."""
    return (party_seats / total_seats) * 100 if total_seats > 0 else 0

def create_election_report(
    election_name: str,
    election_date: datetime,
    total_population: int,
    total_citizens: int,
    electorate_size: int,
    total_votes: int,
    party_results: List[Dict[str, Any]],
    total_seats: int,
    image_paths: Dict[str, str],
    alt_texts: Dict[str, str] = None,
    process: Dict[str, Any] = None,
    data_sources: List[Dict[str, str]] = None,
    appointment_data_sources: List[Dict[str, str]] = None
) -> str:
    """
    Create a markdown report for election results.
    
    Args:
        election_name: Name of the election (e.g., "UK General Election 2024")
        election_date: Date of the election
        total_population: Total population of the country
        electorate_size: Number of eligible voters
        total_votes: Total number of votes cast
        party_results: List of dictionaries containing party results
            Each dict should have:
            - name: Party name
            - votes: Number of votes received
            - seats: Number of seats won
        total_seats: Total number of seats in parliament
        image_paths: Dictionary of image paths
            Keys should be: 'parliament', 'vote_distribution', etc.
        process: Dictionary containing data about the election calculation process
        data_sources: List of dictionaries containing information about the electoral system
            Each dict should have:
            - name: Name of the data source
            - url: URL of the data source
        appointment_data_sources: List of dictionaries containing information about the specific election
            Each dict should have:
            - name: Name of the data source
            - url: URL of the data source
    
    Returns:
        str: Markdown formatted election report
    """
    # Calculate turnout
    turnout = (total_votes / electorate_size) * 100 if electorate_size > 0 else 0
    
    # Calculate percentages and discrepancies for each party
    for party in party_results:
        party['vote_share'] = calculate_vote_share(party['votes'], total_votes)
        party['seat_share'] = calculate_seat_share(party['seats'], total_seats) if total_seats > 0 else 0
        party['representation_gap'] = party['seat_share'] - party['vote_share']
    
    # Sort parties by number of seats (descending)
    party_results.sort(key=lambda x: x['seats'], reverse=True)
    
    # Generate markdown
    md = []
    
    # Header
    md.append(f"# {election_name}")
    md.append(f"Year: {election_date}")
    md.append("")
    
    # Basic Statistics
    md.append("## Election Statistics")
    
    # Add detailed statistics
    if total_population:
        md.append(f"- **Total Population**: {format_number(total_population)}")
    if total_citizens:
        md.append(f"- **Total Citizens**: {format_number(total_citizens)}")
    if electorate_size:
        md.append(f"- **Eligible Voters**: {format_number(electorate_size)}")
    if total_votes:
        md.append(f"- **Total Votes Cast**: {format_number(total_votes)}")
        md.append(f"- **Turnout**: {format_percentage(turnout)}")
    if total_seats > 0:
        md.append(f"- **Parliament Size**: {format_number(total_seats)} seats")
    md.append("")

    # Add vote summary if available
    if process and 'vote_summary' in process:
        md.append(process['vote_summary'])
        md.append("")
    
    # Add seat calculation explanation if available
    if process and 'seat_calculation' in process:
        md.append("## Seat Calculation Process")
        if isinstance(process['seat_calculation'], list):
            for step in process['seat_calculation']:
                # Split step into lines and add each line separately
                for line in step.split('\n'):
                    md.append(line)
                md.append("")
        else:
            md.append(process['seat_calculation'])
        md.append("")
    
    # Visualizations
    md.append("## Visualizations")
    if 'parliament' in image_paths:
        md.append("### Parliament Seating")
        alt_text = alt_texts.get('parliament') if alt_texts else "Parliament seating arrangement"
        md.append(f"![{alt_text}]({image_paths['parliament']})")
        md.append("")
    
    if 'coalitions' in image_paths:
        md.append("### Coalition Possibilities")
        alt_text = alt_texts.get('coalitions') if alt_texts else "Coalition possibilities"
        md.append(f"![{alt_text}]({image_paths['coalitions']})")
        md.append("")
    
    if 'vote_seat_distribution' in image_paths:
        md.append("### Vote vs Seat Distribution")
        alt_text = alt_texts.get('vote_seat_distribution') if alt_texts else "Bar chart comparing vote and seat percentages"
        md.append(f"![{alt_text}]({image_paths['vote_seat_distribution']})")
        md.append("")
    
    if 'vote_distribution' in image_paths:
        md.append("### Party Vote Distribution")
        alt_text = alt_texts.get('vote_distribution') if alt_texts else "Bar chart showing vote percentages for each party"
        md.append(f"![{alt_text}]({image_paths['vote_distribution']})")
        md.append("")
    
    # Results Table
    md.append("## Detailed Results")
    md.append("| Party | Votes | Vote Share | Seats | Seat Share | Representation Gap |")
    md.append("|-------|--------|------------|-------|------------|-------------------|")
    
    for party in party_results:
        md.append(
            f"| {party['name']} | "
            f"{format_number(party['votes'])} | "
            f"{format_percentage(party['vote_share'])} | "
            f"{format_number(party['seats'])} | "
            f"{format_percentage(party['seat_share'])} | "
            f"{format_percentage(party['representation_gap'])} |"
        )
    
    md.append("")
    
    # Analysis section below
    
    # Analysis of Representation
    md.append("## Analysis of Representation")
    md.append("### Most Over-represented Parties")
    over_represented = sorted(party_results, key=lambda x: x['representation_gap'], reverse=True)[:3]
    for party in over_represented:
        md.append(f"- **{party['name']}**: +{format_percentage(party['representation_gap'])}")
    
    md.append("\n### Most Under-represented Parties")
    under_represented = sorted(party_results, key=lambda x: x['representation_gap'])[:3]
    for party in under_represented:
        md.append(f"- **{party['name']}**: {format_percentage(party['representation_gap'])}")
    
    # Add Sources section if data sources are provided
    print("DEBUG: Data sources:", data_sources)
    print("DEBUG: Appointment data sources:", appointment_data_sources)
    if data_sources or appointment_data_sources:
        md.append("\n## Sources")
        if data_sources:
            md.append("\n### Data Sources")
            for source in data_sources:
                md.append(f"- [{source['name']}]({source['url']})")
        if appointment_data_sources:
            md.append("\n### About the Electoral System")
            for source in appointment_data_sources:
                md.append(f"- [{source['name']}]({source['url']})")
    
    return "\n".join(md)

def main():
    """Example usage of the report generator."""
    # This is just an example - in practice, this data would come from your election calculation
    sample_data = {
        'election_name': "UK General Election 2024",
        'election_date': datetime(2024, 2, 15),
        'total_population': 67330000,
        'electorate_size': 47561000,
        'total_votes': 32560000,
        'party_results': [
            {'name': 'Labour', 'votes': 12500000, 'seats': 411},
            {'name': 'Conservative', 'votes': 10200000, 'seats': 121},
            # ... add other parties
        ],
        'total_seats': 650,
        'image_paths': {
            'parliament': 'images/parliament.png',
            'bar_chart': 'images/votes.png'
        }
    }
    
    report = create_election_report(**sample_data)
    
    # Write to file
    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 
                              f"election_report_{sample_data['election_date'].strftime('%Y%m%d')}.md")
    
    with open(output_file, 'w') as f:
        f.write(report)

if __name__ == "__main__":
    main()
