#!/usr/bin/env python3
from restaurant_availability import find_available_restaurants, parse_date_query

print("🍽️  Restaurant Availability Checker - Test Mode")
print("=" * 50)

# Test the date parsing
print("Testing date parsing:")
print(f"'tomorrow night' -> {parse_date_query('tomorrow night')}")
print(f"'tonight' -> {parse_date_query('tonight')}")
print(f"'weekend' -> {parse_date_query('weekend')}")
print()

# Test availability checking
print("Testing availability for tomorrow night, party of 2:")
results = find_available_restaurants("tomorrow night", 2)

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
print("\n💡 This is testing with Yellow Rose (venue_id: 53048)")
print("   To get real data, you need your Resy API key and auth token")