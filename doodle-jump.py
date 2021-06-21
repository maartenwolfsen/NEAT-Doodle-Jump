import pygame
import neat
import time
import os
import random
import keyboard

pygame.font.init()

WINDOW_WIDTH = 480
WINDOW_HEIGHT = 800
FIELD_MARGIN = 5
COLLISION_MARGIN = 10
MAX_GAP = 300
JUMP_THRESHOLD = 210
DEBUG_MODE = False
MAX_GENERATIONS = 500
MAX_PLATFORMS = 7
MAX_WHILE = 30

PLAYER_SPRITE_RIGHT = pygame.image.load(os.path.join("sprites", "player.png"))
PLAYER_SPRITE_LEFT = pygame.transform.flip(PLAYER_SPRITE_RIGHT, True, False)
PLAYER_JUMP_SPRITE_RIGHT = pygame.image.load(os.path.join("sprites", "player_jump.png"))
PLAYER_JUMP_SPRITE_LEFT = pygame.transform.flip(PLAYER_JUMP_SPRITE_RIGHT, True, False)
PLATFORM_SPRITE = pygame.image.load(os.path.join("sprites", "platform.png"))
BG_SPRITE = pygame.image.load(os.path.join("sprites", "bg.png"))
SCORE_FONT = pygame.font.SysFont("Verdana", 36)
DEBUG_FONT = pygame.font.SysFont("Verdana", 14)

class Player:
    VELOCITY_X = 4
    VELOCITY_Y = 10
    JUMP_VELOCITY = 0.4
    MAX_VELOCITY_Y = 10
    JUMP_POWER = 0.08

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.image = PLAYER_SPRITE_RIGHT
        self.height = self.image.get_height()
        self.width = self.image.get_width()
        self.jump_tick = 0
        self.jump_animation_timer = 30
        self.vy = 0

    def moveLeft(self):
        self.velocity_x = -self.VELOCITY_X

    def moveRight(self):
        self.velocity_x = self.VELOCITY_X

    def resetMove(self):
        self.velocity_x = 0

    def jump(self):
        self.velocity_y = -self.VELOCITY_Y
        self.jump_tick = 0

    def move(self):
        self.jump_tick += self.JUMP_VELOCITY

        vy = self.velocity_y + self.JUMP_POWER * self.jump_tick ** 2

        if vy >= self.MAX_VELOCITY_Y:
            vy = self.MAX_VELOCITY_Y

        if vy < 0:
            vy -= 2

        self.vy = vy
        self.y = self.y + vy
        self.x = self.x + self.velocity_x

        if self.jump_tick < 7:
            if self.velocity_x >= 0:
                self.image = PLAYER_JUMP_SPRITE_RIGHT
            else:
                self.image = PLAYER_JUMP_SPRITE_LEFT
        else:
            if self.velocity_x >= 0:
                self.image = PLAYER_SPRITE_RIGHT
            else:
                self.image = PLAYER_SPRITE_LEFT

        if self.x < 0 - (self.width / 2):
            self.x = WINDOW_WIDTH

        if self.x > WINDOW_WIDTH - (self.width / 2):
            self.x = 0 - (self.width / 2)

    def draw(self, win):
        win.blit(self.image, (self.x, self.y))

        if DEBUG_MODE:
            win.blit(
                DEBUG_FONT.render(
                    "Y: " + str(round(self.y)) + "; X: " + str(round(self.x)),
                    1,
                    (0, 0, 0)
                ),
                (self.x, self.y)
            )

            surface = pygame.Surface((self.width / 2, COLLISION_MARGIN))
            surface.set_alpha(128)
            surface.fill((0, 35, 255))
            win.blit(surface, (self.x + (self.width / 4), self.y + self.height))

    def collide(self, platforms):
        player_rect = pygame.Rect(
            self.x + (self.width / 4),
            self.y + self.height,
            self.width / 2,
            COLLISION_MARGIN
        )

        for platform in platforms:
            platform_rect = pygame.Rect(
                platform.x,
                platform.y,
                platform.width,
                platform.height
            )

            if player_rect.colliderect(platform_rect):
                return True

        return False

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

        if DEBUG_MODE:
            win.blit(
                DEBUG_FONT.render(
                    "Y: " + str(round(self.y)) + "; X: " + str(round(self.x)),
                    1,
                    (0, 0, 0)
                ),
                (self.x, self.y)
            )

            surface = pygame.Surface((self.width, self.height))
            surface.set_alpha(128)
            surface.fill((255, 0, 25))
            win.blit(surface, (self.x, self.y))

def draw_window(win, players, platforms, score):
    win.blit(BG_SPRITE, (0, 0))

    for platform in platforms:
        platform.draw(win)

    win.blit(
        SCORE_FONT.render(str(score), 1, (0, 0, 0)),
        (10, 10)
    )

    for player in players:
        player.draw(win)

    pygame.display.update()

def generateInitialPlatforms():
    prev_y = 0
    platforms = []

    for i in range(MAX_PLATFORMS):
        x = random.randrange(
            FIELD_MARGIN,
            WINDOW_WIDTH - PLATFORM_SPRITE.get_width() - FIELD_MARGIN
        )
        min = prev_y + FIELD_MARGIN
        y = 0
        i = 0

        while y < min or y > WINDOW_HEIGHT:
            i += 1

            if i < MAX_WHILE:
                y = random.randrange(
                    min,
                    min + MAX_GAP
                )
            else:
                y = WINDOW_HEIGHT - FIELD_MARGIN
                break

        prev_y = y

        platforms.append(Platform(x, y))

    return platforms

def main(genomes, config):
    networks = []
    ge = []
    players = []

    for _, g in genomes:
        network = neat.nn.FeedForwardNetwork.create(g, config)
        networks.append(network)
        players.append(Player(200, 200))
        g.fitness = 0
        ge.append(g)

    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    platforms = generateInitialPlatforms()
    current_height = 0
    run = True
    score = 0
    old_score = 0
    passive_counter = 0

    while run:
        clock.tick(60)

        # Quit Game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        if len(players) <= 0:
            run = False
            break

        platform_data = []

        # Refresh Platforms
        for platform in platforms:
            if platform.y > WINDOW_HEIGHT:
                platforms.remove(platform)
                platforms.append(Platform(
                    random.randrange(
                        FIELD_MARGIN,
                        WINDOW_WIDTH - PLATFORM_SPRITE.get_width() - FIELD_MARGIN
                    ),
                    0
                ))

            platform_data.append(platform.x)
            platform_data.append(platform.y)

        for index, player in enumerate(players):
            player_data = []

            player.move()
            player_data.append(player.x)
            player_data.append(player.y)

            output = networks[index].activate(platform_data + player_data)

            #print(output)

            # Move Player based on Neural Network Ouput
            if output[0] == -1.0:
                player.moveLeft()
            elif output[0] == 1.0:
                player.moveRight()
            else:
                player.resetMove()

            # Move Platforms if Player Y is above Jump Threshold
            if player.y <= JUMP_THRESHOLD:
                player.y = JUMP_THRESHOLD

                for platform in platforms:
                    current_height = -round(player.vy)
                    score += current_height

                    platform.move(current_height)

            # Check if Player is Passive (non-moving)
            if score > old_score:
                passive_counter = 0
                g.fitness += 0.1
            else:
                passive_counter += 1

            if passive_counter >= 200:
                ge[index].fitness -= 5
                players.pop(index)
                networks.pop(index)
                ge.pop(index)

            # Check Player - Platform Collision
            if player.collide(platforms):
                player.jump()

            # Player Death
            if player.y >= WINDOW_HEIGHT:
                ge[index].fitness -= 5
                players.pop(index)
                networks.pop(index)
                ge.pop(index)

        draw_window(win, players, platforms, score)
        old_score = score

def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())

    winner = p.run(main, MAX_GENERATIONS)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
