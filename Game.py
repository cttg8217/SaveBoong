import pygame
import Town
import MapSprites
import InGameMode
import Mission
clock = pygame.time.Clock()

screen_center_dx_levels = [-200, -100, 0, 100, 200]
screen_center_dy_levels = [-200, -100, 0, 100, 200]
scale_levels = [0.6, 0.8, 1.0, 1.2, 1.4]

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720

logo_image = pygame.image.load('image/logo.png')
new_game_button_image = pygame.image.load('image/new_game_button.png')
new_game_button_image_larger = pygame.transform.smoothscale_by(new_game_button_image, 1.3)


class Game:
    def __init__(self):
        pygame.init()
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.previous_second = 0
        self.font = pygame.font.Font('./fonts/CookieRun Regular.otf', 30)

    def play(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.running = True
        self.main_menu()
        self.main_game()
        pygame.quit()

    def main_game(self):
        self.screen_center_dx_level = 2
        self.screen_center_dy_level = 2
        self.scale_level = 2
        in_game_mode_controller = InGameMode.InGameModeController(self)

        self.setup_map_sprites()
        self.setup_data()
        self.setup_mission_button()
        self.setup_missions()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                self.handle_map_movement(event)
                in_game_mode_controller.handle_event(event)

            self.town_update()

            self.screen.fill('white')

            self.render_map_sprites()
            self.render_data()
            self.render_mission_button()

            in_game_mode_controller.update()

            in_game_mode_group = in_game_mode_controller.sprite_group()
            in_game_mode_group.draw(self.screen)

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

    def get_building_clicked(self):
        for building_sprite in reversed(self.building_sprite_group.sprites()):
            if building_sprite.is_mouse_over():
                print(building_sprite.building.level)
                return building_sprite

        for building in self.town.building_list:
            map_pos = building.map_pos
            tile_sprite = self.tile_sprite_dict[map_pos]
            if tile_sprite.is_mouse_over():
                print(building.level)
                return self.building_sprite_dict[map_pos]

        return None

    def get_tile_clicked(self):
        tile_sprite_dict = self.tile_sprite_dict
        is_building = self.town.is_building
        for map_pos in tile_sprite_dict.keys():
            tile_sprite = tile_sprite_dict[map_pos]
            if not is_building[map_pos] and tile_sprite.is_mouse_over():
                return tile_sprite

        return None

    def town_update(self):
        time = pygame.time.get_ticks()
        if time > self.previous_second + 1000:
            self.previous_second = time
            self.town.update_second()

    def add_building_sprite(self, building):
        building_sprite = MapSprites.BuildingSprite(building)
        self.building_sprite_dict[building.map_pos] = building_sprite
        building_sprite.add(self.building_sprite_group)

    def setup_map_sprites(self):
        self.building_sprite_dict = {}
        self.tile_sprite_dict = {}
        self.building_sprite_group = pygame.sprite.LayeredDirty()
        self.tile_sprite_group = pygame.sprite.Group()

        for building in self.town.building_list:
            self.add_building_sprite(building)

        for map_pos in self.town.is_building.keys():
            tile_sprite = MapSprites.TileSprite(map_pos)
            self.tile_sprite_dict[map_pos] = tile_sprite
            tile_sprite.add(self.tile_sprite_group)

    def render_map_sprites(self):
        self.tile_sprite_group.update(screen_center=self.screen_center_pos, scale=self.scale, is_building=self.town.is_building, buildable=self.town.buildable)
        self.tile_sprite_group.draw(self.screen)

        self.building_sprite_group.update(screen_center=self.screen_center_pos, scale=self.scale)
        for building_sprite in self.building_sprite_group:
            self.building_sprite_group.change_layer(building_sprite, building_sprite.rect.y)
        self.building_sprite_group.draw(self.screen)

    def setup_data(self):
        names = ['money', 'happiness', 'boong', 'population', 'graduates', 'products']
        self.data_sprite_list = []
        for i in range(len(names)):
            new_data_sprite = MapSprites.DataSprite(self.town, names[i], i+1)
            self.data_sprite_list.append(new_data_sprite)

    def render_data(self):
        for data_sprite in self.data_sprite_list:
            if data_sprite.name == 'graduates' and not self.town.school_exists:
                continue

            if data_sprite.name == 'products' and not self.town.is_research_done:
                continue

            data_sprite.update()
            data_sprite.draw(self.screen)

    def setup_mission_button(self):
        self.mission_button_image = pygame.image.load('./image/buttons/mission.png')
        self.mission_button_rect = self.mission_button_image.get_rect(midleft=(260, 75))

    def render_mission_button(self):
        self.screen.blit(self.mission_button_image, self.mission_button_rect)

    def setup_missions(self):
        self.mission_list = []
        for i in range(len(Mission.check_func_list)):
            self.mission_list.append(Mission.Mission(self.town, Mission.check_func_list[i]))
