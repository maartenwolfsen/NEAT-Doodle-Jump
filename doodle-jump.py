import pygame
import neat
import time
import os
import random
import pickle
from shapely.geometry import Polygon
import matplotlib.pyplot as plt

pygame.font.init()

WINDOW_WIDTH = 480
WINDOW_HEIGHT = 800
DEBUG_MODE = False
FIELD_MARGIN = 5
COLLISION_MARGIN = 10
GAP_SIZE = 150
JUMP_THRESHOLD = 210
MAX_STAGNATION = 500
MAX_PLATFORMS = 7
MAX_WHILE = 30
SCROLLING_VELOCITY = 5
RAY_WIDTH = 2

PLAYER_SPRITE_RIGHT = pygame.image.load(os.path.join("sprites", "player.png"))
PLAYER_SPRITE_LEFT = pygame.transform.flip(PLAYER_SPRITE_RIGHT, True, False)
PLAYER_JUMP_SPRITE_RIGHT = pygame.image.load(os.path.join("sprites", "player_jump.png"))
PLAYER_JUMP_SPRITE_LEFT = pygame.transform.flip(PLAYER_JUMP_SPRITE_RIGHT, True, False)
PLATFORM_SPRITE = pygame.image.load(os.path.join("sprites", "platform.png"))
BG_SPRITE = pygame.image.load(os.path.join("sprites", "bg.png"))
SCORE_FONT = pygame.font.SysFont("Verdana", 36)
DEBUG_FONT = pygame.font.SysFont("Verdana", 14)

# Player Class
class Player:
    VELOCITY_X = 4
    VELOCITY_Y = 10
    JUMP_VELOCITY = 0.4
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
        self.stagnation_timer = 0
        self.segments = []

    # Move Player left
    def moveLeft(self):
        self.velocity_x = -self.VELOCITY_X

    # Move Player right
    def moveRight(self):
        self.velocity_x = self.VELOCITY_X

    # Jump by setting Y velocity to max
    def jump(self):
        self.velocity_y = -self.VELOCITY_Y
        self.jump_tick = 0

    # Move Player based on X and Y velocity
    def move(self):
        self.jump_tick += self.JUMP_VELOCITY

        vy = self.velocity_y + self.JUMP_POWER * self.jump_tick ** 2

        if vy >= self.VELOCITY_Y:
            vy = self.VELOCITY_Y

        if vy < 0:
            vy -= 2

        self.vy = vy
        self.y = self.y + vy
        self.x = self.x + self.velocity_x

        # Jump animation
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

        # Place Player on opposite wall when crossing window
        if self.x < 0 - (self.width / 2):
            self.x = WINDOW_WIDTH

        if self.x > WINDOW_WIDTH - (self.width / 2):
            self.x = 0 - (self.width / 2)

    # Draw Player
    def draw(self, win):
        win.blit(self.image, (self.x, self.y))
        self.cast_rays()

        # In Debug Mode, draw visible collision and coordinates
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

            for segment in self.segments:
                pygame.draw.polygon(win, (75, 50, 255), segment.exterior.coords, 2)

    def cast_rays(self):
        self.segments = [
            Polygon([
                (self.x - 200, self.y + (self.height / 2)),
                (self.x - 200, self.y + (self.height / 2) + RAY_WIDTH),
                (self.x + (self.width / 2), self.y + (self.height / 2) + RAY_WIDTH),
                (self.x + (self.width / 2), self.y + (self.height / 2))
            ]),
            Polygon([
                (self.x - 170, self.y + (self.height / 2) - 125),
                (self.x - 170, self.y + (self.height / 2) - 125 - RAY_WIDTH),
                (self.x + (self.width / 2), self.y + (self.height / 2) + RAY_WIDTH),
                (self.x + (self.width / 2), self.y + (self.height / 2))
            ]),
            Polygon([
                (self.x - 30, self.y - 170),
                (self.x - 30 - RAY_WIDTH, self.y - 170),
                (self.x + (self.width / 2), self.y + (self.height / 2) + RAY_WIDTH),
                (self.x + (self.width / 2), self.y + (self.height / 2))
            ]),
            Polygon([
                (self.x + (self.width / 2) - (RAY_WIDTH / 2), self.y - 200),
                (self.x + (self.width / 2) - (RAY_WIDTH / 2), self.y + (self.height / 2)),
                (self.x + (self.width / 2) + (RAY_WIDTH / 2), self.y + (self.height / 2)),
                (self.x + (self.width / 2) + (RAY_WIDTH / 2), self.y - 200)
            ]),
            Polygon([
                (self.x + self.width + 170, self.y + (self.height / 2) - 125),
                (self.x + self.width + 170, self.y + (self.height / 2) - 125 - RAY_WIDTH),
                (self.x + (self.width / 2), self.y + (self.height / 2) + RAY_WIDTH),
                (self.x + (self.width / 2), self.y + (self.height / 2))
            ]),
            Polygon([
                (self.x + self.width + 30, self.y - 170),
                (self.x + self.width + 30 - RAY_WIDTH, self.y - 170),
                (self.x + (self.width / 2), self.y + (self.height / 2) + RAY_WIDTH),
                (self.x + (self.width / 2), self.y + (self.height / 2))
            ]),
            Polygon([
                (self.x + self.width + 200, self.y + (self.height / 2)),
                (self.x + self.width + 200, self.y + (self.height / 2) + RAY_WIDTH),
                (self.x + (self.width / 2), self.y + (self.height / 2) + RAY_WIDTH),
                (self.x + (self.width / 2), self.y + (self.height / 2))
            ]),
            Polygon([
                (self.x - 170, self.y + (self.height / 2) + 125),
                (self.x - 170, self.y + (self.height / 2) + 125 - RAY_WIDTH),
                (self.x + (self.width / 2), self.y + (self.height / 2) + RAY_WIDTH),
                (self.x + (self.width / 2), self.y + (self.height / 2))
            ]),
            Polygon([
                (self.x - 30, self.y + self.height + 170),
                (self.x - 30 - RAY_WIDTH, self.y + self.height + 170),
                (self.x + (self.width / 2), self.y + (self.height / 2) + RAY_WIDTH),
                (self.x + (self.width / 2), self.y + (self.height / 2))
            ]),
            Polygon([
                (self.x + (self.width / 2) - (RAY_WIDTH / 2), self.y + self.height + 200),
                (self.x + (self.width / 2) - (RAY_WIDTH / 2), self.y + (self.height / 2)),
                (self.x + (self.width / 2) + (RAY_WIDTH / 2), self.y + (self.height / 2)),
                (self.x + (self.width / 2) + (RAY_WIDTH / 2), self.y + self.height + 200)
            ]),
            Polygon([
                (self.x + self.width + 170, self.y + (self.height / 2) + 125),
                (self.x + self.width + 170, self.y + (self.height / 2) + 125 - RAY_WIDTH),
                (self.x + (self.width / 2), self.y + (self.height / 2) + RAY_WIDTH),
                (self.x + (self.width / 2), self.y + (self.height / 2))
            ]),
            Polygon([
                (self.x + self.width + 30, self.y + self.height + 170),
                (self.x + self.width + 30 - RAY_WIDTH, self.y + self.height + 170),
                (self.x + (self.width / 2), self.y + (self.height / 2) + RAY_WIDTH),
                (self.x + (self.width / 2), self.y + (self.height / 2))
            ])
        ]

    # Check collision
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
            self.prev_platform = platform.id

            if player_rect.colliderect(platform_rect):
                return True

        return False

    def detect_platform(self, platforms):
        detection = []

        if self.segments:
            for platform in platforms:
                if platform.polygon:
                    value = 0

                    for segment in self.segments:
                        if segment.intersects(platform.polygon):
                            value = 1
                            break

                    detection.append(value)
                else:
                    detection.append(0)
        else:
            return [0, 0, 0, 0, 0, 0, 0]

        return detection


# Platform Class
class Platform:
    VELOCITY = 5

    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.width = PLATFORM_SPRITE.get_width()
        self.height = PLATFORM_SPRITE.get_height()
        self.x = random.randrange(
            FIELD_MARGIN,
            WINDOW_WIDTH - self.width - FIELD_MARGIN
        )
        self.polygon = False

    # Move down (scroll)
    def move(self, y):
        self.y += y

    # Draw Platform
    def draw(self, win):
        win.blit(PLATFORM_SPRITE, (self.x, self.y))

        self.polygon = Polygon([
            (self.x, self.y),
            (self.x + self.width, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x, self.y + self.height)
        ])

        # In Debug Mode, draw visible collision and coordinates
        if DEBUG_MODE:
            # X and Y values
            win.blit(
                DEBUG_FONT.render(
                    "Y: " + str(round(self.y)) + "; X: " + str(round(self.x)),
                    1,
                    (0, 0, 0)
                ),
                (self.x, self.y)
            )

            # Collision area
            surface = pygame.Surface((self.width, self.height))
            surface.set_alpha(128)
            surface.fill((255, 0, 25))
            win.blit(surface, (self.x, self.y))

            # Raycast area
            pygame.draw.polygon(win, (75, 50, 255), self.polygon.exterior.coords, 2)

# Draw objects in window
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

# Generate initial Platforms
def generateInitialPlatforms():
    prev_y = FIELD_MARGIN
    platforms = []

    # Make sure each platform has enough vertical spacing
    for i in range(MAX_PLATFORMS):
        x = random.randrange(
            FIELD_MARGIN,
            WINDOW_WIDTH - PLATFORM_SPRITE.get_width() - FIELD_MARGIN
        )
        y = prev_y + GAP_SIZE
        prev_y = y

        platforms.append(Platform(i, x, y))

    return platforms

# Main Function
def main(genomes, config):
    networks = []
    ge = []
    players = []

    # Set Neural Networks
    for _, g in genomes:
        network = neat.nn.FeedForwardNetwork.create(g, config)
        networks.append(network)
        players.append(Player(200, 200))
        g.fitness = 0
        ge.append(g)

    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    platforms = generateInitialPlatforms()
    platform_i = MAX_PLATFORMS
    current_height = 0
    run = True
    score = 0
    old_score = 0
    stagnation_timer = 0

    while run:
        clock.tick(60)

        # Quit Game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # Stop Generation when there are no players left
        if len(players) <= 0:
            run = False
            return

        platform_data = []

        # Refresh Platforms
        for platform in platforms:
            if platform.y > WINDOW_HEIGHT:
                platforms.remove(platform)
                platforms.append(Platform(
                    platform_i,
                    random.randrange(
                        FIELD_MARGIN,
                        WINDOW_WIDTH - platform.width - FIELD_MARGIN
                    ),
                    -platform.height
                ))
                platform_i += 1

        for index, player in enumerate(players):
            player.move()

            input_data = player.detect_platform(platforms)
            input_data.append((player.vy / 10) if player.vy > 0 else 0)
            input_data.append(((player.vy / 10) if player.vy > -10 else -10) if player.vy < 0 else 0)
            input_data.append(1 if player.velocity_x > 0 else 0)
            input_data.append(1 if player.velocity_x < 0 else 0)

            output = networks[index].activate(input_data)
            action = output.index(max(output))

            # Move Player based on Neural Network Output
            if action == 0:
                player.moveLeft()
            elif action == 1:
                player.moveRight()

            # Move Platforms if Player Y is above Jump Threshold
            if player.y <= JUMP_THRESHOLD:
                player.y = JUMP_THRESHOLD
                current_height = -round(player.vy)

            # Check Player - Platform Collision
            if player.collide(platforms) and index < len(ge):
                player.jump()

            # Player Death
            if player.y >= WINDOW_HEIGHT and index < len(ge):
                players.pop(index)
                networks.pop(index)
                ge.pop(index)

            # Increase fitness if player reaches new height
            if current_height > 1 and index < len(ge):
                ge[index].fitness += 0.1
                player.stagnation_timer = 0
            else:
                player.stagnation_timer += 1

            if player.stagnation_timer > MAX_STAGNATION:
                player.stagnation_timer = 0
                players.pop(index)
                networks.pop(index)
                ge.pop(index)

        if current_height > SCROLLING_VELOCITY:
            current_height = SCROLLING_VELOCITY

        score += current_height

        # Move platforms when Player reaches above Jump Threshold
        for platform in platforms:
            platform.move(current_height)

        draw_window(win, players, platforms, score)
        old_score = score

# Run AI
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

    winner = p.run(main)

    with open('winner', 'wb') as f:
        pickle.dump(winner, f)

# Set Config
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config")
    run(config_path)
