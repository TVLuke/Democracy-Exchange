#!/usr/bin/env python3
import csv
import json
import os
from typing import Dict, List

def extract_party_columns(header: List[str]) -> List[str]:
    """Extract party columns from the CSV header."""
    majority_idx = header.index('Majority')
    other_winner_idx = header.index('Of which other winner')
    return header[majority_idx + 1:other_winner_idx]

def create_voting_district_results(csv_file: str, output_file: str):
    """Convert UK election CSV data to voting district results JSON format."""
    districts = []
    district_counter = 1
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        party_columns = extract_party_columns(reader.fieldnames)
        
        for row in reader:
            # Create district entry
            district = {
                "district": district_counter,
                "name": row['Constituency name'],
                "state": row['Region name'],  # Using region as state equivalent
                "population": None,  # Not available in UK data
                "electorate": int(row['Electorate']),
                "party_results": {}
            }
            
            # Add results for each party
            ind_votes = 0
            first_party = None
            max_votes = 0
            max_party = None
            
            # Check if this is the Speaker's seat
            first_party_col = row.get('First party', '')
            if first_party_col == 'Spk':
                district["party_results"]['Spk'] = {
                    "member": int(row['Of which other winner']) if row.get('Of which other winner') else 1  # Get actual Speaker votes if available
                }
                # Add other parties' votes but don't count them for max_votes
                for party in party_columns:
                    if party != 'All other candidates':
                        votes = row.get(party, '0')
                        if votes and votes.strip() != '':
                            votes_int = int(votes)
                            district["party_results"][party] = {
                                "member": votes_int
                            }
            else:
                # Process all regular parties first
                for party in party_columns:
                    if party != 'All other candidates':
                        votes = row.get(party, '0')
                        if votes and votes.strip() != '':
                            votes_int = int(votes)
                            if votes_int > max_votes:
                                max_votes = votes_int
                                max_party = party
                            if first_party is None and votes_int > 0:
                                first_party = party
                            district["party_results"][party] = {
                                "member": votes_int
                            }
                
                # Handle independent and TUV votes
                ind_votes = int(row.get('All other candidates', '0'))
                if ind_votes > 0:
                    # Check if this was an Independent or TUV win
                    result = row.get('Result', '')
                    if first_party_col == 'Ind' or 'Ind gain' in result:
                        # Independent win
                        district["party_results"]['Ind'] = {
                            "member": ind_votes
                        }
                    elif first_party_col == 'TUV' or 'TUV gain' in result:
                        # TUV win
                        tuv_votes = int(row.get('Of which other winner', '0'))
                        district["party_results"]['TUV'] = {
                            "member": tuv_votes
                        }
                        # Add remaining independent votes
                        remaining_ind = ind_votes - tuv_votes
                        if remaining_ind > 0:
                            district["party_results"]['Ind'] = {
                                "member": remaining_ind
                            }
                    else:
                        # Split the votes only if Ind wasn't listed as first party
                        if ind_votes > max_votes:
                            votes_ind1 = ind_votes // 2
                            votes_ind2 = ind_votes - votes_ind1
                            district["party_results"]['Ind1'] = {
                                "member": votes_ind1
                            }
                            district["party_results"]['Ind2'] = {
                                "member": votes_ind2
                            }
                        else:
                            district["party_results"]['Ind'] = {
                                "member": ind_votes
                            }
            
            districts.append(district)
            district_counter += 1
    
    # Write to JSON file
    with open(output_file, 'w') as f:
        json.dump(districts, f, indent=2)
    
    print(f"Created {output_file} with {len(districts)} districts")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(script_dir, "HoC-GE2024-results-by-constituency.csv")
    output_file = os.path.join(script_dir, "voting_district_results.json")
    
    create_voting_district_results(csv_file, output_file)
