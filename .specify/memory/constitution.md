# game-studio Constitution

## Core Principles

### I. Phase-Gated Delivery (NON-NEGOTIABLE)
Every game-production activity MUST run through the maker pipeline in strict order — `research → brief → approve → scaffold → implement → test → review → output → commit → complete` — with no skipping. Before any build action, agents MUST run `python3 studio-gate.py check --to <phase>`; a phase MUST NOT be marked complete with `--validated` until its validation for that phase has passed.
- **Why**: `studio-gate.py` enforces the transition table and blocks out-of-order or unvalidated transitions (studio-gate.py:61–73, 557–564); AGENTS.md RULE_1–3 makes the gate the source of truth.
- **Influences**: any spec/plan/tasks that define work performed inside the maker pipeline, and any spec touching phase entry/exit.

### II. Evidence-Backed Validation
Each phase MUST record structured validation evidence that matches the required keys and formats (e.g. `tests_passed=<chromium|firefox|both>`, `checklist_run=<n>/<n>`, `mechanics_done=<count>`), and MUST meet that phase's minimum `set-progress` step count before `validate --result pass` is accepted.
- **Why**: `studio-gate.py` defines required evidence per gate (`VALIDATION_EVIDENCE`), regex patterns (`EVIDENCE_PATTERNS`), and minimum steps (`MINIMUM_STEPS_PER_PHASE`); quality is scored GOLD/SILVER/BRONZE/FAIL accordingly.
- **Influences**: acceptance criteria, task definitions-of-done, and any spec that claims completion of a phase.

### III. Quality-First Engine Selection
When selecting an engine or template, specs MUST present 2–4 plausible options and MUST compare what each provides versus what must be built from scratch. Agents MUST NOT default to the lightest option.
- **Why**: AGENTS.md RULE_10 and `<BANNED>` explicitly ban the "lightest = best" heuristic; the brief template and phase scope require a provides-vs-build comparison table.
- **Influences**: engine/architecture decisions, brief and plan artifacts, and any spec that selects tooling.

### IV. Self-Contained, Zero-Dependency Output
Output games MUST be self-contained: no external dependencies, no DOM libraries, no build step (HTML), with shared libraries inlined into the single output file. Python games MUST be a single `.py` file with `try/except` on input handlers.
- **Why**: AGENTS.md `<OUTPUT_FORMAT>` and `<BANNED>` mandate zero external dependencies and no build step except Capsule 3D; libraries are inlined during scaffolding.
- **Influences**: any feature spec affecting game output, packaging, or asset handling.

### V. Traceability to an Approved Brief
Every game MUST trace to an approved brief, and the engine/template choice MUST be an explicit user decision. Agents MUST NOT skip the approval gate or self-approve a review.
- **Why**: Phase 2 approval gate requires `user_approved=yes` (studio-gate.py:106–109); `<BANNED>` forbids self-approving a review; the brief validation checklist requires options be presented to the user.
- **Influences**: scope documents, requirement traceability, and review/approval specs.

### VI. Tamper-Evident State Integrity
Agents MUST verify hash-chain integrity (`python3 studio-gate.py verify`) and MUST STOP and report on a CHAIN BREAK. The `.studio/salt` file MUST never be printed, displayed, or embedded in any prompt or message.
- **Why**: AGENTS.md RULE_4–5; `studio-gate.py` blocks commands when chain verification fails (studio-gate.py:450–467, 537–539, 585–587).
- **Influences**: any spec touching state, secrets, security, or workflow infrastructure.

### VII. Scope Discipline — Park, Do Not Creep
Before working in a phase, agents MUST check that phase's scope and MUST park out-of-bounds ideas rather than implement them. Changes to the gate/workflow infrastructure MUST always be parked and reviewed at pipeline end.
- **Why**: AGENTS.md RULE_7–8; phase scopes are encoded in `PHASE_SCOPES` and the `park`/`parking-lot` commands in `studio-gate.py`.
- **Influences**: change control, scope statements, and any spec proposing work outside a phase's allowed list.

### VIII. Template and Library Consistency
Specs MUST keep templates, `templates/SCHEMA.md`, and the library documentation in sync, and MUST NOT modify shared library code inline. Template schemas MUST NOT change without a corresponding SCHEMA.md update.
- **Why**: AGENTS.md `<BANNED>` forbids schema changes without updating SCHEMA.md; `<LIBRARIES>` requires inlining, not inline edits; the audit checks cross-template variable/engine consistency.
- **Influences**: template/library specs and any change to the variable contract.

### IX. Manual, Cross-Browser Verification
Games MUST be verified manually before the test phase passes: no console errors, every mechanic walked through, edge cases covered, and checked in both Chromium and Firefox. Python games MUST be run end-to-end, with malformed input exercised and `crash.log` confirmed on error.
- **Why**: AGENTS.md Phase 5 prescribes exactly these manual checks; the test gate requires `tests_passed=<chromium|firefox|both>` (studio-gate.py:118–121).
- **Influences**: test plans, verification steps, and acceptance criteria in specs.

## Delivery Principles

I. Product Intent and Scope — Every material change must identify the user or system problem it addresses, its goals, its non-goals, and its intended scope.

II. Evidence Before Implementation — When product behaviour or feasibility is uncertain, investigate the repository, the relevant evidence, and available solution patterns before selecting an approach.

III. Explicit Assumptions — Assumptions that could affect behaviour, scope, architecture, security, data, cost, or validation must be recorded.

IV. Verifiable Outcomes — Requirements must be testable or otherwise verifiable. Acceptance criteria must describe observable outcomes.

V. Traceable Delivery — Each implementation task must trace to an approved requirement or design decision.

VI. Controlled Change — Material changes to approved behaviour, scope, architecture, security, data, or cost require explicit review.

VII. Artifact Consistency — When a later discovery contradicts an earlier artifact, repair the earliest affected artifact and re-check the artifacts that depend on it.

VIII. Proportional Process — Use enough process to control risk, but do not apply full product discovery to routine maintenance or small, well-understood fixes.

**Version**: 1.0.0 | **Ratified**: 2026-10-17 | **Last Amended**: 2026-10-17

**Governance**: This constitution is the source of truth for game-studio; the studio-gate pipeline remains authoritative for phase order and validation, and all specs, plans, and reviews must verify compliance with both.
