# Sound Manager — 8-bit procedural synthesis (numpy + pygame.mixer)
# No external audio files needed.

import pygame
import numpy as np


def _tone(freq, dur_ms, vol=0.4, wtype="square", fade=True):
    n = int(22050 * dur_ms / 1000)
    t = np.linspace(0, dur_ms / 1000, n, endpoint=False)
    if wtype == "square":
        w = np.sign(np.sin(2 * np.pi * freq * t))
    elif wtype == "sawtooth":
        w = 2 * (t * freq % 1) - 1
    elif wtype == "sine":
        w = np.sin(2 * np.pi * freq * t)
    else:
        w = np.random.uniform(-1, 1, n)
    w = w * vol
    if fade:
        fl = min(n // 4, 500)
        if fl > 0:
            w[:fl] *= np.linspace(0, 1, fl)
            w[-fl:] *= np.linspace(1, 0, fl)
    w = np.clip(w, -1, 1)
    return (w * 32767).astype(np.int16)


def _snd_shoot():
    d = np.concatenate([_tone(880, 40, 0.3), _tone(440, 60, 0.25)])
    return pygame.mixer.Sound(buffer=d)


def _snd_explosion():
    n = _tone(0, 300, 0.5, "noise")
    l = _tone(60, 300, 0.4, "sine")
    c = np.clip((n.astype(float) + l.astype(float) * 0.5) / 1.5, -1, 1)
    return pygame.mixer.Sound(buffer=(c * 32767).astype(np.int16))


def _snd_enemy_shoot():
    d = np.concatenate([_tone(220, 50, 0.2), _tone(110, 80, 0.15)])
    return pygame.mixer.Sound(buffer=d)


def _snd_powerup():
    freqs = [523, 659, 784, 1047]
    d = np.concatenate([_tone(f, 70, 0.25) for f in freqs])
    return pygame.mixer.Sound(buffer=d)


def _snd_shield_hit():
    return pygame.mixer.Sound(buffer=_tone(1200, 100, 0.3, "sine"))


def _snd_game_over():
    freqs = [392, 349, 330, 262]
    d = np.concatenate([_tone(f, 250, 0.35) for f in freqs])
    return pygame.mixer.Sound(buffer=d)


def _snd_wave_complete():
    freqs = [523, 659, 784, 1047, 784, 1047]
    d = np.concatenate([_tone(f, 120, 0.3) for f in freqs])
    return pygame.mixer.Sound(buffer=d)


class SoundManager:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self._sounds = {}
        self._volume = 0.6
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self._sounds = {
                "shoot":         _snd_shoot(),
                "explosion":     _snd_explosion(),
                "enemy_shoot":   _snd_enemy_shoot(),
                "powerup":       _snd_powerup(),
                "shield_hit":    _snd_shield_hit(),
                "game_over":     _snd_game_over(),
                "wave_complete": _snd_wave_complete(),
            }
            self._apply_volume()
        except Exception as e:
            print(f"[SoundManager] sound init failed (no audio): {e}")
            self.enabled = False

    def _apply_volume(self):
        for s in self._sounds.values():
            s.set_volume(self._volume)

    def play(self, name):
        if self.enabled and name in self._sounds:
            self._sounds[name].play()

    def set_volume(self, vol):
        self._volume = max(0.0, min(1.0, vol))
        self._apply_volume()
