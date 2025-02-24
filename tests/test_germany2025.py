"""German 2025 Election System Tests

This test suite verifies the German election system calculations
using data from the 2025 election.
"""

import pytest
import os
import sys

# Add the parent directory to the Python path so we can import the main module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import calculate_election_results

def test_germany2025_seat_distribution():
    """Test German 2025 election seat distribution."""
    # Test inputs
    election_id = "germany2025"
    appointments = ["germany"]
    
    # Calculate results
    results, process = calculate_election_results(election_id, appointments)
    
    # Basic assertions
    assert results is not None
    assert "germany" in results
    
    germany_result = results["germany"]
    
    # Expected seat distribution for 2025 election
    expected_seats = {
        'CDU/CSU': 208,
        'AfD': 152,
        'SPD': 120,
        'GRÜNE': 85,
        'Die Linke': 64,
        'SSW': 1
    }
    
    # Print total seats
    total_seats = sum(party.size for party in germany_result["calculated_parties"])
    print(f"\nTotal seats in parliament: {total_seats}")
    
    print("\nSeat distribution differences:")
    print("-" * 50)
    print(f"{'Party':<15} {'Expected':>8} {'Actual':>8} {'Diff':>8}")
    print("-" * 50)
    
    # Check if each party got the expected number of seats
    all_correct = True
    for party_name, expected_seat_count in expected_seats.items():
        party = next((p for p in germany_result["calculated_parties"] if p.name == party_name), None)
        assert party is not None, f"Party {party_name} not found in results"
        
        actual_seats = party.size
        diff = actual_seats - expected_seat_count
        diff_str = f"{diff:+d}" if diff != 0 else "0"
        
        print(f"{party_name:<15} {expected_seat_count:>8d} {actual_seats:>8d} {diff_str:>8}")
        
        if actual_seats != expected_seat_count:
            all_correct = False
    
    print("-" * 50)
    
    # Verify total number of seats
    assert total_seats == 630, f"Expected 630 total seats, got {total_seats}"
    assert all_correct, "Seat distribution does not match expected values"
