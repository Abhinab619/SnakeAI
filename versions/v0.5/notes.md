# Version 0.1

## What changed
- Reward System : -0.1 for idle, -10 for collision, -1 for being away from food, -10 for longer steps w/o food(added base timeout)
                  +15 for food, +1 for being closer to food
- epsilon change from absolute to relative (now learn till 400th game but still makes random moves after it)


## Results
- No more stucking in loops
- Learns to get food at around 150th game
- Max score of 40 around 500th game


## Known Issue
- Makes random moves and dies
- hitting itself consistently


## Next Plans
- Split collison logic in two
- punish more for hitting itself
- Stabilize epsilon (to stop randomness)
