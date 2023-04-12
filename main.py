import pygame as p
import neat
import time, os, random
p.font.init()

WIDTH = 800
HEIGHT = 600

BIRD_IMGS = [p.transform.scale2x(p.image.load(os.path.join('imgs', 'bird1.png'))), p.transform.scale2x(p.image.load(os.path.join('imgs', 'bird2.png'))), p.transform.scale2x(p.image.load(os.path.join('imgs', 'bird3.png')))]
PIPE_IMG = p.transform.scale2x(p.image.load(os.path.join('imgs', 'pipe.png')))
BASE_IMG = p.transform.scale(p.image.load(os.path.join('imgs', 'base.png')),  (1500, 100))
BG_IMG = p.image.load(os.path.join('imgs', 'bg.png'))

STAT_FONT = p.font.SysFont('comicsans', 50)
gen = 0

VEL = 5
PIPE_SPREAD = 300
FIRST_PIPE = 3 * PIPE_SPREAD
BIRD_COORD = (230, 200)
DRAW_LINES = False
class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        d = self.vel*self.tick_count + 1.5*self.tick_count**2

        if d >= 16:
            d = 16
        # very questionable piece of code
        if d < 0:
            d -= 2

        self.y = self.y + d

        if d < 0 or self.y < self.height:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -75:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        else:
            self.img = self.IMGS[0]
            self.img_count = 0
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2-1

        rotated_image = p.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return p.mask.from_surface(self.img)

class Pipe:
    GAP = 165

    def __init__(self, x):
        self.x = x
        self.height = 100
        self.gap = 100

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = p.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        w, h = p.display.get_surface().get_size()
        self.height = random.randrange(50, h-310)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = p.mask.from_surface(self.PIPE_TOP)
        bottom_mask = p.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, top_offset)# if not, returns None
        t_point = bird_mask.overlap(top_mask, bottom_offset)
        if t_point or b_point:
            return True
        return False

class Base:
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= VEL
        self.x2 -= VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 +  self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2  = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def draw_window(win, background, birds, pipes, base, score, gen, pipe_ind):
    win.blit(background, (0,0))

    for bird in birds:
        if DRAW_LINES:
            #try:
            p.draw.line(win, (255, 0, 0), (bird.x + BIRD_IMGS[0].get_width()/2, bird.y + BIRD_IMGS[0].get_height()/2), (pipes[pipe_ind].x, pipes[pipe_ind].bottom), 5)
            p.draw.line(win, (255, 0, 0), (bird.x + BIRD_IMGS[0].get_width()/2, bird.y + BIRD_IMGS[0].get_height()/2), (pipes[pipe_ind].x, pipes[pipe_ind].height), 5)
            #except:
                #pass
        bird.draw(win)
    for pipe in pipes:
        pipe.draw(win)
    base.draw(win)

    text = STAT_FONT.render('Score: ' + str(score), 1, (255, 255, 255))
    w, h = p.display.get_surface().get_size()
    win.blit(text, (w-10-text.get_width(), 10))
    # generations
    score_label = STAT_FONT.render("Gens: " + str(gen),1,(255,255,255))
    win.blit(score_label, (10, 10))
    # alive
    score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(score_label, (10, 50))

    p.display.update()

win = p.display.set_mode((WIDTH, HEIGHT), p.RESIZABLE)
background = p.transform.smoothscale(BG_IMG, (WIDTH, HEIGHT))
clock = p.time.Clock()
def main(genomes, config):
    global gen, win, background, clock
    gen += 1
    w, h = p.display.get_surface().get_size()

    pipes = [Pipe(FIRST_PIPE+PIPE_SPREAD*r) for r in range(7)]
    base = Base(h-70)

    birds = []
    nets = []
    ge = []
    for _, g in genomes:
        g.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(BIRD_COORD[0], BIRD_COORD[1]))
        ge.append(g)

    score = 0
    run = True
    while run and len(birds) > 0:
        clock.tick(120)
        for event in p.event.get():
            if event.type == p.KEYDOWN:
                if event.key == p.K_SPACE:
                    for bird in birds:
                        bird.jump()

            elif event.type == p.QUIT:
                run = False
            elif event.type == p.KEYDOWN:
                if event.key == p.K_ESCAPE:
                    run = False
            elif event.type == p.VIDEORESIZE:
                w, h = event.w, event.h
                win = p.display.set_mode((w, h), p.RESIZABLE)
                background = p.transform.smoothscale(BG_IMG, (w, h))
                base = Base(h-70)

        place_on_axis = []
        for i, pipe in enumerate(pipes):
            if pipe.passed == False:
                place_on_axis.append((pipe.x, i))
        place_on_axis.sort()
        pipe_ind = place_on_axis[0][1]

        for i, bird in enumerate(birds):
            ge[i].fitness += 0.1

            output = nets[i].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:
                bird.jump()

            bird.move()

        remove = []
        add_pipe = False
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[i].fitness -= 1
                    birds.pop(i)
                    nets.pop(i)
                    ge.pop(i)

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove.append(pipe)
            if not pipe.passed and pipe.x + PIPE_IMG.get_width() < BIRD_COORD[0]:
                pipe.passed = True
                add_pipe = True

            pipe.move()

        if add_pipe:
            score += 1
            for g in  ge:
                g.fitness += 5
            pipes.append(Pipe(place_on_axis[-1][0]+PIPE_SPREAD))

            for r in remove:
                pipes.remove(r)

        for i, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= base.y  or  bird.y < -50:
                birds.pop(i)
                nets.pop(i)
                ge.pop(i)


        base.move()
        draw_window(win, background, birds, pipes, base, score, gen, pipe_ind)

        if run is False:
            p.quit()
            quit()

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        config_path)
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())

    winner = p.run(main, 50)
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
