# Stellar Siege — Specification

## 1. Project Overview

**Type:** 2D arcade game (Space Invaders tribute)
**Language:** Python 3
**Framework:** Pygame
**Summary:** Wave-based space shooter with procedural graphics and 8-bit synthesized audio. No external assets required.

---

## 2. Visual & Rendering

### Scene Setup
- **Canvas:** 800x600, 60 FPS
- **Background:** Scrolling parallax starfield (100 stars, 2 speed tiers)
- **Color palette:** Dark background (#000000), cyan player, colored enemies by row (green/yellow/red/purple), yellow player bullets, red enemy bullets

### Entities
| Entity | Visual | Size |
|--------|--------|------|
| Player ship | Cyan geometric polygon with engine glow | 50x40 |
| Enemy | Colored UFO with eyes + antennae, row-based color | 40x30 |
| Player bullet | Yellow rectangle | 4x15 |
| Enemy bullet | Red rectangle (slower) | 4x15 |
| Explosion | 12 colored particles with physics |  |
| Shield | Translucent ellipse overlay | 50x40 |

### HUD
- Top-left: SCORE + HIGH SCORE
- Top-right: WAVE number
- Bottom-right: life indicators (ship triangles)

### Screens
- **Menu:** Title, controls list, high score
- **Playing:** Game world + HUD
- **Paused:** Darkened overlay + "PAUSED" text
- **Game Over:** Score, high score, "PLAY AGAIN" prompt
- **Wave Complete:** Overlay + wave clear announcement

---

## 3. Simulation / Game Logic

### Player
- Horizontal movement (arrows or Q/D), 5 px/frame
- Shoot with SPACE, 12-frame cooldown
- 3 lives, blink invincible for ~0.1s after hit
- Auto-activates 2-second shield after each hit (absorbs 1 bullet)

### Enemy Waves
- 4 rows x 8 enemies = 32 per wave
- March left/right at constant speed, drop 30px at edges
- Speed increases: base 1.5 + 0.3 per wave
- Shoot at intervals: starts 90 frames, -10 per wave (min 30)

### Collision
- Player bullet -> enemy: enemy dies, +100 score, explosion
- Enemy bullet -> player: player loses life (or shield absorbs)
- Enemy -> player: player loses life
- Enemy reaches bottom: game over

### Scoring
- 100 pts per enemy killed
- +500 wave clear bonus
- High score tracked per session

---

## 4. Audio (Procedural, No Files)

All sounds synthesized at runtime via numpy + pygame.mixer.Sound:

| Sound | Method |
|-------|--------|
| shoot | Descending square wave (880->440 Hz) |
| explosion | Noise burst + low sine rumble |
| enemy_shoot | Low square wave (220->110 Hz) |
| powerup | Ascending arpeggio (523->1047 Hz) |
| shield_hit | High sine ping (1200 Hz) |
| game_over | Descending sad arpeggio |
| wave_complete | Victory jingle |

---

## 5. State Machine

States: MENU | PLAYING | PAUSED | GAME_OVER | WAVE_COMPLETE

Transitions:
- MENU --(SPACE)--> PLAYING
- PLAYING --(P)--> PAUSED --(P)--> PLAYING
- PLAYING --(death)--> GAME_OVER
- PLAYING --(clear wave)--> WAVE_COMPLETE --(timer)--> PLAYING
- GAME_OVER --(SPACE)--> PLAYING

---

## 6. File Structure

```
StellarSiege/
├── game.py               # Entry point
├── requirements.txt
├── README.md
├── SPEC.md               # This file
├── src/
│   ├── constants.py      # SCREEN_WIDTH, FPS, speeds, colors, paths
│   ├── entities.py       # Player, Enemy, Bullet, Explosion, StarField
│   ├── sound_manager.py  # SoundManager (procedural synthesis)
│   └── game_state.py     # GameState state machine + all screens
└── assets/
    ├── sounds/           # Reserved for future .wav files
    └── fonts/            # Reserved for custom fonts
```

---

## 7. Dependencies

- pygame >= 2.5.0
- numpy >= 1.24.0

---

## 8. Controls Summary

| Key | Action |
|-----|--------|
| LEFT/RIGHT or Q/D | Move |
| SPACE | Shoot / Start / Restart |
| P | Pause / Resume |
| ESC | Quit |
