# game-studio

A **game template + library system** for building browser-based HTML games and Python games consistently.

**Output goes to:** [`games/`](https://github.com/watanabekidz/games)

---

## What this is

`game-studio` provides the infrastructure for creating new games:

- **Templates** — Reusable game skeletons (DOM grid, Canvas 2D, puzzle, etc.)
- **Libraries** — Shared JavaScript/Python modules for canvas, input, audio, sprites
- **Maker workflow** — A structured AI-agent pipeline for designing, building, testing, and delivering games
- **Conventions** — Consistent patterns so every game looks and feels like it belongs in the same collection

## Quick start

To create a new game, an AI agent reads `AGENTS.md` and follows the maker pipeline:

```
DESIGN → APPROVE → SCAFFOLD → IMPLEMENT → TEST → REVIEW → OUTPUT → COMMIT
```

The finished game lands in `../games/<game-name>/`.

## Directory structure

```
game-studio/
├── AGENTS.md              # Studio conventions + maker pipeline (START HERE)
├── WORKFLOW_STATE.md      # Task tracking for studio work
├── README.md              # This file
├── templates/
│   ├── SCHEMA.md          # Template variable system documentation
│   ├── dom-grid/          # Grid-based DOM game skeleton
│   └── canvas-rpg/        # Canvas 2D RPG game skeleton
├── libraries/
│   ├── README.md          # Library index
│   └── canvas-engine.js   # Shared canvas rendering helpers
└── references/
    └── game-design.md     # Game design patterns reference
```
