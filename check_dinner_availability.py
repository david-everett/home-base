#!/usr/bin/env python3
import re
from datetime import datetime, timedelta
from restaurant_availability import ResyChecker, parse_date_query

def parse_restaurant_file(file_path):
    """Parse markdown file to extract restaurant data"""
    restaurants = []
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Split by ## headers (restaurant names)
    sections = re.split(r'\n## ', content)
    
    for section in sections[1:]:  # Skip the first section (title)
        lines = section.strip().split('\n')
        name = lines[0]  # First line is the restaurant name
        
        # Extract venue ID
        venue_id = None
        location = ""
        cuisine = ""
        
        for line in lines:
            if '**Venue ID:**' in line:
                match = re.search(r'\*\*Venue ID:\*\*\s*(\d+)', line)
                if match:
                    venue_id = match.group(1)
            elif '**Location:**' in line:
                location = line.replace('**Location:**', '').strip()
            elif '**Cuisine:**' in line:
                cuisine = line.replace('**Cuisine:**', '').strip()
        
        if venue_id:  # Only include restaurants with venue IDs
            restaurants.append({
                'name': name,
                'location': location,
                'cuisine': cuisine,
                'venue_id': venue_id
            })
    
    return restaurants

def check_dinner_availability(file_path, when="next tuesday", party_size=2):
    """Check availability for restaurants in the file"""
    
    # Your Resy credentials
    API_KEY = "VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"
    AUTH_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjE3Njk1MjU3MTEsInVpZCI6NzQ2NDIzMSwiZ3QiOiJjb25zdW1lciIsImdzIjpbXSwibGFuZyI6ImVuLXVzIiwiZXh0cmEiOnsiZ3Vlc3RfaWQiOjIyNjY3MjcxfX0.Adkq7-ssfQzI85pG8pOsXjMTJ7QrNiGKfRXIs3i4ZriA3hQFUMeHjeDuKG5--579_dGRO1rYnHUKvUFbMKKS8eCrAZODz_XorcLCq7Ui97_jBKgHhJb_aq9g_DuVnizQF2nxZ1oEEASTWGhKjmlR668oK-Qkew6R3u-VimJeaYJmGLKf"
    
    # Parse the target date
    if "next tuesday" in when.lower():
        today = datetime.now()
        days_ahead = (1 - today.weekday()) % 7  # Tuesday is day 1
        if days_ahead == 0:  # If today is Tuesday, get next Tuesday
            days_ahead = 7
        target_date = (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
    else:
        target_date = parse_date_query(when)
    
    print(f"🍽️  Checking dinner availability for {target_date}")
    print(f"👥  Party size: {party_size}")
    print("=" * 60)
    
    # Parse restaurants from file
    restaurants = parse_restaurant_file(file_path)
    
    if not restaurants:
        print("❌ No restaurants with venue IDs found in the file")
        return
    
    print(f"🔍 Checking {len(restaurants)} restaurants...\n")
    
    # Check availability
    checker = ResyChecker(API_KEY, AUTH_TOKEN)
    available_restaurants = []
    
    for restaurant in restaurants:
        print(f"Checking {restaurant['name']}...")
        
        result = checker.check_availability(
            venue_id=restaurant['venue_id'],
            date=target_date,
            party_size=party_size
        )
        
        if result['available']:
            available_restaurants.append({
                **restaurant,
                **result
            })
            print(f"   ✅ {result['message']}")
        else:
            error_msg = result.get('error', result.get('message', 'No availability'))
            print(f"   ❌ {error_msg}")
    
    print("\n" + "=" * 60)
    print("🎯 RESULTS")
    print("=" * 60)
    
    if not available_restaurants:
        print("😞 No availability found for next Tuesday")
        print("\n💡 Try checking:")
        print("   • Different dates")
        print("   • Smaller party size")
        print("   • Earlier/later time preferences")
        return
    
    print(f"🎉 Found {len(available_restaurants)} restaurants with availability!\n")
    
    for restaurant in available_restaurants:
        print(f"📍 {restaurant['name']} ({restaurant['location']})")
        print(f"   🍜 {restaurant['cuisine']}")
        print(f"   ✅ {restaurant['message']}")
        
        # Show first few time slots
        slots = restaurant.get('slots', [])
        dinner_slots = [slot for slot in slots if '17:' in slot['time'] or '18:' in slot['time'] or '19:' in slot['time'] or '20:' in slot['time']]
        
        if dinner_slots:
            print("   🕐 Dinner times available:")
            for slot in dinner_slots[:4]:  # Show first 4 dinner slots
                print(f"      • {slot['time']} ({slot['type']})")
            if len(dinner_slots) > 4:
                print(f"      • ... and {len(dinner_slots)-4} more times")
        else:
            print("   🕐 Available times:")
            for slot in slots[:3]:  # Show first 3 slots
                print(f"      • {slot['time']} ({slot['type']})")
        
        print(f"   🔗 Book: https://resy.com/cities/new-york-ny/venues/?venue_id={restaurant['venue_id']}&date={target_date}&seats={party_size}")
        print()

if __name__ == "__main__":
    import sys
    
    file_path = "/Users/davideverett/Home Base/restaurants/places_to_try_dinner.md"
    
    if len(sys.argv) > 1:
        when = " ".join(sys.argv[1:])
    else:
        when = "next tuesday"
    
    check_dinner_availability(file_path, when)