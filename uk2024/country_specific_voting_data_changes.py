def changes_for_country(voting_data: list, parties: list) -> list:
    # Remove Speaker from parties list
    parties = [p for p in parties if p['short_name'] != 'Speaker']
    
    # Convert Speaker votes to Conservative votes in voting data
    for district in voting_data:
        if 'Speaker' in district['party_results']:
            # Add Speaker's votes to Conservative party
            speaker_votes = district['party_results']['Speaker']
            if 'Con' not in district['party_results']:
                district['party_results']['Con'] = {}
            
            # Transfer member votes if they exist
            if 'member' in speaker_votes:
                if 'member' not in district['party_results']['Con']:
                    district['party_results']['Con']['member'] = 0
                district['party_results']['Con']['member'] += speaker_votes['member']
            
            # Transfer list votes if they exist
            if 'list' in speaker_votes:
                if 'list' not in district['party_results']['Con']:
                    district['party_results']['Con']['list'] = 0
                district['party_results']['Con']['list'] += speaker_votes['list']
            
            # Remove Speaker entry
            del district['party_results']['Speaker']
    
    return voting_data, parties