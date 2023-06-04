import pygame
from tiles import AnimatedTile
from random import randint

class Enemy(AnimatedTile):
    def __init__(self, size, x, y):
        super().__init__(size, x, y, f"assets/Enemy/run")
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        self.speed = randint(2,4)

    def move(self):
        self.rect.x += self.speed

    def reverse(self):
        self.speed *= -1

    def reverse_image(self):
        if self.speed > 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, offset_x):
        self.rect.x += offset_x
        self.animate()
        self.move()
        self.reverse_image()