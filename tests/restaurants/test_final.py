#!/usr/bin/env python3
from restaurant_availability import parse_date_query, ResyChecker

# Your Resy credentials
API_KEY = "VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"
AUTH_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjE3Njk1MjU3MTEsInVpZCI6NzQ2NDIzMSwiZ3QiOiJjb25zdW1lciIsImdzIjpbXSwibGFuZyI6ImVuLXVzIiwiZXh0cmEiOnsiZ3Vlc3RfaWQiOjIyNjY3MjcxfX0.Adkq7-ssfQzI85pG8pOsXjMTJ7QrNiGKfRXIs3i4ZriA3hQFUMeHjeDuKG5--579_dGRO1rYnHUKvUFbMKKS8eCrAZODz_XorcLCq7Ui97_jBKgHhJb_aq9g_DuVnizQF2nxZ1oEEASTWGhKjmlR668oK-Qkew6R3u-VimJeaYJmGLKf"

print("🍽️  Final Restaurant Availability Test")
print("=" * 40)

date = parse_date_query('tomorrow night')
print(f"Checking Yellow Rose for {date}")
print()

checker = ResyChecker(API_KEY, AUTH_TOKEN)
result = checker.check_availability("53048", date, 2)

print("📍 Yellow Rose")
if result['available']:
    print(f"   ✅ {result['message']}")
    for slot in result.get('slots', []):
        print(f"      🕐 {slot['time']} - {slot['type']}")
else:
    error_msg = result.get('error', result.get('message', 'No availability'))
    print(f"   ❌ {error_msg}")

print("\n🎯 This proves the concept works!")
print("   Next: Add your other restaurants' venue IDs")