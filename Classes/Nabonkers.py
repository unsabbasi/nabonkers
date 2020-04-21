import os
import random
import pygame as pg
from pygame.compat import geterror


if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "Resources")

UP, STEADY, DOWN, BONKED = 'u', 's', 'd', 'b'
SCREENRECT = pg.Rect(0, 0, 1000, 700)


def load_image(file, mode=True):
    """ loads an image, prepares it for play
    """
    file = os.path.join(main_dir, "Resources", file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pg.get_error()))
    if mode:
        return surface.convert_alpha()
    return surface.convert()


def load_sound(name):
    class NoneSound:
        def play(self):
            pass

    if not pg.mixer or not pg.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pg.mixer.Sound(fullname)
    except pg.error:
        print("Cannot load sound: %s" % fullname)
        raise SystemExit(str(geterror()))
    return sound


class Nabunga(pg.sprite.Sprite):
    # quarter up - full up
    frames = []

    bonkedFrame = None

    state = None    # 'up', 'standing', 'down', None
    currentFrame = -1 # 0 - 4 (-1 when not drawn)

    def __init__(self, posRect):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = None
        self.rect = posRect

    def update(self):
        if self.currentFrame == 3:
            self.state = STEADY
        if self.state == BONKED:
            self.image = self.bonkedFrame
            self.state = DOWN
        elif self.state == UP:
            if self.currentFrame != 3:
                self.currentFrame += 1
                self.image = self.frames[self.currentFrame]
        elif self.state == DOWN:
            if self.currentFrame != 0:
                self.currentFrame -= 1
                self.image = self.frames[self.currentFrame]
            else:
                self.kill()     # IMPORTANT; pisses off after going down (and at last frame)

    def getState(self):
        return self.state


class Bonker(pg.sprite.Sprite):

    frames = []
    bonkState = False

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image, self.rect = self.frames[0], self.frames[0].get_rect()

    def update(self):
        self.rect.midtop = pg.mouse.get_pos()
        if self.bonkState:
            self.image = self.frames[1]

    def resetBonkState(self):
        if self.bonkState:
            self.bonkState = False
            self.image = self.frames[0]

    def bonk(self, target):
        if not self.bonkState:
            self.bonkState = True
            hitbox = self.rect.inflate(-5, -5)
            return hitbox.colliderect(target.rect)


def main():
    pg.init()

    all = pg.sprite.RenderUpdates()
    Bonker.containers = all
    clock = pg.time.Clock()


    if pg.get_sdl_version()[0] == 2:
        pg.mixer.pre_init(44100, 32, 2, 1024)
    pg.init()
    if pg.mixer and not pg.mixer.get_init():
        print("Warning, no sound")
        pg.mixer = None
    pg.mixer = None
    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)
    pg.display.set_caption("Nabonkers")
    icon = load_image('icon.png')
    icon = pg.transform.scale(icon, (32, 32))
    pg.display.set_icon(icon)
    pg.mouse.set_visible(0)
    # ------------------------------------------------------------------------------------------------------------------
    nabungaFrames = [load_image('nabunga0.png'), load_image('nabunga1.png'), load_image('nabunga2.png'),
              load_image('nabunga3.png')]
    bonkedFrame = load_image('nabunga_hit.png')
    bonkerFrames = [load_image('bonker0.png'), load_image('bonker1.png')]
    Nabunga.frames = nabungaFrames
    Nabunga.bonkedFrame = bonkedFrame
    Bonker.frames = bonkerFrames
    map = load_image('map.jpg', False)
    background = pg.Surface(screen.get_size()).convert()
    background.blit(map, (0, 0))
    screen.blit(background, (0, 0))
    pg.display.flip()
    # ------------------------------------------------------------------------------------------------------------------
    bonker = Bonker()
    going = True
    while going:
        all.clear(screen, background)
        all.update()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                going = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                bonker.bonkState = True
            elif event.type == pg.MOUSEBUTTONUP:
                bonker.resetBonkState()

        dirty = all.draw(screen)
        pg.display.update(dirty)
        clock.tick(40)


if __name__ == "__main__":
    main()
