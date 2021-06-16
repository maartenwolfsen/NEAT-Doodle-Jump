import pygame
import time
import os
import random
import keyboard

pygame.font.init()

WINDOW_WIDTH = 480
WINDOW_HEIGHT = 800
FIELD_MARGIN = 5
JUMP_THRESHOLD = 210

PLAYER_SPRITE_RIGHT = pygame.image.load(os.path.join("sprites", "player.png"))
PLAYER_SPRITE_LEFT = pygame.transform.flip(PLAYER_SPRITE_RIGHT, True, False)
PLATFORM_SPRITE = pygame.image.load(os.path.join("sprites", "platform.png"))
BG_SPRITE = pygame.image.load(os.path.join("sprites", "bg.png"))

SCORE_FONT = pygame.font.SysFont("Verdana", 36)

class Player:
    VELOCITY_X = 4
    VELOCITY_Y = 10
    JUMP_VELOCITY = 0.4
    MAX_VELOCITY_Y = 10
    JUMP_POWER = 1.5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.height = self.y
        self.jump_tick = 0
        self.has_jumped = False
        self.vy = 0
        self.image = PLAYER_SPRITE_RIGHT

    def moveLeft(self):
        self.velocity_x = -self.VELOCITY_X
        self.image = PLAYER_SPRITE_LEFT

    def moveRight(self):
        self.velocity_x = self.VELOCITY_X
        self.image = PLAYER_SPRITE_RIGHT

    def resetStrafe(self):
        self.velocity_x = 0

    def jump(self):
        if not self.has_jumped:
            self.velocity_y = -self.VELOCITY_Y
            self.jump_tick = 0
            self.height = self.y

    def move(self):
        self.jump_tick += self.JUMP_VELOCITY

        vy = self.velocity_y * self.jump_tick + self.JUMP_POWER * self.jump_tick ** 2

        if vy >= self.MAX_VELOCITY_Y:
            vy = self.MAX_VELOCITY_Y

        if vy < 0:
            vy -= 2

        self.vy = vy
        self.y = self.y + vy
        self.x = self.x + self.velocity_x

    def draw(self, win):
        win.blit(self.image, (self.x, self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.image)

class Platform:
    VELOCITY = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLATFORM_SPRITE.get_width()
        self.height = PLATFORM_SPRITE.get_height()

        self.set_position()

    def set_position(self):
        self.x = random.randrange(
            FIELD_MARGIN,
            WINDOW_WIDTH - self.width - FIELD_MARGIN
        )

    def move(self, y):
        self.y += y

    def draw(self, win):
        win.blit(PLATFORM_SPRITE, (self.x, self.y))

    def collide(self, player):
        player_mask = player.get_mask()
        platform_mask = pygame.mask.from_surface(PLATFORM_SPRITE)

        offset = (self.x - player.x, self.y - round(player.y))
        point = player_mask.overlap(platform_mask, offset)

        return bool(point)

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
    platforms = []
    max_platforms = 7
    current_height = 0

    run = True
    score = 0

    # Generate Platforms
    for i in range(max_platforms):
        platform_x = random.randrange(
            FIELD_MARGIN,
            WINDOW_WIDTH - PLATFORM_SPRITE.get_width() - FIELD_MARGIN
        )
        platform_y = random.randrange(
            FIELD_MARGIN,
            WINDOW_HEIGHT - PLATFORM_SPRITE.get_height() - FIELD_MARGIN
        )

        for platform in platforms:
            while platform_y >= platform.y and platform_y <= platform.y + platform.height:
                platform_y = random.randrange(
                    FIELD_MARGIN,
                    WINDOW_HEIGHT - PLATFORM_SPRITE.get_height() - FIELD_MARGIN
                )

        platforms.append(Platform(
            platform_x,
            platform_y
        ))

    while run:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # TODO: Leave controls to Neural Network
        if keyboard.is_pressed("a"):
            player.moveLeft()
        elif keyboard.is_pressed("d"):
            player.moveRight()
        else:
            player.resetStrafe()

        for platform in platforms:
            if platform.y > WINDOW_HEIGHT:
                platforms.remove(platform)
                platforms.append(Platform(
                    random.randrange(
                        FIELD_MARGIN,
                        WINDOW_WIDTH - PLATFORM_SPRITE.get_width() - FIELD_MARGIN
                    ),
                    -50
                ))

            if platform.collide(player):
                player.jump()

        player.move();

        if player.y <= JUMP_THRESHOLD:
            player.y = JUMP_THRESHOLD

            for platform in platforms:
                current_height = -round(player.vy)
                score = score + current_height
                platform.move(current_height)

        if player.y >= WINDOW_HEIGHT:
            score = "GAME OVER"

        draw_window(win, player, platforms, score)

main()
