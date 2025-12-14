---
name: log-workout
description: Log workouts and check fitness progress against your goals
---

# Log Workout Skill

Track exercises and monitor progress toward fitness goals.

## Usage Examples

### Logging
- "Log squat 200lbs 5 reps 3 sets"
- "Logged bench press 150x5x3 today"
- "Add a 5k run, 27:45"
- "Log deadlift 245lbs for 5 singles"

### Checking Progress
- "How's my squat progressing?"
- "What's my deadlift PR?"
- "Did I hit my workout targets this week?"
- "Show my lifting progress this month"

## Data Sources

- Workouts: `/home/user/home-base/fitness/data/workouts.csv`
- Goals: `/home/user/home-base/fitness/data/goals.json`

## Implementation

### For Logging Workouts

1. **Parse the query** to extract:
   - Exercise: squat, bench_press, deadlift, overhead_press, run, etc.
   - Weight: in lbs (0 for cardio)
   - Reps: number of reps (0 for timed cardio)
   - Sets: number of sets (1 for singles or cardio)
   - Notes: any additional context

2. **Append to workouts.csv**:
   ```csv
   2024-12-14,squat,200,5,3,
   ```

3. **Check for PR**:
   - Compare to goals.json current values
   - If new PR, update goals.json and celebrate

4. **Confirm**:
   ```
   ✓ Logged: Squat 200lbs × 5 reps × 3 sets

   🎉 New PR! Previous best: 195lbs
   Progress toward goal: 200/225 lbs (89%)
   ```

### For Checking Progress

1. **Parse the query** to extract:
   - Exercise (optional, defaults to all)
   - Time period (optional, defaults to all time for PRs, this week for sessions)

2. **Read data files**:
   - Filter workouts.csv by exercise and date
   - Load goals.json for targets

3. **Calculate**:
   - Current PR vs. goal
   - Weekly session count vs. target
   - Progression trend (are weights going up?)

4. **Format response**:
   ```
   Squat Progress:

   Current PR: 195 lbs
   Goal: 225 lbs
   Progress: 87% ████████░░

   Recent sessions:
   - Dec 12: 195 × 5 × 3
   - Dec 8: 195 × 5 × 3
   - Dec 5: 190 × 5 × 3

   Trend: +10 lbs over 2 weeks ↑
   ```

## Notes

- Exercises are normalized: "bench" → "bench_press"
- Weight defaults to lbs
- Cardio uses time in MM:SS format in notes field
