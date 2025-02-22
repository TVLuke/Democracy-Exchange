def changes_for_country(voting_data: list, parties: list) -> list:
    # Remove Speaker from parties list
    parties = [p for p in parties if p['short_name'] != 'Spk']
    
    # Convert Speaker votes to Independent votes in voting data
    for district in voting_data:
        if 'Spk' in district['party_results']:
            # Add Speaker's votes to Independent
            speaker_votes = district['party_results']['Spk']
            if 'Ind' not in district['party_results']:
                district['party_results']['Ind'] = {}
            
            # Transfer member votes if they exist
            if 'member' in speaker_votes:
                if 'member' not in district['party_results']['Ind']:
                    district['party_results']['Ind']['member'] = 0
                district['party_results']['Ind']['member'] += speaker_votes['member']
            
            # Transfer list votes if they exist
            if 'list' in speaker_votes:
                if 'list' not in district['party_results']['Ind']:
                    district['party_results']['Ind']['list'] = 0
                district['party_results']['Ind']['list'] += speaker_votes['list']
            
            # Remove Speaker entry
            del district['party_results']['Spk']
    
    return voting_data, parties