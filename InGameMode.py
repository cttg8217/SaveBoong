import pygame
from abc import *


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
    def __init__(self, names, screen_width, screen_height):
        super().__init__()
        num_items = len(names)
        total_width = (num_items - 1) * 150
        most_left = screen_width // 2 - total_width // 2
        for i in range(num_items):
            x_pos = most_left + 150 * i
            menu_item = InGameMenuItem(names[i], center=(x_pos, screen_height * 0.8))
            menu_item.add(self)

    def get_item_selected(self):
        for menu_item in self:
            if menu_item.is_mouse_over():
                return menu_item.name

        return None


class InGameModeController:
    def __init__(self, game):
        self.in_game_mode = MapView(game)

    def handle_event(self, event):
        next_in_game_mode = self.in_game_mode.handle_event(event)
        self.in_game_mode = next_in_game_mode

    def sprite_group(self):
        return self.in_game_mode.sprite_group


class InGameMode(metaclass=ABCMeta):
    def __init__(self, game):
        self.game = game
        self.sprite_group = pygame.sprite.Group()

    @abstractmethod
    def handle_event(self, event):
        pass


class MapView(InGameMode):
    def __init__(self, game):
        super().__init__(game)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:

            building_clicked = self.game.get_building_clicked()
            if building_clicked is None:
                tile_clicked = self.game.get_tile_clicked()
                print(tile_clicked.map_pos)
                if tile_clicked is not None:
                    tile_clicked.is_selected = True

                    map_pos = tile_clicked.map_pos
                    return EmptyTileOptions(self.game, map_pos)
                    pass
            else:
                pass
                # TODO: building options

        return self


class EmptyTileOptions(InGameMode):
    def __init__(self, game, map_pos):
        super().__init__(game)
        self.map_pos = map_pos

        build_button_base_image = pygame.image.load('image/buttons/build.png')
        build_button_image = pygame.transform.smoothscale_by(build_button_base_image, 0.5)

        self.sprite_group = InGameMenu(['build', 'cancel'], game.screen_width, game.screen_height)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            item_selected = self.sprite_group.get_item_selected()

            if item_selected is None:
                pass
            elif item_selected == 'build':
                pass
                # TODO
            elif item_selected == 'cancel':
                self.game.tile_sprite_dict[self.map_pos].is_selected = False
                return MapView(self.game)

        return self

