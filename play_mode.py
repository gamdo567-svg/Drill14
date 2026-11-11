import random

from pico2d import *
import game_world
import game_framework
from boy import Boy
from grass import Grass
from bird import Bird, BIRD_SIZE_PX

BIRD_COUNT = 10

boy = None


def handle_events():


    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            boy.handle_event(event)


def init():
    global boy

    boy = Boy()
    game_world.add_oject(boy)

    grass = Grass()
    game_world.add_oject(grass, 0)

    # 새 10마리를 하늘 영역(지면과 소년 위쪽)에 무작위로 배치
    for _ in range(BIRD_COUNT):
        x = random.uniform(BIRD_SIZE_PX, get_canvas_width() - BIRD_SIZE_PX)
        y = random.uniform(250, get_canvas_height() - BIRD_SIZE_PX / 2)
        game_world.add_oject(Bird(x, y, random.choice((-1, 1))))


def pause():
    boy.pause()


def resume():
    pass


def finish():
    global boy
    game_world.clear()
    boy = None


def update():
    game_world.update()

def render():
    clear_canvas()
    game_world.render()
    update_canvas()









