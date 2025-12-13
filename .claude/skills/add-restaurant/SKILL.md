---
name: add-restaurant
description: Add restaurants to your lists by searching Resy and confirming before adding
---

# Add Restaurant Skill

Add restaurants to your curated lists by searching the Resy API. This skill handles the full conversational flow: search, disambiguate, confirm, and add.

## Usage Examples

- "Add Yellow Rose to places to try"
- "Add Lilia to places we love for dinner"
- "Add a restaurant called Dhamaka"

## Implementation

When invoked, follow this conversational flow:

### Step 1: Parse the Request

Extract from the user's message:
- **Restaurant name** (required): The venue to search for
- **List type** (optional): "places to try" / "to try" → `try`, "places we love" / "love" / "favorites" → `love`
- **Category** (optional): dinner, brunch, lunch, drinks

### Step 2: Search Resy

Run the search command:
```bash
python3 restaurants/scripts/add_restaurant.py search "restaurant name"
```

This returns JSON with matching venues:
```json
[
  {
    "venue_id": 53048,
    "name": "Yellow Rose",
    "cuisine": "Tex-Mex",
    "location": "East Village",
    "rating": 4.7
  }
]
```

### Step 3: Handle Results

**If no results:** Tell the user no matches were found on Resy.

**If one result:** Skip to confirmation (Step 4).

**If multiple results:** Present numbered options and ask user to pick:
```
Found 2 matches:
1. Yellow Rose - Tex-Mex, East Village (4.7 stars)
2. Centro Balneare Yellow Boat - Italian, Italy

Which one?
```

### Step 4: Gather Missing Info

If list type wasn't specified, ask:
- "Which list: places to try or places we love?"

If category wasn't specified, ask:
- "What category: dinner, brunch, lunch, or drinks?"

### Step 5: Confirm Before Adding

Always confirm before adding:
```
Add Yellow Rose (Tex-Mex, East Village) to places_to_try_dinner.csv?
```

### Step 6: Add to List

On confirmation, run:
```bash
python3 restaurants/scripts/add_restaurant.py add \
  --venue-id 53048 \
  --name "Yellow Rose" \
  --location "East Village" \
  --cuisine "Tex-Mex" \
  --list try \
  --category dinner
```

Report success or failure to the user.

## Parsing Patterns

| User says | List type | Category |
|-----------|-----------|----------|
| "places to try" / "to try" / "want to try" | try | - |
| "places we love" / "favorites" / "love" | love | - |
| "for dinner" / "dinner spot" | - | dinner |
| "for brunch" | - | brunch |
| "for lunch" | - | lunch |
| "for drinks" / "bar" | - | drinks |

## Available Lists

- `places_to_try_dinner.csv`
- `places_to_try_brunch.csv`
- `places_to_try_lunch.csv`
- `places_to_try_drinks.csv`
- `places_we_love_dinner.csv`
- `places_we_love_lunch.csv`

## Error Handling

- **No Resy results:** "Couldn't find [name] on Resy. Check the spelling or try a different name."
- **Already in list:** The script detects duplicates by venue ID and reports it.
- **Invalid list/category combo:** If a file doesn't exist (e.g., places_we_love_brunch.csv), inform the user.
