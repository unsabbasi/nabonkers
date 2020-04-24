import pygame as pg



class Water(pg.sprite.DirtySprite):

    frames = []
    frame = 0
    layer = 0

    def __init__(self):
        pg.sprite.DirtySprite.__init__(self)
        self.image = self.frames[0]
        self.rect = pg.Rect(0, 368, 1000, 39)

    def update(self):
        self.dirty = 1
        if self.frame == 2:
            self.frame = 0
            self.image = self.frames[0]
        elif self.frame == 1:
            self.frame = 2
            self.image = self.frames[2]
        elif self.frame == 0:
            self.frame = 2
            self.image = self.frames[2]