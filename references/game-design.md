# Game Design Reference
<GAME_DESIGN_REFERENCE>
  Patterns and conventions for game design in this project.
</GAME_DESIGN_REFERENCE>

## Existing Game Patterns
<EXISTING_PATTERNS>
  | Game | Type | Pattern | What makes it work |
  |---|---|---|---|
  | Tic Tac Toe | DOM grid, turn-based | Event delegation, CSS Grid, win-combination check | Simple state machine, readable minimax AI |
  | Marco Polo | Canvas 2D, exploration | Game loop with delta time, HUD overlay trading/quizzes, NPC data as JSON | Data-driven NPCs/locations, embedded quiz system |
  | Minecraft Clone | Python 3D, sandbox | 2D Perlin noise heightmap, block dictionary, try/except input handlers | Simple block type system, seed-based procedural generation |

## Recommended Architecture by Game Type
<RECOMMENDED_ARCHITECTURE>
  | Game Type | Engine | Architecture |
  |---|---|---|
  | Turn-based (board, card, puzzle) | DOM (no canvas needed) | State machine → render → event handler → repeat |
  | Real-time 2D (action, platformer, RPG) | Canvas 2D | Game loop (dt) → update state → render → input poll |
  | Educational (quiz, explore) | Canvas 2D + DOM overlay | Data-driven content + canvas rendering + HUD panels |
  | 3D sandbox | Python + Ursina | Entity system, block dictionary, input try/except |

## Cross-Cutting Concerns
<CROSS_CUTTING>
  - **State machine**: Every game should have a clear state machine (menu/playing/paused/gameover)
  - **Score/Progress**: Use localStorage for persistence (optional, fail gracefully)
  - **Responsive**: HTML games should work at 320px minimum width
  - **Audio**: Web Audio API, no external audio files
</CROSS_CUTTING>
