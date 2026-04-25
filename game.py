#!/usr/bin/env python3
"""
Stellar Siege — Entry point.
"""
import pygame
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
os.chdir(os.path.dirname(__file__))

from src.constants import *
from src.sound_manager import SoundManager
from src.entities import Player
from src.game_state import GameState, MENU, PLAYING, PAUSED, GAME_OVER, WAVE_COMPLETE


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    sound = SoundManager(enabled=True)
    state = GameState(sound)
    player = None

    running = True
    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_SPACE:
                    if state.state == MENU:
                        player = Player(sound)
                        state.start_game(player)
                    elif state.state == GAME_OVER:
                        if state.score > state.high_score:
                            state.high_score = state.score
                        player = Player(sound)
                        state.start_game(player)
                    elif state.state == PLAYING:
                        bullet = player.shoot()
                        if bullet:
                            state.player_bullets.add(bullet)

                elif event.key == pygame.K_p:
                    if state.state == PLAYING:
                        state.state = PAUSED
                    elif state.state == PAUSED:
                        state.state = PLAYING

        if state.state == PLAYING:
            player.update(keys)
            player.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        state.update(keys)

        screen.fill(BLACK)
        state.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
