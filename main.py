import pygame
from Town import Town
import Game
import Building


g = Game.Game()
t = Town('안녕', [Building.TownCenter((0, 0), is_upgrading=False)], population=10, money=1000)
g.town = t
g.play()
