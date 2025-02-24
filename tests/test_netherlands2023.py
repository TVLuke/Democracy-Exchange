"""Netherlands 2023 Election System Tests

This test suite verifies the Netherlands election system calculations
using data from the 2023 election.
"""

import pytest
import os
import sys

# Add the parent directory to the Python path so we can import the main module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import calculate_election_results

def test_netherlands2023_seat_distribution():
    """Test Netherlands 2023 election seat distribution."""
    # Test inputs
    election_id = "netherlands2023"
    appointments = ["netherlands"]
    
    # Calculate results
    results, process = calculate_election_results(election_id, appointments)
    
    # Basic assertions
    assert results is not None
    assert "netherlands" in results
    
    netherlands_result = results["netherlands"]
    
    # Expected seat distribution for 2023 election
    expected_seats = {
        'PVV': 37,
        'GL-PvdA': 25,
        'VVD': 24,
        'NSC': 20,
        'D66': 9,
        'BBB': 7,
        'CDA': 5,
        'SP': 5,
        'DENK': 3,
        'PvdD': 3,
        'FVD': 3,
        'SGP': 3,
        'CU': 3,
        'Volt': 2,
        'JA21': 1
    }
    
    # Print total seats
    total_seats = sum(party.size for party in netherlands_result["calculated_parties"])
    print(f"\nTotal seats in parliament: {total_seats}")
    
    print("\nSeat distribution differences:")
    print("-" * 50)
    print(f"{'Party':<40} {'Expected':>8} {'Actual':>8} {'Diff':>8}")
    print("-" * 50)
    
    # Check if each party got the expected number of seats
    all_correct = True
    for party in netherlands_result["calculated_parties"]:
        party_name = party.name
        actual_seats = party.size
        expected = expected_seats.get(party_name, 0)
        diff = actual_seats - expected
        
        print(f"{party_name:<40} {expected:>8} {actual_seats:>8} {diff:>8}")
        
        if diff != 0:
            all_correct = False
            
    assert all_correct, "Seat distribution does not match expected results"
    
    # Verify total number of seats is 150
    assert total_seats == 150, f"Total seats should be 150, got {total_seats}"
