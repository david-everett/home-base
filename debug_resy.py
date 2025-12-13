#!/usr/bin/env python3
import requests
import json

API_KEY = "VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"
AUTH_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjE3Njk1MjU3MTEsInVpZCI6NzQ2NDIzMSwiZ3QiOiJjb25zdW1lciIsImdzIjpbXSwibGFuZyI6ImVuLXVzIiwiZXh0cmEiOnsiZ3Vlc3RfaWQiOjIyNjY3MjcxfX0.Adkq7-ssfQzI85pG8pOsXjMTJ7QrNiGKfRXIs3i4ZriA3hQFUMeHjeDuKG5--579_dGRO1rYnHUKvUFbMKKS8eCrAZODz_XorcLCq7Ui97_jBKgHhJb_aq9g_DuVnizQF2nxZ1oEEASTWGhKjmlR668oK-Qkew6R3u-VimJeaYJmGLKf"

url = "https://api.resy.com/4/find"
headers = {
    'Authorization': f'ResyAPI api_key="{API_KEY}"',
    'x-resy-auth-token': AUTH_TOKEN,
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}

params = {
    "lat": "0",
    "long": "0", 
    "day": "2025-12-14",
    "party_size": "2",
    "venue_id": "53048"
}

print("Testing Resy API call...")
print(f"URL: {url}")
print(f"Headers: {headers}")
print(f"Params: {params}")
print()

try:
    response = requests.get(url, headers=headers, params=params)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print()
    
    if response.text:
        try:
            data = response.json()
            print("JSON Response:")
            print(json.dumps(data, indent=2))
        except:
            print("Raw Response:")
            print(response.text[:1000])
    else:
        print("Empty response")
        
except Exception as e:
    print(f"Error: {e}")