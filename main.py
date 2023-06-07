import pygame
import sys
from settings import *
from level import Level
from overworld import Overworld

class Game:
    def __init__(self):
        #audio
        self.overworld_music = pygame.mixer.Sound("assets/audio/overworld.wav")
        
        #timer
        self.time = 0

        #game attributes
        self.max_level = 3
        
        #overworld
        self.overworld = Overworld(0, self.max_level, screen, self.create_level)
        self.status = "overworld"
        self.overworld_music.play(loops=-1)

    def create_level(self, current_level):
        self.level = Level(current_level, screen, self.create_overworld)
        self.status = "level"
        self.overworld_music.stop()
        self.time = 0

    def create_overworld(self, current_level):
        self.overworld = Overworld(current_level,self.max_level,screen, self.create_level)
        self.status = "overworld"
        self.level.level_music.stop()
        self.overworld_music.play(loops=-1)

    def run(self):
        if self.status == "overworld":
            self.overworld.run()
        else:
            if not self.level.over:
                self.time += 1 / 60
            self.level.run(round(self.time, 2))

pygame.init()
fps = 60
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("GUI-Platformer")
clock = pygame.time.Clock()
game = Game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill("black")
    game.run()

    pygame.display.update()
    clock.tick(fps)