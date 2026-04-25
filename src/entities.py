# ═══════════════════════════════════════════════════════════════
# STELLARSIEGE — Entities (Player, Enemy, Bullet, Explosion)
# ═══════════════════════════════════════════════════════════════

import pygame
import random
from src.constants import *


# ─── PLAYER ───────────────────────────────────────────────────

class Player(pygame.sprite.Sprite):
    def __init__(self, sound_manager):
        super().__init__()
        self.sound = sound_manager
        self._surfaces()
        self.rect = self.image.get_rect(
            midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20)
        )
        self.speed = PLAYER_SPEED
        self.lifes = PLAYER_LIFES
        self.fire_cooldown = 0
        self.shield_active = False
        self.shield_timer = 0
        self.visible = True
        self.blink_timer = 0

    def _surfaces(self):
        # Ship body
        self.image = pygame.Surface(PLAYER_SIZE, pygame.SRCALPHA)
        body = pygame.Surface((36, 24))
        body.fill(CYAN)
        self.image.blit(body, (7, 8))
        # Wings
        wing_l = pygame.Surface((10, 14))
        wing_l.fill(CYAN)
        self.image.blit(wing_l, (0, 18))
        wing_r = pygame.Surface((10, 14))
        wing_r.fill(CYAN)
        self.image.blit(wing_r, (40, 18))
        # Cockpit
        cockpit = pygame.Surface((12, 10))
        cockpit.fill(WHITE)
        self.image.blit(cockpit, (19, 4))
        # Engine glow
        eng = pygame.Surface((8, 6))
        eng.fill(YELLOW)
        self.image.blit(eng, (21, 30))

        # Shield surface (same size)
        self.shield_surf = pygame.Surface(PLAYER_SIZE, pygame.SRCALPHA)
        pygame.draw.ellipse(self.shield_surf, (0, 200, 255, 60), self.shield_surf.get_rect(), 3)

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

        # Shield timer
        if self.shield_timer > 0:
            self.shield_timer -= 1
            if self.shield_timer == 0:
                self.shield_active = False

        # Blink when hit
        if not self.visible:
            self.blink_timer += 1
            if self.blink_timer >= 6:
                self.visible = True
                self.blink_timer = 0

    def shoot(self):
        if self.fire_cooldown == 0:
            self.fire_cooldown = PLAYER_FIRE_RATE
            self.sound.play("shoot")
            return Bullet(self.rect.centerx, self.rect.top)
        return None

    def hit(self):
        if self.shield_active:
            self.sound.play("shield_hit")
            return False
        self.lifes -= 1
        self.sound.play("explosion")
        self.visible = False
        self.blink_timer = 0
        if self.lifes > 0:
            self.shield_active = True
            self.shield_timer = 120  # 2 sec at 60fps
        return self.lifes <= 0

    def draw(self, surface):
        if self.visible:
            surface.blit(self.image, self.rect)
            if self.shield_active:
                surface.blit(self.shield_surf, self.rect)


# ─── ENEMY ─────────────────────────────────────────────────────

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, row, sound_manager):
        super().__init__()
        self.sound = sound_manager
        self.row = row
        self._surfaces()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.base_x = x
        self.direction = 1
        self.drop_pending = False

    def _surfaces(self):
        colors = [GREEN, YELLOW, RED, (180, 100, 255)]
        col = colors[self.row % len(colors)]
        self.image = pygame.Surface(ENEMY_SIZE, pygame.SRCALPHA)
        # Body
        body = pygame.Surface((30, 20))
        body.fill(col)
        self.image.blit(body, (5, 4))
        # Eyes
        eye_l = pygame.Surface((8, 6))
        eye_l.fill(WHITE)
        self.image.blit(eye_l, (6, 6))
        eye_r = pygame.Surface((8, 6))
        eye_r.fill(WHITE)
        self.image.blit(eye_r, (26, 6))
        pupil = pygame.Surface((4, 4))
        pupil.fill(RED)
        self.image.blit(pupil, (8, 7))
        self.image.blit(pupil, (28, 7))
        # Antennae
        ant = pygame.Surface((3, 10))
        ant.fill(col)
        self.image.blit(ant, (12, 0))
        self.image.blit(ant, (25, 0))

    def update(self, dx):
        self.rect.x += dx * self.direction

    def reverse(self):
        self.direction *= -1

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# ─── BULLET ─────────────────────────────────────────────────────

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy=False):
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT), pygame.SRCALPHA)
        color = RED if enemy else YELLOW
        pygame.draw.rect(self.image, color, self.image.get_rect())
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = BULLET_SPEED if not enemy else BULLET_SPEED * 0.6
        self.is_enemy = enemy

    def update(self):
        sign = -1 if not self.is_enemy else 1
        self.rect.y += self.speed * sign
        if self.rect.y < -20 or self.rect.y > SCREEN_HEIGHT + 20:
            self.kill()


# ─── EXPLOSION ─────────────────────────────────────────────────

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.particles = []
        self.frame = 0
        for _ in range(PARTICLE_COUNT):
            angle = random.uniform(0, 6.28)
            speed = random.uniform(2, 6)
            self.particles.append({
                "x": x, "y": y,
                "vx": speed * __import__("math").cos(angle),
                "vy": speed * __import__("math").sin(angle),
                "life": random.randint(EXPLOSION_DURATION // 2, EXPLOSION_DURATION),
                "color": random.choice([YELLOW, RED, WHITE, (255, 150, 0)])
            })

    def update(self):
        self.frame += 1
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
        self.particles = [p for p in self.particles if p["life"] > 0]
        return self.frame < EXPLOSION_DURATION

    def draw(self, surface):
        for p in self.particles:
            alpha = int(255 * p["life"] / EXPLOSION_DURATION)
            size = max(1, int(4 * p["life"] / EXPLOSION_DURATION))
            col = (*p["color"][:3], alpha)
            psurf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.rect(psurf, col, psurf.get_rect())
            surface.blit(psurf, (int(p["x"]) - size, int(p["y"]) - size))


# ─── STARFIELD ──────────────────────────────────────────────────

class StarField:
    def __init__(self):
        self.stars = []
        for _ in range(STAR_COUNT):
            self.stars.append({
                "x": random.uniform(0, SCREEN_WIDTH),
                "y": random.uniform(0, SCREEN_HEIGHT),
                "speed": random.uniform(STAR_SPEED_MIN, STAR_SPEED_MAX),
                "size": random.choice([1, 1, 1, 2])
            })

    def update(self):
        for s in self.stars:
            s["y"] += s["speed"]
            if s["y"] > SCREEN_HEIGHT:
                s["y"] = 0
                s["x"] = random.uniform(0, SCREEN_WIDTH)

    def draw(self, surface):
        for s in self.stars:
            pygame.draw.circle(surface, LIGHT_GRAY, (int(s["x"]), int(s["y"])), s["size"])
