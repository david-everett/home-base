#!/usr/bin/env python3
"""
Google Maps client for geocoding and travel time calculations.

Usage:
  python3 maps_client.py geocode "123 Main St, NYC"
  python3 maps_client.py travel-time "123 Main St, NYC"
  python3 maps_client.py update-restaurants --list try --category dinner
"""

import argparse
import csv
import json
import os
import sys
import time

import requests
from dotenv import load_dotenv


def load_maps_credentials():
    """Load Google Maps API key from environment"""
    load_dotenv()
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        raise ValueError("Missing GOOGLE_MAPS_API_KEY in .env file")
    return api_key


def get_home_address():
    """Get home address from environment"""
    load_dotenv()
    address = os.getenv('HOME_ADDRESS')
    if not address:
        raise ValueError("Missing HOME_ADDRESS in .env file")
    return address


def geocode(address: str, api_key: str) -> dict:
    """
    Convert address to lat/lng coordinates.
    Returns: {"lat": float, "lng": float, "formatted_address": str}
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": api_key
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    if data["status"] != "OK":
        raise ValueError(f"Geocoding failed: {data['status']} - {data.get('error_message', '')}")

    result = data["results"][0]
    location = result["geometry"]["location"]

    return {
        "lat": location["lat"],
        "lng": location["lng"],
        "formatted_address": result["formatted_address"]
    }


def get_travel_time(origin: str, destination: str, api_key: str, mode: str = "transit") -> dict:
    """
    Calculate travel time between two locations.

    Args:
        origin: Starting address or "lat,lng"
        destination: Ending address or "lat,lng"
        api_key: Google Maps API key
        mode: Travel mode (transit, driving, walking, bicycling)

    Returns: {"duration_minutes": int, "distance_km": float, "duration_text": str}
    """
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origin,
        "destinations": destination,
        "mode": mode,
        "key": api_key
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    if data["status"] != "OK":
        raise ValueError(f"Distance Matrix failed: {data['status']}")

    element = data["rows"][0]["elements"][0]

    if element["status"] != "OK":
        raise ValueError(f"Route not found: {element['status']}")

    return {
        "duration_minutes": element["duration"]["value"] // 60,
        "duration_text": element["duration"]["text"],
        "distance_km": element["distance"]["value"] / 1000
    }


def update_restaurant_csv(list_type: str, category: str, api_key: str, home_address: str):
    """
    Update a restaurant CSV file with lat/lng and travel time.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')

    list_prefix = 'places_to_try' if list_type == 'try' else 'places_we_love'
    filename = f"{list_prefix}_{category}.csv"
    filepath = os.path.join(data_dir, filename)

    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return False

    # Read existing data
    rows = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    # Ensure we have the new columns
    new_fields = ['latitude', 'longitude', 'travel_time_minutes']
    for field in new_fields:
        if field not in fieldnames:
            fieldnames.append(field)

    # Update each restaurant
    updated_count = 0
    for row in rows:
        # Skip if already has coordinates and travel time
        if row.get('latitude') and row.get('longitude') and row.get('travel_time_minutes'):
            print(f"Skipping {row['name']} (already has data)")
            continue

        location = row.get('location', '')
        name = row.get('name', '')

        if not location:
            print(f"Skipping {name} (no location)")
            continue

        # Build search query - add NYC context
        search_query = f"{name}, {location}, New York, NY"

        try:
            # Geocode
            print(f"Geocoding {name} ({location})...")
            geo_result = geocode(search_query, api_key)
            row['latitude'] = geo_result['lat']
            row['longitude'] = geo_result['lng']

            # Get travel time
            print(f"  Getting travel time...")
            travel_result = get_travel_time(
                home_address,
                f"{geo_result['lat']},{geo_result['lng']}",
                api_key
            )
            row['travel_time_minutes'] = travel_result['duration_minutes']
            print(f"  -> {travel_result['duration_text']} ({travel_result['duration_minutes']} min)")

            updated_count += 1

            # Rate limiting - be nice to the API
            time.sleep(0.2)

        except Exception as e:
            print(f"  Error: {e}", file=sys.stderr)
            continue

    # Write back
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nUpdated {updated_count} restaurants in {filename}")
    return True


def generate_map_html(list_type: str, category: str, output_path: str, home_coords: dict = None):
    """
    Generate an interactive HTML map of restaurants using Leaflet.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')

    list_prefix = 'places_to_try' if list_type == 'try' else 'places_we_love'
    filename = f"{list_prefix}_{category}.csv"
    filepath = os.path.join(data_dir, filename)

    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return False

    # Read restaurant data
    restaurants = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('latitude') and row.get('longitude'):
                restaurants.append({
                    'name': row['name'],
                    'location': row.get('location', ''),
                    'cuisine': row.get('cuisine', ''),
                    'lat': float(row['latitude']),
                    'lng': float(row['longitude']),
                    'travel_time': row.get('travel_time_minutes', ''),
                    'venue_id': row.get('venue_id', '')
                })

    if not restaurants:
        print("No restaurants with coordinates found", file=sys.stderr)
        return False

    # Calculate map center (average of all points)
    avg_lat = sum(r['lat'] for r in restaurants) / len(restaurants)
    avg_lng = sum(r['lng'] for r in restaurants) / len(restaurants)

    # Build markers JSON
    markers_json = json.dumps(restaurants)
    home_json = json.dumps(home_coords) if home_coords else 'null'

    # Generate HTML
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Restaurant Map - {list_prefix} {category}</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        body {{ margin: 0; padding: 0; }}
        #map {{ width: 100%; height: 100vh; }}
        .restaurant-popup {{ min-width: 200px; }}
        .restaurant-popup h3 {{ margin: 0 0 8px 0; color: #333; }}
        .restaurant-popup p {{ margin: 4px 0; color: #666; font-size: 14px; }}
        .restaurant-popup a {{ color: #e74c3c; text-decoration: none; }}
        .restaurant-popup a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        const restaurants = {markers_json};
        const home = {home_json};

        const map = L.map('map').setView([{avg_lat}, {avg_lng}], 12);

        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors'
        }}).addTo(map);

        // Add home marker if available
        if (home) {{
            const homeIcon = L.divIcon({{
                html: '<div style="background:#3498db;color:white;border-radius:50%;width:30px;height:30px;display:flex;align-items:center;justify-content:center;font-size:16px;border:2px solid white;box-shadow:0 2px 5px rgba(0,0,0,0.3);">🏠</div>',
                className: '',
                iconSize: [30, 30],
                iconAnchor: [15, 15]
            }});
            L.marker([home.lat, home.lng], {{icon: homeIcon}})
                .addTo(map)
                .bindPopup('<b>Home</b>');
        }}

        // Add restaurant markers
        restaurants.forEach(r => {{
            const travelInfo = r.travel_time ? `<p>🚇 ${{r.travel_time}} min from home</p>` : '';
            const bookLink = r.venue_id ? `<p><a href="https://resy.com/cities/ny/venues/${{r.venue_id}}" target="_blank">Book on Resy →</a></p>` : '';

            const popupContent = `
                <div class="restaurant-popup">
                    <h3>${{r.name}}</h3>
                    <p>📍 ${{r.location}}</p>
                    <p>🍽️ ${{r.cuisine}}</p>
                    ${{travelInfo}}
                    ${{bookLink}}
                </div>
            `;

            L.marker([r.lat, r.lng])
                .addTo(map)
                .bindPopup(popupContent);
        }});

        // Fit bounds to show all markers
        const allPoints = restaurants.map(r => [r.lat, r.lng]);
        if (home) allPoints.push([home.lat, home.lng]);
        map.fitBounds(allPoints, {{ padding: [50, 50] }});
    </script>
</body>
</html>'''

    # Write HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Map generated: {output_path}")
    print(f"Restaurants mapped: {len(restaurants)}")
    return True


def main():
    parser = argparse.ArgumentParser(description='Google Maps utilities')
    subparsers = parser.add_subparsers(dest='command', help='Command')

    # Geocode command
    geo_parser = subparsers.add_parser('geocode', help='Geocode an address')
    geo_parser.add_argument('address', help='Address to geocode')

    # Travel time command
    travel_parser = subparsers.add_parser('travel-time', help='Get travel time from home')
    travel_parser.add_argument('destination', help='Destination address')
    travel_parser.add_argument('--mode', default='transit',
                               choices=['transit', 'driving', 'walking', 'bicycling'])

    # Update restaurants command
    update_parser = subparsers.add_parser('update-restaurants',
                                          help='Update restaurant CSV with location data')
    update_parser.add_argument('--list', choices=['try', 'love'], required=True,
                               dest='list_type')
    update_parser.add_argument('--category',
                               choices=['dinner', 'brunch', 'lunch', 'drinks'],
                               required=True)

    # Generate map command
    map_parser = subparsers.add_parser('generate-map',
                                       help='Generate interactive HTML map of restaurants')
    map_parser.add_argument('--list', choices=['try', 'love'], required=True,
                            dest='list_type')
    map_parser.add_argument('--category',
                            choices=['dinner', 'brunch', 'lunch', 'drinks'],
                            required=True)
    map_parser.add_argument('--output', '-o', default=None,
                            help='Output HTML file path (default: restaurants_map.html)')

    args = parser.parse_args()

    try:
        api_key = load_maps_credentials()
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.command == 'geocode':
        result = geocode(args.address, api_key)
        print(json.dumps(result, indent=2))

    elif args.command == 'travel-time':
        home = get_home_address()
        result = get_travel_time(home, args.destination, api_key, args.mode)
        print(json.dumps(result, indent=2))

    elif args.command == 'update-restaurants':
        home = get_home_address()
        update_restaurant_csv(args.list_type, args.category, api_key, home)

    elif args.command == 'generate-map':
        # Get home coordinates for the map
        home = get_home_address()
        home_coords = geocode(home, api_key)

        # Default output path
        output_path = args.output
        if not output_path:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_path = os.path.join(script_dir, '..', 'restaurants_map.html')

        generate_map_html(args.list_type, args.category, output_path, home_coords)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
