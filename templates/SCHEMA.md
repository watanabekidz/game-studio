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

  Engine variables (populated by scaffolder, one per template):
  - `{{library_littlejs}}` — Inlined littlejs.release.js
  - `{{library_zzfx}}` — Inlined zzfxmicro.js
  - `{{library_phaser}}` — Inlined phaser.min.js
  - `{{library_nity}}` — Inlined nity.min.js
  - `{{library_beepmini}}` — Inlined beepmini/b8.min.js
  - `{{library_scorm}}` — Inlined scorm-wrapper.js (optional, for SCORM output)

  README variables (required for every output):
  - `{{game_title}}` — Game title (same as `{{title}}`)
  - `{{game_description}}` — One-line description (same as `{{description}}`)
  - `{{run_instructions}}` — How to open / run the game

  SCORM variables (optional, for LMS packaging):
  - `{{scorm_interaction_code}}` — Unique kebab-case slug for postMessage
  - `{{scorm_lesson_title}}` — Lesson title shown in the LMS
  - `{{scorm_script}}` — SCORM API calls (init, score, complete, finish)
</VARIABLE_CONVENTION>

## Template Directory Structure
<TEMPLATE_DIRECTORY>
  Each template lives in `templates/<name>/` and contains:
  ```
  templates/<name>/
    index.html                      ← Main game file with {{variable}} slots
    README.md.template              ← Output README with {{game_title}} etc.
    template.json                   ← Metadata: name, description, variables[], tier
    imsmanifest.xml.template        ← SCORM manifest (only for SCORM-capable templates)
  ```

  `template.json` format:
  ```json
  {
    "name": "littlejs-action",
    "description": "Platformer/action game using LittleJS engine",
    "tier": 2,
    "type": "platformer",
    "engine": "littlejs",
    "variables": ["title", "description", "controls", "style_overrides", "game_script"],
    "libraries": ["littlejs.release.js", "zzfxmicro.js"],
    "scorm": true,
    "target": "html"
  }
  ```

  New fields:
  - `engine` — Engine this template uses (null / "littlejs" / "phaser" / "nityjs" / "beepmini" / "three" / "babylon")
  - `scorm` — Whether this template supports SCORM output (boolean)
  - `scorm_note` — Optional note about SCORM packaging for this template
  - `extra_assets` — Additional asset directories to copy during scaffolding
  - `scorm_extra_files` — Extra files to include in SCORM zip
</TEMPLATE_DIRECTORY>

## Template Tiers
<TEMPLATE_TIERS>

  | Tier | Description | Engine | Example |
  |---|---|---|---|
  | 1 | Simple DOM-based game | None | Tic Tac Toe clone |
  | 2 | Canvas 2D game with rendering loop | LittleJS / None | Platformer, Snake |
  | 3 | Canvas 2D game with map/state | Phaser / canvas-engine.js | RPG, exploration |
  | 4 | Web 3D game | Three.js / Babylon.js | 3D scene, block game |
  | 5 | Python 3D game | Ursina | Voxel block game |
</TEMPLATE_TIERS>
