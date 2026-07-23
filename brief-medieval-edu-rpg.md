## Game Brief: The Traveller's Tale

### 1. Core Identity
- **Logline**: A weary traveller walks into a medieval tavern — and starts uncovering the stories that built the Middle Ages.
- **Core Pillars**: Historical discovery through conversation; medieval atmosphere; player-driven inquiry; expandable world
- **Player Transformation**: After playing, the learner should be able to explain the social, architectural, and religious forces that shaped medieval Europe — not from rote memorization, but from having lived the conversations.
- **Genre**: Educational 2D RPG (top-down, tilemap-based exploration and NPC dialog)
- **Game type**: Educational
- **Platform(s)**: Web (self-contained HTML via RPG-JS standalone mode)
- **Target Audience**: Middle school / early high school (ages 11-14), history/social studies context
- **Visual style**: 16-bit pixel art, top-down 2D, tilemap-based (Tiled `.tmx` format), retro RPG aesthetic

### Learning Design

- **Learning objectives** (Bloom's Taxonomy):
  | Level | Objective |
  |---|---|
  | Remember | Recall key terms: nave, flying buttress, crusade, pilgrimage, relic |
  | Understand | Explain the purpose of a Gothic cathedral and its role in medieval life |
  | Analyze | Compare the motivations of different participants in the Crusades |
  | Evaluate | Assess how the Catholic Church shaped daily life in medieval Europe |

- **Learning mechanics → Game mechanics mapping** (LM-GM):
  | Learning objective | Learning mechanic | Game mechanic | In-game implementation |
  |---|---|---|---|
  | Understand Gothic architecture | Explore/Identify | Navigate tavern + examine objects | Player clicks on decorative elements; NPC monk explains cathedral features |
  | Analyze Crusade motivations | Listen/Compare | NPC dialog with branching choices | Knight, Monk, and Merchant each give their perspective on the Crusades |
  | Evaluate Church influence | Discuss/Debrief | Decision prompts | Player chooses responses to NPC questions, NPC reacts |
  | Recall historical terms | Practice/Retrieval | Item inspection + journal | Tavern objects (stained glass, relic box, pilgrim badge) reveal terms when examined |

- **Integration strategy**: Endogenous — historical content IS the gameplay. NPCs don't deliver lectures; they have conversations the player initiates. Learning happens through natural inquiry within the game world.
- **Interaction-first design**: Player explores the tavern freely, approaches any NPC, asks questions by selecting dialog options. No walls of text — history unfolds through conversation.
- **Assessment**: Stealth assessment through NPC reactions and dialog choices. The monk may correct a misunderstanding; the knight may challenge a simplistic view. The player internalizes through correction, not testing.

### 2. Game Systems
- **Core Loop**: Enter tavern → approach NPC → engage in dialog about a historical topic → learn through conversation → discover new topics/objects → optionally journal → repeat
- **Mechanics**: 
  - Free-roam top-down movement with WASD/arrow keys
  - Collision with walls, furniture, NPCs
  - NPC interaction via proximity + action button (Enter/Space)
  - Branching dialog trees with choice nodes
  - Object inspection (tavern items: stained glass, relic case, map, etc.)
  - A visible **doorway** leading out (locked/blocked for now — marks future expansion)
- **Controls**: Keyboard (WASD/arrows to move, Enter/Space to interact), mouse click also supported
- **Progression**: No stat-based progression. Progression is knowledge-based — the player unlocks more dialog branches as they ask the right questions. The finale is a "synthesis conversation" where an NPC asks the player to reflect on what they've learned.
- **Data**: Inline history content (NPC dialog scripts, object descriptions) — no external data files

### 3. Scope & Constraints
- **Engine options**:

  | Option | Engine | Provides | You build | Effort on content |
  |---|---|---|---|---|
  | **A (Recommended)** | RPG-JS v5 | Tilemap engine, NPC events, dialog system (showText, showChoices), player entity, camera, sprite animations, standalone mode, inventory, save/load, GUI | Historical dialog content, tavern map, NPC spritesheets, object inspection events, doorway marker | ~80% content, ~20% config |
  | B | Phaser 3 | Tilemap rendering, sprite management, input handling | Dialog system (from scratch), NPC event system, camera/scene management, save/load, inventory, GUI framework | ~40% content, ~60% engine infra |
  | C | Canvas 2D (canvas-engine.js) | DPR-aware canvas, game loop, basic input | Absolutely everything (tilemap, dialog, NPC, collision, camera, save) | ~10% content, ~90% infra |

  **Why RPG-JS wins**: It provides the complete RPG infrastructure (maps, events, dialog, NPCs, cameras, save/load, GUI) out of the box. Nearly all development effort goes into what matters for education: **writing good historical dialog** and **designing the tavern map**. The other options spend most effort re-building RPG systems that RPG-JS already delivers.

- **Cut line**:
  - NOT in scope: Combat, inventory management, character stats (XP/levels), quest log, multiplayer, sound effects, save/load persistence (deferred — RPG-JS supports it but MVP doesn't need it)
  - The doorway is a visual placeholder — the town beyond is NOT implemented
  - Only one map (the tavern interior) — no exterior town or world map
- **Dependencies**: Zero external for the output. RPG-JS is a build-time dependency (via `npm install` + Vite). The built output is self-contained HTML/JS.
- **SCORM target**: No (standard `games/` output)
- **Estimated complexity**: Medium (~300-400 lines of game config/events + historical content). The RPG-JS framework handles the heavy lifting.

### 4. Assumptions & Risk
- **Research conducted**: 
  - RPG-JS v5 docs fully studied (quick start, project structure, map creation, events, dialog, world transitions, spritesheets, TiledMap)
  - Comparable games studied: The Lord's Ledger (medieval economic sim), Cipherfell (medieval mystery RPG for cybersecurity), Universal History Simulator (procedural history sim)
  - Game-based learning framework reviewed (LM-GM model, endogenous integration, stealth assessment)
- **Comparable games**: 
  - The Lord's Ledger: Medieval economic simulation for 6th grade social studies. Proves browser-based medieval education games are viable. Key insight: embedded "Scribe's Notes" model for delivering historical context within gameplay.
  - Cipherfell: Medieval mystery RPG teaching cybersecurity reasoning. Proves narrative RPG format works for delivering abstract educational content. Key insight: NPC inquiry-based learning.
  - Universal History Simulator: LLM-driven procedural history. Proves pixel-art educational history games engage students. Key insight: failure modes are teachable.
- **Key risks**:
  - RPG-JS standalone mode (`provideRpg()`) is experimental — need to verify it works for our use case during scaffold/implement phase
  - Spritesheet creation: need free/pixel-art NPC sprites or generate procedurally (RPG-JS has a built-in character generator)
  - Historical content accuracy: dialog must be accurate enough for classroom use without being dry
- **Assumptions log**:
  - **Assumption**: `provideRpg()` standalone mode will work without a server. (Need to verify — RPG-JS normally runs via Vite dev server.)
  - **Assumption**: Tiled `.tmx` map format is supported by `@rpgjs/tiledmap`. (RPG-JS docs confirm this.)
  - **Fact**: RPG-JS v5.0.0-beta.7 is installed at `engines/rpgjs/`.
  - **Assumption**: The starter template `npx degit rpgjs/starter#v5` produces a scaffold we can modify. (Standard pattern per docs.)
  - **Fact**: OpenCode skills `rpgjs` and `rpgjs-studio` are installed and available.
