import pygame
from support import *
from UI import UI

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, screen, create_jump_particles):
        super().__init__()
        self.display_surface = screen

        #audio
        self.jump_sound = pygame.mixer.Sound("assets/audio/effects/jump.wav")
        self.hit_sound = pygame.mixer.Sound("assets/audio/effects/hit.wav")

        #player sprites
        self.view_direction = "left"
        self.animation_speed = 3
        self.animation_count = 0
        self.import_character_assets()
        self.image = self.sprites[f"idle_{self.view_direction}"][self.animation_count]
        self.rect = self.image.get_rect(topleft=pos)

        #player health
        self.ui = UI(screen)
        self.max_health = 100
        self.cur_health = 100
        self.invincible = False
        self.invincibility_duration = 660
        self.hit_time = 0

        #player dust particles
        self.import_dust_run_particles()
        self.dust_frame_index = 0
        self.dust_animation_speed = 0.15
        self.create_jump_particles = create_jump_particles

        #player movement
        self.direction = pygame.math.Vector2(0,0)
        self.speed = 4
        self.gravity = 0.8
        self.jump_speed = -16

        #player status
        self.on_left = False
        self.on_right = False
        self.floored = False
        self.on_ceiling = False
        self.over = False

    def import_character_assets(self):
        self.sprites = load_sprites("assets/MainCharacters/MaskDude", 32, 32, True)

    def import_dust_run_particles(self):
        self.dust_run_particles = import_folder("assets/Items/dust_particles/run")

    def run_dust_animation(self):
        if self.direction.x != 0 and self.floored:
            self.dust_frame_index += self.dust_animation_speed
            if self.dust_frame_index >= len(self.dust_run_particles):
                self.dust_frame_index = 0

            dust_particle = self.dust_run_particles[int(self.dust_frame_index)]

            if self.view_direction == "right":
                pos = self.rect.bottomleft - pygame.math.Vector2(6, 10)
                self.display_surface.blit(dust_particle, pos)
            else:
                pos = self.rect.bottomright - pygame.math.Vector2(6, 10)
                flipped_dust_particle = pygame.transform.flip(dust_particle, True, False)
                self.display_surface.blit(flipped_dust_particle, pos)

    def get_damage(self, damage):
        if not self.invincible and self.cur_health > 0:
            self.hit_sound.play()
            self.cur_health -= damage
            self.invincible = True
            self.hit_time = pygame.time.get_ticks()

    def invincibility_timer(self):
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.hit_time >= self.invincibility_duration:
                self.invincible = False

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.cur_health <= 0:
            self.image.set_alpha(-1)
        elif self.invincible:
            sprite_sheet = "hit"
        elif self.direction.y < 0:
            sprite_sheet = "jump"
        elif self.direction.y > self.gravity:
            sprite_sheet = "fall"
        elif self.direction.x != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.view_direction
        sprites = self.sprites[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.animation_speed) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        #set the rectangle while on ground
        if self.floored and self.on_right:
            self.rect = self.image.get_rect(bottomright=self.rect.bottomright)
        elif self.floored and self.on_left:
            self.rect = self.image.get_rect(bottomleft=self.rect.bottomleft)
        elif self.floored:
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        #set the rectangle while hitting object from bottom (jumping)
        if self.on_ceiling and self.on_right:
            self.rect = self.image.get_rect(topright=self.rect.topright)
        elif self.on_ceiling and self.on_left:
            self.rect = self.image.get_rect(topleft=self.rect.topleft)
        elif self.on_ceiling:
            self.rect = self.image.get_rect(midtop=self.rect.midtop)

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and not self.over:
            self.view_direction = "left"
            self.direction.x = -1
        elif keys[pygame.K_RIGHT] and not self.over:
            self.view_direction = "right"
            self.direction.x = 1
        else:
            self.direction.x = 0

        if keys[pygame.K_UP] and self.floored and not self.over:
            self.jump()
            self.create_jump_particles(self.rect.midbottom)

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        self.direction.y = self.jump_speed
        self.jump_sound.play()

    def update(self):
        self.get_input()
        self.rect.x += self.direction.x * self.speed
        self.update_sprite()
        self.run_dust_animation()
        
        #UI health
        self.ui.show_health(self.cur_health)
        self.invincibility_timer()
