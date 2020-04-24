import pygame as pg

UP, STEADY, DOWN, BONKED = 'u', 's', 'd', 'b'


class Nabunga(pg.sprite.DirtySprite):
    # quarter up - full up
    frames = []
    bonkedFrame = None
    state = UP
    currentFrame = 0    # 0 - 3
    original = None
    time = None
    layer = 2
    ANIMTIME = 12
    animtimer = ANIMTIME
    def __init__(self, posRect, time, index, name):
        pg.sprite.DirtySprite.__init__(self, self.containers)
        self.image = self.frames[index]
        self.rect = posRect
        self.original = posRect
        self.time = time
        self.name = name
        self.layer = 0

    def update(self):
        self.dirty = 1
        if self.state == STEADY:
            if self.time == 0:
                self.state = DOWN
            else:
                self.time -= 1

        if self.state == BONKED:
            self.image = self.bonkedFrame
            self.rect = self.get_frame_rect(3)
            if self.animtimer != 0:
                self.animtimer -= 1
                return
            else:
                self.animtimer = self.ANIMTIME
            self.state = DOWN

        elif self.state == UP:
            if self.currentFrame != 3:
                self.currentFrame += 1
                self.image = self.frames[self.currentFrame]
                self.rect = self.get_frame_rect(self.currentFrame)
            else:
                self.state = STEADY
                self.rect = self.get_frame_rect(3)

        elif self.state == DOWN:
            if self.currentFrame != 0:
                self.currentFrame -= 1
                self.image = self.frames[self.currentFrame]
                self.rect = self.get_frame_rect(self.currentFrame)
            elif self.currentFrame == 0:
                self.kill()     # IMPORTANT; pisses off after going down (and at last frame)

    def get_frame_rect(self, frame):
        left, top = self.original.topleft
        width, height = self.original.size
        if frame == 1:
            left -= 28
            top -= 42
            width, height = 86, 74
        if frame == 2:
            left -= 35
            top -= 79
            width, height = 96, 111
        if frame == 3:
            left -= 36
            top -= 111
            width, height = 96, 148
        return pg.Rect(left, top, width, height)

    def bonk(self):
        self.state = BONKED

    def getState(self):
        return self.state