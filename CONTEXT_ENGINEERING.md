# Context Engineering: Making AI Actually Useful

## The Problem

Most people use AI like a magic 8-ball:

```
User: "Find me a good restaurant for Saturday"
AI: "Here are some popular restaurants in your area: The Cheesecake Factory..."
User: *closes tab*
```

Generic input → generic output. The AI doesn't know your preferences, your lists, your constraints.

## The Insight

Claude Code changed how developers work with AI. Not because the model got smarter, but because it has **context**:

- `CLAUDE.md` — Project conventions, architecture decisions
- Codebase files — Actual code to reference
- Skills — Workflows encoded as reusable patterns

The result: AI that understands *your* project and gives *specific* answers.

**This pattern works for everything, not just code.**

## The Context Engineering Framework

Three layers turn generic AI into a personalized assistant:

```
┌─────────────────────────────────────────┐
│            NATURAL LANGUAGE             │  ← You talk normally
├─────────────────────────────────────────┤
│               SKILLS                    │  ← Encoded workflows
├─────────────────────────────────────────┤
│            STRUCTURED DATA              │  ← Your context
└─────────────────────────────────────────┘
```

### Layer 1: Structured Data (Your Context)

Raw information organized for AI consumption:

| Format | Best For | Example |
|--------|----------|---------|
| CSV | Lists with IDs, queryable data | Restaurant venues with Resy IDs |
| JSON | Hierarchical, complex relationships | Categorized lists with metadata |
| Markdown | Human-curated, narrative | Notes, preferences, rules |

**Key principle:** Store data in formats that are both human-readable AND machine-parseable.

### Layer 2: Skills (Encoded Workflows)

Skills bridge natural language and action:

```markdown
# Skill: Check Restaurant Availability

## What it does
Queries Resy API for your curated restaurant lists

## Inputs (parsed from natural language)
- Date: "tomorrow", "next Saturday", "Dec 20"
- List: "places we love", "places to try"
- Meal: dinner, brunch, lunch, drinks
- Party size: defaults to 2

## Action
python3 scripts/check_availability.py --date {date} --list {list} --category {meal}

## Output
Available restaurants with time slots and booking links
```

**Key principle:** Skills translate intent into executable actions.

### Layer 3: Natural Language (Your Interface)

With context and skills in place, you just talk:

```
"What's available for dinner Saturday in places to try?"
```

The AI:
1. Parses intent → date: Saturday, list: try, meal: dinner
2. Invokes skill → runs availability script
3. Returns personalized results → your restaurants, filtered by your preferences

---

## Before & After

### Without Context Engineering

```
You: "Help me find a restaurant for Saturday"

AI: "I'd recommend checking OpenTable or Yelp for restaurants in your area.
     Some popular options include..."

Result: Useless generic advice
```

### With Context Engineering

```
You: "What's available Saturday in places to try?"

AI: [Queries your curated list against Resy API]

    Available for Saturday Dec 14 (party of 2):

    ✓ Lilia - 6:00 PM, 6:30 PM, 7:00 PM
    ✓ Don Angie - 5:30 PM, 8:00 PM
    ✗ Carbone - No availability

    Book: [direct Resy links]

Result: Actionable, personalized, immediate
```

---

## The Pattern Applied

### Domain: Restaurants (Implemented)

| Layer | Implementation |
|-------|----------------|
| Data | `places_to_try_dinner.csv`, `directory.json` |
| Skills | `restaurant-availability`, `add-restaurant` |
| Scripts | `check_availability.py`, `resy_client.py` |
| Query | "Check dinner Saturday in places we love" |

### Domain: Personal Finance (Example)

| Layer | Implementation |
|-------|----------------|
| Data | `transactions.csv`, `budgets.json`, `accounts.md` |
| Skills | `spending-summary`, `budget-check`, `log-expense` |
| Scripts | `analyze_spending.py`, `plaid_client.py` |
| Query | "How much did I spend on food this month?" |

### Domain: Fitness (Example)

| Layer | Implementation |
|-------|----------------|
| Data | `workouts.csv`, `goals.json`, `measurements.md` |
| Skills | `log-workout`, `weekly-summary`, `progress-check` |
| Scripts | `analyze_fitness.py`, `apple_health.py` |
| Query | "How's my running progress this month?" |

### Domain: Reading/Learning (Example)

| Layer | Implementation |
|-------|----------------|
| Data | `books.csv`, `reading_list.json`, `notes/` |
| Skills | `add-book`, `reading-summary`, `find-notes` |
| Scripts | `goodreads_client.py`, `search_notes.py` |
| Query | "What did I highlight in Thinking Fast and Slow?" |

---

## Building Your Own Context System

### Step 1: Identify the Domain

Pick something you do repeatedly that involves:
- A set of data you reference
- Decisions based on that data
- Actions you take as a result

Good candidates: restaurants, expenses, workouts, reading, travel, contacts, recipes

### Step 2: Structure Your Data

Ask: "What would the AI need to know to help me?"

```
Restaurants → venue names, IDs for booking APIs, my ratings
Expenses → transactions, categories, budget limits
Workouts → exercises, weights, dates, goals
```

Choose format based on use:
- CSV for lists you'll query programmatically
- JSON for nested/hierarchical data
- Markdown for rules, preferences, notes

### Step 3: Build the Scripts

Create CLI tools that:
- Accept parameters (date, category, amount)
- Query APIs or process data files
- Return structured output

```bash
python3 check_availability.py --date "saturday" --list "love"
python3 log_expense.py --amount 42.50 --category "food" --note "lunch"
python3 log_workout.py --exercise "squat" --weight 185 --reps 5
```

### Step 4: Create the Skills

Write skill files that:
- Describe the workflow in plain english
- Map natural language to script parameters
- Format output for readability

### Step 5: Use It

Talk naturally. Let the system do the translation.

---

## Why This Works

1. **Persistence** — Your context lives in files, not chat history
2. **Precision** — Structured data beats conversational description
3. **Composability** — Skills can be combined, extended, shared
4. **Ownership** — Your data stays yours, in formats you control

---

## The Mental Model

Think of it as building a "second brain" that AI can actually read:

| Without Context | With Context |
|-----------------|--------------|
| AI is a stranger | AI knows your stuff |
| Every conversation starts from zero | Context persists |
| Generic advice | Specific actions |
| You do the work | AI does the work |

---

## Getting Started

1. **Pick one domain** — Start small, prove the pattern
2. **Dump your data** — Get it out of your head and into files
3. **Write one script** — Automate one query or action
4. **Create one skill** — Make it conversational
5. **Use it for a week** — Refine based on real usage

The goal isn't to automate everything. It's to make AI useful for *your* life.

---

## Next Steps

Explore the reference implementation in this repo:
- `/restaurants/` — Full working example
- `/.claude/skills/` — Skill definitions
- `/CLAUDE.md` — Project conventions

Or start building your own domain following the pattern above.
