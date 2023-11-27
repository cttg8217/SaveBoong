import pygame
import Town
import Sprite
import MapSprites

clock = pygame.time.Clock()

screen_center_dx_levels = [-200, -100, 0, 100, 200]
screen_center_dy_levels = [-200, -100, 0, 100, 200]
scale_levels = [0.6, 0.8, 1.0, 1.2, 1.4]

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720

logo_image = pygame.image.load('image/logo.png')
new_game_button_image = pygame.image.load('image/new_game_button.png')
new_game_button_image_larger = pygame.transform.smoothscale_by(new_game_button_image, 1.3)
base_grass = pygame.image.load('image/grass_tile.png')
base_tile = pygame.image.load('image/building_tile.png')


class Game:
    def __init__(self):
        self.town = None
        self.running = False
        self.screen = None
        self.screen_center_dx_level = None
        self.screen_center_dy_level = None
        self.scale_level = None

    def play(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.running = True
        self.main_menu()
        self.main_game()
        pygame.quit()

    def main_game(self):
        self.screen_center_dx_level = 2
        self.screen_center_dy_level = 2
        self.scale_level = 2

        building_sprite_group = pygame.sprite.LayeredDirty()
        tile_sprite_group = pygame.sprite.Group()

        for building in self.town.building_list:
            building_sprite = MapSprites.BuildingSprite(building)
            building_sprite.add(building_sprite_group)

        for map_pos in self.town.is_building.keys():
            tile_sprite = MapSprites.TileSprite(map_pos)
            tile_sprite.add(tile_sprite_group)

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                self.handle_map_movement(event)

            self.screen.fill('white')

            tile_sprite_group.update(is_building=self.town.is_building, screen_center=self.screen_center_pos, scale=self.scale)
            tile_sprite_group.draw(self.screen)

            building_sprite_group.update(screen_center=self.screen_center_pos, scale=self.scale)
            for building_sprite in building_sprite_group:
                building_sprite_group.change_layer(building_sprite, building_sprite.rect.y)
            building_sprite_group.draw(self.screen)

            print(pygame.time.get_ticks())

            pygame.display.flip()
            clock.tick(15)

        pygame.quit()

    def main_menu(self):
        logo_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        new_game_button_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)

        logo_rect = logo_image.get_rect()
        logo_rect.center = logo_pos

        new_game_button_rect = new_game_button_image.get_rect()
        new_game_button_rect.center = new_game_button_pos

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if new_game_button_rect.collidepoint(*mouse_pos):
                        return
                    pass

            self.screen.fill('white')
            self.screen.blit(logo_image, logo_rect)
            self.screen.blit(new_game_button_image, new_game_button_rect)
            pygame.display.flip()

            clock.tick(30)

    def handle_map_movement(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.screen_center_dy_level < len(screen_center_dy_levels) - 1:
                    self.screen_center_dy_level += 1

            elif event.key == pygame.K_DOWN:
                if self.screen_center_dy_level > 0:
                    self.screen_center_dy_level -= 1

            elif event.key == pygame.K_LEFT:
                if self.screen_center_dx_level < len(screen_center_dx_levels) - 1:
                    self.screen_center_dx_level += 1

            elif event.key == pygame.K_RIGHT:
                if self.screen_center_dx_level > 0:
                    self.screen_center_dx_level -= 1

            elif event.key == pygame.K_EQUALS:
                if self.scale_level < len(scale_levels) - 1:
                    self.scale_level += 1

            elif event.key == pygame.K_MINUS:
                if self.scale_level > 0:
                    self.scale_level -= 1

    @property
    def screen_center_pos(self):
        screen_center_x = SCREEN_WIDTH // 2 + screen_center_dx_levels[self.screen_center_dx_level]
        screen_center_y = SCREEN_HEIGHT // 2 + screen_center_dy_levels[self.screen_center_dy_level]
        return screen_center_x, screen_center_y

    @property
    def scale(self):
        scale = scale_levels[self.scale_level]
        return scale
