import pygame
from abc import *


class InGameMenuItem(pygame.sprite.Sprite):
    def __init__(self, image, **kwargs):
        super().__init__()
        self.image = image
        self.rect = image.get_rect(**kwargs)

    def update(self, *args, **kwargs):
        pass


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
                    map_pos = tile_clicked.map_pos
                    return Build(self.game, map_pos)
                    pass
            else:
                pass
                # TODO: building options

        return self


class Build(InGameMode):
    def __init__(self, game, map_pos):
        super().__init__(game)
        self.map_pos = map_pos

        img = pygame.image.load('./image/build_button.png')
        self.house_button_test = InGameMenuItem(img, center=(500, 300))
        self.sprite_group.add(self.house_button_test)

    def handle_event(self, event):
        return self

