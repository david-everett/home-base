---
name: add-restaurant
description: Add restaurants to your lists by searching Resy and confirming before adding (project)
---

# Add Restaurant Skill

Add restaurants to your curated lists by searching the Resy API. Uses a streamlined checkbox UI to gather list/category in one step.

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

**If no results:** Offer to add anyway (see Step 3a below).

**If multiple results:** Use AskUserQuestion with options for each match:
```
questions: [{
  question: "Which restaurant?",
  header: "Restaurant",
  options: [
    { label: "Yellow Rose", description: "Tex-Mex, East Village (4.7★)" },
    { label: "Yellow Boat", description: "Italian, Italy (4.2★)" }
  ],
  multiSelect: false
}]
```

**If one result (or after selection):** Proceed to Step 4.

### Step 3a: Fallback for Non-Resy Restaurants

When Resy search returns no results:

1. **Ask if they want to add anyway:**
```
questions: [{
  question: "[Restaurant] isn't on Resy. Add it anyway?",
  header: "Not on Resy",
  options: [
    { label: "Yes, add it", description: "I'll look up the details for you" },
    { label: "No, skip it", description: "Cancel adding this restaurant" }
  ],
  multiSelect: false
}]
```

2. **If yes, use WebSearch** to find restaurant info:
```
WebSearch: "[restaurant name] NYC restaurant"
```

3. **Present findings for verification** (combine with list/category selection):
```
questions: [
  {
    question: "Found info for [Restaurant]. Confirm details?",
    header: "Location",
    options: [
      { label: "[Found Location]", description: "From web search" },
      { label: "Other", description: "Enter manually" }
    ],
    multiSelect: false
  },
  {
    question: "Cuisine type?",
    header: "Cuisine",
    options: [
      { label: "[Found Cuisine]", description: "From web search" },
      { label: "Other", description: "Enter manually" }
    ],
    multiSelect: false
  },
  // Include list and category questions as in Step 4
]
```

4. **Add without venue_id** - proceed to Step 5 with no `--venue-id` flag.

### Step 4: Gather Missing Info & Confirm (Single UI)

Use AskUserQuestion to gather all missing info in ONE call. Include only questions for missing fields:

```
questions: [
  {
    question: "Which list for [Restaurant Name]?",
    header: "List",
    options: [
      { label: "Places to try", description: "Restaurants you want to check out" },
      { label: "Places we love", description: "Your favorites" }
    ],
    multiSelect: false
  },
  {
    question: "What category?",
    header: "Category",
    options: [
      { label: "Dinner", description: "Evening meals" },
      { label: "Brunch", description: "Weekend brunch spots" },
      { label: "Lunch", description: "Midday meals" },
      { label: "Drinks", description: "Bars and cocktails" }
    ],
    multiSelect: false
  }
]
```

If list and category were already specified in the original request, skip directly to adding.

### Step 5: Add to List

**For Resy restaurants** (with venue_id):
```bash
python3 restaurants/scripts/add_restaurant.py add \
  --venue-id 53048 \
  --name "Yellow Rose" \
  --location "East Village" \
  --cuisine "Tex-Mex" \
  --list try \
  --category dinner
```

**For non-Resy restaurants** (no venue_id):
```bash
python3 restaurants/scripts/add_restaurant.py add \
  --name "Inday" \
  --location "Flatiron" \
  --cuisine "Indian" \
  --list try \
  --category lunch
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

- **No Resy results:** Offer fallback flow (Step 3a) to add manually with web search.
- **Already in list:** The script detects duplicates by venue ID (for Resy) or by name (for non-Resy).
- **Invalid list/category combo:** If a file doesn't exist (e.g., places_we_love_brunch.csv), inform the user.
