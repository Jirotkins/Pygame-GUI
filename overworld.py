import pygame
from game_data import levels
from settings import screen_width
from support import import_folder

class Node(pygame.sprite.Sprite):
    def __init__(self, pos, icon_speed, path):
        super().__init__()
        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect(center = pos)
        self.detection_zone = pygame.Rect(self.rect.centerx - icon_speed/2,
                                           self.rect.centery - icon_speed/2,
                                           icon_speed,icon_speed)

class Icon(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.image = pygame.image.load("assets/MainCharacters/MaskDude/head.png").convert_alpha()
        self.image = pygame.transform.scale2x(self.image)
        self.rect = self.image.get_rect(center = pos)

    def update(self):
        self.rect.center = self.pos

class Overworld:
    def __init__(self, start_level, max_level, surface, create_level):
        #setup
        self.background = import_folder("assets/Background/overworld")
        self.scroll = 0
        self.display_surface = surface
        self.max_level = max_level
        self.current_level = start_level
        self.create_level = create_level

        #movement logic
        self.move_direction = pygame.math.Vector2(0, 0)
        self.speed = 8
        self.moving = False

        #sprites
        self.setup_nodes()
        self.setup_icon()

    def setup_icon(self):
        self.icon = pygame.sprite.GroupSingle()
        icon_sprite = Icon(self.nodes.sprites()[self.current_level].rect.center)
        self.icon.add(icon_sprite)

    def setup_nodes(self):
        self.nodes = pygame.sprite.Group()
        
        for node_data in levels.values():
            node_sprite = Node(node_data["node_pos"], self.speed, node_data["node_graphics"])
            self.nodes.add(node_sprite)

    def draw_paths(self):
        points = [node["node_pos"] for node in levels.values()]
        pygame.draw.lines(self.display_surface, "grey", False, points, 6)

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.moving:
            if keys[pygame.K_RIGHT] and self.current_level < self.max_level:
                self.move_direction = self.get_movement_data("next")
                self.current_level += 1
                self.moving = True
            elif keys[pygame.K_LEFT] and self.current_level > 0:
                self.move_direction = self.get_movement_data("previous")
                self.current_level -= 1
                self.moving = True
            elif keys[pygame.K_SPACE]:
                self.create_level(self.current_level)

    def get_movement_data(self, target):
        start = pygame.math.Vector2(self.nodes.sprites()[self.current_level].rect.center)

        if target == "next":
            end = pygame.math.Vector2(self.nodes.sprites()[self.current_level + 1].rect.center)
        else:
            end = pygame.math.Vector2(self.nodes.sprites()[self.current_level - 1].rect.center)


        return (end - start).normalize()

    def update_icon_pos(self):
        if self.moving and self.move_direction:
            self.icon.sprite.pos += self.move_direction * self.speed
            target_node = self.nodes.sprites()[self.current_level]
            if target_node.detection_zone.collidepoint(self.icon.sprite.pos):
                self.moving = False
                self.move_direction = pygame.math.Vector2(0,0)

    def draw_background(self):
        self.scroll += -2
        bg_width = self.background[0].get_width()
        tiles = int(screen_width / bg_width) + 2
        if abs(self.scroll) > bg_width:
            self.scroll = 0
        for i in range(0, tiles):
            for image in self.background:
                self.display_surface.blit(image, (i * bg_width + self.scroll, 0))

    def run(self):
        self.draw_background()
        self.input()
        self.update_icon_pos()
        self.icon.update()
        self.draw_paths()
        self.nodes.draw(self.display_surface)
        self.icon.draw(self.display_surface)