import pytest
import os
import sys

# Add the parent directory to the Python path so we can import the main module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import calculate_election_results

def test_invalid_election():
    """Test handling of invalid election ID."""
    with pytest.raises(Exception):  # Should raise some kind of exception
        calculate_election_results("nonexistent_election", ["uk"])

def test_invalid_appointment():
    """Test handling of invalid appointment."""
    results = calculate_election_results("germany2021", ["nonexistent_appointment"])
    assert "nonexistent_appointment" not in results

def test_uk2024_uk_appointment():
    """Test UK 2024 election with UK appointment method."""
    # Test inputs
    election_id = "uk2024"
    appointments = ["uk"]
    
    # Calculate results
    results = calculate_election_results(election_id, appointments)
    
    # Basic assertions
    assert results is not None
    assert "uk" in results
    
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

def test_austria2024_austria_appointment():
    """Test Austrian 2024 election with Austrian appointment method."""
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
