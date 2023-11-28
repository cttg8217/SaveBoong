import pygame
from abc import *


class InGameMode(metaclass=ABCMeta):
    def __init__(self):
        self.popup_group = pygame.sprite.Group()


class MapView(InGameMode):
    def __init__(self, game):
        super().__init__()
        self.game = game

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            building_clicked = self.get_building_clicked()
            if building_clicked is None:
                tile_clicked = self.get_tile_clicked()
                if tile_clicked is not None:
                    # TODO: build
                    pass
            else:
                pass
                # TODO: building options

    def get_building_clicked(self):
        for building_sprite in self.game.building_sprite_group:
            if building_sprite.is_mouse_over():
                print(building_sprite.building.level)
                return building_sprite

        for building in self.game.town.building_list:
            map_pos = building.map_pos
            tile_sprite = self.game.tile_sprite_dict[map_pos]
            if tile_sprite.is_mouse_over():
                print(building.level)
                return tile_sprite

        return None

    def get_tile_clicked(self):
        tile_sprite_dict = self.game.tile_sprite_dict
        is_building = self.game.town.is_building
        for map_pos, tile_sprite in tile_sprite_dict:
            if is_building[map_pos]:
                continue
            if tile_sprite.is_mouse_over():
                return tile_sprite

