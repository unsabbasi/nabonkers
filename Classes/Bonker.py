import pygame as pg

class Bonker(pg.sprite.DirtySprite):

    frames = []
    bonkState = False
    layer = 3
    def __init__(self):
        pg.sprite.DirtySprite.__init__(self)
        self.image, self.rect = self.frames[0], self.frames[0].get_rect()

    def update(self):
        self.dirty = 1
        self.rect.midtop = pg.mouse.get_pos()
        if self.bonkState:
            self.image = self.frames[1]

    def resetBonkState(self):
        if self.bonkState:
            self.bonkState = False
            self.image = self.frames[0]

    def bonk(self, nabunga):
        self.bonkState = True