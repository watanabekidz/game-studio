# Existing-Project Inspection

## Repository Structure
- `game-studio` is a **maker/toolkit repo**, not a deployed application: it produces games that land in the sibling repo `../games/` (README.md:26; AGENTS.md `<OUTPUT_FORMAT>`).
- Top-level components: `AGENTS.md` (primary conventions + maker pipeline, 1057 lines), `WORKFLOW_STATE.md` (task tracking), `studio-gate.py` (phase-transition gate CLI), `studio_state.json` (gate state), `templates/` (7 templates), `libraries/` (shared JS, inlined at scaffold), `engines/` (cloned upstream engines, gitignored), `references/`, `scaffolds/`.
- `.studio/` holds `salt` + `gate.log`; `.opencode/` holds commands, skills and a `hook/hooks.yaml`.
- `.specify/` was just installed (init-options.json: `speckit_version` 1.0.13, `integration` opencode, `script` sh, `here: true`).
- `templates/` contains 7 dirs: `dom-grid`, `canvas-rpg`, `littlejs-action`, `phaser-platformer`, `nityjs-action`, `beepmini-retro`, `capsule-scene` (directory listing; matches audit-report.md:43). AGENTS.md also names `phaser-rpg`, `three-js-scene`, `babylon-game` templates that are not present as directories.
- `engines/` = `capsule/` (three.js, no build) and `rpgjs/` (TypeScript/Vite), cloned upstream repos, not submodules (AGENTS.md `<ENGINES>`; `.gitignore` excludes `engines/`).

## Application Entry Points
- Documentation/agent entry point: `AGENTS.md` ("START HERE", README.md:32) — read before any game work.
- Enforced workflow entry point: `python3 studio-gate.py <command>` (check/validate/complete/…); the gate is declared "the source of truth" for phase state (AGENTS.md `<STATE_PERSISTENCE>`, RULE_6).
- Output game entry points: HTML games = single `index.html`; Python games = single `.py` file (AGENTS.md `<OUTPUT_FORMAT>`).
- Only scaffolded pipeline run found: `scaffolds/the-travellers-tale/` — Vite project (`package.json` scripts `dev: vite`, `build: vite build`; `index.html`; `src/`; `dist/`).

## Relevant Components
- `studio-gate.py` — phase gate, SHA-256 hash chain, validators, evidence-pattern checks, scope enforcement, parking lot (whole file, lines 1–1134).
- `studio_state.json` — authoritative state: `validation_chain` (11 entries, genesis + 9 phases + complete), per-phase `quality_levels` all `gold`, `trace_events`, `advisory_warnings`, `parking_lot`.
- Templates: each has `index.html` with `{{variable}}` slots, `template.json` metadata, `README.md.template`; SCORM-capable ones add `imsmanifest.xml.template` (templates/dom-grid/template.json; templates/SCHEMA.md).
- Libraries: `canvas-engine.js`, `input-handler.js`, `physics-engine.js`, `particle-system.js`, `platformer-engine.js`, `scorm-wrapper.js`, plus vendored `littlejs.release.js`, `zzfxmicro.js`, `phaser.min.js`, `nity.min.js`, `beepmini/b8.min.js` (libraries/README.md).
- References: `game-design.md`, `game-based-learning.md` (LM-GM / SCHEMA / MDA frameworks), `reference-clones.md`, `browserquest/` clone.
- `.opencode/hook/hooks.yaml` — two enforced hooks (block `--no-verify`/`core.hooksPath`/`commit -n`; protect generated `.specify`/`.opencode/commands` files).

## Test Strategy
- **No automated test framework exists** — no pytest/jest/npm test config found for the studio itself (searched package.json/pyproject/test configs; only scaffold & engine package.json files exist).
- Testing is **manual, per-phase**, prescribed in AGENTS.md Phase 5 `<PHASE_TEST>`:
  - HTML: open in browser (file://), verify no console errors, walk every mechanic, test edge cases (rapid input, boundaries, empty states), check both Chromium and Firefox.
  - Python: run the file, play a full session, test `try/except` handlers with malformed input, verify `crash.log` on error.
- Gate evidence for the test phase must match `tests_passed=<chromium|firefox|both>` (studio-gate.py:298, 118–121).

## Build and Deployment
- **No CI/CD**: `.github/workflows/` does not exist.
- HTML output: **no build step**, single self-contained file, runnable by opening it (BANNED: external deps, build step; exception: Capsule 3D needs a local HTTP server, AGENTS.md `<ENGINES>`).
- SCORM output: inline `scorm-wrapper.js`, generate `imsmanifest.xml`, `zip -j <game-name>.zip index.html imsmanifest.xml [assets/]`, upload via MCG pipeline (AGENTS.md Phase 7, `<SCORM Output>`).
- Standalone output: copy to `../games/<game-name>/` with a required `README.md` cross-reference; update output registry in `../games/AGENTS.md`; a pre-commit hook in `games/` blocks un-gated commits (AGENTS.md Phase 7/8; studio-gate.py:876–921).
- Engines updated on demand via `bash engines/update.sh` (git pull --ff-only) before scaffolding (AGENTS.md `<ENGINE_UPDATE_ON_DEMAND>`).
- Decorated git history via gate hash chain; quality scored GOLD/SILVER/BRONZE/FAIL (studio-gate.py:284–288, 469–480).

## Coding Conventions
- Template slots use `{{variable_name}}` double-mustache; variable list documented in `templates/SCHEMA.md` (SCHEMA.md:8–37).
- Output games: single `index.html`, vanilla JS, scoped `<style>`, no external deps, no DOM libraries, no build step; Python games single `.py` with `try/except` on input handlers; `user-select: none` on game surfaces; **LF line endings** (`.gitattributes`: `* text=auto`); must work in Chromium **and** Firefox (AGENTS.md `<OUTPUT_FORMAT>`, `<BANNED>`).
- Shared library code is **inlined**, never modified inline or referenced via external `<script src>` (AGENTS.md `<TEMPLATES>`, `<LIBRARIES>`:185–210).
- Commit format: `<game-name>: <description>` (e.g. `snake: initial implementation`); separate commits in `games/` vs `game-studio/` (AGENTS.md `<GIT>`).
- `AGENTS.md` uses a hybrid format — both `## SECTION` headings and `<SECTION>` XML tags; new sections must include both (AGENTS.md `<HYBRID_FORMAT>`).
- Banned: external dependencies, DOM libs (jQuery/React), build step, skipping phases, self-approving a review, modifying template schemas without updating SCHEMA.md, defaulting to the lightest engine (AGENTS.md `<BANNED>`).

## Data Stores and Migrations
- No database or migration system exists (no evidence found).
- State files (JSON/Markdown, file-based): `studio_state.json` (gate state + hash chain), `.studio/salt` (hash secret), `.studio/gate.log` (append log), `WORKFLOW_STATE.md` (human-readable STATE/TASKS/RUN_LOG/ERROR_LOG, with explicit valid-phase transition table).
- No schema-migration mechanism; "migrations" are not part of this project — template schema changes are governed by updating `templates/SCHEMA.md` (AGENTS.md `<BANNED>`).

## External Services
- No runtime external services in output games — zero external dependencies is mandatory (AGENTS.md `<BANNED>`; audit-report.md Phase 8: "No fetch/curl in project code").
- Build-time/optional: SCORM LMS delivery via the "Education MCG pipeline" (`media_upload_url` → `curl -T` → `scorm_upload` → `lesson_create`) (AGENTS.md Phase 7).
- Research-time only: `websearch` for comparable games; GitHub reference-clone sources (`opengaming/osgameclones`, `references/reference-clones.md`); free asset libraries (Kenney, OpenGameArt, itch.io, CraftPix, Quaternius, Poly Haven, Freesound, game-icons.net, Piskel) (AGENTS.md Phase 0/4).
- Installed agent skills: `rpgjs`, `rpgjs-studio` from `RSamaium/RPG-JS@v5` (skills-lock.json).

## Security and Access Controls
- **Salt secrecy**: `.studio/salt` is the hash-chain secret; it MUST NOT be printed, displayed, or embedded in a prompt/message (AGENTS.md RULE_5).
- **Tamper detection**: SHA-256 hash chain; `studio-gate.py verify` reports CHAIN BREAK and the agent MUST stop and report (AGENTS.md RULE_4; studio-gate.py:450–467). Gate commands block on chain-integrity failure (studio-gate.py:537–539, 585–587).
- **Hook-enforced controls** (`.opencode/hook/hooks.yaml`): block any git command that disables hooks (`--no-verify`, `core.hooksPath=…`, `commit -n`), with session stop; protect generated files (`.opencode/commands/speckit*.md`, `.specify/scripts/`, `.specify/templates/`, `.specify/presets/`) from hand-edits.
- Security scan (audit-report.md Phase 8): clean — no hardcoded secrets, no dangerous shell patterns, no network exfiltration; "no unescaped user input" prompt-injection surface.
- Ethical/legal access controls (AGENTS.md `<STUDYING_EXISTING_GAMES>`): only permissive licenses may be cloned; never copy code/assets into outputs; never commit cloned repos; produce free open games only.
- SCORM assets must be embedded/shipped, never CDN (AGENTS.md Phase 4 asset rules).

## Observability
- Gate log: `.studio/gate.log` (timestamped entries; AGENTS.md `<STATE_PERSISTENCE>`, studio-gate.py `log()`).
- Structured trace events: `studio_state.json` `trace_events` (capped 200), `validation_runs`, `advisory_warnings` (capped 100), `quality_levels`, `parking_lot` (studio-gate.py:397–407, 645–694).
- Human-readable status: `WORKFLOW_STATE.md` (STATE/TASKS/RUN_LOG/ERROR_LOG/STATUS) and `python3 studio-gate.py status` / `trace` / `resume`.
- Runtime (output games): browser console must be error-free; Python games write `crash.log` on error (AGENTS.md Phase 5).
- Self-audit checklist after any studio change (AGENTS.md `<SELF_AUDIT>`).

## Known Constraints
- `AGENTS.md` is 1057 lines, flagged as exceeding the 500-line threshold (audit-report.md:33, WARN, non-blocking). `AGENTS.md.pre-speckit.bak` also present.
- No CI, no automated tests — verification is manual and gate-evidence-based.
- `studio-gate.py` and `studio_state.json` are the authoritative workflow; after context compaction the agent MUST re-read the gate section and trust the script, not memory (AGENTS.md RULE_6, `<STATE_PERSISTENCE>`).
- Template/library/engine consistency must be maintained by hand (audit Phase 3 checks variable/engine/SCORM consistency across templates).
- `engines/` is cloned and gitignored — external repos with independent branches (`main`, `v5`), update is on demand.
- RPG-JS standalone mode (`provideRpg()`) is documented as experimental and must be verified during scaffold/implement (brief-medieval-edu-rpg.md:77,81).
- SCORM wrapping has a fixed pipeline; Ursina is not web-capable (AGENTS.md `<SCORM Output>`).

## Existing Behaviour That Must Remain Unchanged
- The maker pipeline phase order and gates: `research → brief → approve → scaffold → implement → test → review → output → commit → complete`, with no skipping (AGENTS.md; WORKFLOW_STATE.md; studio-gate.py:61–73).
- Gate invariants: `validate --result pass` before `complete --validated`; `--game <name>` required on `complete`/`validate`; output gate verifies `../games/<name>/index.html`; commit gate verifies a registry row in `../games/AGENTS.md` (AGENTS.md RULE_9b; studio-gate.py:876–914).
- Output contract: self-contained, zero-dependency games; required README cross-reference; registry update; commit format `<game-name>: <description>`.
- `.studio/salt` secrecy and hash-chain verification behaviour.
- Template `{{variable}}` contract and `templates/SCHEMA.md` as the source of truth for variables.
- Hook-enforced blocks (`--no-verify`, generated-file edits) and the `engines/` gitignore boundary.

## Spec Kit Adoption Notes
- Spec Kit was just installed (`speckit_version` 1.0.13; `.specify/` present; `AGENTS.md` already carries `<!-- SPECKIT-BRIDGE START -->` and `<!-- SPECKIT START -->` sections pointing at `specs/` as the source of truth).
- Two workflow systems now coexist: the pre-existing `studio-gate.py` maker pipeline (authoritative for game production) and Spec Kit's `.specify/` workflow. Future specs should state how they reconcile — do not let `/speckit.*` phases silently bypass or reorder the gate phases.
- Editable per the kit's own rule: `.specify/memory/constitution.md` and `specs/`; NOT editable: `.opencode/commands/speckit*.md`, `.specify/scripts/`, `.specify/templates/`, `.specify/presets/` (hooks.yaml `protect-generated-files`; AGENTS.md SPECKIT-BRIDGE).
- `git commit --no-verify` is blocked at the hook layer — checks cannot be skipped, matching the gate's "no skipping phases" rule.
- `specs/` does not yet exist (no evidence found); `feature_numbering` is `sequential`, scripts are `sh`, integration is `opencode`.
