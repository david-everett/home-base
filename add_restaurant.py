#!/usr/bin/env python3
"""
Add restaurant to lists by searching Resy API.

Modes:
  --search "name"  Search Resy for venues, output JSON
  --add            Add a restaurant to a CSV list
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime

import requests
from dotenv import load_dotenv


def load_resy_credentials():
    """Load Resy credentials from environment variables"""
    load_dotenv()
    api_key = os.getenv('RESY_API_KEY')
    auth_token = os.getenv('RESY_AUTH_TOKEN')

    if not api_key or not auth_token:
        raise ValueError(
            "Missing Resy credentials. Please set RESY_API_KEY and "
            "RESY_AUTH_TOKEN in .env file"
        )

    return api_key, auth_token


def search_venues(query: str, api_key: str, auth_token: str) -> list:
    """Search Resy API for venues matching query"""
    url = "https://api.resy.com/3/venuesearch/search"

    headers = {
        'Authorization': f'ResyAPI api_key="{api_key}"',
        'x-resy-auth-token': auth_token,
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        'Accept': 'application/json',
        'Referer': 'https://resy.com/'
    }

    payload = {
        "geo": {
            "latitude": 40.705,
            "longitude": -73.9038
        },
        "highlight": {
            "pre_tag": "",
            "post_tag": ""
        },
        "per_page": 5,
        "query": query,
        "slot_filter": {
            "day": datetime.now().strftime('%Y-%m-%d'),
            "party_size": 2
        },
        "types": ["venue", "cuisine"]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        hits = data.get('search', {}).get('hits', [])
        results = []

        for hit in hits:
            # Extract cuisine (first item from list)
            cuisine_list = hit.get('cuisine', [])
            cuisine = cuisine_list[0] if cuisine_list else 'Unknown'

            # Get neighborhood/location
            location = hit.get('neighborhood', hit.get('locality', 'Unknown'))

            # Get rating
            rating_data = hit.get('rating', {})
            rating = rating_data.get('average', 0)

            results.append({
                'venue_id': hit.get('id', {}).get('resy'),
                'name': hit.get('name', 'Unknown'),
                'cuisine': cuisine,
                'location': location,
                'rating': round(rating, 1) if rating else None,
                'url_slug': hit.get('url_slug', '')
            })

        return results

    except requests.RequestException as e:
        print(f"Error searching Resy: {e}", file=sys.stderr)
        return []


def add_restaurant(venue_id: int, name: str, location: str, cuisine: str,
                   list_type: str, category: str, notes: str = '',
                   restaurants_dir: str = None) -> bool:
    """Add a restaurant to the appropriate CSV file"""
    if restaurants_dir is None:
        restaurants_dir = '/Users/davideverett/Home Base/restaurants'

    # Build filename
    list_prefix = 'places_to_try' if list_type == 'try' else 'places_we_love'
    filename = f"{list_prefix}_{category}.csv"
    filepath = os.path.join(restaurants_dir, filename)

    # Check if file exists
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return False

    # Check for duplicates
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if str(row.get('venue_id')) == str(venue_id):
                print(f"Already exists: {name} (ID: {venue_id}) in {filename}")
                return False

    # Append to CSV
    with open(filepath, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([name, venue_id, location, cuisine, notes])

    print(f"Added {name} to {filename}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Search and add restaurants to lists',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Command')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for venues')
    search_parser.add_argument('query', help='Restaurant name to search')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add restaurant to list')
    add_parser.add_argument('--venue-id', type=int, required=True)
    add_parser.add_argument('--name', required=True)
    add_parser.add_argument('--location', required=True)
    add_parser.add_argument('--cuisine', required=True)
    add_parser.add_argument('--list', choices=['try', 'love'], required=True,
                           dest='list_type')
    add_parser.add_argument('--category',
                           choices=['dinner', 'brunch', 'lunch', 'drinks'],
                           required=True)
    add_parser.add_argument('--notes', default='')
    add_parser.add_argument('--restaurants-dir',
                           default='/Users/davideverett/Home Base/restaurants')

    args = parser.parse_args()

    if args.command == 'search':
        try:
            api_key, auth_token = load_resy_credentials()
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        results = search_venues(args.query, api_key, auth_token)
        print(json.dumps(results, indent=2))

    elif args.command == 'add':
        success = add_restaurant(
            venue_id=args.venue_id,
            name=args.name,
            location=args.location,
            cuisine=args.cuisine,
            list_type=args.list_type,
            category=args.category,
            notes=args.notes,
            restaurants_dir=args.restaurants_dir
        )
        sys.exit(0 if success else 1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
