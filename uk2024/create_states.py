#!/usr/bin/env python3
import csv
import json
import os
from collections import defaultdict

def calculate_populations(population_csv: str) -> tuple[dict, dict]:
    """Calculate total population for each region and constituency from age bands data."""
    region_populations = defaultdict(int)
    constituency_populations = defaultdict(int)
    seen_con_age = set()  # Track unique (constituency, age) combinations
    seen_region_age = set()  # Track unique (region, age) combinations
    
    with open(population_csv, 'r') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            region = row['rn_name']
            constituency = row['con_name']
            age = row['age']
            
            # Add the population for this age band
            population = float(row['con_number'].replace(',', '.'))  # Handle decimal comma
            
            # For constituencies, only count each age band once
            con_age_key = (constituency, age)
            if con_age_key not in seen_con_age:
                constituency_populations[constituency] += int(population)
                seen_con_age.add(con_age_key)
            
            # For regions, handle each age band once
            region_age_key = (region, age)
            if row['nat_name'] == 'Northern Ireland':
                # For Northern Ireland, use national totals
                nat_age_key = ('Northern Ireland', age)
                if nat_age_key not in seen_region_age:
                    nat_number = float(row['nat_number'].replace(',', '.'))  # Handle decimal comma
                    region_populations['Northern Ireland'] += int(nat_number)
                    seen_region_age.add(nat_age_key)
            elif row['rn_number']:  # If we have a regional number, use that
                if region_age_key not in seen_region_age:
                    rn_number = float(row['rn_number'].replace(',', '.'))  # Handle decimal comma
                    region_populations[region] += int(rn_number)
                    seen_region_age.add(region_age_key)
            elif region == 'Scotland':  # For Scotland, sum up all constituency numbers
                region_populations[region] += int(population)  # Add all numbers, no need to track age bands
    
    return dict(region_populations), dict(constituency_populations)

def create_states_json(election_csv: str, population_csv: str, states_output: str, districts_output: str):
    """Create states.json and update voting_district_results.json with population data."""
    states = defaultdict(lambda: {"name": "", "population": 0, "electorate": 0})
    
    # First get the regions from election data
    with open(election_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            region = row['Region name']
            states[region]["name"] = region
    
    # Calculate population data
    region_populations, constituency_populations = calculate_populations(population_csv)
    
    # Add population data to states
    for region, population in region_populations.items():
        if region in states:
            states[region]["population"] = population
    
    # Convert defaultdict to regular dict for JSON serialization
    states_dict = {k: dict(v) for k, v in states.items()}
    
    # Write states.json file
    with open(states_output, 'w') as f:
        json.dump(states_dict, f, indent=2)
    
    print(f"Created {states_output} with {len(states_dict)} states")
    
    # Update voting_district_results.json with population data
    with open(districts_output, 'r') as f:
        districts = json.load(f)
    
    # Add population to each district
    for district in districts:
        district_name = district['name']
        if district_name in constituency_populations:
            district['population'] = constituency_populations[district_name]
    
    # Write updated voting_district_results.json
    with open(districts_output, 'w') as f:
        json.dump(districts, f, indent=2)
    
    print(f"Updated {districts_output} with population data")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    election_csv = os.path.join(script_dir, "HoC-GE2024-results-by-constituency.csv")
    population_csv = os.path.join(script_dir, "population_by_age", "Age bands-Table 1.csv")
    states_output = os.path.join(script_dir, "states.json")
    districts_output = os.path.join(script_dir, "voting_district_results.json")
    
    create_states_json(election_csv, population_csv, states_output, districts_output)
