---
name: spending-summary
description: Check spending and budget status from your personal finance data
---

# Spending Summary Skill

Check your spending against budgets and analyze expenses.

## Usage Examples

- "How much have I spent on dining this month?"
- "Am I on track for my food budget?"
- "What did I spend last week?"
- "Show me my biggest expenses this month"
- "How much am I over budget on shopping?"

## Data Sources

- Transactions: `/home/user/home-base/finance/data/transactions.csv`
- Budgets: `/home/user/home-base/finance/data/budgets.json`

## Implementation

When the user asks about spending:

1. **Parse the query** to extract:
   - Time period: "this month", "last week", "December"
   - Category: "dining", "food", "transport" (optional, defaults to all)
   - Comparison: budget check vs. raw total

2. **Read the data files**:
   - Load transactions.csv and filter by date range
   - Load budgets.json if doing budget comparison

3. **Calculate**:
   - Sum spending by category for the period
   - Compare against monthly budget limits (pro-rated if partial month)
   - Identify largest transactions if requested

4. **Format response**:
   ```
   December spending (as of Dec 14):

   Category      | Spent   | Budget  | Status
   --------------|---------|---------|--------
   Dining        | $221.00 | $500.00 | ✓ On track
   Food          | $104.50 | $400.00 | ✓ On track
   Subscriptions | $12.99  | $100.00 | ✓ On track
   Shopping      | $89.00  | $300.00 | ✓ On track
   Transport     | $18.50  | $200.00 | ✓ On track
   Coffee        | $15.00  | $50.00  | ✓ On track

   Total: $460.99
   ```

5. **Alert** if spending exceeds 80% of budget (configurable threshold in budgets.json)

## Notes

- Budgets are monthly; pro-rate when checking mid-month
- Categories in transactions map to budget categories
- "On track" means projected month-end spending stays under budget
