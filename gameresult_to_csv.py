#!/usr/bin/env python3
"""
Convert GameResult.json to CSV format.
Handles nested structures by flattening arrays and objects into strings.
"""

import json
import csv
import sys
from datetime import datetime

def flatten_value(value):
    """Convert nested structures to strings for CSV."""
    if value is None:
        return ''
    elif isinstance(value, bool):
        return str(value)
    elif isinstance(value, (int, float)):
        return value
    elif isinstance(value, str):
        return value
    elif isinstance(value, list):
        # Convert list to comma-separated string
        return ', '.join(str(item) for item in value)
    elif isinstance(value, dict):
        # Handle special date format
        if '__type' in value and value['__type'] == 'Date':
            return value.get('iso', '')
        # Convert dict to string representation
        if len(value) == 0:
            return ''
        items = []
        for k, v in value.items():
            if isinstance(v, (list, dict)):
                v_str = flatten_value(v)
            else:
                v_str = str(v)
            items.append(f"{k}: {v_str}")
        return '; '.join(items)
    else:
        return str(value)

def extract_fields(game_result):
    """Extract and flatten all fields from a game result."""
    row = {}
    
    # Simple fields
    row['objectId'] = game_result.get('objectId', '')
    row['adversary'] = game_result.get('adversary', '')
    row['adversaryLevel'] = game_result.get('adversaryLevel', '')
    row['scenario'] = game_result.get('scenario', '')
    row['usingEvents'] = game_result.get('usingEvents', False)
    row['usingTokens'] = game_result.get('usingTokens', False)
    row['isMultiplayer'] = game_result.get('isMultiplayer', False)
    row['waveNumber'] = game_result.get('waveNumber', '')
    row['endingResult'] = game_result.get('endingResult', '')
    row['blightCard'] = game_result.get('blightCard', '')
    row['blightCardFlipped'] = game_result.get('blightCardFlipped', False)
    row['blightRemaining'] = game_result.get('blightRemaining', '')
    row['score'] = game_result.get('score', '')
    row['turn'] = game_result.get('turn', '')
    row['invaderCardsInDeck'] = game_result.get('invaderCardsInDeck', '')
    row['invaderCardsNotInDeck'] = game_result.get('invaderCardsNotInDeck', '')
    row['blightOnIsland'] = game_result.get('blightOnIsland', '')
    row['dahanOnIsland'] = game_result.get('dahanOnIsland', '')
    row['terrorLevel'] = game_result.get('terrorLevel', '')
    row['installationId'] = game_result.get('installationId', '')
    
    # Date fields
    end_date = game_result.get('endDate', {})
    if isinstance(end_date, dict) and 'iso' in end_date:
        row['endDate'] = end_date['iso']
    else:
        row['endDate'] = ''
    
    row['createdAt'] = game_result.get('createdAt', '')
    row['updatedAt'] = game_result.get('updatedAt', '')
    
    # Array fields - convert to comma-separated strings
    row['spirits'] = flatten_value(game_result.get('spirits', []))
    row['boards'] = flatten_value(game_result.get('boards', []))
    row['powerProgressionSpirits'] = flatten_value(game_result.get('powerProgressionSpirits', []))
    row['practiceModes'] = flatten_value(game_result.get('practiceModes', []))
    row['powerCardsInDiscard'] = flatten_value(game_result.get('powerCardsInDiscard', []))
    row['emptyPresenceTrackNodes'] = flatten_value(game_result.get('emptyPresenceTrackNodes', []))
    
    # Nested objects - convert to strings
    row['layout'] = flatten_value(game_result.get('layout', {}))
    
    # powerCardsOwned is a nested object with arrays - convert to string
    power_cards_owned = game_result.get('powerCardsOwned', {})
    if power_cards_owned:
        # Format: "Spirit1: card1, card2; Spirit2: card3, card4"
        cards_strs = []
        for spirit, cards in power_cards_owned.items():
            cards_list = ', '.join(str(card) for card in cards) if isinstance(cards, list) else str(cards)
            cards_strs.append(f"{spirit}: {cards_list}")
        row['powerCardsOwned'] = '; '.join(cards_strs)
    else:
        row['powerCardsOwned'] = ''
    
    return row

def main():
    """Main function to convert JSON to CSV."""
    input_file = 'GameResult2.json'
    output_file = 'GameResult2.csv'
    
    print(f"Reading {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {input_file} not found!", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {input_file}: {e}", file=sys.stderr)
        sys.exit(1)
    
    if 'results' not in data:
        print("Error: 'results' key not found in JSON", file=sys.stderr)
        sys.exit(1)
    
    results = data['results']
    print(f"Found {len(results)} game results")
    
    # Extract all rows
    rows = []
    for i, game_result in enumerate(results):
        try:
            row = extract_fields(game_result)
            rows.append(row)
        except Exception as e:
            print(f"Warning: Error processing game result {i+1}: {e}", file=sys.stderr)
            continue
    
    if not rows:
        print("Error: No valid game results found", file=sys.stderr)
        sys.exit(1)
    
    # Get all column names from the first row
    fieldnames = list(rows[0].keys())
    
    # Write to CSV
    print(f"Writing to {output_file}...")
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Successfully converted {len(rows)} game results to {output_file}")
    print(f"   Columns: {len(fieldnames)}")
    print(f"   Sample columns: {', '.join(fieldnames[:10])}...")

if __name__ == '__main__':
    main()
