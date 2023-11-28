import pygame
from os import listdir
from abc import *

building_images = {}
building_image_dir = './image/buildings/'
for image_path in listdir(building_image_dir):
    type_id = image_path[:-4]
    image = pygame.image.load(building_image_dir + image_path)
    building_images[type_id] = image

grass_tile_image = pygame.image.load('./image/grass_tile.png')
grass_tile_selected_image = pygame.image.load('./image/grass_tile_selected.png')
building_tile_image = pygame.image.load('./image/building_tile.png')

image_memo = {}
mask_memo = {}


class MapSprite(pygame.sprite.DirtySprite):
    def __init__(self):
        super().__init__()
        self.image = None
        self.mask = None
        self.rect = None
        self.dirty = 1
        self.data_before = None

    @abstractmethod
    def data(self, screen_center, scale, **kwargs):
        pass

    @abstractmethod
    def memo_id(self, scale, **kwargs):
        pass

    @abstractmethod
    def create_image(self, scale, **kwargs):
        pass

    def update(self, screen_center, scale, **kwargs):
        memo_id = self.memo_id(scale, **kwargs)
        if self.data(screen_center, scale, **kwargs) != self.data_before:
            if memo_id not in image_memo.keys():
                new_image = self.create_image(scale, **kwargs)
                image_memo[memo_id] = new_image
                mask_memo[memo_id] = pygame.mask.from_surface(new_image)

        self.image = image_memo[memo_id]
        self.mask = mask_memo[memo_id]
        self.rect = self.image.get_rect()

        self.rect.midbottom = self.screen_pos(screen_center, scale)
        self.dirty = 1

    def screen_pos(self, screen_center, scale):
        map_x, map_y = self.map_pos
        center_x, center_y = screen_center
        screen_x = (170 * map_x + 170 * map_y) * scale + center_x
        screen_y = (-95 * map_x + 95 * map_y) * scale + center_y
        return screen_x, screen_y

    def is_mouse_over(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_x, mouse_y = mouse_pos
        rect_x, rect_y = self.rect.x, self.rect.y
        return self.rect.collidepoint(mouse_pos) and self.mask.get_at((mouse_x-rect_x, mouse_y-rect_y))


class BuildingSprite(MapSprite):
    def __init__(self, building):
        super().__init__()
        self.building = building
        building.connected_sprite = self

    def data(self, screen_center, scale, **kwargs):
        return [self.building.type_id, self.building.level, screen_center, scale]

    def memo_id(self, scale, **kwargs):
        return f'{self.building.type_id}{self.building.level}_{scale}'

    def create_image(self, scale, **kwargs):
        base_image = building_images[f'{self.building.type_id}{self.building.level}']
        new_image = pygame.transform.smoothscale_by(base_image, scale)
        return new_image

    @property
    def map_pos(self):
        return self.building.map_pos


class TileSprite(MapSprite):
    def __init__(self, map_pos):
        super().__init__()
        self.is_selected = False
        self.map_pos = map_pos

    def data(self, screen_center, scale, **kwargs):
        is_building = kwargs['is_building']
        return [is_building[self.map_pos], self.is_selected, screen_center, scale]

    def memo_id(self, scale, **kwargs):
        is_building = kwargs['is_building']
        return f'{is_building[self.map_pos]}{self.is_selected}{scale}'

    def create_image(self, scale, **kwargs):
        is_building = kwargs['is_building']
        if is_building[self.map_pos]:
            base_image = building_tile_image
        elif self.is_selected:
            base_image = grass_tile_selected_image
        else:
            base_image = grass_tile_image

        new_image = pygame.transform.smoothscale_by(base_image, scale)
        return new_image


def screen_pos(map_pos, screen_center, scale):
    map_x, map_y = map_pos
    center_x, center_y = screen_center
    screen_x = (170 * map_x + 170 * map_y) * scale + center_x
    screen_y = (-95 * map_x + 95 * map_y) * scale + center_y
    return screen_x, screen_y
