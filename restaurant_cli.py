#!/usr/bin/env python3
import argparse
from restaurant_directory import RestaurantDirectory, print_restaurants

def main():
    directory = RestaurantDirectory()
    
    parser = argparse.ArgumentParser(description='Restaurant Directory Manager')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add restaurant
    add_parser = subparsers.add_parser('add', help='Add a restaurant')
    add_parser.add_argument('name', help='Restaurant name')
    add_parser.add_argument('status', choices=['love', 'try'], help='love or try')
    add_parser.add_argument('category', choices=['dinner', 'brunch', 'drinks', 'lunch', 'dessert'], help='Category')
    add_parser.add_argument('--location', default='', help='Location')
    add_parser.add_argument('--cuisine', default='', help='Cuisine type')
    add_parser.add_argument('--venue-id', help='Resy venue ID')
    add_parser.add_argument('--notes', default='', help='Notes')
    add_parser.add_argument('--price', default='', help='Price range')
    add_parser.add_argument('--rating', default='', help='Rating')
    
    # List restaurants
    list_parser = subparsers.add_parser('list', help='List restaurants')
    list_parser.add_argument('--status', choices=['love', 'try'], help='Filter by status')
    list_parser.add_argument('--category', choices=['dinner', 'brunch', 'drinks', 'lunch', 'dessert'], help='Filter by category')
    list_parser.add_argument('--simple', action='store_true', help='Simple list without details')
    
    # Search
    search_parser = subparsers.add_parser('search', help='Search restaurants')
    search_parser.add_argument('query', help='Search query')
    
    # Move restaurant
    move_parser = subparsers.add_parser('move', help='Move restaurant between lists')
    move_parser.add_argument('name', help='Restaurant name')
    move_parser.add_argument('from_status', choices=['love', 'try'], help='Current status')
    move_parser.add_argument('to_status', choices=['love', 'try'], help='New status')
    
    # Remove restaurant
    remove_parser = subparsers.add_parser('remove', help='Remove a restaurant')
    remove_parser.add_argument('name', help='Restaurant name')
    
    # Stats
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'add':
        result = directory.add_restaurant(
            name=args.name,
            status=args.status,
            category=args.category,
            location=args.location,
            cuisine=args.cuisine,
            venue_id=getattr(args, 'venue_id', None),
            notes=args.notes,
            price_range=args.price,
            rating=args.rating
        )
        print(result)
    
    elif args.command == 'list':
        restaurants = directory.list_restaurants(args.status, args.category)
        if not any(restaurants.values()):
            print("No restaurants found.")
        else:
            print_restaurants(restaurants, show_details=not args.simple)
    
    elif args.command == 'search':
        results = directory.search_restaurants(args.query)
        if not any(any(cats.values()) for cats in results.values()):
            print(f"No restaurants found matching '{args.query}'")
        else:
            print(f"Search results for '{args.query}':")
            print_restaurants(results)
    
    elif args.command == 'move':
        result = directory.move_restaurant(args.name, args.from_status, args.to_status)
        print(result)
    
    elif args.command == 'remove':
        result = directory.remove_restaurant(args.name)
        print(result)
    
    elif args.command == 'stats':
        stats = directory.get_stats()
        print("\n📊 Restaurant Directory Stats")
        print("=" * 40)
        
        print(f"\n🍽️ PLACES WE LOVE ({stats['totals']['love']} total)")
        for category, count in stats['places_we_love'].items():
            if count > 0:
                emoji_map = {"dinner": "🌙", "brunch": "🌅", "lunch": "☀️", "drinks": "🍸", "dessert": "🧁"}
                print(f"  {emoji_map.get(category, '🍽️')} {category.capitalize()}: {count}")
        
        print(f"\n🎯 PLACES TO TRY ({stats['totals']['try']} total)")
        for category, count in stats['places_to_try'].items():
            if count > 0:
                emoji_map = {"dinner": "🌙", "brunch": "🌅", "lunch": "☀️", "drinks": "🍸", "dessert": "🧁"}
                print(f"  {emoji_map.get(category, '🍽️')} {category.capitalize()}: {count}")
        
        print(f"\n📈 Overall Total: {stats['totals']['overall']} restaurants")

if __name__ == '__main__':
    main()