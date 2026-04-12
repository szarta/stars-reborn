# Stars Reborn — Schemas

JSON Schema definitions for all Stars Reborn game objects and API contracts.

This is a standalone artifact. Both `stars-reborn-engine` and `stars-reborn-ui`
depend on these schemas directly. The `stars-reborn-game` integration repo
bundles them into the final application so no online connectivity is required
at runtime.

For the meaning and design rationale behind each schema, see
`stars-reborn-design`.

## Contents

| Schema | Description |
|--------|-------------|
| `battle.json` | Battle report: rounds, events, surviving/destroyed ships |
| `planet.json` | Planet state: hab values, minerals, population, infrastructure, owner |
| `player.json` | Player state: race, known planets, fleets, tech levels |
| `race.json` | Race definition: PRT, LRTs, economy parameters, hab ranges, tech costs |
| `tech.json` | Technology item catalog: all 180+ items with costs, stats, and requirements |
| `turn.json` | Turn input/output wrapper: player orders in, game state out |
| `universe.json` | Universe snapshot: all planets, all fleets, all players |
| `request-create-new-game.json` | API request to create a new game |
| `request-create-tutorial-game.json` | API request to create a tutorial game |
| `request-validate-race.json` | API request to validate a race design |
| `response-create-new-game.json` | API response for new game creation |
| `response-create-tutorial-game.json` | API response for tutorial game creation |
| `response-validate-race.json` | API response for race validation |
