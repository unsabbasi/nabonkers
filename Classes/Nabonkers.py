import os
from Classes.Nabunga import Nabunga
from Classes.Bonker import Bonker
from Classes.Water import Water
from Classes.Clouds import Clouds
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
OCCUPIED = []


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
    waterFrames = [load_image('w0.jpg', False), load_image('w1.jpg', False), load_image('w2.png')]
    cloudFrame = [load_image('c.jpg', False)]
    Water.frames = waterFrames
    Clouds.frames = cloudFrame
    Nabunga.frames = nabungaFrames
    Nabunga.bonkedFrame = bonkedFrame
    Bonker.frames = bonkerFrames
    map = load_image('map.jpg', False)
    title = load_image('title.jpg', False)
    background = pg.Surface(screen.get_size()).convert()
    background.blit(title, (0, 0))
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
    clouds = Clouds(SCREENRECT)
    water = Water()
    all.add(bonker, layer=bonker.layer)
    all.add(clouds, layer=clouds.layer)
    all.add(water, layer=clouds.layer)

    music = load_sound('music1.wav')
    music.play(-1)
    music.set_volume(0.3)
    going = True
    time = 100
    timer2 = time
    gameState = False
    while going:
        escapeState = pg.key.get_pressed()
        if escapeState[pg.K_ESCAPE]:
            going = False
        #all.clear(screen, background)
        #all.update()
        if not gameState:
            keyState = pg.key.get_pressed()
            if keyState[pg.K_RETURN]:
                gameState = True
                print('pressed enter')
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    going = False
            screen.blit(background, (0, 0))
            pg.display.update()
        if gameState:
            all.clear(screen, background)
            all.update()
            background.blit(map, (0, 0))
            if timer2 != 0:
                timer2 -= 1
            else:
                for hole in holes:
                    chance = randint(1, 4)
                    if hole not in OCCUPIED and chance == 1:
                        if last_nabunga:
                            last_nabunga.sprite.state = DOWN
                            #OCC    UPIED.pop(last_nabunga.sprite.hole)
                        n = Nabunga(hole, 40, 0, holes.index(hole), OCCUPIED)
                        OCCUPIED.append(hole)
                        all.add(n, layer=Nabunga.layer)
                        timer2 = time

            hitsMade = 0    # "Per Click"
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    going = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    bonker.bonkState = True
                    for nabunga in nabungas:
                        # print(nabunga.name)
                        bonker.bonk(nabunga)
                        hitbox = bonker.rect.inflate(1, 1)
                        if hitbox.colliderect(nabunga.rect) and nabunga.getState() in [UP, STEADY]:
                            nabunga.bonk()
                            hitsMade += 1
                    if hitsMade > 0:
                        index = randint(0, (len(hitSounds) - 1))
                        hitSounds[index].play()
                    elif hitsMade == 0:
                        missSound.play()
                elif event.type == pg.MOUSEBUTTONUP:
                    bonker.resetBonkState()
                hitsMade = 0

            dirty = all.draw(screen)
            pg.display.update(dirty)
        pg.event.pump()
        clock.tick(40)

    pg.quit()
    # TODO: Add music selection, score, Maryam Talal WHOOPASS sequence

if __name__ == "__main__":
    main()
