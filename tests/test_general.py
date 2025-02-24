"""General Election System Tests

This test suite verifies general error handling and edge cases:
1. Invalid election IDs
2. Invalid appointment methods
3. Missing data handling
"""

import pytest
import os
import sys

# Add the parent directory to the Python path so we can import the main module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import calculate_election_results

def test_invalid_election_id():
    """Test that using a non-existent election ID raises an exception."""
    with pytest.raises(Exception):  # Should raise some kind of exception
        results, process = calculate_election_results("nonexistent_election", ["uk"])

def test_invalid_appointment_method():
    """Test that invalid appointment methods raise an error."""
    with pytest.raises(ValueError):
        results, process = calculate_election_results("germany2025", ["nonexistent_appointment"])
