import pygame
from os import listdir

building_images = {}
building_image_dir = './image/buildings/'
for image_path in listdir(building_image_dir):
    type_id = image_path[:-4]
    image = pygame.image.load(building_image_dir + image_path)
    building_images[type_id] = image

grass_tile_image = pygame.image.load('./image/grass_tile.png')
building_tile_image = pygame.image.load('./image/building_tile.png')

image_memo = {}


class BuildingSprite(pygame.sprite.DirtySprite):
    def __init__(self, building):
        super().__init__()
        self.building = building

        self.image = None
        self.rect = None
        self.dirty = 1
        self.data_before = None

    def update(self, screen_center, scale):
        if [self.building.type_id, self.building.level, screen_center, scale] != self.data_before:
            memo_id = f'{self.building.type_id}{self.building.level}_{scale}'

            if memo_id not in image_memo.keys():
                base_image = building_images[f'{self.building.type_id}{self.building.level}']
                image_memo[memo_id] = pygame.transform.smoothscale_by(base_image, scale)

            self.image = image_memo[memo_id]

            self.rect = self.image.get_rect()
            self.rect.midbottom = screen_pos(self.building.map_pos, screen_center, scale)
            self.dirty = 1


class TileSprite(pygame.sprite.DirtySprite):
    def __init__(self, map_pos):
        super().__init__()
        self.map_pos = map_pos
        self.image = None
        self.rect = None
        self.dirty = 1
        self.data_before = None

    def update(self, is_building, screen_center, scale):
        if self.data_before != [is_building[self.map_pos], screen_center, scale]:
            memo_id = f'{is_building[self.map_pos]}{scale}'

            if memo_id not in image_memo.keys():
                if is_building[self.map_pos]:
                    base_image = building_tile_image
                else:
                    base_image = grass_tile_image

                image_memo[memo_id] = pygame.transform.smoothscale_by(base_image, scale)

            self.image = image_memo[memo_id]

            self.rect = self.image.get_rect()
            self.rect.midbottom = screen_pos(self.map_pos, screen_center, scale)
            self.dirty = 1


def screen_pos(map_pos, screen_center, scale):
    map_x, map_y = map_pos
    center_x, center_y = screen_center
    screen_x = (170 * map_x + 170 * map_y) * scale + center_x
    screen_y = (-95 * map_x + 95 * map_y) * scale + center_y
    return screen_x, screen_y
