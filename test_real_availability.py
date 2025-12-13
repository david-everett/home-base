#!/usr/bin/env python3
from restaurant_availability import find_available_restaurants, parse_date_query, ResyChecker

# Your Resy credentials
API_KEY = "VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"
AUTH_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjE3Njk1MjU3MTEsInVpZCI6NzQ2NDIzMSwiZ3QiOiJjb25zdW1lciIsImdzIjpbXSwibGFuZyI6ImVuLXVzIiwiZXh0cmEiOnsiZ3Vlc3RfaWQiOjIyNjY3MjcxfX0.Adkq7-ssfQzI85pG8pOsXjMTJ7QrNiGKfRXIs3i4ZriA3hQFUMeHjeDuKG5--579_dGRO1rYnHUKvUFbMKKS8eCrAZODz_XorcLCq7Ui97_jBKgHhJb_aq9g_DuVnizQF2nxZ1oEEASTWGhKjmlR668oK-Qkew6R3u-VimJeaYJmGLKf"

print("🍽️  Restaurant Availability Checker - LIVE TEST")
print("=" * 50)

print("Testing availability for tomorrow night, party of 2:")
date = parse_date_query('tomorrow night')
print(f"Date: {date}")
print()

# Test directly with credentials
checker = ResyChecker(API_KEY, AUTH_TOKEN)
result = checker.check_availability("53048", date, 2)

print("📍 Yellow Rose (NYC) - American")
if result['available']:
    print(f"   ✅ {result['message']}")
    for slot in result.get('slots', []):
        print(f"      🕐 {slot['time']} - {slot['type']}")
else:
    error_msg = result.get('error', result.get('message', 'No availability'))
    print(f"   ❌ {error_msg}")

print()

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

if available_count > 0:
    print("\n🎉 Found availability! You can book through Resy.")
else:
    print("\n😞 No availability found for tomorrow night.")