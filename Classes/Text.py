import pygame as pg


class Text(pg.sprite.DirtySprite):

    TITLE_SIZE = 87
    NOT_TITLE_SIZE = 12

    def __init__(self, image, function):
        pg.sprite.DirtySprite.__init__(self)
        self.colour = (255, 255, 255)
        self.function = function
        self.lastScore = 0
        self.score = 0
        self.dizzy = 0

        if function == 'score':
            self.font = image
            self.image = self.font.render("Score:    ", False, self.colour)
            self.rect = pg.Rect(17, 720, 10, 10)
            return
        elif function == 'track1':
            self.font = image
            self.image = self.font.render("Track 1", False, self.colour)
            self.rect = pg.Rect(340, 720, 20, 12)
            return
        elif function == 'track2':
            self.font = image
            self.image = self.font.render("Track 2", False, self.colour)
            self.rect = pg.Rect(480, 720, 20, 12)
            return
        elif function == 'track3':
            self.font = image
            self.image = self.font.render("Track 3", False, self.colour)
            self.rect = pg.Rect(620, 720, 20, 12)
            return
        elif function == 'title':
            self.rect = pg.Rect(157, 192, 686, 72)
        elif function == 'subtitle':
            self.rect = pg.Rect(380, 554, 239, 12)

        self.image = image
        self.original = self.image

    def update(self):
        self.dirty = 1
        if self.function == 'score':
            if self.score != self.lastScore or self.score == 0:
                msg = "Score: %d" % self.score
                self.image = self.font.render(msg, False, self.colour)

        elif self.function == 'title' or self.function == 'subtitle':
            if self.dizzy:
                self.spin()

    def spin(self):
        center = self.rect.center
        self.dizzy = self.dizzy + 20
        print('spinning by ' + str(self.dizzy))
        if self.dizzy >= 360:
            self.dizzy = 0
            self.image = self.original
        else:
            rotate = pg.transform.rotate
            self.image = rotate(self.original, self.dizzy)
        self.rect = self.image.get_rect(center=center)

    def increment(self):
        self.lastScore = self.score
        self.score += 1

    def mouseover(self):
        if self.function == 'title' or 'subtitle':
            if not self.dizzy:
                self.dizzy = 1
                self.original = self.image
                print('mouseover')

    def get_rect(self):
        return self.rect
