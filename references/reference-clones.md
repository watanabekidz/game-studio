# Reference Game Clones

<REFERENCE_CLONES>
  Curated open-source game clones for study during Phase 0: Research.
  Each entry was chosen for: clean architecture, good documentation, permissive
  license (MIT/Apache 2.0), and relevance to this project's stack.

  This is NOT a comprehensive list. The full osgameclones database (1,000+
  entries) lives at [`opengaming/osgameclones`](https://github.com/opengaming/osgameclones).
</REFERENCE_CLONES>

---

## Vanilla JS / Canvas (Zero Dependencies)

| Game | Genre | Repo | Why study it |
|---|---|---|---|
| **Vampire Survivors Clone** | Roguelite / Bullet Heaven | [`ricardo-foundry/canvas-vampire-survivors`](https://github.com/ricardo-foundry/canvas-vampire-survivors) | Zero-dependency vanilla JS. Modular ES module architecture. Fixed-step game loop. i18n built-in. Shows how to build a complete commercial-quality game with zero build step. **Best example of the "open file and play" pattern.** |
| **Slice Frenzy** | Arcade / Slicer | [`riiyansh-singh/slice-frenzy`](https://github.com/riiyansh-singh/slice-frenzy) | Dark-mode neon arcade in vanilla JS. Blade trail rendering, particle effects, procedural audio, touch + mouse input. Well-structured single-file game. |
| **Ghost Hunter** | Rhythm Arcade | [`karthiknvd/ghost-hunter`](https://github.com/karthiknvd/ghost-hunter) | 100% synthesized procedural audio via Web Audio API (no sound files). Canvas rendering with cyber-ethereal visual style. Clean JS architecture. |
| **Canvas Game Arcade** | Multi-genre (52 games) | [`forinda/canvas-games`](https://github.com/forinda/canvas-games) | 52 games with **step-by-step tutorials** and **76 concept reference pages** (math, physics, algorithms, design patterns). Best educational resource for learning game dev patterns. |

## Phaser 3 / TypeScript

| Game | Genre | Repo | Why study it |
|---|---|---|---|
| **Tower Defense** | Tower Defense | [`Real-Fruit-Snacks/Tower-Defense`](https://github.com/Real-Fruit-Snacks/Tower-Defense) | Phaser 3 + TypeScript. All art drawn from graphics primitives (no sprite sheets). A* pathfinding, procedural levels, roguelite unlocks. Shows how to build a complex game system without external art assets. |
| **Polished Arcade Shooter** | Shoot-'em-up | [`phaethix/polished-arcade-shooter`](https://github.com/phaethix/polished-arcade-shooter) | TypeScript + Canvas 2D. Six game modes, procedural audio, local meta-progression. Fixed-timestep game loop. Clean typed domain modules. Good reference for larger game architectures. |

## How to Use During Research

```markdown
## RESEARCH
**Open-source references**: 
- [canvas-vampire-survivors](https://github.com/ricardo-foundry/canvas-vampire-survivors)
  — studied their modular ES module architecture and fixed-step game loop.
  Key takeaway: using ES module imports without a bundler keeps zero-dep promise.
- [Tower-Defense](https://github.com/Real-Fruit-Snacks/Tower-Defense)
  — studied their A* pathfinding on a grid and tower placement system.
  Key takeaway: drawing all art from Graphics primitives eliminates asset pipeline.
```

## License Notes

All listed repos use permissive licenses (MIT or equivalent). When studying:

1. **Clone locally** for exploration: `git clone <url>`
2. **Read the source** — focus on architecture, patterns, data flow
3. **NEVER copy code or assets** into output games
4. **Attribute** the reference in your research log
5. The cloned repo stays on your machine — it's gitignored at the project level
