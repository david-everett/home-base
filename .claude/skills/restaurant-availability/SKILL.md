---
name: restaurant-availability
description: Check restaurant availability from your organized lists (places we love vs places to try) for specific dates, with automatic filtering to exclude late dining after 8:30pm
---

# Restaurant Availability Skill

This skill checks restaurant availability from your organized markdown files in the `restaurants/` directory. It can handle natural language queries and automatically filters out late dining slots.

## Usage Examples

- "Look up dinner spots next tuesday in places i want to try"
- "Check brunch availability tomorrow in places we love" 
- "Find lunch spots this friday to try"

## Implementation

When invoked:

1. **Parse the user's natural language query** to extract:
   - Date (next tuesday, tomorrow, this friday, etc.)
   - List type (places we love vs places to try)
   - Category (dinner, brunch, lunch, drinks)

2. **Map to CLI arguments** for check_restaurants.py:
   - "places to try" / "places i want to try" / "to try" → `--list try`
   - "places we love" / "we love" / "favorites" → `--list love`
   - Extract date verbatim → `--date "next tuesday"`
   - Extract category → `--category dinner`

3. **Construct and execute command:**
   ```bash
   python3 restaurants/scripts/check_availability.py \
       --date "next tuesday" \
       --list try \
       --category dinner \
       --party-size 2 \
       --max-time 20:30 \
       --concise
   ```

4. **Parse and format output** for user-friendly presentation

## Query Parsing Examples

| User Query | Parsed Arguments |
|------------|------------------|
| "dinner next tuesday in places to try" | `--date "next tuesday" --list try --category dinner` |
| "brunch tomorrow at places we love" | `--date tomorrow --list love --category brunch` |
| "lunch this friday to try" | `--date "this friday" --list try --category lunch` |
| "drinks on 2025-12-20 at our favorites" | `--date 2025-12-20 --list love --category drinks` |

## Natural Language Patterns

**List type indicators:**
- "places to try" / "want to try" / "to try" → `--list try`
- "places we love" / "we love" / "favorites" / "our favorites" → `--list love`

**Date indicators:**
- "next tuesday" / "tomorrow" / "this friday" / "weekend" → pass as-is to `--date`
- Explicit dates (2025-12-20) → pass as-is to `--date`

**Category indicators:**
- "dinner" / "supper" → `--category dinner`
- "brunch" → `--category brunch`
- "lunch" → `--category lunch`
- "drinks" / "cocktails" → `--category drinks`

## Default Parameters

- Party size: 2 (can be overridden if user mentions "for 4", "party of 6", etc. → `--party-size N`)
- Max time: 20:30 (8:30pm) - filters out late dining slots (via `--max-time 20:30`)
- Concise output: enabled by default (`--concise`) - shows time ranges instead of listing all individual slots for faster processing

## Required Files

- `restaurants/scripts/check_availability.py` - Unified CLI script with full parameterization
- `restaurants/scripts/resy_client.py` - Core ResyChecker class and date parsing
- `.env` - API credentials (RESY_API_KEY, RESY_AUTH_TOKEN)
- `restaurants/data/*.csv` - CSV files with restaurant data and venue IDs