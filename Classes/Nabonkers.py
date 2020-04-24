import os
from random import randint
import pygame as pg
from pygame.compat import geterror


if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")
if not pg.mixer:
    print("Warning, sound disabled")
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


class Nabunga(pg.sprite.DirtySprite):
    # quarter up - full up
    frames = []
    bonkedFrame = None
    state = UP
    currentFrame = 0    # 0 - 3
    original = None
    time = None
    layer = 0
    ANIMTIME = 12
    animtimer = ANIMTIME
    def __init__(self, posRect, time, index, name):
        pg.sprite.DirtySprite.__init__(self, self.containers)
        self.image = self.frames[index]
        self.rect = posRect
        self.original = posRect
        self.time = time
        self.name = name

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


class Bonker(pg.sprite.DirtySprite):

    frames = []
    bonkState = False
    layer = 1
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


def main():
    pg.init()

    clock = pg.time.Clock()
    # Don't know what this does but don't touch it
    if pg.get_sdl_version()[0] == 2:
        pg.mixer.pre_init(44100, 32, 2, 1024)
    pg.init()
    # This might be broken

    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)
    pg.display.set_caption("Nabonkers!")
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
    hitSounds = [load_sound('track2.wav'), load_sound('track3.wav')]
    missSound = load_sound('track5.wav')
    # ------------------------------------------------------------------------------------------------------------------
    # Define pop-up coordinates; dimensions for nabunga0.png
    holes = []

    # left top width height
    topBottom = 650
    topTop= 455
    l= 66
    w, h = 32, 37    # of nabunga0
    # bottom row
    for i in range(0, 9, 2):
        left = i*100 + l
        rect = pg.Rect(left, topBottom, w, h)
        holes.append(rect)
    # top row
    for i in range(1, 8, 2):
        left = i*100 + l
        rect = pg.Rect(left, topTop, w, h)
        holes.append(rect)

    # len(holes) = 9

    # ------------------------------------------------------------------------------------------------------------------
    nabungas = pg.sprite.Group()
    last_nabunga = pg.sprite.GroupSingle()
    all = pg.sprite.LayeredDirty()
    Nabunga.containers = nabungas
    bonker = Bonker()
    all.add(bonker, layer=bonker.layer)

    going = True
    time = 100
    timer2 = time
    while going:
        all.clear(screen, background)
        all.update()
        # Create nabungas

        for hole in holes:
            chance = randint(1, 4)
            if chance == 1:
                if timer2 != 0:
                    timer2 -= 1
                else:
                    if last_nabunga:
                        last_nabunga.sprite.state = DOWN
                    n = Nabunga(hole, 40, 0, holes.index(hole))
                    all.add(n, layer=Nabunga.layer)
                    timer2 = time

        for event in pg.event.get():
            if event.type == pg.QUIT:
                going = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                bonker.bonkState = True
                for nabunga in nabungas:
                    # print(nabunga.name)
                    bonker.bonk(nabunga)
                    hitbox = bonker.rect.inflate(1, 1)
                    if hitbox.colliderect(nabunga.rect):
                        nabunga.bonk()
                        index = randint(0, (len(hitSounds)-1))
                        hitSounds[index].play()
                    else:
                        missSound.play()
            elif event.type == pg.MOUSEBUTTONUP:
                bonker.resetBonkState()

        dirty = all.draw(screen)
        pg.display.update(dirty)
        clock.tick(40)

    pg.quit()
    # TODO: Add background animation (simple water movement)

if __name__ == "__main__":
    main()
