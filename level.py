import pygame
from tiles import Tile, StaticTile, Coin
from settings import tile_size, screen_width, screen_height
from player import Player
from support import import_csv_layout, import_cut_graphics
from enemy import Enemy
from support import import_folder, draw_text
from game_data import levels
from UI import UI
from particles import ParticleEffect

class Level:
    def __init__(self, current_level, surface, create_overworld):
        self.display_surface = surface
        self.world_offset = 0
        self.current_x = 0
        self.offset = 0

        #audio
        self.coin_sound = pygame.mixer.Sound("assets/audio/effects/coin.wav")
        self.stomp_sound = pygame.mixer.Sound("assets/audio/effects/stomp.wav")
        self.level_music = pygame.mixer.Sound("assets/audio/level.wav")
        self.level_music.play(loops=-1)

        #game over
        self.over = False
        self.font_small = pygame.font.Font("assets/UI/ARCADEPI.TTF", 30)
        self.font_big = pygame.font.Font("assets/UI/ARCADEPI.TTF", 50)

        #overworld
        self.create_overworld = create_overworld
        self.current_level = current_level
        level_data = levels[self.current_level]

        #background
        self.bg = import_folder("assets/Background/forest/layers")
        self.bg_width = pygame.Surface.get_width(self.bg[0])

        #player
        player_layout = import_csv_layout(level_data["checks"])
        self.player = pygame.sprite.GroupSingle()
        self.end = pygame.sprite.GroupSingle()
        self.start = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)

        #dust particles and enemy explosion
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_floored = False
        self.explosion_sprites = pygame.sprite.Group()

        #player stats
        self.coins = 0
        self.max_coins = 0
        self.ui = UI(self.display_surface)

        #terrain setup
        terrain_layout = import_csv_layout(level_data["terrain"])
        self.level_width = len(terrain_layout[0]) * tile_size
        self.terrain_sprites = self.create_tile_group(terrain_layout, "terrain")

        #decorations setup
        decoration_layout = import_csv_layout(level_data["decorations"])
        self.decoration_sprites = self.create_tile_group(decoration_layout, "decorations")

        #coins setup
        coin_layout = import_csv_layout(level_data["coins"])
        self.coin_sprites = self.create_tile_group(coin_layout, "coins")

        #enemy setup
        enemy_layout = import_csv_layout(level_data["enemies"])
        self.enemy_sprites = self.create_tile_group(enemy_layout, "enemies")

        #constraint
        constraint_layout = import_csv_layout(level_data["constraints"])
        self.constraint_sprites = self.create_tile_group(constraint_layout, "constraints")

    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != "-1":
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == "terrain":
                        terrain_tile_list = import_cut_graphics("assets/Terrain/terrain_tiles.png")
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == "decorations":
                        decorations_tile_list = import_cut_graphics("assets/Items/decorations.png")
                        tile_surface = decorations_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == "coins":
                        sprite = Coin(tile_size, x ,y, "assets/Items/coins")
                        self.max_coins += 1

                    if type == "enemies":
                        sprite = Enemy(tile_size, x, y)

                    if type == "constraints":
                        sprite = Tile(tile_size, x, y)

                    sprite_group.add(sprite)

        return sprite_group

    def create_jump_particles(self, pos):
        jump_particle_sprite = ParticleEffect(pos, "jump")
        self.dust_sprite.add(jump_particle_sprite)

    def get_player_floor(self):
        if self.player.sprite.floored:
            self.player_floored = True
        else:
            self.player_floored = False

    def create_landing_dust(self):
        if not self.player_floored and self.player.sprite.floored and not self.dust_sprite.sprites():
            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom, "land")
            self.dust_sprite.add(fall_dust_particle)

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < screen_width/3 and direction_x < 0 and not self.over:
            self.world_offset = 8
            player.speed = 0
        elif player_x > (screen_width/3)*2 and direction_x > 0 and not self.over:
            self.world_offset = -8
            player.speed = 0
        else:
            self.world_offset = 0
            player.speed = 4

    def horizontal_collision(self):
        player = self.player.sprite

        player.rect.x += player.direction.x * player.speed

        for sprite in self.terrain_sprites.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right

        if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
            player.on_left = False
        if player.on_right and (player.rect.right > self.current_x or player.direction.x <= 0):
            player.on_right = False

    def vertical_collision(self):
        player = self.player.sprite
        player.apply_gravity()

        for sprite in self.terrain_sprites.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.floored = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y *= -0.3
                    player.on_ceiling = True

        if player.floored and player.direction.y < 0 or player.direction.y > player.gravity:
            player.floored = False
        if player.on_ceiling and player.direction.y > 0:
            player.on_ceiling = False

    def enemy_collision(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraint_sprites, False):
                enemy.reverse()

    def player_setup(self, layout):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == "0":
                    start_surface = pygame.image.load("assets/Items/Checkpoints/Start/Start (Idle).png").convert_alpha()
                    sprite = StaticTile(tile_size, x, y, start_surface)
                    self.start.add(sprite)

                    sprite = Player((x, y), self.display_surface, self.create_jump_particles)
                    self.player.add(sprite)
                if val == "1":
                    end_surface = pygame.image.load("assets/Items/Checkpoints/End/End (Idle).png").convert_alpha()
                    sprite = StaticTile(tile_size, x, y, end_surface)
                    self.end.add(sprite)

    def draw_background(self, offset_x):
        self.offset += offset_x
        for x in range(-1, int(self.level_width / self.bg_width + 3)):
            speed = 1   
            for image in self.bg:
                self.display_surface.blit(image, ((x * self.bg_width + self.offset * speed), 0))
                if self.offset > 0:
                    speed -= 0.04
                else:
                    speed += 0.04

    def check_death(self):
        if self.player.sprite.rect.top > screen_height or self.player.sprite.cur_health <= 0:
            self.over = True
            self.game_over()

    def game_over(self):
        draw_text("GAME OVER!", self.font_big, "WHITE", self.display_surface, (screen_width/2 - 170, screen_height/2))
        draw_text("press ESC to return to menu", self.font_small, "WHITE", self.display_surface, (screen_width/2-280, screen_height/2 + 60))


    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            self.create_overworld(self.current_level)


    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.end, False):
            self.create_overworld(self.current_level)

    def check_coin_collisions(self):
        collided_coins = pygame.sprite.spritecollide(self.player.sprite, self.coin_sprites, True)
        if collided_coins:
            self.coin_sound.play()
            for coin in collided_coins:
                self.coins += 1

    def check_enemy_collisions(self):
        enemy_collisions = pygame.sprite.spritecollide(self.player.sprite, self.enemy_sprites, False)

        if enemy_collisions:
            for enemy in enemy_collisions:
                enemy_center = enemy.rect.centery
                enemy_top = enemy.rect.top
                player_bottom = self.player.sprite.rect.bottom
                if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 0:
                    self.stomp_sound.play()
                    self.player.sprite.direction.y = -10
                    explosion_sprite = ParticleEffect(enemy.rect.center, "explosion")
                    self.explosion_sprites.add(explosion_sprite)
                    enemy.kill()

                else:
                    self.player.sprite.get_damage(20)

    def run(self):
        #player input
        self.get_input()

        #background
        self.draw_background(self.world_offset)

        #terrain tiles
        self.terrain_sprites.update(self.world_offset)
        self.terrain_sprites.draw(self.display_surface)

        #enemy
        self.enemy_sprites.update(self.world_offset)
        self.constraint_sprites.update(self.world_offset)
        self.enemy_collision()
        self.enemy_sprites.draw(self.display_surface)
        self.explosion_sprites.update(self.world_offset)
        self.explosion_sprites.draw(self.display_surface)

        #decoration tiles
        self.decoration_sprites.update(self.world_offset)
        self.decoration_sprites.draw(self.display_surface)

        #coins
        self.coin_sprites.update(self.world_offset)
        self.coin_sprites.draw(self.display_surface)

        #player sprites
        self.end.update(self.world_offset)
        self.end.draw(self.display_surface)
        self.start.update(self.world_offset)
        self.start.draw(self.display_surface)

        self.scroll_x()

        #player
        self.player.update()
        self.horizontal_collision()
        self.get_player_floor()
        self.vertical_collision()
        self.create_landing_dust()
        self.check_death()
        self.check_win()
        self.check_coin_collisions()
        self.check_enemy_collisions()
        self.player.draw(self.display_surface)

        #dust particles
        self.dust_sprite.update(self.world_offset)
        self.dust_sprite.draw(self.display_surface)

        #UI coins
        self.ui.show_coins(self.coins, self.max_coins)