"""UK Election System Tests

This test suite verifies the UK election system calculations:
1. First-past-the-post voting system
2. Speaker's seat allocation
3. Regional party representation
"""

import pytest
import os
import sys

# Add the parent directory to the Python path so we can import the main module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import calculate_election_results

def test_uk2024_seat_distribution():
    """Test UK 2024 election with first-past-the-post system."""
    # Test inputs
    election_id = "uk2024"
    appointments = ["uk"]
    
    # Calculate results
    results, process = calculate_election_results(election_id, appointments)
    
    # Basic assertions
    assert results is not None
    assert isinstance(results, dict), f"results should be a dict but is {type(results)}"
    assert "uk" in results.keys(), f"'uk' not found in results keys: {list(results.keys())}"
    
    uk_result = results["uk"]
    
    # Expected seat distribution based on the 2024 UK election results
    expected_seats = {
        'Lab': 411,  # Labour Party
        'Con': 121,  # Conservative Party
        'LD': 72,    # Liberal Democrats
        'SNP': 9,    # Scottish National Party
        'SF': 7,     # Sinn Féin
        'RUK': 5,    # Reform UK
        'DUP': 5,    # Democratic Unionist Party
        'Green': 4,  # Green Party
        'PC': 4,     # Plaid Cymru
        'SDLP': 2,   # Social Democratic & Labour Party
        'APNI': 1,   # Alliance Party of Northern Ireland
        'UUP': 1,    # Ulster Unionist Party
        'TUV': 1     # Traditional Unionist Voice
    }
    
    # Check if each party got the expected number of seats
    for party_name, expected_seat_count in expected_seats.items():
        party = next((p for p in uk_result["calculated_parties"] if p.name == party_name), None)
        assert party is not None, f"Party {party_name} not found in results"
        assert party.size == expected_seat_count, \
            f"Expected {expected_seat_count} seats for {party_name}, but got {party.size}"
