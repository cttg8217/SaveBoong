import pygame
from abc import *


class InGamePopup(metaclass=ABCMeta):
    def __init__(self):
        self.popup_group = pygame.sprite.Group()


class MapView(InGamePopup):
    def __init__(self, game):
        super().__init__()
        self.game = game

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_pos = event.pos

            building_clicked = self.get_building_clicked(mouse_pos)
            if building_clicked is not None:
                pass
                # TODO: Building Options

    def get_building_clicked(self, mouse_pos):
        for building_sprite in self.game.building_sprite_dict.values():
            rect = building_sprite.rect
            if rect.collidepoint(mouse_pos):
                if building_sprite.mask.get_at((mouse_pos[0] - rect.x, mouse_pos[1] - rect.y)):
                    print(building_sprite.building.level)
                    return building_sprite

        return None

    def get_tile_clicked(self, mouse_pos):
        tile_sprite_dict = self.game.tile_sprite_dict
        is_building = self.game.town.is_building
        for map_pos, tile_sprite in tile_sprite_dict:
            if is_building[map_pos]:
                continue

