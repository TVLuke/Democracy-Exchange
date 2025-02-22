"""Austrian Election System Tests

This test suite verifies the Austrian election system calculations:
1. Proportional representation system
2. National threshold handling
3. Regional party calculations
"""

import pytest
import os
import sys

# Add the parent directory to the Python path so we can import the main module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import calculate_election_results

def test_austria2024_seat_distribution():
    """Test Austrian 2024 election with proportional representation."""
    # Test inputs
    election_id = "austria2024"
    appointments = ["austria"]
    
    # Calculate results
    results = calculate_election_results(election_id, appointments)
    
    # Basic assertions
    assert results is not None
    assert "austria" in results
    
    austria_result = results["austria"]
    
    # Expected seat distribution
    expected_seats = {
        'FPÖ': 57,
        'ÖVP': 51,
        'SPÖ': 41,
        'NEOS': 18,
        'GRÜNE': 16
    }
    
    # Check if each party got the expected number of seats
    for party_name, expected_seat_count in expected_seats.items():
        party = next((p for p in austria_result["calculated_parties"] if p.name == party_name), None)
        assert party is not None, f"Party {party_name} not found in results"
        assert party.size == expected_seat_count, \
            f"Expected {expected_seat_count} seats for {party_name}, but got {party.size}"
