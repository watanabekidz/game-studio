# Template Schema
<TEMPLATE_SCHEMA>
  Documentation for the template variable system.
</TEMPLATE_SCHEMA>

## Variable Convention
<VARIABLE_CONVENTION>
  Templates use `{{variable_name}}` double-mustache delimiters for slots
  that get replaced with game-specific content during scaffolding.

  Variable types:
  - `{{title}}` — Game title (string)
  - `{{description}}` — One-line game description (string)
  - `{{controls}}` — Controls help text (string)
  - `{{instruction}}` — In-game instruction text (string)
  - `{{style_overrides}}` — Additional CSS rules (string)
  - `{{game_script}}` — Game-specific JS logic (string)
  - `{{library_canvas_engine}}` — Inlined canvas-engine.js (string, populated by scaffolder)

  README variables (required for every output):
  - `{{game_title}}` — Game title (same as `{{title}}`)
  - `{{game_description}}` — One-line description (same as `{{description}}`)
  - `{{run_instructions}}` — How to open / run the game
</VARIABLE_CONVENTION>

## Template Directory Structure
<TEMPLATE_DIRECTORY>
  Each template lives in `templates/<name>/` and contains:
  ```
  templates/<name>/
    index.html              ← Main game file with {{variable}} slots
    README.md.template      ← Output README with {{game_title}} etc.
    template.json           ← Metadata: name, description, variables[], tier
  ```

  `template.json` format:
  ```json
  {
    "name": "dom-grid",
    "description": "Grid-based game using DOM elements (like Tic Tac Toe)",
    "tier": 1,
    "type": "turn-based",
    "variables": ["title", "description", "style_overrides", "game_script"],
    "libraries": [],
    "target": "html"
  }
  ```
</TEMPLATE_DIRECTORY>

## Template Tiers
<TEMPLATE_TIERS>

  | Tier | Description | Example |
  |---|---|---|
  | 1 | Simple DOM-based game | Tic Tac Toe clone |
  | 2 | Canvas 2D game with rendering loop | Snake, Pong |
  | 3 | Canvas 2D game with map/state | RPG-like, exploration |
  | 4 | Python 3D game | Ursina-based block game |
</TEMPLATE_TIERS>
