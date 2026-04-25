#!/usr/bin/env python3
"""
Stellar Siege — A classic space invaders game with 8-bit sounds.
"""

import pygame
import sys
from constants import *
from sound_manager import SoundManager
from entities import Player
from game_state import GameState, MENU, PLAYING, PAUSED, GAME_OVER, WAVE_COMPLETE


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
        dt = clock.tick(FPS)
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

        # Update
        if state.state == PLAYING:
            player.update(keys)
            player.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        state.update(keys)

        # Draw
        screen.fill(BLACK)
        state.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
