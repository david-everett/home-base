# Home Base

A life automation platform powered by Claude Code. The goal is to create systems using skills, MCP servers, and custom scripts that maximize Claude's ability to automate personal tasks.

## Philosophy

Build reusable automation patterns that:
- Use natural language as the interface (via Claude Code skills)
- Store data in human-readable formats (markdown) alongside structured formats (JSON)
- Delegate complex logic to scripts that skills can invoke
- Grow incrementally - each new automation follows the same pattern

## Planned Automation Domains

| Domain | Status | Description |
|--------|--------|-------------|
| Restaurants | Active | Check availability on Resy, manage curated lists |
| Calendar/Scheduling | Planned | Meeting scheduling, event reminders |
| Tasks/Productivity | Planned | Todo lists, project tracking |
| Finance/Budgeting | Planned | Expense tracking, budget alerts |

## Architecture

### Building Blocks

1. **Skills** (`.claude/skills/[name]/SKILL.md`)
   - Natural language interface layer
   - Parse user intent, invoke scripts, format output
   - Registered automatically when placed in `.claude/skills/`

2. **Custom Scripts** (Python, Bash, etc.)
   - Contain the automation logic
   - Called by skills with parsed arguments
   - Handle API calls, data processing, external services

3. **Data Files**
   - Markdown (`.md`) - Human-curated lists, easy to read and edit
   - JSON (`.json`) - Structured data for programmatic access

4. **MCP Servers** (optional)
   - External tool integrations
   - Configured in Claude Code settings

### Permissions

Configure in `.claude/settings.local.json`:
```json
{
  "permissions": {
    "allow": [
      "Skill(skill-name)",
      "Bash(python3:*)"
    ]
  }
}
```

## Current Implementation: Restaurant Availability

Reference implementation demonstrating the pattern.

### Components

- **Skill:** `.claude/skills/restaurant-availability/SKILL.md`
- **Script:** `check_restaurants.py` (invokes Resy API)
- **Data:** `restaurants/*.md` (markdown files with venue IDs)
- **Credentials:** `.env` (RESY_API_KEY, RESY_AUTH_TOKEN)

### Usage

Ask naturally: "Check dinner availability next Tuesday in places to try"

The skill parses the query and runs:
```bash
python3 check_restaurants.py --date "next tuesday" --list try --category dinner
```

### Data Structure

Restaurant lists organized by:
- **List type:** `places_we_love` vs `places_to_try`
- **Category:** dinner, brunch, lunch, drinks, dessert

Each restaurant in markdown includes venue ID for API lookups.

## Creating New Automations

Follow this pattern for new domains:

### Step 1: Design the Data Structure

Choose format based on use case:
- Markdown for human-curated lists (restaurants, contacts, bookmarks)
- JSON for structured/computed data (transactions, metrics)

### Step 2: Build the Script

Create a CLI tool that:
- Accepts command-line arguments for flexibility
- Handles the core automation logic (API calls, processing)
- Outputs results in a parseable format

Example: `python3 my_automation.py --arg1 value --arg2 value`

### Step 3: Create the Skill

Add `.claude/skills/[name]/SKILL.md`:

```markdown
---
name: my-automation
description: Brief description for skill discovery
---

# My Automation Skill

## Usage Examples
- "Natural language example 1"
- "Natural language example 2"

## Implementation

When invoked:
1. Parse user query to extract parameters
2. Map to CLI arguments
3. Execute: `python3 my_script.py --args`
4. Format output for user
```

### Step 4: Configure Permissions

Add to `.claude/settings.local.json`:
```json
"Skill(my-automation)"
```

## Key Conventions

- **Markdown for lists** - Human-readable, version-controllable, easy to edit
- **JSON for data** - Structured, queryable, API-friendly
- **Python for logic** - Scripts handle complexity, skills handle NL interface
- **Absolute paths** - Scripts use full paths for reliability
- **Credentials in .env** - Never commit secrets, use environment variables

## Directory Structure

```
Home Base/
├── .claude/
│   ├── skills/
│   │   └── [skill-name]/
│   │       └── SKILL.md
│   ├── settings.json
│   └── settings.local.json
├── [domain]/                    # Data files per domain
│   └── *.md or *.json
├── [script].py                  # Automation scripts
├── .env                         # Credentials (not committed)
└── claude.md                    # This file
```
