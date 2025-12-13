#!/usr/bin/env python3
"""
Unified restaurant availability checker with full parameterization.
Supports natural language dates and filters results by time.
"""

import argparse
import csv
import os
import re
import sys
from datetime import datetime
from restaurant_availability import (
    ResyChecker,
    parse_date_query,
    load_resy_credentials
)

def parse_restaurant_csv(file_path):
    """Parse CSV file to extract restaurant data"""
    restaurants = []

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('venue_id'):  # Only include restaurants with venue IDs
                restaurants.append({
                    'name': row['name'],
                    'venue_id': row['venue_id'],
                    'location': row['location'],
                    'cuisine': row['cuisine'],
                    'notes': row.get('notes', '')  # Optional field
                })

    return restaurants

def filter_time_slots(slots, max_time_str="20:30"):
    """Filter out time slots after specified time (default 8:30pm)"""
    filtered = []
    for slot in slots:
        time_str = slot.get('time', '00:00')
        try:
            # Compare time strings directly (HH:MM format)
            if time_str <= max_time_str:
                filtered.append(slot)
        except Exception:
            # If comparison fails, include it to be safe
            filtered.append(slot)
    return filtered

def build_restaurant_file_path(base_dir, list_type, category):
    """Build path to restaurant CSV file"""
    filename = f"{list_type}_{category}.csv"
    return os.path.join(base_dir, filename)

def main():
    parser = argparse.ArgumentParser(
        description='Check restaurant availability on Resy',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --date "next tuesday" --list try --category dinner
  %(prog)s --date tomorrow --list love --category brunch --party-size 4
  %(prog)s --date 2025-12-20 --list try --category dinner --max-time 19:00
        """
    )

    # Required arguments
    parser.add_argument(
        '--date',
        required=True,
        help='Date in natural language (tomorrow, next tuesday) or YYYY-MM-DD'
    )

    parser.add_argument(
        '--list',
        required=True,
        choices=['try', 'love'],
        help='Restaurant list: "try" (places_to_try) or "love" (places_we_love)'
    )

    parser.add_argument(
        '--category',
        required=True,
        choices=['dinner', 'brunch', 'lunch', 'drinks'],
        help='Meal category'
    )

    # Optional arguments
    parser.add_argument(
        '--party-size',
        type=int,
        default=2,
        help='Number of people (default: 2)'
    )

    parser.add_argument(
        '--max-time',
        default='20:30',
        help='Filter out times after this (HH:MM format, default: 20:30)'
    )

    parser.add_argument(
        '--restaurants-dir',
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'restaurants'),
        help='Directory containing restaurant markdown files'
    )

    parser.add_argument(
        '--concise',
        action='store_true',
        help='Concise output (show time ranges instead of all slots)'
    )

    args = parser.parse_args()

    # Load credentials from .env
    try:
        api_key, auth_token = load_resy_credentials()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Parse date
    try:
        target_date = parse_date_query(args.date)
    except Exception as e:
        print(f"Error parsing date '{args.date}': {e}")
        sys.exit(1)

    # Build file path
    list_type = 'places_to_try' if args.list == 'try' else 'places_we_love'
    file_path = build_restaurant_file_path(
        args.restaurants_dir,
        list_type,
        args.category
    )

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: Restaurant file not found: {file_path}")
        sys.exit(1)

    # Parse restaurants from file
    restaurants = parse_restaurant_csv(file_path)

    if not restaurants:
        print(f"No restaurants with venue IDs found in {file_path}")
        sys.exit(1)

    # Print header
    print(f"🍽️  Checking {args.category} availability")
    print(f"📅  Date: {target_date}")
    print(f"👥  Party size: {args.party_size}")
    print(f"🕐  Max time: {args.max_time}")
    print(f"📋  List: {list_type}")
    print(f"🔍  Checking {len(restaurants)} restaurants...")
    print("=" * 60)
    print()

    # Check availability
    checker = ResyChecker(api_key, auth_token)
    available_restaurants = []
    unavailable_restaurants = []

    for restaurant in restaurants:
        if not args.concise:
            print(f"Checking {restaurant['name']}...")

        result = checker.check_availability(
            venue_id=restaurant['venue_id'],
            date=target_date,
            party_size=args.party_size
        )

        if result['available']:
            # Filter by max time
            filtered_slots = filter_time_slots(
                result['slots'],
                args.max_time
            )

            if filtered_slots:
                available_restaurants.append({
                    **restaurant,
                    'slots': filtered_slots
                })
            else:
                unavailable_restaurants.append({
                    **restaurant,
                    'message': f'No availability before {args.max_time}'
                })
        else:
            unavailable_restaurants.append({
                **restaurant,
                'message': result.get('error', result.get('message', 'No availability'))
            })

    # Display results
    print()
    print("=" * 60)
    print()

    if available_restaurants:
        print(f"✅ AVAILABLE ({len(available_restaurants)}):")
        print()

        for resto in available_restaurants:
            print(f"📍 {resto['name']}")
            print(f"   Location: {resto['location']}")
            print(f"   Cuisine: {resto['cuisine']}")

            if args.concise:
                # Show time range instead of all slots
                first_time = resto['slots'][0]['time']
                last_time = resto['slots'][-1]['time']
                slot_count = len(resto['slots'])

                # Get unique slot types
                slot_types = list(set(slot['type'] for slot in resto['slots']))
                types_str = ', '.join(slot_types)

                print(f"   Times: {first_time} - {last_time} ({slot_count} slots)")
                if len(slot_types) > 1:
                    print(f"   Seating: {types_str}")
            else:
                print(f"   Available times:")
                for slot in resto['slots']:
                    print(f"      🕐 {slot['time']} - {slot['type']}")

            print(f"   Book: https://resy.com/cities/ny/venues/{resto['venue_id']}?date={target_date}&seats={args.party_size}")
            print()
    else:
        print(f"❌ No restaurants available before {args.max_time}")
        print()

    if unavailable_restaurants:
        print(f"⛔ UNAVAILABLE ({len(unavailable_restaurants)}):")
        print()
        for resto in unavailable_restaurants:
            print(f"   {resto['name']}: {resto['message']}")
        print()

    print("=" * 60)
    print(f"Summary: {len(available_restaurants)}/{len(restaurants)} restaurants available")

if __name__ == "__main__":
    main()
