import pygame
from os import listdir
from abc import *
from math import floor

building_images = {}
building_image_dir = './image/buildings/'
for image_path in listdir(building_image_dir):
    type_id = image_path[:-4]
    image = pygame.image.load(building_image_dir + image_path)
    building_images[type_id] = image

grass_tile_buildable_image = pygame.image.load('./image/grass_tile.png')

grass_tile_not_buildable_image = pygame.image.load('./image/grass_tile.png')
grass_tile_not_buildable_image.set_alpha(200)

grass_tile_selected_image = pygame.image.load('./image/grass_tile_selected.png')

grass_tile_selected_not_buildable_image = pygame.image.load('./image/grass_tile_selected.png')
grass_tile_selected_not_buildable_image.set_alpha(200)

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
        return [self.building.is_earthquake, self.building.type_id, self.building.level, self.building.is_upgrading, screen_center, scale]

    def memo_id(self, scale, **kwargs):
        return f'{self.building.is_earthquake}{self.building.type_id}{self.building.level}{self.building.is_upgrading}_{scale}'

    def create_image(self, scale, **kwargs):
        if self.building.is_upgrading:
            base_image = building_images['building']
        elif self.building.is_earthquake:
            base_image = building_images['earthquake']
        else:
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
        buildable = kwargs['buildable']
        return [buildable[self.map_pos], is_building[self.map_pos], self.is_selected, screen_center, scale]

    def memo_id(self, scale, **kwargs):
        is_building = kwargs['is_building']
        buildable = kwargs['buildable']
        return f'{buildable[self.map_pos]}{is_building[self.map_pos]}{self.is_selected}{scale}'

    def create_image(self, scale, **kwargs):
        is_building = kwargs['is_building']
        buildable = kwargs['buildable']
        if is_building[self.map_pos]:
            base_image = building_tile_image
        elif self.is_selected:
            if buildable[self.map_pos]:
                base_image = grass_tile_selected_image
            else:
                base_image = grass_tile_selected_not_buildable_image
        else:
            if buildable[self.map_pos]:
                base_image = grass_tile_buildable_image
            else:
                base_image = grass_tile_not_buildable_image

        new_image = pygame.transform.smoothscale_by(base_image, scale)
        return new_image


def screen_pos(map_pos, screen_center, scale):
    map_x, map_y = map_pos
    center_x, center_y = screen_center
    screen_x = (170 * map_x + 170 * map_y) * scale + center_x
    screen_y = (-95 * map_x + 95 * map_y) * scale + center_y
    return screen_x, screen_y


class DataSprite(pygame.sprite.Group):
    def __init__(self, town, name, level):
        super().__init__()
        self.town = town
        self.name = name
        self.level = level

        self.base_sprite = DataBoxBaseSprite(name, midleft=(20, self.level*50))
        self.text_sprite = DataBoxTextSprite(name)

        self.base_sprite.add(self)
        self.text_sprite.add(self)

    def update(self):
        data = getattr(self.town, self.name)
        self.text_sprite.update(data, midleft=(140, self.level*50))

    def draw(self, surface):
        surface.blit(self.base_sprite.image, self.base_sprite.rect)
        surface.blit(self.text_sprite.image, self.text_sprite.rect)


class DataBoxBaseSprite(pygame.sprite.Sprite):
    def __init__(self, name, **kwargs):
        super().__init__()
        self.image = pygame.image.load(f'./image/databoxes/{name}.png')
        self.rect = self.image.get_rect(**kwargs)


class DataBoxTextSprite(pygame.sprite.Sprite):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.image = None
        self.rect = None
        self.font = pygame.font.Font('./fonts/CookieRun Regular.otf', 20)

    def update(self, data, **kwargs):
        self.image = self.font.render(str(floor(data)), True, '#AA5B00')
        self.rect = self.image.get_rect(**kwargs)
