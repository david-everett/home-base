#!/usr/bin/env python3
import requests
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
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

# Sample restaurant data with venue IDs
restaurants = [
    {"name": "Yellow Rose", "location": "NYC", "cuisine": "American", "venue_id": "53048"},
    {"name": "Watawa", "location": "Astoria", "cuisine": "sushi", "venue_id": None},
    {"name": "Mono Mono", "location": "Bowery", "cuisine": "Korean", "venue_id": None},
    {"name": "Lilia", "location": "Williamsburg", "cuisine": "Italian", "venue_id": None},
]

class ResyChecker:
    def __init__(self, api_key: str = None, auth_token: str = None):
        self.api_key = api_key
        self.auth_token = auth_token
        self.session = requests.Session()
        
        if api_key and auth_token:
            self.session.headers.update({
                'Authorization': f'ResyAPI api_key="{api_key}"',
                'x-resy-auth-token': auth_token,
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Referer': 'https://resy.com/'
            })
    
    def check_availability(self, venue_id: str, date: str, party_size: int = 2) -> Dict:
        """Check availability for a restaurant on a given date"""
        url = "https://api.resy.com/4/find"
        params = {
            "lat": "0",
            "long": "0", 
            "day": date,
            "party_size": str(party_size),
            "venue_id": venue_id
        }
        
        try:
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return self._parse_availability(data)
            else:
                return {"available": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def _parse_availability(self, data: Dict) -> Dict:
        """Parse Resy API response to extract availability info"""
        try:
            venues = data.get("results", {}).get("venues", [])
            if not venues:
                return {"available": False, "slots": [], "message": "No availability"}
            
            venue = venues[0]
            slots = venue.get("slots", [])
            
            if not slots:
                return {"available": False, "slots": [], "message": "No time slots available"}
            
            available_times = []
            for slot in slots:
                config = slot.get("config", {})
                date_info = slot.get("date", {})
                available_times.append({
                    "time": date_info.get("start", "Unknown").split(" ")[-1][:5],  # Extract HH:MM
                    "type": config.get("type", "Standard"),
                    "token": config.get("token", ""),
                    "end_time": date_info.get("end", "Unknown").split(" ")[-1][:5]
                })
            
            return {
                "available": True,
                "slots": available_times,
                "message": f"Found {len(available_times)} available slots"
            }
        except Exception as e:
            return {"available": False, "error": f"Parse error: {str(e)}"}

def parse_date_query(query: str) -> str:
    """Convert natural language to YYYY-MM-DD format"""
    query = query.lower().strip()
    today = datetime.now()

    # Check if it's already in YYYY-MM-DD format
    if re.match(r'\d{4}-\d{2}-\d{2}', query):
        return query

    if 'tomorrow' in query:
        target = today + timedelta(days=1)
    elif 'tonight' in query or 'today' in query:
        target = today
    elif 'weekend' in query:
        # Next Saturday
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0:
            days_until_saturday = 7
        target = today + timedelta(days=days_until_saturday)
    else:
        # Handle "next [weekday]" and "this [weekday]"
        weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }

        target = None

        if 'next' in query:
            for day_name, day_num in weekdays.items():
                if day_name in query:
                    days_ahead = (day_num - today.weekday()) % 7
                    if days_ahead == 0:  # If today is that day, get next week
                        days_ahead = 7
                    target = today + timedelta(days=days_ahead)
                    break
        elif 'this' in query:
            for day_name, day_num in weekdays.items():
                if day_name in query:
                    days_ahead = (day_num - today.weekday()) % 7
                    if days_ahead == 0:  # If today is that day, use today
                        days_ahead = 0
                    target = today + timedelta(days=days_ahead)
                    break

        # Default to tomorrow if no match found
        if target is None:
            target = today + timedelta(days=1)

    return target.strftime('%Y-%m-%d')

def find_available_restaurants(when: str = "tomorrow night", party_size: int = 2, 
                             api_key: str = None, auth_token: str = None) -> List[Dict]:
    """Find restaurants available for a given time"""
    date = parse_date_query(when)
    checker = ResyChecker(api_key, auth_token)
    
    results = []
    
    for restaurant in restaurants:
        if not restaurant.get('venue_id'):
            continue
            
        print(f"Checking {restaurant['name']}...")
        
        availability = checker.check_availability(
            venue_id=restaurant['venue_id'],
            date=date,
            party_size=party_size
        )
        
        result = {
            **restaurant,
            'date': date,
            'party_size': party_size,
            **availability
        }
        
        results.append(result)
    
    return results

if __name__ == "__main__":
    print("🍽️  Restaurant Availability Checker")
    print("=" * 40)
    
    # Test without authentication (will show structure but may not work)
    when = input("When do you want to dine? (tomorrow night/tonight/weekend): ").strip()
    if not when:
        when = "tomorrow night"
    
    party_size = input("Party size (default 2): ").strip()
    if not party_size:
        party_size = 2
    else:
        party_size = int(party_size)
    
    print(f"\nSearching for availability {when} for party of {party_size}...")
    print(f"Date: {parse_date_query(when)}")
    print()
    
    results = find_available_restaurants(when, party_size)
    
    available_count = 0
    for result in results:
        print(f"📍 {result['name']} ({result['location']}) - {result['cuisine']}")
        
        if result['available']:
            available_count += 1
            print(f"   ✅ {result['message']}")
            for slot in result.get('slots', []):
                print(f"      🕐 {slot['time']} - {slot['type']}")
        else:
            error_msg = result.get('error', result.get('message', 'No availability'))
            print(f"   ❌ {error_msg}")
        print()
    
    print(f"Summary: {available_count}/{len(results)} restaurants have availability")
    
    if available_count == 0:
        print("\n💡 To get real availability data, you need:")
        print("   1. Your Resy API key")  
        print("   2. Your Resy auth token")
        print("   3. Venue IDs for your restaurants")