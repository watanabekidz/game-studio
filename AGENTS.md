# AGENTS

<AGENTS>

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



  ### Updating Engines On Demand
  <ENGINE_UPDATE_ON_DEMAND>
    Before using any engine for game creation, **always pull the latest version**
    to ensure you're working against the most recent upstream changes:

    ```bash
    # Update the engine
    bash engines/update.sh

    # Or update individually
    cd engines/capsule && git pull origin main
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

  ### Engine Sizes & Capabilities

   | Engine | Minified | Gzipped | Physics | Audio | Tilemaps | Best for |
   |---|---|---|---|---|---|---|
   | None (DOM) | 0 KB | 0 KB | — | — | — | Grid games, cards |
   | canvas-engine.js | ~2 KB | ~1 KB | — | — | — | Educational interactives |
   | LittleJS | ~30 KB | ~10 KB | Arcade (AABB) | ZzFX synth | ✅ | Tiny action games |
   | Phaser | ~500 KB | ~120 KB | Arcade + Matter.js | Web Audio | ✅ | Full 2D games, RPGs |
   | Three.js | ~600 KB | ~150 KB | — (add your own) | — | — | 3D visualization |
   | Babylon.js | ~800 KB | ~200 KB | Havok | Web Audio | — | Full 3D games |
   | Ursina | Python | — | ✅ | ✅ | — | Voxel/block games |
   | **Capsule** | three.js runtime | — | ✅ (via cannon-es) | Web Audio | — | 3D scenes, no build, AI-friendly |
   | **NityJS** | ~110 KB | ~25 KB | Rigidbody2D | Web Audio | ✅ | Unity-style 2D, component-based |
   | **BeepMini** | ~132 KB | ~35 KB | Arcade | Chiptune synth | ✅ | Retro 8-bit, fantasy console |

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
   RESEARCH → BRIEF → APPROVE → SCAFFOLD → IMPLEMENT → TEST → REVIEW → OUTPUT → COMMIT
  ```

  ### Phase 0: Research
  <PHASE_RESEARCH>
    Before writing any game brief, conduct structured research to ground design
    decisions in real-world context. This phase prevents building in a vacuum.

    **Required steps:**

    1. **Search comparable games** — Use `websearch` to find 2-3 existing games
       in the same genre. Answer: What mechanics do they share? What's the
       complexity level? What platforms do they target?

    2. **Research genre conventions** — Search for the game genre to identify
       standard mechanics, UX patterns, and scope expectations. For educational
       games, also search learning-science best practices for the target age group.

    3. **Research technical constraints** — If using a new engine from `engines/`
       or `libraries/`, verify it supports the target platform (SCORM, browser, etc.).
       Check the engine's documentation for any API surface or setup requirements.

    4. **(Optional) Study existing open-source implementations** — If the game genre
       has well-established open-source clones, the agent MAY:
       - Reference [`opengaming/osgameclones`](https://github.com/opengaming/osgameclones)
         — a curated database of 1,000+ open-source game clones
       - Browse or clone an open-source (MIT, Apache 2.0, GPL, zlib) implementation
         to study its architecture, data structures, and game loop patterns
       - Start with the curated list in `references/reference-clones.md` for
         hand-picked, well-documented examples with clean architecture
       - Extract DESIGN PATTERNS and ARCHITECTURE IDEAS — never code or assets
       - See the STUDYING_EXISTING_GAMES section below for ethical guidelines

    5. **Log findings in WORKFLOW_STATE.md** — Record research sources and key
       findings under a RESEARCH section. This prevents re-researching later.

    **Output:** A research entry in WORKFLOW_STATE.md with:
    ```
    ## RESEARCH
    **Comparable games**: [titles and key takeaways]
    **Genre conventions**: [patterns identified]
    **Technical constraints**: [engine compatibility notes, platform limits]
    **Open-source references**: [repo URLs and what was learned, if any]
    **Sources**: [links searched]
    ```

    **Entry gate**: Read WORKFLOW_STATE.md — no blocked tasks.
    **Exit gate**: Research logged, ready for brief writing.
  </PHASE_RESEARCH>

  ### Phase 0.5: Brief
  <PHASE_BRIEF>
    Write a structured game brief that captures the full design intent before
    any code is written. This replaces the previous simple spec with a format
    borrowed from professional game design documents, non-fiction briefs, and
    course-studio planning patterns.

    **Required steps:**

    1. Review Phase 0 research findings
    2. Write the game brief using the template below
    3. Run the validation checklist against the brief
    4. Fix any validation failures

    ```
    ## Game Brief: <name>

    ### 1. Core Identity
    - **Logline**: One sentence pitch (fits in a tweet)
    - **Core Pillars**: 3-5 design anchors that define the game
    - **Player Transformation**: What does the player know/feel/do differently after playing?
    - **Genre**: e.g. "Retro 2D platformer", "Educational puzzle", "Top-down RPG"
    - **Platform(s)**: Web, SCORM, or both?
    - **Target Audience**: Age group, gaming experience level
    - **Visual style**: Canvas 2D, DOM, pixel art, three.js 3D?

    ### 2. Game Systems
    - **Core Loop**: The primary action cycle the player repeats
    - **Mechanics**: Rules, interactions, win/lose/draw conditions
    - **Controls**: Input devices and action mappings
    - **Progression**: Scoring, levels, difficulty curve
    - **Data**: Any embedded content (levels, facts, maps, questions)

    ### 3. Scope & Constraints
    - **Engine match**: Which engine/template from templates/, libraries/,
      or engines/ fits best, and why
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
    - [ ] Engine match is justified (not the default pick)
    - [ ] Cut line explicitly states what's NOT included
    - [ ] Assumptions are flagged, not hidden as facts
    - [ ] Research was conducted (Phase 0 completed)
    - [ ] SCORM compatibility checked against the engine table
    ```

    **Entry gate**: Phase 0 research logged in WORKFLOW_STATE.md.
    **Exit gate**: Brief written and validated, ready for user approval.
  </PHASE_BRIEF>

  ### Phase 0.75: Approval
  <PHASE_APPROVAL>
    Present the game brief to the user for approval.

    - **Approved** → proceed to Phase 1 (Scaffold).
    - **Changes requested** → revise brief, re-present.
    - **Rejected** → mark task as `cancelled` in WORKFLOW_STATE.md.

    Include the validation checklist results when presenting:
    ```
    Validation: ✅ 9/9 passed
    Risks flagged: [key risks]
    Research conducted: [sources searched]
    ```
  </PHASE_APPROVAL>

  ### Phase 1: Scaffold
  <PHASE_SCAFFOLD>
    0. **If using a 3D engine** from `engines/`, first run `bash engines/update.sh`
       to pull the latest upstream changes before scaffolding.
    1. Select the best-matching template from `templates/` (or engine from `engines/`)
    2. Read `templates/SCHEMA.md` for variable rules
    3. Copy the template directory to a working location
    4. Populate all `{{variable_name}}` slots
    5. Inline any required libraries from `libraries/`
    6. Generate a `README.md` from the template's `README.md.template`
       (populate `{{game_title}}`, `{{game_description}}`, etc.)
    7. Verify the scaffold produces a valid HTML/Python file

    **Exit gate**: Scaffolded game opens without errors.
    It has placeholder content but runs.
  </PHASE_SCAFFOLD>

  ### Phase 2: Implement
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

    **Exit gate**: All core mechanics work. Code is self-contained.
  </PHASE_IMPLEMENT>

  ### Phase 3: Test
  <PHASE_TEST>
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
  </PHASE_TEST>

  ### Phase 4: Review
  <PHASE_REVIEW>
    Run this checklist:

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
  </PHASE_REVIEW>

  ### Phase 5: Output
  <PHASE_OUTPUT>
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
        - Update `../games/README.md` if adding a notable new game

    2b. For SCORM output:
        - Wrap `index.html` with `scorm-wrapper.js` (inline at top)
        - Append `postMessage` iframe-height footer
        - Generate `imsmanifest.xml` from template
        - Zip: `zip -j <game-name>.zip index.html imsmanifest.xml`
        - Upload via MCG pipeline:
          `media_upload_url` → `curl -T` → `scorm_upload` → `lesson_create`

    **This README cross-reference is required for every standalone output game.**
    It ensures any agent or person browsing the output can find the maker.
  </PHASE_OUTPUT>

  ### Phase 6: Commit
  <PHASE_COMMIT>
    1. Update WORKFLOW_STATE.md: mark task done, log the run, record errors
    2. `cd ../games && git add <game-name>/ && git commit -m "<game-name>: <description>"`
    3. `cd ../game-studio && git add templates/ && git commit -m "studio: <description>"` (if templates changed)
    4. Report summary to user
  </PHASE_COMMIT>

</MAKER_PIPELINE>

## State Persistence
<STATE_PERSISTENCE>
  After EVERY phase transition, update the STATE section of WORKFLOW_STATE.md.
  This ensures that if context is lost, the next agent can reconstruct exactly
  where the pipeline was.

  Fields to update: `current_phase`, `last_phase_completed`, `active_task_id`,
  `active_game_name`.

  To reconstruct after context loss: read WORKFLOW_STATE.md → STATE → resume.
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
