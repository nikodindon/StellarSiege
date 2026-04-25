# STELLAR SIEGE
### A Space Invaders Tribute — Python · Pygame · 8-bit Sounds

---

## Overview

**Stellar Siege** is a classic space invaders game written in Python 3 with Pygame.
No external assets needed — ships, bullets, explosions and all sounds are generated
procedurally at runtime (numpy + pygame.mixer).

Wave-based progression, increasing difficulty, high score tracking, shield power-up,
particle explosions, and a retro aesthetic.

---

## Quick Start

```bash
# 1. Create & activate a virtual environment
python3 -m venv .venv && source .venv/bin/activate   # Linux/macOS
# python -m venv .venv && .venv\Scripts\activate      # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python game.py
```

---

## Controls

| Key | Action |
|-----|--------|
| `←` `→` or `Q` `D` | Move ship |
| `SPACE` | Shoot |
| `P` | Pause / Resume |
| `ESC` | Quit |

---

## Architecture

```
StellarSiege/
├── game.py                  # Entry point
├── requirements.txt
├── README.md
├── SPEC.md
├── src/
│   ├── constants.py         # All tunable constants
│   ├── entities.py           # Player, Enemy, Bullet, Explosion, StarField
│   ├── sound_manager.py     # Procedural 8-bit sound synthesis
│   └── game_state.py         # State machine (Menu/Playing/Paused/GameOver)
└── assets/
    ├── sounds/               # Reserved for future .wav files
    └── fonts/               # Reserved for custom fonts
```

### Design Decisions

**Pure Python + Pygame** — zero external assets, procedural generation for all visuals
and audio. Makes the codebase portable, auditable, and easy to fork.

**State machine** — `GameState` manages the game loop, state transitions, and rendering.
Clean separation between logic (`update`) and drawing (`draw`).

**Entity-based** — each game object (`Player`, `Enemy`, `Bullet`, `Explosion`) is
self-contained with its own `update()` / `draw()` method.

**Sound synthesis** — `SoundManager` generates 8-bit sounds via numpy at runtime.
No `.wav`/`.ogg` files needed. All sounds are small, crisp, and loop-friendly.

---

## Gameplay Features

| Feature | Description |
|---------|-------------|
| Wave system | 4 rows x 8 enemies per wave; speed increases each wave |
| Scoring | 100 pts per enemy; +500 wave clear bonus |
| Lives | 3 lives; blinking invincibility after a hit |
| Shield | 2-second shield activates after each hit (absorbs 1 bullet) |
| Enemy AI | Enemies march left/right, drop, and fire back at intervals |
| Explosion particles | Per-enemy burst with 12 colored particles |
| Starfield | Parallax scrolling star background |
| High score | Persists for the session |

---

## Requirements

- Python 3.9+
- pygame >= 2.5.0
- numpy >= 1.24.0

---

## Future Ideas (PRs welcome)

- [ ] Boss enemy every 5 waves
- [ ] Power-ups: rapid fire, spread shot, bomb
- [ ] Sound toggle (M key)
- [ ] Save high score to file
- [ ] Multiple player colors / ship skins
- [ ] Level editor or custom wave definitions
- [ ] Pack to .exe with PyInstaller

---

## License

MIT — do whatever you want with it.
