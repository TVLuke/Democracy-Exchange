def changes_for_country(voting_data: list, parties: list) -> tuple[list, list]:
    """
    Modify the voting data to handle party name changes and vote aggregation.

    This function performs the following changes:
    1. Renames 'CDU' to 'CDU/CSU' and aggregates votes from 'CSU' into 'CDU/CSU'.
    2. Renames 'GRÜNE/B 90' to 'GRÜNE'.

    Args:
        voting_data (list): List of district voting results.

    Returns:
        list: Modified voting data with updated party names and aggregated votes.
    """
    for district in voting_data:
        party_results = district.get('party_results', {})
        
        # Handle CDU/CSU merge
        cdu_data = party_results.pop('CDU', {'member': 0, 'list': 0})
        csu_data = party_results.pop('CSU', {'member': 0, 'list': 0})
        
        # Combine votes and store under CDU/CSU if either party had votes
        if cdu_data.get('member', 0) > 0 or cdu_data.get('list', 0) > 0 or csu_data.get('member', 0) > 0 or csu_data.get('list', 0) > 0:
            party_results['CDU/CSU'] = {
                'member': cdu_data.get('member', 0) + csu_data.get('member', 0),
                'list': cdu_data.get('list', 0) + csu_data.get('list', 0)
            }
        
        # Handle GRÜNE name change
        if 'GRÜNE/B 90' in party_results:
            grune_data = party_results.pop('GRÜNE/B 90')
            if 'GRÜNE' in party_results:
                # Add to existing GRÜNE votes if present
                party_results['GRÜNE'] = {
                    'member': party_results['GRÜNE'].get('member', 0) + grune_data.get('member', 0),
                    'list': party_results['GRÜNE'].get('list', 0) + grune_data.get('list', 0)
                }
            else:
                # Create new GRÜNE entry
                party_results['GRÜNE'] = grune_data
        
        district['party_results'] = party_results
    
    # Update parties list to match changes
    # Remove CDU and CSU, add CDU/CSU if not already present
    parties = [p for p in parties if p['short_name'] not in ['CDU', 'CSU']]
    cdu_csu = next((p for p in parties if p['short_name'] == 'CDU/CSU'), None)
    if not cdu_csu:
        parties.append({
            'short_name': 'CDU/CSU',
            'color': '#000000',  # Black
            'left_to_right': 6  # Center-right
        })
    
    # Remove GRÜNE/B 90 if it exists (already handled by rename)
    parties = [p for p in parties if p['short_name'] != 'GRÜNE/B 90']
    
    return voting_data, parties