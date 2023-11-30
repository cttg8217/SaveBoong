import pygame
from abc import *
from building_data import data


class ErrorMessage(pygame.sprite.Sprite):
    def __init__(self, game, name):
        super().__init__()
        self.game = game
        self.image = pygame.image.load(f'./image/errors/{name}.png')
        self.rect = self.image.get_rect(center=(game.screen_width // 2, game.screen_height // 2))

    def is_mouse_over(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(*mouse_pos)


class InGameMenuItem(pygame.sprite.Sprite):
    def __init__(self, name, **kwargs):
        super().__init__()
        self.name = name
        self.image = pygame.image.load(f'./image/buttons/{name}.png')
        self.rect = self.image.get_rect(**kwargs)

    def is_mouse_over(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(*mouse_pos)


class InGameMenu(pygame.sprite.Group):
    def __init__(self, names, screen_width, screen_height, level=0):
        super().__init__()
        num_items = len(names)
        total_width = (num_items - 1) * 150
        most_left = screen_width // 2 - total_width // 2
        for i in range(num_items):
            x_pos = most_left + 150 * i
            menu_item = InGameMenuItem(names[i], center=(x_pos, screen_height * 0.8 - 145 * level))
            menu_item.add(self)

    def get_item_selected(self):
        for menu_item in self:
            if menu_item.is_mouse_over():
                return menu_item.name

        return None


class InGameModeController:
    def __init__(self, game):
        self.game = game
        self.in_game_mode = MapView(game)

    def handle_event(self, event):
        next_in_game_mode = self.in_game_mode.handle_event(event)
        self.in_game_mode = next_in_game_mode

    def update(self):
        if not self.game.town.earthquake_checked:
            if self.game.town.earthquake_harm:
                self.in_game_mode = ErrorScreen(self.game, 'earthquake_fix')
            else:
                self.in_game_mode = ErrorScreen(self.game, 'earthquake_safe')

        self.game.town.earthquake_checked = True
        self.in_game_mode.update()

    def sprite_group(self):
        return self.in_game_mode.sprite_group


class InGameMode(metaclass=ABCMeta):
    def __init__(self, game):
        self.game = game
        self.sprite_group = pygame.sprite.Group()

    @abstractmethod
    def handle_event(self, event):
        pass

    def update(self):
        pass


class MapView(InGameMode):
    def __init__(self, game):
        super().__init__(game)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:

            building_sprite_clicked = self.game.get_building_clicked()
            if building_sprite_clicked is None:
                tile_clicked = self.game.get_tile_clicked()
                print(tile_clicked.map_pos)
                if tile_clicked is not None:
                    tile_clicked.is_selected = True

                    map_pos = tile_clicked.map_pos
                    return EmptyTileOptions(self.game, map_pos)
            else:
                return BuildingOptions(self.game, building_sprite_clicked.building)

        return self


class EmptyTileOptions(InGameMode):
    def __init__(self, game, map_pos):
        super().__init__(game)
        self.map_pos = map_pos
        self.sprite_group = InGameMenu(['build'], game.screen_width, game.screen_height)

    def __del__(self):
        self.game.tile_sprite_dict[self.map_pos].is_selected = False

    def update(self):
        self.game.tile_sprite_dict[self.map_pos].is_selected = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            item_selected = self.sprite_group.get_item_selected()

            if item_selected is None:
                return MapView(self.game)
            elif item_selected == 'build':
                return Build(self.game, self.map_pos)

        return self


class Build(InGameMode):
    def __init__(self, game, map_pos):
        super().__init__(game)
        self.map_pos = map_pos

        sprite_group_0 = InGameMenu(['build_house', 'build_hospital', 'build_library', 'build_school'],
                                    game.screen_width, game.screen_height, level=0)
        sprite_group_1 = InGameMenu(['build_shop', 'build_stadium', 'build_park', 'build_laboratory'],
                                    game.screen_width, game.screen_height, level=1)
        sprite_group_2 = InGameMenu(['build_weather_center', 'build_art_center', 'build_factory'],
                                    game.screen_width, game.screen_height, level=2)
        self.sprite_group.add(sprite_group_0, sprite_group_1, sprite_group_2)

    def __del__(self):
        self.game.tile_sprite_dict[self.map_pos].is_selected = False

    def update(self):
        print('Hi')
        self.game.tile_sprite_dict[self.map_pos].is_selected = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            item_selected = self.get_item_selected()
            if item_selected is None:
                return MapView(self.game)

            build_price = data[item_selected]['upgrade_price'][0]
            if self.game.town.money < build_price:
                return ErrorScreen(self.game, 'less_money')

            new_building = self.game.town.build(self.map_pos, item_selected)
            self.game.add_building_sprite(new_building)
            return MapView(self.game)

        return self

    def get_item_selected(self):
        for sprite in self.sprite_group:
            if sprite.is_mouse_over():
                return sprite.name[6:]

        return None


class ErrorScreen(InGameMode):
    def __init__(self, game, name):
        super().__init__(game)
        self.error_sprite = ErrorMessage(game, name)
        self.error_sprite.add(self.sprite_group)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            return MapView(self.game)

        return self


class TextSprite(pygame.sprite.Sprite):
    def __init__(self, text, size, color, **kwargs):
        super().__init__()
        font = pygame.font.Font('./fonts/CookieRun Regular.otf', size)
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect(**kwargs)


class BuildingOptions(InGameMode):
    def __init__(self, game, building):
        super().__init__(game)
        self.building = building
        building_max_level = building.data['max_level']
        label = f'{building.name}({building.level}/{building_max_level}Lv)'
        self.building_name_sprite = TextSprite(label, 30, 'black', center=(self.game.screen_width//2, self.game.screen_height * 0.8 - 100))
        self.building_name_sprite.add(self.sprite_group)

        option_names = []
        is_max_level = (building.level == building_max_level)
        if not is_max_level:
            option_names.append('check_upgrade')
        self.building_options = InGameMenu(option_names, game.screen_width, game.screen_height)
        self.sprite_group.add(self.building_options)

        print([self.sprite_group])

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            selected_option = self.building_options.get_item_selected()
            if selected_option is None:
                return MapView(self.game)
            else:
                pass
        return self
