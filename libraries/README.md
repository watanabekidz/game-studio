# Libraries
<LIBRARIES_INDEX>
  Shared libraries that get inlined into game output during scaffolding.
  Engines (LittleJS, Phaser, Three.js, Babylon.js) are vendored copies
  of their respective open-source MIT/Apache 2.0 releases.
</LIBRARIES_INDEX>

## Available Libraries

| Library | Size | Description | When to use |
|---|---|---|---|
| `canvas-engine.js` | ~2 KB | DPR-aware canvas, game loop, tweening | Any Canvas 2D game |
| `input-handler.js` | ~2 KB | Keyboard tracking, bindings, just-pressed | Any interactive game |
| `physics-engine.js` | ~2 KB | AABB collision, gravity, platform resolve | Platformer, physics games |
| `particle-system.js` | ~2 KB | Emitter-based 2D particles with camera offset | Action games, feedback |
| `platformer-engine.js` | ~4 KB | Player entity, camera, parallax, update helper | Side-scrollers, platformers |
| `scorm-wrapper.js` | ~2 KB | LMS API (LMSInitialize, LMSSetValue, LMSCommit) | SCORM 1.2 packaging |
| `littlejs.release.js` | ~30 KB | Full 2D game engine (physics, particles, audio, input) | Tiny action games |
| `zzfxmicro.js` | ~1 KB | Procedural sound effect generator | Audio in LittleJS games |
| `phaser.min.js` | ~500 KB | Full 2D framework (scenes, tilemaps, Matter.js physics) | RPGs, complex 2D games |

## Adding a New Library

1. Create the `.js` file in this directory
2. Update this README with the entry
3. Update AGENTS.md CONVENTIONS library table
4. If vendoring from open-source: record the version and source URL in this README

## Vendored Sources

| Library | Version | Source |
|---|---|---|
| `littlejs.release.js` | latest (main) | https://github.com/KilledByAPixel/LittleJS |
| `zzfxmicro.js` | latest (master) | https://github.com/KilledByAPixel/ZzFX |
| `phaser.min.js` | latest | https://github.com/phaserjs/phaser |
