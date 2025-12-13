#!/usr/bin/env python3
import sys
sys.path.append('/Users/davideverett/Home Base')

from restaurant_availability import ResyChecker
from datetime import datetime

# API credentials
API_KEY = "VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"
AUTH_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjE3Njk1MjU3MTEsInVpZCI6NzQ2NDIzMSwiZ3QiOiJjb25zdW1lciIsImdzIjpbXSwibGFuZyI6ImVuLXVzIiwiZXh0cmEiOnsiZ3Vlc3RfaWQiOjIyNjY3MjcxfX0.Adkq7-ssfQzI85pG8pOsXjMTJ7QrNiGKfRXIs3i4ZriA3hQFUMeHjeDuKG5--579_dGRO1rYnHUKvUFbMKKS8eCrAZODz_XorcLCq7Ui97_jBKgHhJb_aq9g_DuVnizQF2nxZ1oEEASTWGhKjmlR668oK-Qkew6R3u-VimJeaYJmGLKf"

# Restaurants from places_to_try_dinner.md
restaurants = [
    {"name": "Mono Mono", "location": "Bowery", "cuisine": "Korean", "venue_id": "59569"},
    {"name": "Au Zaatar", "location": "EV", "cuisine": "Middle Eastern", "venue_id": "3708"},
    {"name": "Rolos", "location": "Ridgewood", "cuisine": "American", "venue_id": "36902"},
    {"name": "Sweet Afton", "location": "Astoria", "cuisine": "American", "venue_id": "36742"},
    {"name": "Mam", "location": "Lower East Side", "cuisine": "Vietnamese", "venue_id": "80206"},
    {"name": "Theodora", "location": "Fort Greene", "cuisine": "Mediterranean", "venue_id": "73589"},
    {"name": "5ive Spice", "location": "Grammercy", "cuisine": "Vietnamese", "venue_id": "69009"},
    {"name": "Dhamaka", "location": "Lower East Side", "cuisine": "Indian", "venue_id": "48994"},
    {"name": "Ladybird", "location": "East Village", "cuisine": "Vegan", "venue_id": "618"},
    {"name": "Ayat", "location": "Ditmas Park", "cuisine": "Middle Eastern", "venue_id": "78974"},
]

def filter_early_times(slots):
    """Filter out time slots after 8:30pm"""
    filtered = []
    for slot in slots:
        time_str = slot['time']
        try:
            # Parse time in HH:MM format
            hour, minute = map(int, time_str.split(':'))
            # Filter out times after 20:30 (8:30pm)
            if hour < 20 or (hour == 20 and minute <= 30):
                filtered.append(slot)
        except:
            # If parsing fails, include it to be safe
            filtered.append(slot)
    return filtered

def main():
    # Next Tuesday is 2025-12-16
    date = "2025-12-16"
    party_size = 2

    print(f"🍽️  Checking availability for Tuesday, December 16th, 2025")
    print(f"   Party size: {party_size}")
    print(f"   Filtering times after 8:30pm")
    print("=" * 60)
    print()

    checker = ResyChecker(api_key=API_KEY, auth_token=AUTH_TOKEN)

    available_restaurants = []
    unavailable_restaurants = []

    for restaurant in restaurants:
        print(f"Checking {restaurant['name']}...")

        availability = checker.check_availability(
            venue_id=restaurant['venue_id'],
            date=date,
            party_size=party_size
        )

        if availability['available']:
            # Filter times after 8:30pm
            filtered_slots = filter_early_times(availability['slots'])

            if filtered_slots:
                available_restaurants.append({
                    **restaurant,
                    'slots': filtered_slots
                })
            else:
                unavailable_restaurants.append({
                    **restaurant,
                    'message': 'No availability before 8:30pm'
                })
        else:
            unavailable_restaurants.append({
                **restaurant,
                'message': availability.get('error', availability.get('message', 'No availability'))
            })

    print()
    print("=" * 60)
    print()

    if available_restaurants:
        print(f"✅ AVAILABLE RESTAURANTS ({len(available_restaurants)}):")
        print()

        for resto in available_restaurants:
            print(f"📍 {resto['name']}")
            print(f"   Location: {resto['location']}")
            print(f"   Cuisine: {resto['cuisine']}")
            print(f"   Available times:")
            for slot in resto['slots']:
                print(f"      🕐 {slot['time']} - {slot['type']}")
                # Generate booking URL
                print(f"         Book: https://resy.com/cities/ny/venues/{resto['venue_id']}?date={date}&seats={party_size}")
            print()
    else:
        print("❌ No restaurants with availability before 8:30pm")
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
