import pygame as pg

class Clouds(pg.sprite.DirtySprite):

    frames = []
    layer = 0
    speed = 1

    def __init__(self, screen):
        pg.sprite.DirtySprite.__init__(self)
        self.image = self.frames[0]
        self.rect = pg.Rect(0, 120, 1000, 205)
        self.screen = screen

    def update(self):
        self.dirty = 1
        if self.rect.left <= self.screen.right:
            self.rect.move_ip(self.speed, 0)
        else:
            self.rect = pg.Rect(-1000, 120, 1000, 205)
