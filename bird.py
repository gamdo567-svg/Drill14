"""새떼 비행 애니메이션 (bird_animation.png)

핵심 원칙: 모든 '변화량'은 (초당 변화량) x game_framework.frame_time 으로 계산한다.
  - 위치   : x += 방향 x FLY_SPEED_PPS x frame_time
  - 프레임 : frame += FRAMES_PER_SECOND x frame_time  (14프레임 주기로 순환)
따라서 FPS가 30이든 300이든 1초 동안 이동한 거리와 넘어간 프레임 수가 같다.
"""
import random

from pico2d import load_image, get_canvas_width

import game_framework

# ---------------------------------------------------------------------------
# 스프라이트 시트(bird_animation.png, 918 x 506) 분석 결과
#   - 5열 x 3행, 총 14프레임 (마지막 행은 4프레임)
#   - 가로 간격 182px : 모든 칸에서 눈(동공) 중심이 칸 왼쪽 +123px에 위치
#   - 세로 간격 170px : 0번 프레임과 13번 프레임의 눈 높이 차가 정확히 340px(=2행)
#   - 이미지 높이가 506px 이라 마지막 행은 170px이 아닌 166px만 존재
# ---------------------------------------------------------------------------
SHEET_HEIGHT = 506
FRAME_STRIDE_X = 182
FRAME_STRIDE_Y = 170
FRAME_W = 182
FRAME_H = 170
FRAMES_PER_ROW = 5
FRAMES_PER_ACTION = 14


def _build_frame_table():
    """프레임 번호 -> (left, bottom, w, h, dy) 표를 미리 만든다.

    pico2d 의 clip_draw 는 이미지 '아래쪽' 기준 좌표를 쓰므로
    위쪽 기준(top)으로 잰 값을 bottom 으로 변환한다.
    시트 밖으로 벗어나는 칸(마지막 행)은 높이를 잘라내고,
    잘린 만큼 중심이 위로 이동하므로 dy 로 보정해 몸통이 흔들리지 않게 한다.
    """
    table = []
    for i in range(FRAMES_PER_ACTION):
        col, row = i % FRAMES_PER_ROW, i // FRAMES_PER_ROW
        left = col * FRAME_STRIDE_X
        top = row * FRAME_STRIDE_Y
        h = min(FRAME_H, SHEET_HEIGHT - top)
        bottom = SHEET_HEIGHT - (top + h)
        dy = (FRAME_H - h) / 2  # 잘린 픽셀의 절반만큼 위로 올려 그린다
        table.append((left, bottom, FRAME_W, h, dy))
    return table


FRAMES = _build_frame_table()


# ---------------------------------------------------------------------------
# 물리 단위 -> 픽셀 단위 변환 (boy.py 와 같은 기준: 10px = 30cm)
# ---------------------------------------------------------------------------
PIXEL_PER_METER = (10.0 / 0.3)
FLY_SPEED_KMPH = 20.0                                # 새의 순항 속도 (km/h)
FLY_SPEED_MPM = (FLY_SPEED_KMPH * 1000.0 / 60.0)     # m/min
FLY_SPEED_MPS = (FLY_SPEED_MPM / 60.0)               # m/s
FLY_SPEED_PPS = (FLY_SPEED_MPS * PIXEL_PER_METER)    # pixel/s

BIRD_SIZE_M = 2.4                                    # 화면에 그릴 새 한 칸의 가로 크기 (m)
BIRD_SIZE_PX = BIRD_SIZE_M * PIXEL_PER_METER
BIRD_SCALE = BIRD_SIZE_PX / FRAME_W                  # 원본 182px -> 화면 크기 배율

# ---------------------------------------------------------------------------
# 날갯짓 애니메이션 속도 (시간 기준)
#   한 번의 날갯짓(14프레임 한 바퀴)에 걸리는 시간을 정하고,
#   거기서 '1초에 몇 프레임을 넘겨야 하는가'를 계산한다.
# ---------------------------------------------------------------------------
TIME_PER_ACTION = 0.5                                # 날갯짓 1회 = 0.5초
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION              # 초당 날갯짓 2회
FRAMES_PER_SECOND = FRAMES_PER_ACTION * ACTION_PER_TIME  # 초당 28프레임 진행


class Bird:
    image = None

    def __init__(self, x, y, direction=1):
        if Bird.image is None:
            Bird.image = load_image('bird_animation.png')  # 10마리가 이미지 하나를 공유
        self.x, self.y = x, y
        self.dir = direction
        # 모든 새가 똑같이 움직이면 한 덩어리로 보이므로 속도에 ±15% 개체차를 주고,
        # 날갯짓 시작 프레임도 무작위로 해 서로 다른 박자로 날개를 치게 한다.
        self.speed = FLY_SPEED_PPS * random.uniform(0.85, 1.15)
        self.frame = random.uniform(0, FRAMES_PER_ACTION) % FRAMES_PER_ACTION

    def update(self):
        dt = game_framework.frame_time
        # 프레임 진행량 = 초당 프레임 수 x 경과 시간(s), 14프레임 주기로 순환
        self.frame = (self.frame + FRAMES_PER_SECOND * dt) % FRAMES_PER_ACTION
        # 이동 거리 = 속도(px/s) x 경과 시간(s)
        self.x += self.dir * self.speed * dt

        # 화면 끝에 닿으면 방향 전환. 한 프레임에 많이 이동해 경계를 넘어가도
        # 경계 안으로 되돌려 놓아 화면 밖에 끼는 일이 없게 한다.
        half_w = BIRD_SIZE_PX / 2
        if self.x > get_canvas_width() - half_w:
            self.x = get_canvas_width() - half_w
            self.dir = -1
        elif self.x < half_w:
            self.x = half_w
            self.dir = 1

    def draw(self):
        left, bottom, w, h, dy = FRAMES[int(self.frame)]
        y = self.y + dy * BIRD_SCALE
        if self.dir == 1:   # 원본 스프라이트는 오른쪽을 보고 있음
            Bird.image.clip_draw(left, bottom, w, h,
                                 self.x, y, w * BIRD_SCALE, h * BIRD_SCALE)
        else:               # 왼쪽으로 날 때는 좌우 반전('h')해서 그림
            Bird.image.clip_composite_draw(left, bottom, w, h, 0, 'h',
                                           self.x, y, w * BIRD_SCALE, h * BIRD_SCALE)
