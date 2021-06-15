import pygame
import time
import os
import random
import keyboard

pygame.font.init()

WINDOW_WIDTH = 480
WINDOW_HEIGHT = 800
FIELD_MARGIN = 5

PLAYER_SPRITE = pygame.image.load(os.path.join("sprites", "player.png"))
PLATFORM_SPRITE = pygame.image.load(os.path.join("sprites", "platform.png"))
BG_SPRITE = pygame.image.load(os.path.join("sprites", "bg.png"))

SCORE_FONT = pygame.font.SysFont("Verdana", 36)

class Player:
    VELOCITY_X = 4
    VELOCITY_Y = 10
    MAX_VELOCITY_Y = 10
    JUMP_POWER = 1.5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.height = self.y
        self.jump_tick = 0

    def moveLeft(self):
        self.velocity_x = -self.VELOCITY_X

    def moveRight(self):
        self.velocity_x = self.VELOCITY_X

    def resetStrafe(self):
        self.velocity_x = 0

    def jump(self):
        self.velocity_y = -self.VELOCITY_Y
        self.jump_tick = 0
        self.height = self.y

    def move(self):
        self.jump_tick += 1

        vy = self.velocity_y * self.jump_tick + self.JUMP_POWER * self.jump_tick ** 2

        if vy >= self.MAX_VELOCITY_Y:
            vy = self.MAX_VELOCITY_Y

        if vy < 0:
            vy -= 2

        vx = self.velocity_x

        self.y = self.y + vy
        self.x = self.x + vx



    def draw(self, win):
        win.blit(PLAYER_SPRITE, (self.x, self.y))

class Platform:
    VELOCITY = 5

    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = PLATFORM_SPRITE.get_width()

        self.set_position()

    def set_position(self):
        self.x = random.randrange(
            FIELD_MARGIN,
            WINDOW_WIDTH - self.width - FIELD_MARGIN
        )

    def draw(self, win):
        win.blit(PLATFORM_SPRITE, (self.x, self.y))

def draw_window(win, player, platforms, score):
    win.blit(BG_SPRITE, (0, 0))

    scoreText = SCORE_FONT.render(str(score), 1, (0, 0, 0))
    win.blit(
        scoreText,
        (10, 10)
    )

    for platform in platforms:
        platform.draw(win)

    player.draw(win)

    pygame.display.update()

def main():
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    player = Player(200, 200)
    platforms = [Platform()]

    run = True
    score = 0

    while run:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        if keyboard.is_pressed("a"):
            player.moveLeft()
        elif keyboard.is_pressed("d"):
            player.moveRight()
        else:
            player.resetStrafe()

        if keyboard.is_pressed("w"):
            player.jump()

        player.move();

        draw_window(win, player, platforms, score)

main()
