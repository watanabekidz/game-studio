# AGENTS

<AGENTS>

## Mandatory Gate Protocol
<GATE_PROTOCOL>
  ### Phase Transition Gate — MUST READ BEFORE ANY BUILD ACTION

  This project uses `studio-gate.py` to enforce phase ordering. The gate
  maintains a SHA-256 hash chain to detect skipped or tampered steps.

  ### RULES (not suggestions — all are mandatory)

  <GATE_RULES>
    RULE_1: Before calling ANY builder tool or writing any code, you must run:
      `python3 studio-gate.py check --to <phase>`
      If exit code is 2 (GATE BLOCKED), STOP. Read the error and fix it.

    RULE_2: After completing ALL work in a phase, run:
      `python3 studio-gate.py complete --phase <phase> [--validated] [--tag "<note>"]`
      This appends a hash chain entry to studio_state.json.

    RULE_3: The `--validated` flag means you ran the required validation
      for that phase. Only use `--validated` AFTER running validation.
      Do NOT use it as a shortcut.

    RULE_3b (iterative validation loop):
      Always use `validate` before `complete --validated`. The workflow is:
        1. Do the work for a phase
        2. Run validation: `python3 studio-gate.py validate --phase <X> --gate <G> --result <pass|fail>`
        3. If fail → fix issues → re-run validation (go to step 2)
        4. If pass → now `complete --validated` is allowed
        5. The gate BLOCKS `complete --validated` unless the latest
           validation for that phase passed.

    RULE_4: Run `python3 studio-gate.py verify` to check hash chain integrity.
      If it reports a CHAIN BREAK, the state file has been tampered with.
      STOP and report it.

    RULE_5: The `.studio/salt` file is the secret for the hash chain. Never
      print, display, or embed its contents in a prompt or message.

    RULE_6: After context compaction, re-read this section BEFORE
      proceeding. The gate script is the source of truth for what phase
      you're in — not your memory of the conversation.

    RULE_7 (scope enforcement): Before starting work in ANY phase, you MUST
      check the phase scope:
        `python3 studio-gate.py check --to <phase> --scope`
      This prints what work is ALLOWED and what is OUT OF BOUNDS.
      DO NOT do work listed as out-of-bounds. Instead, park the idea:
        `python3 studio-gate.py park --title "<idea>" --description "<why it's out of scope>"`
      Parked ideas are reviewed between phases or at session end.

    RULE_8 (infrastructure boundaries): User requests for gate changes,
      modifications to studio-gate.py, or workflow infrastructure are
      ALWAYS out-of-bounds during game production phases. They MUST be
      parked and reviewed at pipeline end.

    RULE_9b (game-scoped gate — NEVER SKIP THIS):
      The `--game <name>` flag is REQUIRED on every `complete` and `validate`
      command. This:
      a) Ties the hash chain entry to a specific game name (directory name,
         e.g. "snake", "space-invaders")
      b) Enables output-phase validation: when you complete the `output` phase,
         the gate verifies the game directory exists at `../games/<game-name>/`
      c) Enables commit-phase validation: the gate checks `../games/AGENTS.md`
         for a registry entry matching the game
      d) Allows the pre-commit hook in `games/` to block un-gated commits
      
      Without `--game`, the `output` and `commit` phase validators will
      refuse to pass.

    RULE_10 (quality-first engine selection — NEVER SKIP THIS):
      When selecting an engine or template, you MUST:
      a) List ALL plausible engine/template options (minimum 2, max 4)
      b) For each option, evaluate what the engine PROVIDES vs what you
         would need to BUILD — the more you build, the less effort goes
         into game content, and the LOWER the quality
      c) Present the options to the user with a quality comparison table.
         DO NOT default to the lightest option. The lightest option often
         requires the most infrastructure code, leaving less effort for
         the actual game.
      d) The "lightest = best" heuristic is a KNOWN BIAS. Consciously
         override it by comparing "effort spent on engine infrastructure"
         vs "effort spent on game content" for each option.
      e) A recommendation is optional. Presenting a clear choice is mandatory.
  </GATE_RULES>

  ### Valid Phase Sequence

  ```
  None → research
  research → brief
  brief → approve
  approve → scaffold
  scaffold → implement
  implement → test
  test → review
  review → output
  output → commit
  commit → complete
  ```

  ### Quick Reference

  | Action | Command |
  |--------|---------|
  | Check if you can enter a phase (shows scope) | `python3 studio-gate.py check --to <next>` |
  | Mark phase complete (scoped to game) | `python3 studio-gate.py complete --phase <phase> --validated --game <name> --tag "done"` |
  | Record a validation result WITH evidence | `python3 studio-gate.py validate --phase <phase> --gate <gate> --result pass --evidence key=val --game <name>` |
  | Record a work step (minimum steps enforced) | `python3 studio-gate.py set-progress --phase <phase> --message "<what I did>"` |
  | Record an advisory warning | `python3 studio-gate.py warn --phase <phase> --message "<finding>"` |
  | View structured trace events | `python3 studio-gate.py trace [--phase <phase>]` |
  | View gate status | `python3 studio-gate.py status` |
  | View allowed/blocked work in a phase | `python3 studio-gate.py check --to <phase> --scope` |
  | Park an out-of-bounds idea | `python3 studio-gate.py park --title "<idea>"` |
  | Verify chain integrity | `python3 studio-gate.py verify` |
  | Resume after interruption | `python3 studio-gate.py resume` |

  > **IMPORTANT**: The `--game <name>` flag is now REQUIRED for `complete` and
  > `validate` commands. This ties the hash chain entry to a specific game and
  > enables the output-side gate check in `games/verify-gate.py`.

  **Quality enforcement**: `validate --result pass` now requires adequate
  `set-progress` steps (defined per phase) and evidence values matching
  expected patterns. Results in a quality score (🥇GOLD/🥈SILVER/🥉BRONZE/FAIL)
  recorded in `studio_state.json`.
</GATE_PROTOCOL>

## Overview
<OVERVIEW>
  This file defines the game-studio conventions and maker pipeline. It is the
  primary document for AI agents tasked with creating new games. The output
  of this pipeline goes to the sibling `games/` repository.

  The studio provides templates, libraries, and a structured workflow so every
  game is consistent, self-contained, and follows the project's conventions.
</OVERVIEW>

## Project Relationships
<PROJECT_RELATIONSHIPS>
  ```
   game-studio/    ← THE MAKER (templates, libraries, engines, pipeline, conventions)
       │
       │ (output types)
       ├──→ games/          ← Standalone playable games
       └──→ MCG (SCORM)     ← LMS-hosted educational interactives

   The `engines/` directory holds cloned 3D engine tooling used during
   implementation. See the ENGINES section for details.
  ```

  All new games are built in game-studio, then placed into games/.
  Existing games (tic-tac-toe, marco-polo, minecraft) live in games/ already.

  SCORM output goes to the Education MCG pipeline for LMS hosting.
</PROJECT_RELATIONSHIPS>

## Conventions
<CONVENTIONS>

### Output Game Format
<OUTPUT_FORMAT>
  Every game in `games/` follows these rules:
  - HTML games: single `index.html`, vanilla JS, scoped `<style>`
  - Python games: single `.py` file, `try/except` on input handlers
  - Zero external dependencies for HTML games
  - Game surfaces use `user-select: none` (existing pattern)
  - LF line endings (`.gitattributes` enforces this)
  - Works in both Chromium and Firefox
</OUTPUT_FORMAT>

### Templates
<TEMPLATES>
  Templates live in `templates/`. Each template directory contains:
  - An `index.html` with `{{variable_name}}` double-mustache slots
  - A `template.json` with metadata (tier, type, description, variable list)
  - Shared JavaScript from `libraries/` is inlined during scaffolding

  When scaffolding a new game:
  1. Pick the closest-matching template
  2. Populate all `{{variable_name}}` slots with game-specific content
  3. Add game-specific logic in a new `<script>` block
  4. Do NOT modify the shared library code inline — import from libraries/

  See `templates/SCHEMA.md` for the full variable system.
</TEMPLATES>

### Libraries
<LIBRARIES>
  Libraries live in `libraries/`. They provide reusable game infrastructure:

  | Library | Purpose | When to use |
  |---|---|---|
  | `canvas-engine.js` | DPR-aware rendering, game loop, tweening | Any Canvas 2D game |
  | `input-handler.js` | Keyboard tracking, bindings, just-pressed | Any interactive game |
  | `physics-engine.js` | AABB collision, gravity, platform resolve | Platformer, physics games |
  | `particle-system.js` | Emitter-based 2D particle effects | Action games, feedback |
  | `platformer-engine.js` | Player entity, camera, parallax, update loop | Side-scrollers, platformers |
  | `scorm-wrapper.js` | LMSInitialize/LMSSetValue/LMSCommit/LMSFinish | SCORM 1.2 packaging |
  | `littlejs.release.js` | Full 2D game engine (physics, particles, audio, input) | Tiny action games (<50KB) |
  | `zzfxmicro.js` | Procedural sound effect generator | Audio in LittleJS-based games |
  | `phaser.min.js` | Full 2D framework (scenes, tilemaps, Matter.js) | RPGs, complex 2D games |
  | `nity.min.js` | Unity-style 2D engine (GO-Component, physics, tilemaps) | Complex 2D with many interacting objects |
  | `beepmini/b8.min.js` | Retro fantasy console (pixel art, chiptune, tilemaps) | Retro 8-bit games, game jams |

  During scaffolding, library code is inlined into the output HTML file
  so the game remains self-contained. Never create external `<script src=>`
  dependencies in output games.
</LIBRARIES>

### Git
<GIT>
  - Commit format: `<game-name>: <description>` (e.g. `snake: initial implementation`)
  - Commit in `games/` when adding the new game output
  - Commit in `game-studio/` when adding templates or libraries
</GIT>

</CONVENTIONS>

### Engines (3D)
<ENGINES>
  The `engines/` directory holds **cloned 3D engines** used during the maker pipeline.
  These are full upstream repositories cloned as-is (not submodules). They provide
  the runtime for 3D games and are updated on demand.

  | Engine | Location | Run command | Format |
  |---|---|---|---|
  | **Capsule** | `engines/capsule/` | `python3 -m http.server 8000` (in engine dir) | HTML/JS (three.js) — no build step |
  | **RPG-JS** | `engines/rpgjs/` | `npm run dev` (Vite, port 5173) | TypeScript (CanvasEngine) — Vite build step required |

  ### Capsule
  <ENGINE_CAPSULE>
    A minimalist three.js game engine/editor where all game logic is plain HTML, CSS,
    and JavaScript — no build step, no bundler, nothing to compile. Ideal for AI
    agent workflows because every file is readable text.

    **Pipeline integration:**
    1. Agent writes/edits game logic in `engines/capsule/index.html`
    2. Agent places 3D assets (`.glb`) in `engines/capsule/assets/`
    3. Developer opens `http://localhost:8000` to play
    4. Add `?edit` to the URL for the visual editor
    5. Export as standalone app: `engines/capsule/export/build.sh`

    **Key files:** `index.html` (entry), `scene.js` (3D scene logic), `assets/` (GLB models, textures)
  </ENGINE_CAPSULE>



  ### RPG-JS
  <ENGINE_RPGJS>
    A TypeScript framework for building 2D browser RPGs and MMORPGs. Write gameplay
    once, run as a standalone RPG or a networked MMORPG. Provides maps, players,
    events, NPCs, dialog, inventory, skills, save/load, GUI, i18n, and multiplayer
    room synchronization out of the box.

    **License**: MIT — free for commercial use.
    **Upstream**: https://github.com/RSamaium/RPG-JS (branch `v5`)

    **Pipeline integration:**
    1. Agent scaffolds a new RPG project from the starter (`npx degit rpgjs/starter#v5`)
       or uses the sample projects in `engines/rpgjs/samples/` as reference
    2. Agent writes game logic in TypeScript (player, events, maps)
    3. Developer runs `npm run dev` to test in browser
    4. For SCORM output, build with `npm run build` (produces static HTML/JS),
       then wrap with `scorm-wrapper.js`

    **Key directories:**
    - `packages/` — engine packages (server, client, core, GUI, etc.)
    - `samples/sample-dev/` — reference implementation
    - `samples/cloudflare-mmorpg/` — MMORPG on Cloudflare Workers
    - `playground/games/` — independent demo games

    **Run commands:**
    ```bash
    # Dev server (RPG mode)
    cd engines/rpgjs && npm run dev

    # Dev server (MMORPG mode)
    cd engines/rpgjs && RPG_TYPE=mmorpg npm run dev

    # Sample project dev
    cd engines/rpgjs/samples/sample-dev && npm run dev
    ```

    **SCORM note:** RPG-JS has a server/client architecture. In standalone RPG mode,
    `provideRpg()` runs server logic client-side, so the Vite build produces a
    self-contained bundle that can be wrapped with `scorm-again`.
    See the SCORM Output section for the standard wrapping pipeline.
  </ENGINE_RPGJS>


  ### Updating Engines On Demand
  <ENGINE_UPDATE_ON_DEMAND>
    Before using any engine for game creation, **always pull the latest version**
    to ensure you're working against the most recent upstream changes:

    ```bash
    # Update the engine
    bash engines/update.sh

    # Or update individually
    cd engines/capsule && git pull origin main
    cd engines/rpgjs && git pull origin v5
    ```

    This is automated in `engines/update.sh` and is also a required step in the
    Scaffold phase (Phase 1) of the maker pipeline.
  </ENGINE_UPDATE_ON_DEMAND>

</ENGINES>

## Banned / Avoid
<BANNED>
  - **No external dependencies** in output games (CDN, npm, etc.)
  - **No DOM libraries** (jQuery, React, etc.) — vanilla JS only
  - **No build step** — output games must be runnable by opening the file
    (Exception: 3D scenes from `engines/capsule/` require a local HTTP server.)
  - **No skipping phases** in the maker pipeline
  - **No self-approving a review** — run the checklist and confirm each item
  - **No modifying template schemas** without updating SCHEMA.md
  - **No defaulting to the lightest engine without quality analysis.** The
    "lightest = best" heuristic is banned. You MUST compare all plausible
    options on quality factors: built-in features vs what you'd build from
    scratch. An engine that provides more built-in features (tilemaps,
    physics, camera, sprites) means more effort goes into game content,
    which means higher quality.
</BANNED>

## Studying Existing Games (Ethical Guidelines)
<STUDYING_EXISTING_GAMES>
  During Phase 0: Research, agents MAY study existing open-source games to
  understand architecture, mechanics, and design patterns. This is a standard
  industry practice — the academic consensus is that cloning for learning is
  beneficial and widely accepted. However, there are clear ethical boundaries.

  ### ✅ Allowed
  - **Cloning open-source repos** (MIT, Apache 2.0, GPL, zlib, BSD) for local
    study. A curated reference database exists at
    [`opengaming/osgameclones`](https://github.com/opengaming/osgameclones)
    (1,000+ entries).
  - **Reading source code** to understand game loops, ECS patterns, physics
    architectures, or rendering pipelines.
  - **Extracting design ideas** — mechanics, level structures, UX patterns.
    Game mechanics are explicitly NOT copyrightable under US/EU law.
  - **Attributing sources** in the research log.
  - **Building something original** inspired by what you studied.

  ### ❌ NOT Allowed
  - **Copying code** directly (except per the license terms of the source repo).
  - **Copying assets** — art, sprites, audio, 3D models. These ARE copyrightable
    and are NOT covered by "fair use for study."
  - **Creating consumer confusion** — the output game must be clearly distinct
    from the studied game in name, visual style, and branding.
  - **Cloning proprietary/closed-source games** — only open-source repos with
    permissive licenses may be cloned for study.
  - **Distributing cloned code** — clonned repos are for local study only and
    must never be committed to the game-studio or games repositories.
    (The `engines/` and `libraries/` gitignore rules already enforce this.)
  - **Profiting from a clone** — this project produces free, open games only.

  ### 📚 Curated Reference List
  A hand-picked set of exemplary open-source game clones is maintained in
  `references/reference-clones.md`. Each entry was selected for:
  - Clean, well-documented code architecture
  - Permissive license (MIT/Apache 2.0)
  - Relevance to this project's tech stack (HTML5/JS/Canvas)
  - Educational value (design patterns, game loops, architecture)

  This is the **recommended starting point** for study material during research.

  ### 📚 Full Database: osgameclones
  For games not covered by the curated list, the
  [`opengaming/osgameclones`](https://github.com/opengaming/osgameclones)
  repository catalogs 1,000+ open-source game clones organized by original game.
  Browse it via websearch when the curated list doesn't cover a needed genre.
</STUDYING_EXISTING_GAMES>

## Tool Selection Matrix
<TOOL_SELECTION_MATRIX>
  When scoping a new game, use this matrix to pick the right engine and template.
  The choice depends on game type, scope, and output target.

  ### Decision Tree

  ```
   GAME CONCEPT
   │
   ├─ 3D?
   │   ├─ Voxel / block world → Ursina (Python)          [minecraft pattern]
   │   ├─ Interactive 3D scene (no build, AI-friendly)
   │   │   └─ → Capsule/Three.js                        [capsule-scene template]
   │   ├─ Lightweight 3D (vendored) → Three.js           [libraries/]
   │   └─ Full 3D (vendored) → Babylon.js                [libraries/]
  │
   └─ 2D?
       ├─ DOM-based (grid, cards, trivia) → dom-grid   [no engine, tier 1]
       ├─ Educational interactive → canvas-engine.js    [course-studio pattern]
       │
       ├─ Platformer / Action
       │   ├─ Tiny (<50KB target) → LittleJS + ZzFX   [littlejs-action template]
       │   ├─ Full-featured → Phaser                   [phaser-platformer template]
       │   └─ Component-based, Unity-style → NityJS    [nityjs-action template]
       │
       ├─ RPG / Exploration (tilemaps, NPCs, inventory)
       │   ├─ Scene-based → Phaser                     [phaser-rpg template]
       │   └─ Component-based → NityJS                 [nityjs-action template]
       │
       ├─ Retro 8-bit / Pixel art / Fantasy console
       │   └─ → BeepMini                               [beepmini-retro template]
       │
       ├─ Puzzle / Mini-game
       │   ├─ Simple → dom-grid
       │   ├─ Complex → Phaser or LittleJS
       │   └─ Component logic → NityJS                 [nityjs-action template]
       │
       └─ Unity developer / Porting from Unity
           └─ → NityJS                                 [nityjs-action template]
  ```

  ### Quality Comparison Framework

  When selecting an engine, DO NOT default to the lightest option. Instead,
  map the game's required MECHANICS to what each engine PROVIDES vs what
  you'd have to BUILD:

  ```
  Game Mechanic          │ Engine provides it?           │ You build from scratch
  ───────────────────────┼───────────────────────────────┼──────────────────────
  Player movement        │ Phaser, NityJS, LittleJS,     │ canvas-engine.js,
                         │ Capsule, Babylon, Ursina      │ DOM
  Camera / viewport      │ Phaser, NityJS, Capsule       │ canvas-engine.js,
                         │                               │ LittleJS, DOM
  Tilemap / game world   │ Phaser, NityJS, LittleJS,     │ canvas-engine.js,
                         │ BeepMini                      │ DOM, Capsule, 3D
  Sprite rendering       │ Phaser, NityJS, LittleJS,     │ canvas-engine.js,
                         │ BeepMini, Capsule, Three.js   │ DOM
  Physics / collision    │ Phaser, NityJS, LittleJS,     │ canvas-engine.js,
                         │ Capsule, Babylon, Ursina      │ DOM, Three.js
  Audio                  │ Phaser, LittleJS+ZzFX,        │ canvas-engine.js, DOM
                         │ BeepMini, Babylon, Ursina     │
  Scene management       │ Phaser, NityJS, Capsule       │ canvas-engine.js,
                         │                               │ LittleJS, DOM
  NPC / entity system    │ Phaser, NityJS                │ All others
  ```

  **Interpretation**: The more mechanics an engine provides for free, the
  more development effort goes into GAME CONTENT rather than ENGINE
  INFRASTRUCTURE. A 500KB engine that provides tilemaps + camera +
  sprites + physics + scene management can produce a HIGHER QUALITY game
  than a 2KB engine where 80% of the code is building those systems from
  scratch — because more effort goes into the actual game.

  ### Engine Sizes & Capabilities

  ### Available Templates

  | Template | Engine | Type | Output target |
  |---|---|---|---|
  | `dom-grid/` | None (DOM) | Turn-based, grid | `games/` |
  | `canvas-rpg/` | canvas-engine.js | Exploration, Canvas 2D | `games/` |
  | `littlejs-action/` | LittleJS + ZzFX | Platformer, action | `games/` or SCORM |
  | `phaser-platformer/` | Phaser | Platformer, action | `games/` or SCORM |
  | `phaser-rpg/` | Phaser | RPG, exploration | `games/` or SCORM |
   | `three-js-scene/` | Three.js | 3D scene, visualization | `games/` |
   | `babylon-game/` | Babylon.js | 3D game | `games/` |
   | `capsule-scene/` | Three.js / Capsule | AI-friendly 3D, no build step | `games/` or standalone |
   | `nityjs-action/` | NityJS | Unity-style 2D, component-based | `games/` or SCORM |
   | `beepmini-retro/` | BeepMini | Retro 8-bit, pixel art, chiptune | `games/` or SCORM (extra assets) |

  ### SCORM Output

  Any Canvas/2D template **and** the following libraries/engines can produce SCORM 1.2 packages:

  | Engine | SCORM | Notes |
  |---|---|---|
  | LittleJS | ✅ | Self-contained HTML, inline library |
  | Phaser | ✅ | Self-contained HTML, inline library |
  | NityJS | ✅ | Self-contained HTML, inline library |
  | BeepMini | ✅ | Include `beepmini/b8.min.js` + `beepmini/assets/` folder |
  | Capsule | ⚠️ | Use single-file HTML export, then wrap |
  | Three.js/Babylon.js | ✅ | Self-contained HTML, inline library |
  | Ursina (Python) | ❌ | Desktop app, not web |
  | Canvas 2D templates | ✅ | Standard pipeline |

  The standard SCORM pipeline:
  1. Inline `scorm-wrapper.js` at the top of the HTML
  2. Wrap game init with LMS calls (LMSInitialize, LMSSetValue, LMSCommit)  
  3. Generate `imsmanifest.xml` declaring the game a SCO
  4. Zip: `zip -j <game-name>.zip index.html imsmanifest.xml [assets/]`

  When targeting SCORM, the output phase produces a `.zip` instead of (or alongside) the `games/` output. See Phase 5 for details.
</TOOL_SELECTION_MATRIX>

## Maker Pipeline
<MAKER_PIPELINE>

  When asked to create a new game, follow these phases **in strict order**.

   ```
    Phase 0: RESEARCH → Phase 1: BRIEF → Phase 2: APPROVE → Phase 3: SCAFFOLD →
    Phase 4: IMPLEMENT → Phase 5: TEST → Phase 6: REVIEW →
    Phase 7: OUTPUT → Phase 8: COMMIT
   ```

  ### Phase 0: Research
  <PHASE_RESEARCH>
    Before writing any game brief, conduct structured research to ground design
    decisions in real-world context. This phase prevents building in a vacuum.

    **Required steps:**

    0. **Determine game type** — At pipeline start, ask the user:
       - Is this an **educational game** (primary goal: teach a topic)?
       - Or an **entertainment game** (primary goal: fun / challenge)?

       If the user hasn't specified, ask them before proceeding.

       If **educational**:
       - Read `references/game-based-learning.md` for pedagogical guidelines
       - Record in evidence: `game_type=educational`
       - Apply the LM-GM framework: map each learning objective to a game mechanic
       - Use the SCHEMA process: Specification → Content Hierarchy → Engineering → Assessment

       If **entertainment**:
       - Record in evidence: `game_type=entertainment`
       - Proceed with standard game design pipeline (no educational overlays)

       This decision gates the entire pipeline. Record it:
       ```bash
       python3 studio-gate.py set-progress --phase research --message "Game type: educational or entertainment"
       ```

    1. **Run gate entry check:**
       ```bash
       python3 studio-gate.py check --to research
       python3 studio-gate.py set-progress --phase research --message "Starting research"
       ```

    2. **Search comparable games** — Use `websearch` to find 2-3 existing games
       in the same genre. Answer: What mechanics do they share? What's the
       complexity level? What platforms do they target?

    3. **Research genre conventions** — Search for the game genre to identify
       standard mechanics, UX patterns, and scope expectations. For educational
       games, also search learning-science best practices for the target age group.

    4. **Research technical constraints** — If using a new engine from `engines/`
       or `libraries/`, verify it supports the target platform (SCORM, browser, etc.).
       Check the engine's documentation for any API surface or setup requirements.

    5. **(Optional) Study existing open-source implementations** — If the game genre
       has well-established open-source clones, the agent MAY:
       - Reference [`opengaming/osgameclones`](https://github.com/opengaming/osgameclones)
         — a curated database of 1,000+ open-source game clones
       - Browse or clone an open-source (MIT, Apache 2.0, GPL, zlib) implementation
         to study its architecture, data structures, and game loop patterns
       - Start with the curated list in `references/reference-clones.md` for
         hand-picked, well-documented examples with clean architecture
       - Extract DESIGN PATTERNS and ARCHITECTURE IDEAS — never code or assets
       - See the STUDYING_EXISTING_GAMES section below for ethical guidelines

    6. **Log findings** — Record research sources and key findings.

    7. **Record progress for each major step:**
       ```bash
       python3 studio-gate.py set-progress --phase research --message "<what I did>"
       ```

    8. **Validate and complete the phase:**
       ```bash
       python3 studio-gate.py validate --phase research --gate research --result pass --evidence research_complete=<count>_sources --evidence game_type=<educational|entertainment>
       python3 studio-gate.py complete --phase research --validated --tag "Research done"
       ```

    **Entry gate**: `python3 studio-gate.py check --to research`
    **Exit gate**: `python3 studio-gate.py complete --phase research --validated`
  </PHASE_RESEARCH>

  ### Phase 1: Brief
  <PHASE_BRIEF>
    Write a structured game brief that captures the full design intent before
    any code is written. This replaces the previous simple spec with a format
    borrowed from professional game design documents, non-fiction briefs, and
    course-studio planning patterns.

    **Required steps:**

    1. **Run gate entry check:**
       ```bash
       python3 studio-gate.py check --to brief
       python3 studio-gate.py set-progress --phase brief --message "Starting brief"
       ```

    2. Review Phase 0 research findings
    3. Write the game brief using the template below
    4. Run the validation checklist against the brief
    5. Fix any validation failures
    6. Save the brief to `brief-<game-name>.md`
    7. Record progress for each major step:
       ```bash
       python3 studio-gate.py set-progress --phase brief --message "<what I did>"
       ```
    8. Validate and complete the phase:
       ```bash
       python3 studio-gate.py validate --phase brief --gate brief --result pass --evidence brief_written=<game-name>
       python3 studio-gate.py complete --phase brief --validated --tag "Brief ready"
       ```

    ```
    ## Game Brief: <name>

    ### 1. Core Identity
    - **Logline**: One sentence pitch (fits in a tweet)
    - **Core Pillars**: 3-5 design anchors that define the game
    - **Player Transformation**: What does the player know/feel/do differently after playing?
    - **Genre**: e.g. "Retro 2D platformer", "Educational puzzle", "Top-down RPG"
    - **Game type**: Educational or Entertainment? (determined in Phase 0 step 0)
    - **Platform(s)**: Web, SCORM, or both?
    - **Target Audience**: Age group, gaming experience level
    - **Visual style**: Canvas 2D, DOM, pixel art, three.js 3D?

    ### If Educational: Learning Design
    (Required when game_type=educational. Skip for entertainment games.)

    - **Learning objectives**: What specific knowledge/skills will the player gain? (Use Bloom's Taxonomy: remember, understand, apply, analyze, evaluate, create)
    - **Learning mechanics → Game mechanics mapping** (LM-GM model):
      ```
      | Learning objective | Learning mechanic | Game mechanic | In-game implementation |
      |---|---|---|---|
      | ... | Identify, sequence, explore... | Match, arrange, navigate... | ... |
      ```
    - **Integration strategy**: Endogenous (learning IS the gameplay) or exogenous (learning bolted on)? Target endogenous.
    - **Interaction-first design**: How does the player DO something before being told?
    - **Assessment**: How will learning be measured? (Stealth assessment through gameplay, not just external quizzes)
    - **Reference**: See `references/game-based-learning.md` for detailed guidelines

    ### 2. Game Systems
    - **Core Loop**: The primary action cycle the player repeats
    - **Mechanics**: Rules, interactions, win/lose/draw conditions
    - **Controls**: Input devices and action mappings
    - **Progression**: Scoring, levels, difficulty curve
    - **Data**: Any embedded content (levels, facts, maps, questions)

    ### 3. Scope & Constraints
    - **Engine match**: List 2-4 plausible options from templates/, libraries/,
      or engines/. For each, provide:
      * What the engine provides (tilemaps, physics, camera, sprites, etc.)
      * What you would build from scratch
      * A quality assessment: does more effort go into game content or
        engine infrastructure?
      **Do NOT present only one option.**
    - **Engine comparison table**:
      ```
      | Option | Engine | Provides | You build | Effort on content |
      |---|---|---|---|---|
      | A | ... | ... | ... | ~70% |
      | B | ... | ... | ... | ~30% |
      ```
    - **Cut line**: What is explicitly NOT in scope
    - **Dependencies**: Must be zero for HTML games (exception: engines/ or libraries/)
    - **SCORM target**: Yes/No (determines wrapper and packaging)
    - **Estimated complexity**: Small (<100 lines), Medium (<300), Large (300+)

    ### 4. Assumptions & Risk
    - **Research conducted**: Summary of Phase 0 findings
    - **Comparable games**: 1-3 games analyzed and what was learned
    - **Key risks**: Open questions, unknowns, technical challenges
    - **Assumptions log**: Separated facts from inferences (label each as
      "Fact:" or "Assumption:")
    ```

    **Validation checklist** (must pass before approval):

    ```
    Brief Validation:
    - [ ] Logline is one sentence, under 280 chars
    - [ ] Core pillars are 3-5 items, non-overlapping
    - [ ] Player transformation is concrete and measurable
    - [ ] Genre matches a supported engine/template
    - [ ] Engine options presented to user (min 2, max 4)
    - [ ] Quality comparison table included: "engine provides" vs "you build"
    - [ ] User asked for their preference, not told a single choice
    - [ ] Cut line explicitly states what's NOT included
    - [ ] Assumptions are flagged, not hidden as facts
    - [ ] Research was conducted (Phase 0 completed)
    - [ ] SCORM compatibility checked against the engine table
    ```

    **Entry gate**: `python3 studio-gate.py check --to brief`
    **Exit gate**: `python3 studio-gate.py complete --phase brief --validated`
  </PHASE_BRIEF>

  ### Phase 2: Approval
  <PHASE_APPROVAL>
    Present the game brief to the user for approval.

    1. **Run gate entry check:**
       ```bash
       python3 studio-gate.py check --to approve
       python3 studio-gate.py set-progress --phase approve --message "Presenting brief for approval"
       ```

    2. Present the engine/template options as a **menu of choices** with a
       recommendation, not as a single dictated decision. The user should
       be able to choose.

    3. Include the validation checklist results when presenting:
       ```
       Validation: ✅ 9/9 passed
       Engine options: [A/B/C/D with recommendation]
       Risks flagged: [key risks]
       Research conducted: [sources searched]
       ```

    4. After user response:
       - **Approved** → validate and complete the phase, proceed to Scaffold:
         ```bash
         python3 studio-gate.py validate --phase approve --gate approval --result pass --evidence user_approved=yes
         python3 studio-gate.py complete --phase approve --validated --tag "User approved"
         ```
       - **Changes requested** → revise brief, re-present.
       - **Rejected** → mark task as `cancelled` in state.

    **Entry gate**: `python3 studio-gate.py check --to approve`
    **Exit gate**: `python3 studio-gate.py complete --phase approve --validated`
  </PHASE_APPROVAL>

  ### Phase 3: Scaffold
  <PHASE_SCAFFOLD>
    0. **Run gate entry check:**
       ```bash
       python3 studio-gate.py check --to scaffold
       python3 studio-gate.py set-progress --phase scaffold --message "Starting scaffold"
       ```
    1. **If using a 3D engine** from `engines/`, first run `bash engines/update.sh`
       to pull the latest upstream changes before scaffolding.
    2. Select the best-matching template from `templates/` (or engine from `engines/`)
       per the user's approved choice from Phase 2 (Approval).
    3. Read `templates/SCHEMA.md` for variable rules
    4. Copy the template directory to a working location
    5. Populate all `{{variable_name}}` slots
    6. Inline any required libraries from `libraries/`
    7. Generate a `README.md` from the template's `README.md.template`
       (populate `{{game_title}}`, `{{game_description}}`, etc.)
    8. Verify the scaffold produces a valid HTML/Python file
    9. Record progress and complete:
       ```bash
       python3 studio-gate.py set-progress --phase scaffold --message "<what I did>"
       python3 studio-gate.py validate --phase scaffold --gate scaffold --result pass --evidence template_used=<template_name>
       python3 studio-gate.py complete --phase scaffold --validated --tag "Scaffold done"
       ```

    **Entry gate**: `python3 studio-gate.py check --to scaffold`
    **Exit gate**: `python3 studio-gate.py complete --phase scaffold --validated`
  </PHASE_SCAFFOLD>

  ### Phase 4: Implement
  <PHASE_IMPLEMENT>
    Add game-specific logic:

    **Step 1: Source assets (if needed)**
    If the game requires sprites, audio, or visual assets beyond what can be
    procedurally generated, source them from free asset libraries:

    | Library | Type | License | Best for |
    |---|---|---|---|
    | [Kenney.nl](https://kenney.nl) | 2D sprites, 3D models, UI, audio | CC0 (no credit needed) | **Best single source** — 60,000+ consistent-style assets |
    | [OpenGameArt.org](https://opengameart.org) | 2D, 3D, audio | Mixed (filter by CC0) | Community art, retro/pixel styles |
    | [itch.io Free Assets](https://itch.io/game-assets/free) | 2D, 3D, audio | Varies by creator | Indie art packs, complete kits |
    | [CraftPix](https://craftpix.net/freebies) | 2D sprites, tilesets, UI | Attribution required | Polished 2D game art |
    | [Quaternius](https://quaternius.com) | 3D models (low-poly) | CC0 | 3D games using Capsule/Three.js |
    | [Poly Haven](https://polyhaven.com) | 3D models, PBR textures, HDRIs | CC0 | Photorealistic 3D assets |
    | [Freesound.org](https://freesound.org) | Sound effects, music | Varies (filter by CC0) | Audio-only needs |
    | [Game-Icons.net](https://game-icons.net) | UI icons | CC0/CC-BY | UI element icons |
    | [Piskel](https://www.piskelapp.com) | Pixel art editor (in-browser) | Free tool | Creating custom pixel art |

    **Asset rules for this project:**
    - Prefer CC0-licensed assets (no attribution needed, no restrictions)
    - For CC-BY assets, include attribution in the game's README.md
    - For SCORM output, ALL assets must be embedded or shipped alongside the
      HTML file (no CDN URLs)
    - Procedural generation (ZzFX audio, Canvas primitives, Graphics primitives)
      is preferred over external assets when possible — it keeps games self-contained

    **Step 2: Implement game logic**
    - Core mechanics from the game brief
    - Win/lose/draw conditions
    - Score tracking, levels, progression
    - Edge case handling (rapid input, empty states, boundary conditions)

    Follow the conventions in the CONVENTIONS section of this file.
    Do NOT mark implementation complete until all brief mechanics exist.

    **Gate commands**:
    ```bash
    python3 studio-gate.py check --to implement
    # ...do the work...
    python3 studio-gate.py set-progress --phase implement --message "<what I did>"
    python3 studio-gate.py validate --phase implement --gate implement --result pass --evidence mechanics_done=<count>
    python3 studio-gate.py complete --phase implement --validated --tag "Implementation done"
    ```

    **Entry gate**: `python3 studio-gate.py check --to implement`
    **Exit gate**: `python3 studio-gate.py complete --phase implement --validated`
  </PHASE_IMPLEMENT>

  ### Phase 5: Test
  <PHASE_TEST>
    **Gate entry**:
    ```bash
    python3 studio-gate.py check --to test
    python3 studio-gate.py set-progress --phase test --message "Starting tests"
    ```

    **For HTML games:**
    1. Open in browser (file:// works)
    2. Verify no console errors
    3. Walk through every mechanic (start, play, win/lose, restart)
    4. Test edge cases: rapid input, boundary conditions, empty states
    5. Check in Firefox if Chromium was used (and vice versa)

    **For Python games:**
    1. Run `python <game>.py` — no import errors
    2. Play one full session
    3. Test `try/except` handlers with malformed input
    4. Verify `crash.log` is written on error

    **If tests fail:**
    1. Diagnose (console error, visual bug, logic error)
    2. Fix and retest
    3. Same failure 3 times → record in ERROR_LOG, escalate to user

    **Gate exit**:
    ```bash
    python3 studio-gate.py set-progress --phase test --message "<results>"
    python3 studio-gate.py validate --phase test --gate test --result pass --evidence tests_passed=<chromium|firefox|both>
    python3 studio-gate.py complete --phase test --validated --tag "Tests passed"
    ```

    **Entry gate**: `python3 studio-gate.py check --to test`
    **Exit gate**: `python3 studio-gate.py complete --phase test --validated`
  </PHASE_TEST>

  ### Phase 6: Review
  <PHASE_REVIEW>
    **Gate entry**:
    ```bash
    python3 studio-gate.py check --to review
    python3 studio-gate.py set-progress --phase review --message "Starting review"
    ```

    Run this checklist and fix any failures:

    ```
    Review Checklist:
    - [ ] Follows output format conventions (single-file, vanilla JS, scoped CSS)
    - [ ] No banned patterns (npm, DOM libs, hardcoded secrets)
    - [ ] Game is self-contained (no external file dependencies)
    - [ ] Edge cases handled (empty state, rapid input, boundaries)
    - [ ] Works in both Chromium and Firefox
    - [ ] Test results recorded in WORKFLOW_STATE.md
    - [ ] Matches the approved game brief (logline, pillars, mechanics)
    ```

    **Gate exit**:
    ```bash
    python3 studio-gate.py set-progress --phase review --message "Checklist passed"
    python3 studio-gate.py validate --phase review --gate review --result pass --evidence checklist_run=<pass_count>/<total>
    python3 studio-gate.py complete --phase review --validated --tag "Review passed"
    ```

    **Entry gate**: `python3 studio-gate.py check --to review`
    **Exit gate**: `python3 studio-gate.py complete --phase review --validated`
  </PHASE_REVIEW>

  ### Phase 7: Output
  <PHASE_OUTPUT>
    **Gate entry**:
    ```bash
    python3 studio-gate.py check --to output
    python3 studio-gate.py set-progress --phase output --message "Starting output placement"
    ```

    1. Determine output target:
       - **Standalone**: game goes to `../games/<game-name>/`
       - **SCORM**: game is packaged as a SCORM 1.2 zip
       - **Both**: do both

    2a. For standalone output:
        - Create a `README.md` with game-studio attribution
        - Copy to `../games/<game-name>/`:
          - `index.html` or `.py` file
          - `README.md` (required — cross-reference to game-studio)
          - `requirements.txt` (only for Python games)
        - Verify it runs from its new location
        - Update the output registry in `../games/AGENTS.md`

    2b. For SCORM output:
        - Wrap `index.html` with `scorm-wrapper.js` (inline at top)
        - Append `postMessage` iframe-height footer
        - Generate `imsmanifest.xml` from template
        - Zip: `zip -j <game-name>.zip index.html imsmanifest.xml`
        - Upload via MCG pipeline:
          `media_upload_url` → `curl -T` → `scorm_upload` → `lesson_create`

    **This README cross-reference is required for every standalone output game.**
    It ensures any agent or person browsing the output can find the maker.

    **Gate exit**:
    ```bash
    python3 studio-gate.py set-progress --phase output --message "Game placed in ../games/<game-name>/"
    python3 studio-gate.py validate --phase output --gate output --result pass --evidence output_placed=<game-dir-name> --game <game-dir-name>
    python3 studio-gate.py complete --phase output --validated --game <game-dir-name> --tag "Output done"
    ```
    
    > **Note**: `--game <game-dir-name>` (e.g. `--game snake`) is REQUIRED here.
    > The output phase validator verifies that `../games/<game-dir-name>/index.html`
    > exists before allowing the gate to pass. The pre-commit hook in `games/`
    > will block commits for any game not in the gate chain.

    **Entry gate**: `python3 studio-gate.py check --to output`
    **Exit gate**: `python3 studio-gate.py complete --phase output --validated`
  </PHASE_OUTPUT>

  ### Phase 8: Commit
  <PHASE_COMMIT>
    **Gate entry**:
    ```bash
    python3 studio-gate.py check --to commit
    python3 studio-gate.py set-progress --phase commit --message "Committing game"
    ```

    1. Update WORKFLOW_STATE.md: mark task done, log the run, record errors
    2. `cd ../games && git add <game-name>/ && git commit -m "<game-name>: <description>"`
    3. `cd ../game-studio && git add templates/ && git commit -m "studio: <description>"` (if templates changed)
    4. Report summary to user

    **Gate exit**:
    ```bash
    python3 studio-gate.py validate --phase commit --gate commit --result pass --evidence committed=<sha> --game <game-dir-name>
    python3 studio-gate.py complete --phase commit --validated --game <game-dir-name> --tag "Committed"
    python3 studio-gate.py check --to complete
    python3 studio-gate.py complete --phase complete --validated --game <game-dir-name> --tag "Pipeline complete"
    ```
    
    > **Note**: The commit phase validator checks that `../games/AGENTS.md`
    > contains a registry entry for the game. Update the output registry BEFORE
    > running commit validation.

    **Entry gate**: `python3 studio-gate.py check --to commit`
    **Exit gate**: `python3 studio-gate.py complete --phase complete --validated`
  </PHASE_COMMIT>

</MAKER_PIPELINE>

## State Persistence
<STATE_PERSISTENCE>
  The gate state in `studio_state.json` is the authoritative source of truth
  for what phase you're in. The hash chain prevents tampering.

  After EVERY phase transition:
  1. `python3 studio-gate.py complete` handles state automatically
  2. Optionally update WORKFLOW_STATE.md for human readability

  To reconstruct after context loss:
  ```bash
  python3 studio-gate.py resume
  ```
  This reads the gate state and tells you exactly where to pick up.
  The gate is the source of truth — not your memory or the conversation.
</STATE_PERSISTENCE>

## Error Recovery
<ERROR_RECOVERY>
  | Error Type | Handling |
  |---|---|
  | Test failure (first attempt) | Diagnose and fix, retest |
  | Test failure (3 attempts) | Record in ERROR_LOG, escalate |
  | Import/runtime error | Check dependencies, fix, retest |
  | Agent context loss | Reload AGENTS.md + WORKFLOW_STATE.md → resume |
  | Brief rejected | Revise brief per feedback, re-present |
  | Task infeasible | Mark `blocked` with reason, move to next task |
</ERROR_RECOVERY>

## Self-Audit
<SELF_AUDIT>
  After any game-studio change:
  1. Templates still produce valid output (open a scaffolded game)
  2. Libraries still inline correctly
  3. WORKFLOW_STATE.md STATE section is current
  4. No files created outside expected directories
</SELF_AUDIT>

## Hybrid Format Note
<HYBRID_FORMAT>
  This file uses both `## SECTION` Markdown headings and `<SECTION>` XML tags
  for cross-model compatibility. When adding new sections, include both.
</HYBRID_FORMAT>

</AGENTS>

<!-- SPECKIT-BRIDGE START -->
# Spec-Driven Development (Spec Kit)

This project uses Spec Kit. Requirements are written down before code is written, and the
artifacts under `specs/` are the source of truth.

**First act of any session in this project: check the workflow before acting.** If the request
is software work, `spec-driven-development` applies — do not improvise from memory. Prefer
`.opencode/commands/speckit.md` (the `/speckit` entry point): it classifies the request, picks the
smallest workflow that fits, and routes. You are not exempt because the task looks simple.

**Load the `spec-driven-development` skill before specifying, planning, or implementing.**
It carries the workflow, approval gates, traceability and verification rules.

**The skill loads on roughly 60% of relevant requests — `/speckit` is the reliable path.** Invoke
it when you need the workflow to apply for certain.

**End every response with the four-bucket handoff** — Done (with evidence) · Continuing · Decision
needed · Approval required — defined in `.opencode/autonomy-contract.md`. Reversible, in-scope work
is autonomous; only the irreversible, external, or costly needs approval.

## Two rules that are enforced, not advised

`.opencode/hook/hooks.yaml` (requires the `opencode-yaml-hooks` plugin) runs below the prompt layer,
so unlike everything above it cannot be talked out of:

- **`git commit --no-verify` is blocked.** Do not try to skip the project's checks, and do not route
  around this with an equivalent — fix what the check is complaining about, or run the check
  directly to see the failure.
- **Generated files are not hand-edited.** `.opencode/commands/speckit*.md`, `.specify/scripts/`,
  `.specify/templates/` and `.specify/presets/` are regenerated and an edit there is lost. Change
  the kit instead. `.specify/memory/constitution.md` and `specs/` are yours to edit.

## If you cannot invoke `/speckit.*` commands

Agents that do not read `.opencode/commands/` (e.g. Freebuff/Codebuff) can run each step by
reading the command prompt directly and following it as instructions:

| Step | File |
| --- | --- |
| entry point | `.opencode/commands/speckit.md` |
| fast lane (small work) | `.opencode/commands/speckit.quick.md` |
| constitution | `.opencode/commands/speckit.constitution.md` |
| specify | `.opencode/commands/speckit.specify.md` |
| plan | `.opencode/commands/speckit.plan.md` |
| tasks | `.opencode/commands/speckit.tasks.md` |
| implement | `.opencode/commands/speckit.implement.md` |
| converge | `.opencode/commands/speckit.converge.md` |
| clarify | `.opencode/commands/speckit.clarify.md` |
| analyze | `.opencode/commands/speckit.analyze.md` |
| checklist | `.opencode/commands/speckit.checklist.md` |

Substitute the user's feature description wherever the prompt expects `$ARGUMENTS`.
<!-- SPECKIT-BRIDGE END -->
<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
<!-- SPECKIT END -->

<!-- SPECKIT-COMMANDS START -->
## Commands

Detected for this project by `speckit-init`. Run `./scripts/verify` for test → lint → typecheck.

| Purpose | Command |
| --- | --- |
| install | unresolved — set by hand, or re-run `speckit-init` after adding a manifest |
| test | unresolved — set by hand, or re-run `speckit-init` after adding a manifest |
| lint | unresolved — set by hand, or re-run `speckit-init` after adding a manifest |
| typecheck | unresolved — set by hand, or re-run `speckit-init` after adding a manifest |
| build | unresolved — set by hand, or re-run `speckit-init` after adding a manifest |
<!-- SPECKIT-COMMANDS END -->
