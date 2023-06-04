import pygame

class UI:
    def __init__(self, surface):
        #setup
        self.display_surface = surface
        
        #health
        self.health_bar = pygame.image.load("assets/UI/health_bar.png").convert_alpha()
        self.healt_bar_topleft = (54, 39)
        self.bar_height = 4

        #coins
        self.coin = pygame.image.load("assets/UI/coin.png").convert_alpha()
        self.coin_rect = self.coin.get_rect(topleft = (15, 65))
        self.font = pygame.font.Font("assets/UI/ARCADEPI.TTF", 30)

    def show_health(self, current):
        self.display_surface.blit(self.health_bar, (20, 10))
        current_bar_width = current * 1.52 #152 pixels is whole bar
        health_bar_rect = pygame.Rect((self.healt_bar_topleft), (current_bar_width, self.bar_height))
        pygame.draw.rect(self.display_surface, "#dc4949", health_bar_rect)

    def show_coins(self, amount, max_amount):
        self.display_surface.blit(self.coin, self.coin_rect)
        coin_amount_surface = self.font.render(str(f"{amount}/{max_amount}"), False, "white")
        coin_amount_rect = coin_amount_surface.get_rect(midleft=(self.coin_rect.right + 5, self.coin_rect.centery))
        self.display_surface.blit(coin_amount_surface, coin_amount_rect)