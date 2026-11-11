from pico2d import load_image

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
