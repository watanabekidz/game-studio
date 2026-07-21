#!/usr/bin/env python3
"""
studio-gate.py — Phase transition gate for game-studio.

Enforces that each phase of the maker pipeline completes validation
before the next phase begins. Uses a SHA-256 hash chain with a
project-local salt to detect state tampering.

Usage:
  python3 studio-gate.py init
  python3 studio-gate.py check --from <phase> --to <phase> [--scope]
  python3 studio-gate.py complete --phase <phase> [--validated] [--tag <note>] [--game <name>]
  python3 studio-gate.py validate --phase <phase> --gate <gate> --result <pass|fail> [--summary <text>] [--evidence key=val ...] [--game <name>]
  python3 studio-gate.py set-progress --phase <phase> --message "<note>" [--game <name>]
  python3 studio-gate.py warn --phase <phase> --message "<finding>" [--severity <info|warn|critical>] [--game <name>]
  python3 studio-gate.py trace [--phase <phase>]
  python3 studio-gate.py park --title "<idea>" [--description "<detail>"]
  python3 studio-gate.py parking-lot [--clear]
  python3 studio-gate.py resume
  python3 studio-gate.py status
  python3 studio-gate.py verify

Phases:
  research → brief → approve → scaffold → implement → test → review → output → commit → complete

Exit codes:
  0 = gate passed
  1 = usage error
  2 = gate blocked
"""

import json, hashlib, os, sys, time, re, pathlib
from pathlib import Path

# ─── Paths ──────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.resolve()
STATE_PATH = PROJECT_ROOT / "studio_state.json"
SALT_PATH = PROJECT_ROOT / ".studio" / "salt"
GATE_LOG = PROJECT_ROOT / ".studio" / "gate.log"
OUTPUT_DIR = PROJECT_ROOT.parent / "games"

# Games created before the gate system: OK without a gate chain
LEGACY_GAMES = {"tic-tac-toe", "README", "AGENTS", "WORKFLOW_STATE"}

# ─── Phase definitions ──────────────────────────────────────────────

VALID_PHASES = [
    "research",
    "brief",
    "approve",
    "scaffold",
    "implement",
    "test",
    "review",
    "output",
    "commit",
    "complete",
]

VALID_TRANSITIONS = {
    None:              ["research", "brief"],
    "research":        ["brief"],
    "brief":           ["approve"],
    "approve":         ["scaffold"],
    "scaffold":        ["implement"],
    "implement":       ["test"],
    "test":            ["review"],
    "review":          ["output"],
    "output":          ["commit"],
    "commit":          ["complete"],
    "complete":        [],  # terminal
}

REQUIRES_VALIDATION = {
    "approve":   "Game brief approval gate (brief → approve)",
    "implement": "Scaffold validation (scaffold → implement)",
    "test":      "Implementation testing (implement → test)",
    "review":    "Test results gate (test → review)",
    "output":    "Review checklist (review → output)",
    "commit":    "Output verification (output → commit)",
    "complete":  "Commit verification (commit → complete)",
}

VALID_GATES = {
    "brief":      ["brief"],
    "approve":    ["approval"],
    "scaffold":   ["scaffold"],
    "implement":  ["implement"],
    "test":       ["test"],
    "review":     ["review"],
    "output":     ["output"],
    "commit":     ["commit"],
    "research":   ["research"],
}

VALIDATION_EVIDENCE = {
    ("research", "research"): {
        "required": ["research_complete", "game_type"],
        "description": "Research logged in WORKFLOW_STATE.md. Evidence: 'research_complete=<sources_searched>' 'game_type=<educational|entertainment>'",
    },
    ("brief", "brief"): {
        "required": ["brief_written", "options_presented"],
        "description": "Game brief written with 2-4 engine options and quality comparison. Evidence: 'brief_written=<game_name>' 'options_presented=<count>'",
    },
    ("approve", "approval"): {
        "required": ["user_approved"],
        "description": "User approved the game brief. Evidence: 'user_approved=yes'",
    },
    ("scaffold", "scaffold"): {
        "required": ["template_used"],
        "description": "Template used and game runs. Evidence: 'template_used=<template_name>'",
    },
    ("implement", "implement"): {
        "required": ["mechanics_done"],
        "description": "Core mechanics from brief implemented. Evidence: 'mechanics_done=<count>'",
    },
    ("test", "test"): {
        "required": ["tests_passed"],
        "description": "Game tested — no console errors. Evidence: 'tests_passed=<chromium|firefox>'",
    },
    ("review", "review"): {
        "required": ["checklist_run"],
        "description": "Review checklist completed. Evidence: 'checklist_run=<pass_count>/<total>'",
    },
    ("output", "output"): {
        "required": ["output_placed"],
        "description": "Game placed in ../games/<name>/. Evidence: 'output_placed=<path>'",
    },
    ("commit", "commit"): {
        "required": ["committed"],
        "description": "Game committed to git. Evidence: 'committed=<sha>'",
    },
}

# Phase scope definitions
PHASE_SCOPES = {
    "research": {
        "allowed": [
            "Determine game type: ask user if educational or entertainment",
            "If educational: read references/game-based-learning.md for pedagogical guidelines",
            "Search comparable games via websearch",
            "Research genre conventions and technical constraints",
            "Log findings in WORKFLOW_STATE.md",
            "Record thoroughness evidence (set-progress, warn, trace)",
        ],
        "out_of_bounds": [
            "Writing the game brief (phase: brief)",
            "Template selection or scaffolding",
            "Any code writing",
            "Gate or infrastructure changes",
            "Proceeding without determining game type",
        ],
    },
    "brief": {
        "allowed": [
            "Write game brief (logline, pillars, mechanics, scope, cut line)",
            "Create engine comparison table: what each engine provides vs what you'd build",
            "Present 2-4 engine/template options with quality-first analysis",
            "Run the validation checklist against the brief",
            "Record thoroughness evidence (set-progress, warn, trace)",
        ],
        "out_of_bounds": [
            "Code writing or scaffolding",
            "Template selection",
            "Gate or infrastructure changes",
            "Presenting only one engine option to the user",
            "Defaulting to lightest engine without quality comparison",
        ],
    },
    "approve": {
        "allowed": [
            "Present game brief with engine options to user for approval",
            "Let user choose among engine options — do not dictate a single choice",
            "Revise brief based on user feedback",
            "Record thoroughness evidence (set-progress, warn, trace)",
        ],
        "out_of_bounds": [
            "Any code writing",
            "Template selection (phase: scaffold)",
            "Presenting only one engine option",
            "Burying the engine choice — it must be explicit",
        ],
    },
    "scaffold": {
        "allowed": [
            "Select best-matching template from templates/",
            "Read SCHEMA.md for variable rules",
            "Copy template, populate {{variable}} slots, inline libraries",
            "Generate README.md from template",
            "Verify scaffolded game opens without errors",
            "Record thoroughness evidence (set-progress, warn, trace)",
        ],
        "out_of_bounds": [
            "Game-specific logic (phase: implement)",
            "Gate or infrastructure changes",
        ],
    },
    "implement": {
        "allowed": [
            "Implement core mechanics from the game brief",
            "Win/lose/draw conditions, score tracking, progression",
            "Edge case handling (rapid input, empty states, boundaries)",
            "Record thoroughness evidence (set-progress, warn, trace)",
        ],
        "out_of_bounds": [
            "Template changes (go back to scaffold)",
            "Gate or infrastructure changes",
        ],
    },
    "test": {
        "allowed": [
            "Open in browser and verify no console errors",
            "Walk through every mechanic (start, play, win/lose, restart)",
            "Test edge cases: rapid input, boundary, empty states",
            "Check in both Chromium and Firefox",
            "Record thoroughness evidence (set-progress, warn, trace)",
        ],
        "out_of_bounds": [
            "Game logic changes (phase: implement)",
            "Gate or infrastructure changes",
        ],
    },
    "review": {
        "allowed": [
            "Run review checklist (conventions, banned patterns, self-contained, edge cases)",
            "Cross-browser verification",
            "Record thoroughness evidence (set-progress, warn, trace)",
        ],
        "out_of_bounds": [
            "Game logic changes",
            "Gate or infrastructure changes",
        ],
    },
    "output": {
        "allowed": [
            "Create README.md with game-studio attribution",
            "Copy to ../games/<game-name>/",
            "Verify it runs from its new location",
            "Update AGENTS.md output registry",
            "Update WORKFLOW_STATE.md",
            "Record thoroughness evidence (set-progress, warn, trace)",
        ],
        "out_of_bounds": [
            "Game logic changes",
            "Gate or infrastructure changes",
        ],
    },
    "commit": {
        "allowed": [
            "Stage game files intentionally (no git add .)",
            "Commit with format: <game-name>: <description>",
            "Record thoroughness evidence (set-progress, warn, trace)",
        ],
        "out_of_bounds": [
            "Game logic changes",
            "Gate or infrastructure changes",
        ],
    },
    "complete": {
        "allowed": [
            "Final summary to user",
            "Workflow state marked complete",
        ],
        "out_of_bounds": [
            "Any game work",
        ],
    },
}

# Minimum set-progress steps per phase
MINIMUM_STEPS_PER_PHASE = {
    "research":  3,  # search, log, review
    "brief":     3,  # write brief, validate, fix
    "approve":   1,  # present to user
    "scaffold":  4,  # pick template, populate, inline, verify
    "implement": 6,  # mechanics, edge cases, polish
    "test":      3,  # open, walk through, cross-browser
    "review":    2,  # checklist, fix findings
    "output":    3,  # README, copy, verify, update registry
    "commit":    2,  # stage, commit
}

COMPLETION_QUALITY = {
    "gold":   {"label": "GOLD",   "minimum_steps_factor": 1.0, "allow_warnings": False},
    "silver": {"label": "SILVER", "minimum_steps_factor": 1.0, "allow_warnings": True},
    "bronze": {"label": "BRONZE", "minimum_steps_factor": 0.6, "allow_warnings": True},
}

EVIDENCE_PATTERNS = {
    "research_complete": r"^\d+.*",
    "game_type":        r"^(educational|entertainment)$",
    "brief_written":     r"^.+$",
    "options_presented": r"^[2-4]$",
    "user_approved":     r"^yes$",
    "template_used":     r"^[a-z-]+$",
    "mechanics_done":    r"^\d+$",
    "tests_passed":      r"^(chromium|firefox|both)$",
    "checklist_run":     r"^\d+/\d+$",
    "output_placed":     r"^.+$",
    "committed":         r"^[a-f0-9]{7,}$",
}

# Preflight checks
def _check_minimum_steps(state, phase, gate, evidence):
    min_steps = MINIMUM_STEPS_PER_PHASE.get(phase, 1)
    steps = evidence.get("_step_count", "")
    override = evidence.get("step_override", "")
    if override:
        return True, ""
    if not steps:
        return False, (
            f"Minimum step tracking not satisfied for '{phase}'.\n"
            f"  Required: at least {min_steps} set-progress steps\n"
            f"  Found: none recorded\n"
            f"  Use: python3 studio-gate.py set-progress --phase {phase} --message \"<what I did>\"\n"
            f"  Override: --evidence step_override=<reason>"
        )
    try:
        step_count = int(steps)
    except (ValueError, TypeError):
        return True, ""
    if step_count < min_steps:
        bronze_min = max(1, int(min_steps * 0.6))
        if step_count >= bronze_min:
            return True, ""
        return False, (
            f"Minimum step tracking not satisfied for '{phase}'.\n"
            f"  Required: at least {min_steps} steps\n"
            f"  Found: {step_count} steps\n"
            f"  Minimum: {bronze_min} steps\n"
            f"  Record more steps or use: --evidence step_override=<reason>"
        )
    return True, ""

def _check_evidence_patterns(state, phase, gate, evidence):
    if not evidence:
        return True, ""
    mismatches = []
    for key, value in evidence.items():
        pattern = EVIDENCE_PATTERNS.get(key)
        if pattern and str(value).strip():
            if not re.match(pattern, str(value).strip()):
                mismatches.append((key, value, pattern))
    if mismatches:
        lines = [f"    • {k}=\"{v}\" does not match {p}" for k, v, p in mismatches]
        return False, (
            f"Evidence value pattern mismatch.\n" + "\n".join(lines) +
            "\n\nUse the correct format for each key."
        )
    return True, ""

PHASE_PREFLIGHT_CHECKS = {
    "research":  [_check_minimum_steps, _check_evidence_patterns],
    "brief":     [_check_minimum_steps, _check_evidence_patterns],
    "approve":   [_check_minimum_steps, _check_evidence_patterns],
    "scaffold":  [_check_minimum_steps, _check_evidence_patterns],
    "implement": [_check_minimum_steps, _check_evidence_patterns],
    "test":      [_check_minimum_steps, _check_evidence_patterns],
    "review":    [_check_minimum_steps, _check_evidence_patterns],
    "output":    [_check_minimum_steps, _check_evidence_patterns],
    "commit":    [_check_minimum_steps, _check_evidence_patterns],
}

def run_preflight_checks(state, phase, gate, evidence):
    checks = PHASE_PREFLIGHT_CHECKS.get(phase, [])
    for check_fn in checks:
        ok, reason = check_fn(state, phase, gate, evidence)
        if not ok:
            return False, [reason]
    return True, []

# ─── Core functions ─────────────────────────────────────────────────

def load_salt():
    if not SALT_PATH.exists():
        print("ERROR: Salt file not found. Run: python3 studio-gate.py init", file=sys.stderr)
        sys.exit(1)
    return SALT_PATH.read_text().strip()

def hash_entry(entry, prev_hash, salt):
    hash_data = {
        "phase": entry["phase"],
        "prev_hash": prev_hash,
        "timestamp": entry["timestamp"],
        "validated": entry.get("validated", False),
        "tag": entry.get("tag", ""),
    }
    # Only include game in hash if non-empty (preserves backward compatibility
    # with pre-game-scoping chain entries)
    game = entry.get("game", "")
    if game:
        hash_data["game"] = game
    raw = json.dumps(hash_data, sort_keys=True) + salt
    return hashlib.sha256(raw.encode()).hexdigest()

DEFAULT_STATE = {
    "current_phase": None,
    "last_phase_completed": None,
    "phase_progress": "",
    "validation_chain": [],
    "validation_runs": [],
    "trace_events": [],
    "quality_levels": {},
    "advisory_warnings": [],
    "parking_lot": [],
}

def load_state():
    if not STATE_PATH.exists():
        return dict(DEFAULT_STATE)
    try:
        with open(STATE_PATH) as f:
            loaded = json.load(f)
        result = dict(DEFAULT_STATE)
        result.update(loaded)
        return result
    except (json.JSONDecodeError, OSError) as e:
        print(f"ERROR: Cannot read state file: {e}", file=sys.stderr)
        sys.exit(2)

def write_state(state):
    tmp = STATE_PATH.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
        f.write("\n")
    tmp.rename(STATE_PATH)

def log(message):
    ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
    with open(GATE_LOG, "a") as f:
        f.write(f"[{ts}] {message}\n")

def get_latest_validation(state, phase):
    runs = state.get("validation_runs", [])
    phase_runs = [r for r in runs if r.get("phase") == phase]
    return phase_runs[-1] if phase_runs else None

def record_validation(state, phase, gate, result, summary="", evidence=None):
    if "validation_runs" not in state:
        state["validation_runs"] = []
    entry = {
        "phase": phase, "gate": gate, "result": result,
        "summary": summary, "evidence": evidence or {},
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    state["validation_runs"].append(entry)
    return entry

def verify_chain(chain, salt, quiet=False):
    valid = True
    for i, entry in enumerate(chain):
        prev_hash = chain[i-1]["hash"] if i > 0 else entry.get("prev_hash", "0"*64)
        expected = hash_entry(entry, prev_hash, salt)
        actual = entry.get("hash", "")
        if expected != actual:
            if not quiet:
                print(f"CHAIN BREAK at entry {i} ({entry.get('phase')}):")
                print(f"  Expected: {expected}")
                print(f"  Actual:   {actual}")
            valid = False
        else:
            if not quiet:
                print(f"  [{i}] {entry['phase']:16s} hash={entry['hash'][:12]} ✓")
    if valid and not quiet:
        print(f"Chain verified: {len(chain)} entries, all hashes match.")
    return valid

def compute_quality_level(phase, step_count, warnings_count, evidence, all_checks_passed):
    min_steps = MINIMUM_STEPS_PER_PHASE.get(phase, 1)
    if not all_checks_passed:
        return "fail", "One or more checks failed"
    if step_count >= min_steps and warnings_count == 0:
        return "gold", f"Full compliance: {step_count}/{min_steps} steps, 0 warnings"
    if step_count >= min_steps:
        return "silver", f"All steps met ({step_count}/{min_steps}), {warnings_count} warning(s)"
    bronze_min = max(1, int(min_steps * 0.6))
    if step_count >= bronze_min:
        return "bronze", f"Partial steps ({step_count}/{min_steps}), {warnings_count} warning(s)"
    return "fail", f"Insufficient steps: {step_count}/{min_steps}"

# ─── Commands ───────────────────────────────────────────────────────

def cmd_init():
    if not SALT_PATH.exists():
        SALT_PATH.parent.mkdir(parents=True, exist_ok=True)
        import secrets
        salt = hashlib.sha256(secrets.token_bytes(32)).hexdigest()
        SALT_PATH.write_text(salt + "\n")
        print("Salt file created.")
    else:
        print("Salt file already exists.")
    state = load_state()
    if not state.get("validation_chain"):
        salt = load_salt()
        genesis = {
            "phase": "genesis",
            "prev_hash": "0" * 64,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "validated": True,
            "tag": "Gate initialized",
        }
        genesis["hash"] = hash_entry(genesis, genesis["prev_hash"], salt)
        state["validation_chain"] = [genesis]
        write_state(state)
        log(f"Gate initialized: genesis={genesis['hash'][:12]}")
        print("Gate initialized. Genesis hash:", genesis["hash"][:16] + "...")
    else:
        print("Gate already initialized. Chain length:", len(state["validation_chain"]))
    return 0

def cmd_check(from_phase, to_phase, scope_only=False):
    state = load_state()
    salt = load_salt()
    chain = state.get("validation_chain", [])

    if scope_only and to_phase:
        scope = PHASE_SCOPES.get(to_phase, {})
        allowed = scope.get("allowed", [])
        out = scope.get("out_of_bounds", [])
        print("=" * 60)
        print(f"  SCOPE: Phase '{to_phase}'")
        print("=" * 60)
        print()
        print("  ✅ ALLOWED work in this phase:")
        for item in allowed:
            print(f"    • {item}")
        if out:
            print()
            print("  🚫 OUT OF BOUNDS (park these ideas):")
            for item in out:
                print(f"    • {item}")
        print()
        print(f"  python3 studio-gate.py park --title \"...\"")
        return 0

    if not verify_chain(chain, salt, quiet=True):
        print("GATE BLOCKED: Hash chain integrity check FAILED.", file=sys.stderr)
        return 2

    if from_phase not in VALID_TRANSITIONS:
        print(f"GATE BLOCKED: Unknown from-phase '{from_phase}'.", file=sys.stderr)
        return 2

    allowed = VALID_TRANSITIONS[from_phase]
    if to_phase not in allowed:
        print(f"GATE BLOCKED: Transition {from_phase} → {to_phase} is not allowed.", file=sys.stderr)
        print(f"Allowed: {', '.join(allowed)}", file=sys.stderr)
        return 2

    if from_phase is not None and state.get("last_phase_completed") != from_phase:
        last = state.get("last_phase_completed")
        print(f"GATE BLOCKED: Last completed phase is '{last}', not '{from_phase}'.", file=sys.stderr)
        print(f"Complete '{from_phase}' first: python3 studio-gate.py complete --phase {from_phase}", file=sys.stderr)
        return 2

    if to_phase in REQUIRES_VALIDATION:
        last_entry = chain[-1] if chain else None
        if last_entry and last_entry.get("phase") == from_phase:
            if not last_entry.get("validated", False):
                what = REQUIRES_VALIDATION[to_phase]
                print(f"GATE BLOCKED: {what} not completed.", file=sys.stderr)
                print(f"Complete with: python3 studio-gate.py complete --phase {from_phase} --validated", file=sys.stderr)
                return 2

    print(f"GATE PASSED: {from_phase or 'start'} → {to_phase}")

    # Auto-show scope for target phase
    if to_phase and to_phase in PHASE_SCOPES and to_phase not in ("complete",):
        scope = PHASE_SCOPES[to_phase]
        print()
        print(f"  ── Scope for '{to_phase}' ──")
        for item in scope.get("allowed", []):
            print(f"    ✅ {item}")
        for item in scope.get("out_of_bounds", []):
            print(f"    🚫 {item}")
        print()
    return 0

def cmd_complete(phase, validated=False, tag="", game=""):
    state = load_state()
    salt = load_salt()
    chain = state.get("validation_chain", [])

    if not verify_chain(chain, salt, quiet=True):
        print("GATE BLOCKED: Hash chain integrity check FAILED.", file=sys.stderr)
        return 2

    if validated:
        last = get_latest_validation(state, phase)
        if last is None:
            print(f"GATE BLOCKED: No validation run for '{phase}'.", file=sys.stderr)
            print(f"Run: python3 studio-gate.py validate --phase {phase} --gate <gate> --result pass", file=sys.stderr)
            print(f"Available gates: {', '.join(VALID_GATES.get(phase, []))}", file=sys.stderr)
            return 2
        if last.get("result") != "pass":
            print(f"GATE BLOCKED: Latest validation for '{phase}' FAILED.", file=sys.stderr)
            return 2

    prev_hash = chain[-1]["hash"] if chain else "0" * 64
    entry = {
        "phase": phase,
        "game": game,
        "prev_hash": prev_hash,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "validated": validated,
        "tag": tag or "",
    }
    entry["hash"] = hash_entry(entry, prev_hash, salt)
    chain.append(entry)

    state["current_phase"] = phase
    state["last_phase_completed"] = phase
    state["validation_chain"] = chain
    state["phase_progress"] = ""
    state.pop("phase_step", None)
    state["active_game"] = game
    write_state(state)
    log(f"Phase completed: {phase} game={game} validated={validated} hash={entry['hash'][:12]} tag={tag}")
    print(f"Phase '{phase}' completed{' for game='+game if game else ''}. Chain entry hash: {entry['hash'][:16]}...")

    # Show quality
    quality_levels = state.get("quality_levels", {})
    ql = quality_levels.get(phase, "unknown")
    if ql in COMPLETION_QUALITY:
        icons = {"gold": "🥇", "silver": "🥈", "bronze": "🥉"}
        print(f"  {icons.get(ql, '❓')} Quality: {COMPLETION_QUALITY[ql]['label']}")

    # Show warnings
    warnings = state.get("advisory_warnings", [])
    phase_warns = [w for w in warnings if w.get("phase") == phase and w.get("severity") in ("warn", "critical")]
    if phase_warns:
        print(f"  ⚠️  Advisory warnings ({len(phase_warns)}):")
        for w in phase_warns[:3]:
            print(f"      • {w.get('message','')}")

    # Show parking lot
    parking = state.get("parking_lot", [])
    if parking:
        print(f"  📋 Parking lot: {len(parking)} item(s) — run 'parking-lot' to view")

    print()
    return 0

def cmd_set_progress(phase, message, step=None):
    state = load_state()
    state["phase_progress"] = message
    state["current_phase"] = phase
    if step:
        state["phase_step"] = step
    else:
        state.pop("phase_step", None)
    if "trace_events" not in state:
        state["trace_events"] = []
    trace = {
        "phase": phase,
        "step": step or message,
        "message": message,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    state["trace_events"].append(trace)
    if len(state["trace_events"]) > 200:
        state["trace_events"] = state["trace_events"][-200:]
    write_state(state)
    log(f"Progress: {phase} — {message}")
    phase_steps = [t for t in state.get("trace_events", []) if t.get("phase") == phase]
    min_steps = MINIMUM_STEPS_PER_PHASE.get(phase, 1)
    print(f"Progress recorded: [{phase}] {message}")
    if step:
        print(f"  Step: {step}")
    print(f"  Trace: step {len(phase_steps)}/{min_steps} for this phase")
    if len(phase_steps) >= min_steps:
        print(f"  ✅ Minimum steps met for '{phase}'")
    else:
        print(f"  ⚡ Need {min_steps - len(phase_steps)} more step(s)")
    return 0

def cmd_warn(phase, message, severity="info"):
    state = load_state()
    if "advisory_warnings" not in state:
        state["advisory_warnings"] = []
    entry = {
        "phase": phase, "message": message,
        "severity": severity,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    state["advisory_warnings"].append(entry)
    if len(state["advisory_warnings"]) > 100:
        state["advisory_warnings"] = state["advisory_warnings"][-100:]
    write_state(state)
    log(f"Warning [{severity}] {phase}: {message}")
    icons = {"info": "ℹ️", "warn": "⚠️", "critical": "🚫"}
    print(f"{icons.get(severity, 'ℹ️')} Advisory warning: [{phase}] {message}")
    return 0

def cmd_trace(phase=None):
    state = load_state()
    events = state.get("trace_events", [])
    if phase:
        events = [e for e in events if e.get("phase") == phase]
    if not events:
        print("No trace events recorded.")
        return 0
    from collections import OrderedDict
    phases = OrderedDict()
    for e in events:
        p = e.get("phase", "?")
        if p not in phases:
            phases[p] = []
        phases[p].append(e)
    print("=== Structured Trace Events ===\n")
    for p, p_events in phases.items():
        min_steps = MINIMUM_STEPS_PER_PHASE.get(p, 1)
        print(f"  [{p}] — {len(p_events)} events (min: {min_steps})")
        for i, ev in enumerate(p_events, 1):
            ts = ev.get("timestamp", "")[11:19]
            msg = ev.get("message", "")
            print(f"    {i:2d}. {ts} {msg}")
        print()
    if phase:
        warnings = state.get("advisory_warnings", [])
        active = [w for w in warnings if w.get("phase") == phase]
        if active:
            print(f"  Advisory warnings: {len(active)}")
            for w in active:
                icons = {"info": "ℹ️", "warn": "⚠️", "critical": "🚫"}
                print(f"    {icons.get(w.get('severity','info'), 'ℹ️')} {w.get('message','')}")
    print(f"Total: {len(events)} events across {len(phases)} phase(s)")
    return 0

def cmd_resume():
    state = load_state()
    current = state.get("current_phase")
    last = state.get("last_phase_completed")
    progress = state.get("phase_progress", "")
    print("=== Studio Resume ===\n")
    if current is None:
        print("  No work has been started yet.")
        print("  Next step: python3 studio-gate.py check --to research")
        return 0
    print(f"  Current phase:        {current}")
    print(f"  Last completed phase: {last}")
    if progress:
        print(f"  Last progress note:   {progress}")
    print()
    if current == last:
        available = VALID_TRANSITIONS.get(last, [])
        if available:
            print(f"  Next step: python3 studio-gate.py check --to {available[0]}")
        else:
            print("  Pipeline complete.")
    else:
        print(f"  Phase '{current}' in progress. Continue working, then validate and complete.")
    return 0

def cmd_park(title, description=""):
    state = load_state()
    if "parking_lot" not in state:
        state["parking_lot"] = []
    entry = {
        "id": len(state["parking_lot"]) + 1,
        "title": title, "description": description,
        "phase": state.get("current_phase", "?"),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    state["parking_lot"].append(entry)
    write_state(state)
    log(f"Parked: #{entry['id']} — {title}")
    print(f"📋 Parked idea #{entry['id']}: {title}")
    if description:
        print(f"   {description}")
    print(f"  Parking lot: {len(state['parking_lot'])} item(s)")
    return 0

def cmd_parking_lot():
    state = load_state()
    items = state.get("parking_lot", [])
    if not items:
        print("📋 Parking lot is empty.")
        return 0
    print(f"📋 Parking Lot ({len(items)} item(s))")
    print("=" * 60)
    for item in items:
        ts = item.get("timestamp", "")[:10]
        print(f"  #{item['id']} [{item.get('phase','?')}] {item['title']} ({ts})")
        if item.get("description"):
            for line in item["description"].split("\n"):
                print(f"     {line}")
        print()
    print("  Clear: python3 studio-gate.py parking-lot --clear")
    return 0

def cmd_park_clear():
    state = load_state()
    state["parking_lot"] = []
    write_state(state)
    print("Parking lot cleared.")
    return 0

def cmd_status():
    state = load_state()
    chain = state.get("validation_chain", [])
    runs = state.get("validation_runs", [])
    print("=== Studio Gate Status ===")
    print(f"Current phase:      {state.get('current_phase', 'none')}")
    print(f"Last completed:     {state.get('last_phase_completed', 'none')}")
    print(f"Chain length:       {len(chain)}")
    progress = state.get("phase_progress", "")
    if progress:
        print(f"Phase progress:     {progress}")
    parking = state.get("parking_lot", [])
    if parking:
        print(f"Parking lot:        {len(parking)} item(s)")
    print(f"Validation runs:    {len(runs)}")
    quality_levels = state.get("quality_levels", {})
    if quality_levels:
        ql_strs = []
        for p, ql in quality_levels.items():
            icons = {"gold": "🥇", "silver": "🥈", "bronze": "🥉"}
            ql_strs.append(f"{p}={icons.get(ql, '')}{ql}")
        print(f"Quality levels:     {', '.join(ql_strs)}")
    trace_count = len(state.get("trace_events", []))
    warn_count = len(state.get("advisory_warnings", []))
    if trace_count or warn_count:
        print(f"Trace events:       {trace_count}  Warnings: {warn_count}")
    print()
    if chain:
        last = chain[-1]
        print(f"Last chain entry:")
        print(f"  Phase:      {last.get('phase')}")
        print(f"  Validated:  {last.get('validated', False)}")
        print(f"  Hash:       {last.get('hash', '')[:20]}...")
        print(f"  Tag:        {last.get('tag', '')}")
        print()
    last_phase = state.get("last_phase_completed")
    if last_phase in VALID_TRANSITIONS:
        next_phases = VALID_TRANSITIONS[last_phase]
        print(f"Available from '{last_phase}':")
        for p in next_phases:
            req = REQUIRES_VALIDATION.get(p)
            note = f" (requires: {req})" if req else ""
            print(f"  → {p}{note}")
    return 0

def cmd_verify():
    state = load_state()
    salt = load_salt()
    chain = state.get("validation_chain", [])
    if not chain:
        print("No chain entries to verify.")
        return 0
    return 0 if verify_chain(chain, salt, quiet=False) else 2

def cmd_validate(phase, gate, result, summary="", evidence=None):
    state = load_state()
    if phase not in VALID_PHASES:
        print(f"ERROR: Unknown phase '{phase}'.", file=sys.stderr)
        return 1
    available = VALID_GATES.get(phase, [])
    if not available:
        print(f"ERROR: Phase '{phase}' has no gates defined.", file=sys.stderr)
        return 1
    if gate not in available:
        print(f"ERROR: Gate '{gate}' not valid for '{phase}'. Available: {', '.join(available)}", file=sys.stderr)
        return 1
    if result not in ("pass", "fail"):
        print(f"ERROR: --result must be 'pass' or 'fail'.", file=sys.stderr)
        return 1

    evidence = evidence or {}
    if result == "pass":
        phase_steps = [t for t in state.get("trace_events", []) if t.get("phase") == phase]
        if "_step_count" not in evidence:
            evidence["_step_count"] = str(len(phase_steps))

        # Hardened gate: output phase verifies the game landed in games/
        if phase == "output":
            game_name = evidence.get("output_placed", "")
            if game_name:
                game_path = OUTPUT_DIR / game_name / "index.html"
                py_path = OUTPUT_DIR / game_name / (game_name + ".py")
                if not game_path.exists() and not py_path.exists():
                    print("=" * 60)
                    print("  ❌ OUTPUT GATE BLOCKED: Game not found in output directory")
                    print("=" * 60)
                    print(f"  Expected: {game_path} or {py_path}")
                    print(f"  Output placement requires: output_placed=<game_directory_name>")
                    print("  Copy the game to ../games/<name>/ before completing output phase.")
                    print()
                    return 2

        # Hardened gate: commit phase verifies the AGENTS.md registry was updated
        if phase == "commit":
            commit_sha = evidence.get("committed", "")
            if commit_sha:
                agents_path = OUTPUT_DIR / "AGENTS.md"
                if not agents_path.exists():
                    print("=" * 60)
                    print("  ❌ COMMIT GATE BLOCKED: AGENTS.md not found in games/")
                    print("=" * 60)
                    print("  The output registry must be updated before committing.")
                    print()
                    return 2
                # Check the game has a registry entry
                game_name = evidence.get("game_name", "")
                if game_name:
                    content = agents_path.read_text()
                    if f"| {game_name} " not in content:
                        print("=" * 60)
                        print(f"  ❌ COMMIT GATE BLOCKED: '{game_name}' not in output registry")
                        print("=" * 60)
                        print("  Update ../games/AGENTS.md output registry with a row for this game.")
                        print()
                        return 2
        warnings = state.get("advisory_warnings", [])
        phase_warnings = len([w for w in warnings if w.get("phase") == phase and w.get("severity") in ("warn", "critical")])

        preflight_ok, preflight_reasons = run_preflight_checks(state, phase, gate, evidence)
        if not preflight_ok:
            print("=" * 60)
            print("  ❌ PRECONDITION GATE BLOCKED")
            print("=" * 60)
            for reason in preflight_reasons:
                for line in reason.split("\n"):
                    print(f"  {line}")
            print()
            return 2

        reqs = VALIDATION_EVIDENCE.get((phase, gate))
        if reqs:
            required_keys = reqs.get("required", [])
            missing = [k for k in required_keys if k not in evidence or not evidence[k]]
            if missing:
                print("=" * 60)
                print(f"  ❌ GATE BLOCKED: Evidence missing for {phase}/{gate}")
                print("=" * 60)
                print(f"  Required: {', '.join(required_keys)}")
                print(f"  Missing:  {', '.join(missing)}")
                print(f"  {reqs.get('description', '')}")
                print()
                return 2
            print(f"  ✅ Evidence verified for {phase}/{gate}:")
            for k, v in evidence.items():
                vs = str(v)
                if len(vs) > 60:
                    vs = vs[:57] + "..."
                print(f"     • {k}={vs}")

    entry = record_validation(state, phase, gate, result, summary, evidence)
    write_state(state)
    label = "✓ PASS" if result == "pass" else "✗ FAIL"
    log(f"Validation: {phase}/{gate} {label}")
    print(f"Validation recorded: {phase}/{gate} → {label}")
    if summary:
        print(f"  Summary: {summary}")

    if result == "pass":
        raw_steps = evidence.get("_step_count", "0")
        step_count = int(raw_steps) if raw_steps.isdigit() else 0
        warnings = state.get("advisory_warnings", [])
        pwc = len([w for w in warnings if w.get("phase") == phase and w.get("severity") in ("warn", "critical")])
        ql, qr = compute_quality_level(phase, step_count, pwc, evidence, True)
        if "quality_levels" not in state:
            state["quality_levels"] = {}
        state["quality_levels"][phase] = ql
        write_state(state)
        icons = {"gold": "🥇", "silver": "🥈", "bronze": "🥉"}
        print(f"\n{icons.get(ql, '❓')} Quality: {COMPLETION_QUALITY[ql]['label']}")
        print(f"   {qr}")
        print(f"\nNext: python3 studio-gate.py complete --phase {phase} --validated --tag \"<note>\"")

    return 0 if result == "pass" else 2

# ─── Main ───────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]

    if cmd == "init":
        return cmd_init()

    elif cmd == "check":
        from_phase = None
        to_phase = None
        scope_only = False
        args = sys.argv[2:]
        for i, arg in enumerate(args):
            if arg == "--from" and i + 1 < len(args):
                from_phase = args[i + 1]
            elif arg == "--to" and i + 1 < len(args):
                to_phase = args[i + 1]
            elif arg == "--scope":
                scope_only = True
        if from_phase is None:
            state = load_state()
            from_phase = state.get("last_phase_completed")
        if scope_only and to_phase:
            return cmd_check(from_phase, to_phase, scope_only=True)
        if to_phase is None:
            print("Usage: python3 studio-gate.py check --from <phase> --to <phase> [--scope]", file=sys.stderr)
            return 1
        return cmd_check(from_phase, to_phase)

    elif cmd == "complete":
        phase = None
        validated = False
        tag = ""
        game = ""
        args = sys.argv[2:]
        for i, arg in enumerate(args):
            if arg == "--phase" and i + 1 < len(args):
                phase = args[i + 1]
            if arg == "--validated":
                validated = True
            if arg == "--tag" and i + 1 < len(args):
                tag = args[i + 1]
            if arg == "--game" and i + 1 < len(args):
                game = args[i + 1]
        if phase is None:
            print("Usage: python3 studio-gate.py complete --phase <phase> [--validated] [--tag <note>] [--game <name>]", file=sys.stderr)
            return 1
        return cmd_complete(phase, validated, tag, game)

    elif cmd == "validate":
        phase = None
        gate = None
        result = None
        summary = ""
        evidence = {}
        args = sys.argv[2:]
        for i, arg in enumerate(args):
            if arg == "--phase" and i + 1 < len(args):
                phase = args[i + 1]
            elif arg == "--gate" and i + 1 < len(args):
                gate = args[i + 1]
            elif arg == "--result" and i + 1 < len(args):
                result = args[i + 1]
            elif arg == "--summary" and i + 1 < len(args):
                summary = args[i + 1]
            elif arg == "--evidence" and i + 1 < len(args):
                kv = args[i + 1]
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    evidence[k.strip()] = v.strip()
            elif arg == "--game" and i + 1 < len(args):
                evidence["game_name"] = args[i + 1]
        if not phase or not gate or not result:
            print(f"Usage: studio-gate.py validate --phase <phase> --gate <gate> --result <pass|fail> [--game <name>]", file=sys.stderr)
            return 1
        return cmd_validate(phase, gate, result, summary, evidence)

    elif cmd == "set-progress":
        phase = None
        message = None
        step = None
        args = sys.argv[2:]
        for i, arg in enumerate(args):
            if arg == "--phase" and i + 1 < len(args):
                phase = args[i + 1]
            elif arg == "--message" and i + 1 < len(args):
                message = args[i + 1]
            elif arg == "--step" and i + 1 < len(args):
                step = args[i + 1]
            elif arg == "--game" and i + 1 < len(args):
                pass  # recorded for informational purposes
        if not phase or not message:
            print("Usage: python3 studio-gate.py set-progress --phase <phase> --message \"<note>\" [--game <name>]", file=sys.stderr)
            return 1
        return cmd_set_progress(phase, message, step)

    elif cmd == "warn":
        phase = None
        message = None
        severity = "info"
        args = sys.argv[2:]
        for i, arg in enumerate(args):
            if arg == "--phase" and i + 1 < len(args):
                phase = args[i + 1]
            elif arg == "--message" and i + 1 < len(args):
                message = args[i + 1]
            elif arg == "--severity" and i + 1 < len(args):
                severity = args[i + 1]
        if not phase or not message:
            print("Usage: python3 studio-gate.py warn --phase <phase> --message \"<finding>\"", file=sys.stderr)
            return 1
        return cmd_warn(phase, message, severity)

    elif cmd == "trace":
        phase = None
        args = sys.argv[2:]
        for i, arg in enumerate(args):
            if arg == "--phase" and i + 1 < len(args):
                phase = args[i + 1]
        return cmd_trace(phase)

    elif cmd == "resume":
        return cmd_resume()

    elif cmd == "park":
        title = None
        description = ""
        args = sys.argv[2:]
        for i, arg in enumerate(args):
            if arg == "--title" and i + 1 < len(args):
                title = args[i + 1]
            elif arg == "--description" and i + 1 < len(args):
                description = args[i + 1]
        if not title:
            print("Usage: python3 studio-gate.py park --title \"<idea>\" [--description \"<detail>\"]", file=sys.stderr)
            return 1
        return cmd_park(title, description)

    elif cmd == "parking-lot":
        args = sys.argv[2:]
        if "--clear" in args:
            return cmd_park_clear()
        return cmd_parking_lot()

    elif cmd == "status":
        return cmd_status()

    elif cmd == "verify":
        return cmd_verify()

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print(__doc__)
        return 1

if __name__ == "__main__":
    sys.exit(main())
