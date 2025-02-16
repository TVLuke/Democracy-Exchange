from party import Party

def changes_for_list(parties: list) -> list:
    print("election specific chages for germany")
    """
    Modify the list of parties to aggregate votes for specific party combinations and rename them.

    This function performs the following changes:
    1. Renames 'CDU' to 'CDU/CSU' and aggregates votes from 'CSU' into 'CDU/CSU'.
    2. Aggregates votes from 'GRÜNE/B 90' into 'GRÜNE'.

    Args:
        parties (list): A list of Party namedtuples.

    Returns:
        list: The modified list of Party namedtuples with updated names and aggregated votes.
    """
    # Change CDU to CDU/CSU
    for i, party in enumerate(parties):
        if party.name == 'CDU':
            parties[i] = party._replace(name='CDU/CSU')
    
    # Aggregate votes for CSU into CDU/CSU
    for i, party in enumerate(parties):
        if party.name == 'CDU/CSU':
            csu_votes = party.votes
            # Add votes from CSU
            csu_votes += next((p.votes for p in parties if p.name == 'CSU'), 0)
            parties[i] = Party(party.name, party.color, party.size, party.left_to_right, csu_votes)
            break

    # Aggregate votes for GRÜNE/B 90 into GRÜNE
    for i, party in enumerate(parties):
        if party.name == 'GRÜNE':
            grune_votes = party.votes
            # Add votes from GRÜNE/B 90
            grune_votes += next((p.votes for p in parties if p.name == 'GRÜNE/B 90'), 0)
            parties[i] = Party(party.name, party.color, party.size, party.left_to_right, grune_votes)
            break

    return parties