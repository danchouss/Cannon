import numpy as np
import pygame as pg
from random import randint

pg.init()
pg.font.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
CYAN = (24, 244, 219)

SCREEN_SIZE = (800, 600)


def rand_color():
    return (randint(0, 255), randint(0, 255), randint(0, 255))



class Shell: #создаёт пульку, отвеает за её движение и отрисовку
    def __init__(self, coord, vel, rad=20, color=None):
        self.coord = coord
        self.vel = vel
        if color == None:
            color = rand_color()
        self.color = color
        self.rad = rad
        self.is_alive = True

    def check_corners(self, refl_ort=0.8, refl_par=0.9):
        for i in range(2):
            if self.coord[i] < self.rad:
                self.coord[i] = self.rad
                self.vel[i] = -int(self.vel[i] * refl_ort)
                self.vel[1 - i] = int(self.vel[1 - i] * refl_par)
            elif self.coord[i] > SCREEN_SIZE[i] - self.rad:
                self.coord[i] = SCREEN_SIZE[i] - self.rad
                self.vel[i] = -int(self.vel[i] * refl_ort)
                self.vel[1 - i] = int(self.vel[1 - i] * refl_par)

    def move(self, time=1, grav=0): #Двигает шарик (пульку)
        self.vel[1] += grav
        for i in range(2):
            self.coord[i] += time * self.vel[i]
        self.check_corners()
        if self.vel[0] ** 2 + self.vel[1] ** 2 < 2 ** 2 and self.coord[1] > SCREEN_SIZE[1] - 2 * self.rad:
            self.is_alive = False

    def draw(self, screen): #рисует шарик (пульку) на поверхности
        pg.draw.circle(screen, self.color, self.coord, self.rad)

    def draw2(self, screen): #рисует шарик (пульку) на поверхности
        pg.draw.circle(screen, self.color, self.coord, self.rad, randint(0, 10))




class Cannon:

    def __init__(self, coord=[30, SCREEN_SIZE[1] // 2], angle=0, max_pow=50, min_pow=10, color=RED):
        self.coord = coord
        self.angle = angle
        self.max_pow = max_pow
        self.min_pow = min_pow
        self.color = color
        self.active = False
        self.pow = min_pow

    def activate(self): #заряжаем пушку
        self.active = True

    def gain(self, inc=2):
        if self.active and self.pow < self.max_pow:
            self.pow += inc

    def strike(self): # делаем пульку
        vel = self.pow
        angle = self.angle
        ball = Shell(list(self.coord), [int(vel * np.cos(angle)), int(vel * np.sin(angle))])
        self.pow = self.min_pow
        self.active = False
        return ball

    def set_angle(self, target_pos):
        self.angle = np.arctan2(target_pos[1] - self.coord[1], target_pos[0] - self.coord[0])

    #эти два def двигают пушку по вертикали и по горизонтали
    def move_x(self, inc):
        if ((self.coord[0] > 30 or inc > 0) and
                (self.coord[0] < SCREEN_SIZE[1] - 30 or inc < 0)):self.coord[0] += inc

    def move_y(self, inc):
            if ((self.coord[1] > 30 or inc > 0) and
                    (self.coord[1] < SCREEN_SIZE[1] - 30 or inc < 0)):self.coord[1] += inc

    def draw(self, screen): #рисует ПУШКУ
        gun_shape = []
        vec_1 = np.array([int(5 * np.cos(self.angle - np.pi / 2)), int(5 * np.sin(self.angle - np.pi / 2))])
        vec_2 = np.array([int(self.pow * np.cos(self.angle)), int(self.pow * np.sin(self.angle))])
        gun_pos = np.array(self.coord)
        gun_shape.append((gun_pos + vec_1).tolist())
        gun_shape.append((gun_pos + vec_1 + vec_2).tolist())
        gun_shape.append((gun_pos + vec_2 - vec_1).tolist())
        gun_shape.append((gun_pos - vec_1).tolist())
        pg.draw.polygon(screen, self.color, gun_shape)


class Target:
    # создаёт вторую цель (незаполненные шарики и смотрит на столкновения и прочее)
    def __init__(self, coord=None, color=None, rad=30): #выставляет координаты
        if coord == None:
            coord = [randint(rad, SCREEN_SIZE[0] - rad), randint(rad, SCREEN_SIZE[1] - rad)]
        self.coord = coord
        self.rad = rad

        if color == None:
            color = rand_color()
        self.color = color

    def check_collision(self, ball): #проверка на столкновение
        dist = sum([(self.coord[i] - ball.coord[i]) ** 2 for i in range(2)]) ** 0.5
        min_dist = self.rad + ball.rad
        return dist <= min_dist

    def draw(self, screen): #рисует цельки на экране
        pg.draw.circle(screen, self.color, self.coord, self.rad)

    def move(self):
        pass

class Target2: #создаёт вторую цель (незаполненные шарики и смотрит на столкновения и прочее)
    def __init__(self, coord=None, color=None, rad=30): #выставляет координаты
        if coord == None:
            coord = [randint(rad, SCREEN_SIZE[0] - rad), randint(rad, SCREEN_SIZE[1] - rad)]
        self.coord = coord
        self.rad = rad

        if color == None:
            color = rand_color()
        self.color = color

    def check_collision(self, ball): #проверка на столкновение
        dist = sum([(self.coord[i] - ball.coord[i]) ** 2 for i in range(2)]) ** 0.5
        min_dist = self.rad + ball.rad
        return dist <= min_dist

    def draw(self, screen): #рисует цельки на экране
        pg.draw.circle(screen, self.color, self.coord, self.rad, 10)

    def move(self):
        pass



class MovingTarget(Target): #неожиданно, но оно двигает цельки и отражает их от стенок
    def __init__(self, coord=None, color=None, rad=30):
        super().__init__(coord, color, rad)
        self.vx = randint(-7, +7)
        self.vy = randint(-7, +7)

    def move(self):
        if self.coord[0]> 799 or self.coord[0]<1:
            self.vx = -self.vx

        if self.coord[1] > 599 or self.coord[1]<1:
            self.vy = -self.vy

        self.coord[1] += self.vy
        self.coord[0] += self.vx

class MovingTarget(Target2): #неожиданно, но оно двигает цельки и отражает их от стенок
    def __init__(self, coord=None, color=None, rad=30):
        super().__init__(coord, color, rad)
        self.vx = randint(-7, +7)
        self.vy = randint(-7, +7)

    def move(self):
        if self.coord[0]> 799 or self.coord[0]<1:
            self.vx = -self.vx

        if self.coord[1] > 599 or self.coord[1]<1:
            self.vy = -self.vy

        self.coord[1] += self.vy
        self.coord[0] += self.vx


#для таблицы подсчёта очков и метода вычисления очков
class ScoreTable:

    def __init__(self, t_destr=0, b_used=0):
        self.t_destr = t_destr
        self.b_used = b_used
        self.font = pg.font.SysFont("arial", 30)

    def score(self):
        return self.t_destr - self.b_used

    def draw(self, screen):
        score_surf = []
        score_surf.append(self.font.render("Сбито: {}".format(self.t_destr), True, WHITE))
        score_surf.append(self.font.render("Количесвтво нарядов: {}".format(self.b_used), True, WHITE))
        score_surf.append(self.font.render("Итоговый счёт: {}".format(self.score()), True, RED))
        for i in range(3):
            screen.blit(score_surf[i], [10, 10 + 30 * i])


class Manager:  #manager, который курирует собития, движение шарикка, создание целей..

    def __init__(self, n_targets=1):
        self.balls = []
        self.gun = Cannon()
        self.targets = []
        self.score_t = ScoreTable()
        self.n_targets = n_targets
        self.new_mission()

    def new_mission(self): #должна добавлять новые цели
        for i in range(self.n_targets):
            self.targets.append(Target(rad=randint(max(1, 30 - 2 * max(0, self.score_t.score())),
                                                   30 - max(0, self.score_t.score()))))
        for i in range(self.n_targets):
            self.targets.append(MovingTarget(rad=randint(max(1, 30 - 2 * max(0, self.score_t.score())),
                                                         30 - max(0, self.score_t.score()))))

    def process(self, events, screen): #отвечает за все игровые процессы

        done = self.handle_events(events)

        if pg.mouse.get_focused():
            mouse_pos = pg.mouse.get_pos()
            self.gun.set_angle(mouse_pos)

        self.move()
        self.collide()
        self.draw(screen)

        if len(self.targets) == 0 and len(self.balls) == 0:
            self.new_mission()

        return done

    def handle_events(self, events): #отвечает за реакцию на действия пользователя (тык мышкой и тд)
        done = False
        for event in events:
            if event.type == pg.QUIT:
                done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.gun.move_y(-5)
                elif event.key == pg.K_DOWN:
                    self.gun.move_y(5)
                elif event.key == pg.K_LEFT:
                    self.gun.move_x(-5)
                elif event.key == pg.K_RIGHT:
                    self.gun.move_x(5)
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.gun.activate()
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.balls.append(self.gun.strike())
                    self.score_t.b_used += 1
                    self.gun.color = BLACK
        return done

    def draw(self, screen): #рисует снаряд пушку и цель, и счётчик очков
        for ball in self.balls:
            tmp = randint(1, 2)
            if tmp == 1:
                ball.draw(screen)
            if tmp == 2:
                ball.draw2(screen)

        for target in self.targets:
            target.draw(screen)
        self.gun.draw(screen)
        self.score_t.draw(screen)

    def move(self): # двигает пушку и снаряд (плюс стрирает мусор с поля игры)
        dead_balls = []
        for i, ball in enumerate(self.balls):
            ball.move(grav=2)
            if not ball.is_alive:
                dead_balls.append(i)
        for i in reversed(dead_balls):
            self.balls.pop(i)
        for i, target in enumerate(self.targets):
            target.move()
        self.gun.gain()

    def collide(self): #проверка на попадание cнаряда в цель

        collisions = []
        targets_c = []
        for i, ball in enumerate(self.balls):
            for j, target in enumerate(self.targets):
                if target.check_collision(ball):
                    collisions.append([i, j])
                    targets_c.append(j)
        targets_c.sort()
        for j in reversed(targets_c):
            self.score_t.t_destr += 1
            self.targets.pop(j)


screen = pg.display.set_mode(SCREEN_SIZE)

done = False
clock = pg.time.Clock()

mgr = Manager(n_targets=5)

#обновляет экран и запускает игрульку
while not done:
    clock.tick(42)
    screen.fill(CYAN)

    done = mgr.process(pg.event.get(), screen)

    pg.display.flip()

pg.quit()