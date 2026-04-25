# ═══════════════════════════════════════════════════════════════
# STELLARSIEGE — Game State (Menu, Playing, GameOver, etc.)
# ═══════════════════════════════════════════════════════════════

import pygame
from src.constants import *
from src.entities import Enemy, StarField

# States
MENU = "menu"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"
WAVE_COMPLETE = "wave_complete"


class GameState:
    def __init__(self, sound_manager):
        self.sound = sound_manager
        self.state = MENU
        self.score = 0
        self.high_score = 0
        self.wave = 1
        self.player = None
        self.enemies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.explosions = []
        self.enemy_move_timer = 0
        self.enemy_shoot_timer = 0
        self.enemy_bullet_interval = 90
        self.wave_complete_timer = 0
        self.starfield = StarField()

    def start_game(self, player):
        self.state = PLAYING
        self.score = 0
        self.wave = 1
        self.player = player
        self.player_bullets.empty()
        self.enemy_bullets.empty()
        self.explosions = []
        self._spawn_wave()

    def _spawn_wave(self):
        self.enemies.empty()
        self.enemy_bullets.empty()
        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                x = ENEMY_MARGIN_X + col * ENEMY_SPACING_X
                y = ENEMY_MARGIN_TOP + row * ENEMY_SPACING_Y
                self.enemies.add(Enemy(x, y, row, self.sound))
        # Speed scales with wave
        self.enemy_move_timer = 0
        self.enemy_bullet_interval = max(30, 90 - (self.wave - 1) * 10)
        self.enemy_shoot_timer = 0

    def next_wave(self):
        self.wave += 1
        self.score += 500  # wave bonus
        self.sound.play("wave_complete")
        self.wave_complete_timer = 120
        self._spawn_wave()

    def add_explosion(self, x, y):
        from entities import Explosion
        self.explosions.append(Explosion(x, y))

    def update(self, keys):
        self.starfield.update()

        if self.state == WAVE_COMPLETE:
            self.wave_complete_timer -= 1
            if self.wave_complete_timer <= 0:
                self.state = PLAYING
            for e in list(self.explosions):
                if not e.update():
                    self.explosions.remove(e)
            return

        if self.state != PLAYING:
            return

        # ── Enemy movement ──
        all_at_edge = True
        for e in self.enemies:
            e.update(ENEMY_SPEED + (self.wave - 1) * 0.3)
            # Check if any enemy can still move
            if e.direction == 1 and e.rect.right < SCREEN_WIDTH - 10:
                all_at_edge = False
            elif e.direction == -1 and e.rect.left > 10:
                all_at_edge = False

        if all_at_edge and self.enemies:
            for e in self.enemies:
                e.reverse()
                e.rect.y += ENEMY_DROP
            # Check if any enemy reached player
            for e in self.enemies:
                if e.rect.bottom >= self.player.rect.top:
                    self.player.lifes = 0
                    self.state = GAME_OVER
                    self.sound.play("game_over")
                    return

        # ── Enemy shooting ──
        self.enemy_shoot_timer += 1
        if self.enemy_shoot_timer >= self.enemy_bullet_interval and self.enemies:
            self.enemy_shoot_timer = 0
            shooters = list(self.enemies)
            shooter = shooters[self.enemy_move_timer % len(shooters)]
            self.enemy_bullets.add(Bullet(shooter.rect.centerx, shooter.rect.bottom, enemy=True))
            self.sound.play("enemy_shoot")

        # ── Bullets ──
        self.player_bullets.update()
        self.enemy_bullets.update()

        # ── Explosions ──
        for e in list(self.explosions):
            if not e.update():
                self.explosions.remove(e)

        # ── Collision: player bullets → enemies ──
        hits = pygame.sprite.groupcollide(
            self.player_bullets, self.enemies, True, True
        )
        for bullet, enemy_list in hits.items():
            e = enemy_list[0]
            self.score += ENEMY_SCORE
            self.add_explosion(e.rect.centerx, e.rect.centery)
            self.sound.play("explosion")

        # ── Collision: enemy bullets → player ──
        if pygame.sprite.spritecollide(self.player, self.enemy_bullets, True):
            if self.player.hit():
                self.state = GAME_OVER
                self.sound.play("game_over")

        # ── Collision: enemies → player ──
        if pygame.sprite.spritecollide(self.player, self.enemies, True):
            if self.player.hit():
                self.state = GAME_OVER
                self.sound.play("game_over")

        # ── Wave cleared ──
        if not self.enemies:
            self.next_wave()

    def draw(self, surface):
        self.starfield.draw(surface)

        if self.state == MENU:
            self._draw_menu(surface)
        elif self.state == GAME_OVER:
            self._draw_game_over(surface)
        elif self.state == WAVE_COMPLETE:
            self._draw_wave_complete(surface)
        else:
            # Playing or Paused
            self._draw_game(surface)
            if self.state == PAUSED:
                self._draw_paused(surface)

    def _draw_game(self, surface):
        for e in self.enemies:
            e.draw(surface)
        self.player.draw(surface)
        for b in self.player_bullets:
            surface.blit(b.image, b.rect)
        for b in self.enemy_bullets:
            surface.blit(b.image, b.rect)
        for ex in self.explosions:
            ex.draw(surface)
        self._draw_hud(surface)

    def _draw_hud(self, surface):
        font = pygame.font.Font(None, 28)
        sc = font.render(f"SCORE: {self.score}", True, WHITE)
        surface.blit(sc, (10, 8))
        hs = font.render(f"HIGH: {self.high_score}", True, LIGHT_GRAY)
        surface.blit(hs, (10, 34))
        wv = font.render(f"WAVE {self.wave}", True, CYAN)
        surface.blit(wv, (SCREEN_WIDTH - 100, 8))
        # Lifes
        for i in range(self.player.lifes):
            x = SCREEN_WIDTH - 20 - i * 25
            pygame.draw.polygon(surface, CYAN,
                [(x, SCREEN_HEIGHT - 8), (x - 8, SCREEN_HEIGHT - 18), (x + 8, SCREEN_HEIGHT - 18)])

    def _draw_menu(self, surface):
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("STELLAR SIEGE", True, CYAN)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 160))
        sub = pygame.font.Font(None, 28).render("PRESS  SPACE  TO  START", True, WHITE)
        surface.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 240))
        controls = [
            "ARROWS or Q/D  —  MOVE",
            "SPACE  —  SHOOT",
            "P  —  PAUSE",
            "ESC  —  QUIT",
        ]
        for i, line in enumerate(controls):
            t = pygame.font.Font(None, 22).render(line, True, LIGHT_GRAY)
            surface.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 310 + i * 26))
        if self.high_score > 0:
            hs = pygame.font.Font(None, 26).render(f"HIGH SCORE: {self.high_score}", True, YELLOW)
            surface.blit(hs, (SCREEN_WIDTH // 2 - hs.get_width() // 2, 460))

    def _draw_paused(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))
        t = pygame.font.Font(None, 60).render("PAUSED", True, WHITE)
        surface.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
        h = pygame.font.Font(None, 24).render("PRESS P TO RESUME", True, LIGHT_GRAY)
        surface.blit(h, (SCREEN_WIDTH // 2 - h.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

    def _draw_game_over(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        t = pygame.font.Font(None, 64).render("GAME OVER", True, RED)
        surface.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 180))
        sc = pygame.font.Font(None, 32).render(f"SCORE: {self.score}", True, WHITE)
        surface.blit(sc, (SCREEN_WIDTH // 2 - sc.get_width() // 2, 260))
        if self.score >= self.high_score:
            hs = pygame.font.Font(None, 28).render("NEW HIGH SCORE!", True, YELLOW)
            surface.blit(hs, (SCREEN_WIDTH // 2 - hs.get_width() // 2, 300))
        else:
            hs = pygame.font.Font(None, 24).render(f"HIGH SCORE: {self.high_score}", True, LIGHT_GRAY)
            surface.blit(hs, (SCREEN_WIDTH // 2 - hs.get_width() // 2, 300))
        prompt = pygame.font.Font(None, 24).render("PRESS SPACE TO PLAY AGAIN", True, WHITE)
        surface.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 380))

    def _draw_wave_complete(self, surface):
        # Draw game behind
        self._draw_game(surface)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))
        t = pygame.font.Font(None, 56).render(f"WAVE {self.wave - 1} CLEAR!", True, GREEN)
        surface.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
        bonus = pygame.font.Font(None, 24).render("+500 BONUS", True, YELLOW)
        surface.blit(bonus, (SCREEN_WIDTH // 2 - bonus.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
