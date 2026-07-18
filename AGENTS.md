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
  game-studio/    ← THE MAKER (templates, libraries, pipeline, conventions)
      │
      │ (output)
      ▼
  games/          ← THE OUTPUT (playable games, one directory per game)
  ```

  All new games are built in game-studio, then placed into games/.
  Existing games (tic-tac-toe, marco-polo, minecraft) live in games/ already.
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
  | `input-handler.js` | Unified keyboard/mouse/touch input | Any interactive game |

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

## Banned / Avoid
<BANNED>
  - **No external dependencies** in output games (CDN, npm, etc.)
  - **No DOM libraries** (jQuery, React, etc.) — vanilla JS only
  - **No build step** — output games must be runnable by opening the file
  - **No skipping phases** in the maker pipeline
  - **No self-approving a review** — run the checklist and confirm each item
  - **No modifying template schemas** without updating SCHEMA.md
</BANNED>

## Maker Pipeline
<MAKER_PIPELINE>

  When asked to create a new game, follow these phases **in strict order**.

  ```
  DESIGN → APPROVE → SCAFFOLD → IMPLEMENT → TEST → REVIEW → OUTPUT → COMMIT
  ```

  ### Phase 0: Design
  <PHASE_DESIGN>
    Before writing any code, write a game spec:

    ```
    ## Game Spec: <name>
    - **Concept**: 2-3 sentence pitch
    - **Core mechanics**: Interaction model, rules, win/lose conditions
    - **Controls**: Keyboard, mouse, touch?
    - **Visual style**: Canvas, DOM, CSS shapes, pixel art?
    - **Data**: Levels, facts, maps, or other embedded content
    - **Template match**: Which template in templates/ fits best
    - **Dependencies**: Must be zero for HTML games
    - **Estimated complexity**: Small (<100 lines), Medium (<300), Large (300+)
    ```

    **Entry gate**: Read WORKFLOW_STATE.md — no blocked tasks.
    **Exit gate**: Spec written, ready for approval.
  </PHASE_DESIGN>

  ### Phase 0.5: Approval
  <PHASE_APPROVAL>
    Present the spec to the user for approval.
    - Approved → proceed to Phase 1.
    - Changes requested → revise spec, re-present.
    - Rejected → mark task as `cancelled` in WORKFLOW_STATE.md.
  </PHASE_APPROVAL>

  ### Phase 1: Scaffold
  <PHASE_SCAFFOLD>
    1. Select the best-matching template from `templates/`
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
    - Core mechanics from the spec
    - Win/lose/draw conditions
    - Score tracking, levels, progression
    - Edge case handling (rapid input, empty states, boundary conditions)

    Follow the conventions in the CONVENTIONS section of this file.
    Do NOT mark implementation complete until all spec mechanics exist.

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
    - [ ] Matches the approved spec
    ```
  </PHASE_REVIEW>

  ### Phase 5: Output
  <PHASE_OUTPUT>
    1. Create a `README.md` in the game directory with:
       - Game title and one-line description
       - "Built by the game-studio template system" attribution
       - Link back to `../game-studio/`
       - How to open / run the game
    2. Copy the finished game to `../games/<game-name>/`:
       - `index.html` or `.py` file
       - `README.md` (required — cross-reference to game-studio)
       - `requirements.txt` (only for Python games)
    3. Verify it runs from its new location (file paths are relative)
    4. Update `../games/README.md` if adding a notable new game

    **This README cross-reference is required for every output game.**
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
  | Design rejected | Revise spec per feedback, re-present |
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
