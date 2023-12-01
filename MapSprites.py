import pygame
from os import listdir
from abc import *
from math import floor

# 각종 이미지 로드
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

# memoizaton에 이용
image_memo = {}
mask_memo = {}


# 맵상의 빌딩, 타일 클래스의 부모 클래스가 됨. DirtySprite를 이용하여 변경사항이 있을 때만 다시 render함.
class MapSprite(pygame.sprite.DirtySprite):
    def __init__(self):
        super().__init__()
        self.image = None
        self.mask = None
        self.rect = None
        self.dirty = 1
        self.data_before = None

    # 이전 화면과 해당 스프라이트가 변했는지 확인하기 위해 현재 스프라이트의 위치, 배율, 선택 여부 등 데이터를 만드는 메서드
    @abstractmethod
    def data(self, screen_center, scale, **kwargs):
        pass

    # 아래에 있는 memoization을 위한 id를 생성
    @abstractmethod
    def memo_id(self, scale, **kwargs):
        pass

    @abstractmethod
    def create_image(self, scale, **kwargs):
        pass

    # 랙을 줄이기 위해, 화면이 바뀌어도 새로 계산하지 않고, 같은 이미지를 예전에 만들었다면 dict에서 찾아서 재활용하는 memoization을 활용함.
    def update(self, screen_center, scale, **kwargs):
        memo_id = self.memo_id(scale, **kwargs)
        if self.data(screen_center, scale, **kwargs) != self.data_before:
            if memo_id not in image_memo.keys(): # 이전에 만들어진 적 없는 이미지인 경우에만 새로 만듦.
                new_image = self.create_image(scale, **kwargs)
                image_memo[memo_id] = new_image
                mask_memo[memo_id] = pygame.mask.from_surface(new_image)

        self.image = image_memo[memo_id]
        self.mask = mask_memo[memo_id]
        self.rect = self.image.get_rect()

        self.rect.midbottom = self.screen_pos(screen_center, scale)
        self.dirty = 1

    # 맵상의 위치를 화면 상 위치로 변환
    def screen_pos(self, screen_center, scale):
        map_x, map_y = self.map_pos
        center_x, center_y = screen_center
        screen_x = (170 * map_x + 170 * map_y) * scale + center_x
        screen_y = (-95 * map_x + 95 * map_y) * scale + center_y
        return screen_x, screen_y

    # 마우스가 위에 있는지 확인. mask를 이용해, rect 위에 있지만 실제 이미지 위에 없으면 없는 것으로 처리.
    def is_mouse_over(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_x, mouse_y = mouse_pos
        rect_x, rect_y = self.rect.x, self.rect.y
        return self.rect.collidepoint(mouse_pos) and self.mask.get_at((mouse_x-rect_x, mouse_y-rect_y))


# 건물 스프라이트
class BuildingSprite(MapSprite):
    def __init__(self, building):
        super().__init__()
        self.building = building

    def data(self, screen_center, scale, **kwargs):
        return [self.building.is_earthquake, self.building.type_id, self.building.level, self.building.is_upgrading, screen_center, scale]

    def memo_id(self, scale, **kwargs):
        return f'{self.building.is_earthquake}{self.building.type_id}{self.building.level}{self.building.is_upgrading}_{scale}'

    def create_image(self, scale, **kwargs):
        if self.building.is_upgrading:
            base_image = building_images['building']
        elif self.building.is_earthquake:  # 건물이 부서졌다면 지진 이미지
            base_image = building_images['earthquake']
        else:
            base_image = building_images[f'{self.building.type_id}{self.building.level}']
        new_image = pygame.transform.smoothscale_by(base_image, scale)
        return new_image

    @property
    def map_pos(self):
        return self.building.map_pos


# 타일 스프라이트 (건물의 밑바닥, 건물 없는 곳의 잔디)
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
        # 건물 제작 가능 구역인지, 현재 선택된 타일인지의 경우마다 서로 다른 이미지 선택
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


# 맵상의 위치를 스크린 상의 중심에 대한 상대 위치로 변경
def screen_pos(map_pos, screen_center, scale):
    map_x, map_y = map_pos
    center_x, center_y = screen_center
    screen_x = (170 * map_x + 170 * map_y) * scale + center_x
    screen_y = (-95 * map_x + 95 * map_y) * scale + center_y
    return screen_x, screen_y


# 화면 상의 행복도, 인구 등 데이터를 보여주는 sprite
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
        data = getattr(self.town, self.name)  # self.town에서 self.name (str 형)의 값을 가져오는 함수 getattr
        self.text_sprite.update(data, midleft=(140, self.level*50))

    def draw(self, surface):
        surface.blit(self.base_sprite.image, self.base_sprite.rect)
        surface.blit(self.text_sprite.image, self.text_sprite.rect)


# 데이터박스를 보여주는 sprite
class DataBoxBaseSprite(pygame.sprite.Sprite):
    def __init__(self, name, **kwargs):
        super().__init__()
        self.image = pygame.image.load(f'./image/databoxes/{name}.png')
        self.rect = self.image.get_rect(**kwargs)


# 데이터 text를 보여주는 sprite
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
