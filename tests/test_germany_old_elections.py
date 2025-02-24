"""German Old Election System Tests

This test suite verifies the old German election system calculations
using data from the 2021 election.
"""

import pytest
import os
import sys

# Add the parent directory to the Python path so we can import the main module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import calculate_election_results

def test_germany2021_old_seat_distribution():
    """Test German 2021 election with old proportional representation."""
    # Test inputs
    election_id = "germany2021"
    appointments = ["germany_old"]
    
    # Calculate results
    results = calculate_election_results(election_id, appointments)
    
    # Basic assertions
    assert results is not None
    assert "germany_old" in results
    
    germany_old_result = results["germany_old"]
    
    # Expected seat distribution for 2021 election using old system
    expected_seats = {
        'DIE LINKE': 39,
        'SPD': 206,
        'GRÜNE': 118,
        'SSW': 1,
        'FDP': 91,
        'CDU/CSU': 197,
        'AfD': 83
    }
    
    # Print total seats
    total_seats = sum(party.size for party in germany_old_result["calculated_parties"])
    print(f"\nTotal seats in parliament: {total_seats}")
    
    print("\nSeat distribution differences:")
    print("-" * 50)
    print(f"{'Party':<15} {'Expected':>8} {'Actual':>8} {'Diff':>8}")
    print("-" * 50)
    
    # Check if each party got the expected number of seats
    all_correct = True
    for party_name, expected_seat_count in expected_seats.items():
        party = next((p for p in germany_old_result["calculated_parties"] if p.name == party_name), None)
        assert party is not None, f"Party {party_name} not found in results"
        
        actual_seats = party.size
        diff = actual_seats - expected_seat_count
        diff_str = f"{diff:+d}" if diff != 0 else "0"
        
        print(f"{party_name:<15} {expected_seat_count:>8d} {actual_seats:>8d} {diff_str:>8}")
        
        if actual_seats != expected_seat_count:
            all_correct = False
    
    print("-" * 50)
    assert all_correct, "Seat distribution does not match expected values"
