#!/usr/bin/env python3
import json
from typing import List, Dict, Optional
from datetime import datetime

class RestaurantDirectory:
    def __init__(self, data_file: str = "restaurant_directory.json"):
        self.data_file = data_file
        self.restaurants = self.load_data()
    
    def load_data(self) -> Dict:
        """Load restaurant data from JSON file"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "places_we_love": {
                    "dinner": [],
                    "brunch": [],
                    "drinks": [],
                    "lunch": [],
                    "dessert": []
                },
                "places_to_try": {
                    "dinner": [],
                    "brunch": [],
                    "drinks": [],
                    "lunch": [],
                    "dessert": []
                }
            }
    
    def save_data(self):
        """Save restaurant data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.restaurants, f, indent=2)
    
    def add_restaurant(self, name: str, status: str, category: str, 
                      location: str = "", cuisine: str = "", 
                      venue_id: str = None, notes: str = "", 
                      price_range: str = "", rating: str = ""):
        """Add a restaurant to the directory"""
        if status not in ["love", "try"]:
            raise ValueError("Status must be 'love' or 'try'")
        
        if category not in ["dinner", "brunch", "drinks", "lunch", "dessert"]:
            raise ValueError("Category must be one of: dinner, brunch, drinks, lunch, dessert")
        
        restaurant = {
            "name": name,
            "location": location,
            "cuisine": cuisine,
            "venue_id": venue_id,
            "notes": notes,
            "price_range": price_range,
            "rating": rating,
            "added_date": datetime.now().isoformat()
        }
        
        status_key = "places_we_love" if status == "love" else "places_to_try"
        self.restaurants[status_key][category].append(restaurant)
        self.save_data()
        
        return f"Added {name} to {status_key.replace('_', ' ')} → {category}"
    
    def list_restaurants(self, status: str = None, category: str = None) -> Dict:
        """List restaurants by status and/or category"""
        if status and status not in ["love", "try"]:
            raise ValueError("Status must be 'love' or 'try'")
        
        if category and category not in ["dinner", "brunch", "drinks", "lunch", "dessert"]:
            raise ValueError("Category must be one of: dinner, brunch, drinks, lunch, dessert")
        
        result = {}
        
        for status_key, categories in self.restaurants.items():
            status_name = status_key.replace("places_", "").replace("_", " ")
            
            # Filter by status if specified
            if status:
                target_status = "places_we_love" if status == "love" else "places_to_try"
                if status_key != target_status:
                    continue
            
            result[status_name] = {}
            
            for cat_name, restaurants in categories.items():
                # Filter by category if specified
                if category and cat_name != category:
                    continue
                
                if restaurants:  # Only include categories with restaurants
                    result[status_name][cat_name] = restaurants
        
        return result
    
    def search_restaurants(self, query: str) -> Dict:
        """Search restaurants by name, location, or cuisine"""
        query = query.lower()
        results = {"we love": {}, "to try": {}}
        
        for status_key, categories in self.restaurants.items():
            status_name = status_key.replace("places_", "").replace("_", " ")
            
            for category, restaurants in categories.items():
                matches = []
                for restaurant in restaurants:
                    # Search in name, location, cuisine, notes
                    searchable = f"{restaurant.get('name', '')} {restaurant.get('location', '')} {restaurant.get('cuisine', '')} {restaurant.get('notes', '')}".lower()
                    
                    if query in searchable:
                        matches.append(restaurant)
                
                if matches:
                    if category not in results[status_name]:
                        results[status_name][category] = []
                    results[status_name][category] = matches
        
        return results
    
    def move_restaurant(self, name: str, from_status: str, to_status: str) -> str:
        """Move a restaurant from 'try' to 'love' or vice versa"""
        if from_status not in ["love", "try"] or to_status not in ["love", "try"]:
            raise ValueError("Status must be 'love' or 'try'")
        
        from_key = "places_we_love" if from_status == "love" else "places_to_try"
        to_key = "places_we_love" if to_status == "love" else "places_to_try"
        
        # Find and remove restaurant from source
        restaurant_found = None
        source_category = None
        
        for category, restaurants in self.restaurants[from_key].items():
            for i, restaurant in enumerate(restaurants):
                if restaurant['name'].lower() == name.lower():
                    restaurant_found = restaurants.pop(i)
                    source_category = category
                    break
            if restaurant_found:
                break
        
        if not restaurant_found:
            return f"Restaurant '{name}' not found in {from_key.replace('_', ' ')}"
        
        # Add to destination
        self.restaurants[to_key][source_category].append(restaurant_found)
        self.save_data()
        
        return f"Moved {name} from {from_key.replace('_', ' ')} to {to_key.replace('_', ' ')}"
    
    def remove_restaurant(self, name: str) -> str:
        """Remove a restaurant from the directory"""
        for status_key, categories in self.restaurants.items():
            for category, restaurants in categories.items():
                for i, restaurant in enumerate(restaurants):
                    if restaurant['name'].lower() == name.lower():
                        removed = restaurants.pop(i)
                        self.save_data()
                        return f"Removed {removed['name']} from {status_key.replace('_', ' ')} → {category}"
        
        return f"Restaurant '{name}' not found"
    
    def get_stats(self) -> Dict:
        """Get statistics about the directory"""
        stats = {
            "places_we_love": {},
            "places_to_try": {},
            "totals": {"love": 0, "try": 0, "overall": 0}
        }
        
        for status_key, categories in self.restaurants.items():
            status_name = status_key.replace("places_", "").replace("_", " ")
            
            for category, restaurants in categories.items():
                count = len(restaurants)
                stats[status_key][category] = count
                
                if "love" in status_key:
                    stats["totals"]["love"] += count
                else:
                    stats["totals"]["try"] += count
        
        stats["totals"]["overall"] = stats["totals"]["love"] + stats["totals"]["try"]
        return stats

def print_restaurants(restaurants_dict: Dict, show_details: bool = True):
    """Pretty print restaurant directory"""
    for status, categories in restaurants_dict.items():
        if not categories:
            continue
            
        print(f"\n{'='*50}")
        print(f"🍽️  {status.upper()}")
        print('='*50)
        
        for category, restaurants in categories.items():
            if not restaurants:
                continue
                
            # Category emoji mapping
            emoji_map = {
                "dinner": "🌙",
                "brunch": "🌅", 
                "lunch": "☀️",
                "drinks": "🍸",
                "dessert": "🧁"
            }
            
            print(f"\n{emoji_map.get(category, '🍽️')} {category.upper()} ({len(restaurants)})")
            print("-" * 40)
            
            for restaurant in restaurants:
                name = restaurant['name']
                location = restaurant.get('location', '')
                cuisine = restaurant.get('cuisine', '')
                notes = restaurant.get('notes', '')
                venue_id = restaurant.get('venue_id', '')
                
                print(f"• {name}")
                
                if show_details:
                    details = []
                    if location: details.append(f"📍 {location}")
                    if cuisine: details.append(f"🍜 {cuisine}")
                    if venue_id: details.append(f"🆔 {venue_id}")
                    if notes: details.append(f"💭 {notes}")
                    
                    for detail in details:
                        print(f"  {detail}")
                
                if show_details and restaurant != restaurants[-1]:
                    print()

if __name__ == "__main__":
    # Demo with your restaurants
    directory = RestaurantDirectory()
    
    # Add your sample restaurants
    sample_restaurants = [
        # Dinner places we love
        ("Watawa", "love", "dinner", "Astoria", "Sushi", None, "Amazing sushi"),
        ("Lilia", "love", "dinner", "Williamsburg", "Italian", None, "Best pasta"),
        ("Il Posto Accanto", "love", "dinner", "EV", "Italian", None, "Cozy spot"),
        
        # Places to try for dinner
        ("Mono Mono", "try", "dinner", "Bowery", "Korean", None, "Heard great things"),
        ("Menkoi Sato", "try", "dinner", "WV", "Ramen", None, ""),
        ("Au Zaatar", "try", "dinner", "EV", "Middle Eastern", None, ""),
        ("Fonda", "try", "dinner", "Park Slope", "Mexican", None, ""),
        ("Don Udon", "try", "dinner", "Crown Heights", "Japanese", None, ""),
        
        # Brunch spots to try  
        ("Yellow Rose", "try", "brunch", "EV", "Tex-Mex", "53048", "Donuts on weekends"),
        
        # Drinks
        ("Cervezaria Havemeyer", "try", "drinks", "", "", None, ""),
        
        # Lunch/casual
        ("Outside dumpling story", "love", "lunch", "Grant St", "Skewers", None, "After 5pm, cash only"),
        ("Chili", "try", "lunch", "Murray Hill", "", None, ""),
    ]
    
    print("🍽️ Setting up your restaurant directory...")
    
    for name, status, category, location, cuisine, venue_id, notes in sample_restaurants:
        try:
            directory.add_restaurant(name, status, category, location, cuisine, venue_id, notes)
        except:
            pass  # Skip duplicates
    
    print("\n🎯 Your Restaurant Directory")
    all_restaurants = directory.list_restaurants()
    print_restaurants(all_restaurants)
    
    print("\n📊 STATS")
    stats = directory.get_stats()
    print(f"Places We Love: {stats['totals']['love']}")
    print(f"Places To Try: {stats['totals']['try']}")
    print(f"Total: {stats['totals']['overall']}")
    
    print(f"\n💡 Search example: directory.search_restaurants('sushi')")
    print(f"💡 Move to favorites: directory.move_restaurant('Mono Mono', 'try', 'love')")