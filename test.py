# 一个【简化版】开心消消乐示例（Python + pygame）
# 功能：棋盘生成、点击交换、三连消除、下落补齐
# 适合新手理解核心逻辑，不是商业完整版

import pygame
import random
import sys
import asyncio
import math
import traceback
from pathlib import Path
pygame.init()
ASSET_DIR = Path(__file__).resolve().parent

# ================== 开关配置 ==================
ENABLE_BOMB = False
ENABLE_PARTICLE = False
ENABLE_POP_ANIM = True
ENABLE_RANDOM_MOVE = True
ENABLE_SPAWN_ANIM = True
SIMPLE_POP_EFFECT = False

POP_DURATION_MS = 900
SPAWN_DURATION_MS = 460
ANIM_FPS = 60
ENABLE_SPECIAL_CLEAR = True
SPECIAL_5_RADIUS = 1
TRIGGER_DELAY_MS = 160
POP_HOLD = 0.22
POP_FEEL = "heavy"

if sys.platform == "emscripten":
    ENABLE_RANDOM_MOVE = False
    ENABLE_SPAWN_ANIM = False
    SIMPLE_POP_EFFECT = False
    POP_DURATION_MS = 640
    SPAWN_DURATION_MS = 220
    TRIGGER_DELAY_MS = 240
    POP_HOLD = 0.26

# ================== 基本配置 ==================
ROWS, COLS = 8, 8
TOP_MARGIN = 40

# 最大步数限制
MAX_MOVES = 30
moves_left = MAX_MOVES
score = 0
SCORE_PER_BLOCK = 10

processing = False
pending_matches = None
pending_groups = None

# 窗口大小：使用当前屏幕尺寸
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
if not WIDTH or not HEIGHT:
    WIDTH, HEIGHT = 960, 540
if sys.platform == "emscripten":
    WIDTH, HEIGHT = 960, 540

# 根据窗口大小动态计算格子尺寸
def get_cell_size():
    margin = 40
    available_w = WIDTH - margin * 2
    available_h = HEIGHT - TOP_MARGIN - margin
    return max(1, min(available_w // COLS, available_h // ROWS))

CELL_SIZE = get_cell_size()

flags = pygame.RESIZABLE
if sys.platform == "emscripten":
    flags = 0
screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("消消乐 Demo")

clock = pygame.time.Clock()

# 加载图片方块
def load_block_image(path, color):
    try:
        return pygame.image.load(str(path)).convert_alpha()
    except Exception:
        surf = pygame.Surface((64, 64), pygame.SRCALPHA)
        surf.fill(color)
        return surf

images_raw = [
    load_block_image(ASSET_DIR / "images/red.png", (220, 60, 60)),
    load_block_image(ASSET_DIR / "images/green.png", (70, 200, 90)),
    load_block_image(ASSET_DIR / "images/blue.png", (80, 120, 220)),
    load_block_image(ASSET_DIR / "images/yellow.png", (230, 210, 80)),
    load_block_image(ASSET_DIR / "images/purple.png", (160, 90, 200)),
]
bomb_image_raw = None
if ENABLE_BOMB:
    try:
        bomb_image_raw = pygame.image.load(str(ASSET_DIR / "images/bomb.png")).convert_alpha()
    except Exception:
        bomb_image_raw = None

images = []
bomb_image = None

# ================== 屏幕抖动配置 ==================
ENABLE_SHAKE = True
SHAKE_DURATION = 220  # ms，更缓的衰减
SHAKE_INTENSITY = 2.5 # 非整数，小幅连续抖动，更高级

shake_time = 0

if sys.platform == "emscripten":
    ENABLE_SHAKE = True
    SHAKE_DURATION = 140
    SHAKE_INTENSITY = 1.4

def trigger_shake():
    global shake_time
    shake_time = pygame.time.get_ticks()

def recalc_layout():
    global CELL_SIZE
    CELL_SIZE = get_cell_size()

def rebuild_scaled_assets():
    global images, bomb_image
    images = [pygame.transform.smoothscale(img, (CELL_SIZE, CELL_SIZE)) for img in images_raw]
    bomb_image = None
    if bomb_image_raw is not None:
        bomb_image = pygame.transform.smoothscale(bomb_image_raw, (CELL_SIZE, CELL_SIZE))

recalc_layout()
rebuild_scaled_assets()

# ================== 数据结构 ==================
class Block:
    def __init__(self, kind):
        self.kind = kind  # int index for normal block
        # self.is_bomb = is_bomb  # Removed bomb attribute

    def __eq__(self, other):
        if other is None:
            return False
        # return self.kind == other.kind and self.is_bomb == other.is_bomb
        return self.kind == other.kind

    def __repr__(self):
        # return f"Block({self.kind}{'B' if self.is_bomb else ''})"
        return f"Block({self.kind})"

def random_kind():
    return random.randint(0, len(images) - 1)

def random_block():
    # 移除随机生成炸弹的逻辑，只生成普通方块
    return Block(random_kind())

def init_board_no_triple():
    board = []
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            available = list(range(len(images)))
            # 检查左边和上面两个是否有连续两个相同，避免三连
            if c >= 2 and row[c-1].kind == row[c-2].kind:
                if row[c-1].kind in available:
                    available.remove(row[c-1].kind)
            if r >= 2 and board[r-1][c].kind == board[r-2][c].kind:
                if board[r-1][c].kind in available:
                    available.remove(board[r-1][c].kind)
            kind = random.choice(available)
            # 生成时暂不生成炸弹，避免初始炸弹太多
            row.append(Block(kind))
        board.append(row)
    return board

board = init_board_no_triple()
selected = None

# ================== 核心逻辑 ==================
def draw_board(offsets=None, pop_scale=None):
    global shake_time
    screen.fill((30, 30, 30))

    # 屏幕抖动偏移
    shake_x = shake_y = 0
    if ENABLE_SHAKE and shake_time:
        elapsed = pygame.time.get_ticks() - shake_time
        if elapsed < SHAKE_DURATION:
            t = elapsed / SHAKE_DURATION
            # 使用 smootherstep（更平滑的缓出曲线）
            smooth = 1 - (t * t * (3 - 2 * t))
            strength = SHAKE_INTENSITY * smooth

            # 使用低频噪声式抖动，避免帧间突变
            shake_x = strength * math.sin(elapsed * 0.04)
            shake_y = strength * math.cos(elapsed * 0.04)
        else:
            shake_x = shake_y = 0
            shake_time = 0

    # 计算棋盘居中偏移
    board_w = CELL_SIZE * COLS
    board_h = CELL_SIZE * ROWS
    offset_x = (WIDTH - board_w) // 2 + shake_x
    offset_y = TOP_MARGIN + (HEIGHT - TOP_MARGIN - board_h) // 2 + shake_y
    offset_x_i = int(offset_x)
    offset_y_i = int(offset_y)
    for r in range(ROWS):
        for c in range(COLS):
            block = board[r][c]
            if block is not None:
                # if block.is_bomb:
                #     img = bomb_image
                # else:
                rect = pygame.Rect(
                    offset_x_i + c * CELL_SIZE,
                    offset_y_i + r * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                base_size = CELL_SIZE
                scale = 1.0
                if pop_scale and (r, c) in pop_scale:
                    scale = pop_scale[(r, c)]
                size = max(1, int(base_size * scale))
                img_base = images[block.kind]
                if size == base_size:
                    img_scaled = img_base
                else:
                    img_scaled = pygame.transform.smoothscale(img_base, (size, size))
                img_offset_x, img_offset_y = 0, 0
                if offsets and (r, c) in offsets:
                    img_offset_x, img_offset_y = offsets[(r, c)]
                # 居中绘制
                img_offset_x += (base_size - size) // 2
                img_offset_y += (base_size - size) // 2
                screen.blit(img_scaled, rect.move(img_offset_x, img_offset_y))

    if selected:
        r, c = selected
        rect = pygame.Rect(
            offset_x_i + c * CELL_SIZE,
            offset_y_i + r * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
        pygame.draw.rect(screen, (255, 255, 255), rect, 3)

    # 显示剩余步数
    if moves_text_surface is not None:
        screen.blit(moves_text_surface, (20, 10))
    if score_text_surface is not None:
        screen.blit(score_text_surface, (20, 50))

def find_matches():
    matched = set()

    # 横向
    for r in range(ROWS):
        count = 1
        for c in range(1, COLS):
            b1 = board[r][c]
            b0 = board[r][c - 1]
            # 允许炸弹参与匹配，仅根据kind判断
            if b1 is not None and b0 is not None and b1.kind == b0.kind:
                count += 1
            else:
                if count >= 3:
                    for k in range(count):
                        matched.add((r, c - 1 - k))
                count = 1
        if count >= 3:
            for k in range(count):
                matched.add((r, COLS - 1 - k))

    # 纵向
    for c in range(COLS):
        count = 1
        for r in range(1, ROWS):
            b1 = board[r][c]
            b0 = board[r - 1][c]
            # 允许炸弹参与匹配，仅根据kind判断
            if b1 is not None and b0 is not None and b1.kind == b0.kind:
                count += 1
            else:
                if count >= 3:
                    for k in range(count):
                        matched.add((r - 1 - k, c))
                count = 1
        if count >= 3:
            for k in range(count):
                matched.add((ROWS - 1 - k, c))

    # 新增：检测所有炸弹方块，直接加入其位置
    # if ENABLE_BOMB:
    #     for r in range(ROWS):
    #         for c in range(COLS):
    #             block = board[r][c]
    #             if block is not None and block.is_bomb:
    #                 matched.add((r, c))

    return matched

def find_matches_with_groups():
    # 返回所有匹配位置及其连线分组（用于判断是否>=4连）
    matched = set()
    groups = []

    # 横向
    for r in range(ROWS):
        count = 1
        start_c = 0
        for c in range(1, COLS):
            b1 = board[r][c]
            b0 = board[r][c - 1]
            if b1 is not None and b0 is not None and b1.kind == b0.kind:
                count += 1
            else:
                if count >= 3:
                    group = [(r, cc) for cc in range(c - count, c)]
                    matched.update(group)
                    groups.append(group)
                count = 1
                start_c = c
        if count >= 3:
            group = [(r, cc) for cc in range(COLS - count, COLS)]
            matched.update(group)
            groups.append(group)

    # 纵向
    for c in range(COLS):
        count = 1
        start_r = 0
        for r in range(1, ROWS):
            b1 = board[r][c]
            b0 = board[r - 1][c]
            if b1 is not None and b0 is not None and b1.kind == b0.kind:
                count += 1
            else:
                if count >= 3:
                    group = [(rr, c) for rr in range(r - count, r)]
                    matched.update(group)
                    groups.append(group)
                count = 1
                start_r = r
        if count >= 3:
            group = [(rr, c) for rr in range(ROWS - count, ROWS)]
            matched.update(group)
            groups.append(group)

    # 炸弹方块加入matched，但不计入groups
    # if ENABLE_BOMB:
    #     for r in range(ROWS):
    #         for c in range(COLS):
    #             block = board[r][c]
    #             if block is not None and block.is_bomb:
    #                 matched.add((r, c))

    return matched, groups

def get_area(r, c, radius):
    area = []
    for rr in range(r - radius, r + radius + 1):
        for cc in range(c - radius, c + radius + 1):
            if 0 <= rr < ROWS and 0 <= cc < COLS:
                area.append((rr, cc))
    return area

def ease_out_cubic(t):
    return 1 - (1 - t) ** 3

def ease_in_out_cubic(t):
    if t < 0.5:
        return 4 * t * t * t
    return 1 - ((-2 * t + 2) ** 3) / 2

def handle_window_events():
    global WIDTH, HEIGHT, screen
    for event in pygame.event.get([pygame.QUIT, pygame.VIDEORESIZE]):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            recalc_layout()
            rebuild_scaled_assets()

async def remove_and_drop(matches, groups=None):
    global score
    # 触发屏幕抖动
    if ENABLE_SHAKE:
        trigger_shake()
    # 生成炸弹的逻辑：只有玩家交换或消除操作形成 >=4 个相连方块时才生成炸弹
    # groups是匹配分组列表，里面是连线位置列表
    # 对于每个group，如果长度>=4，则在该组随机一个位置生成炸弹方块

    # if ENABLE_BOMB and groups:
    #     for group in groups:
    #         if len(group) >= 4:
    #             # 选择一个位置生成炸弹
    #             br, bc = random.choice(group)
    #             board[br][bc] = Block(board[br][bc].kind, is_bomb=True)

    # 扩展匹配，炸弹消除周围3x3
    # if ENABLE_BOMB:
    #     expanded = set(matches)
    #     # 先找到所有炸弹（注意：炸弹不需要三连，find_matches已保证所有炸弹都在matches）
    #     bombs = [pos for pos in matches if board[pos[0]][pos[1]] is not None and board[pos[0]][pos[1]].is_bomb]
    #     for br, bc in bombs:
    #         expanded.update(get_bomb_area(br, bc))
    #     matches = expanded

    if ENABLE_SPECIAL_CLEAR and groups:
        expanded = set(matches)
        for group in groups:
            group_len = len(group)
            if group_len >= 5:
                cr, cc = group[group_len // 2]
                expanded.update(get_area(cr, cc, SPECIAL_5_RADIUS))
                continue
            if group_len == 4:
                rows = {r for r, _ in group}
                cols = {c for _, c in group}
                if len(rows) == 1:
                    r = next(iter(rows))
                    expanded.update((r, c) for c in range(COLS))
                elif len(cols) == 1:
                    c = next(iter(cols))
                    expanded.update((r, c) for r in range(ROWS))
        matches = expanded
    gained = len(matches) * SCORE_PER_BLOCK
    if gained:
        score += gained
        update_score_text()

    if TRIGGER_DELAY_MS > 0:
        await asyncio.sleep(TRIGGER_DELAY_MS / 1000)

    # 缩小消失动画（更丝滑：8步，每步75ms，动画后统一消除）
    if ENABLE_POP_ANIM:
        if SIMPLE_POP_EFFECT:
            steps = 6
            board_w = CELL_SIZE * COLS
            board_h = CELL_SIZE * ROWS
            offset_x = (WIDTH - board_w) // 2
            offset_y = TOP_MARGIN + (HEIGHT - TOP_MARGIN - board_h) // 2
            overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            for i in range(steps):
                handle_window_events()
                draw_board()
                if i % 2 == 0:
                    alpha = int(220 * (1 - i / max(1, steps - 1)))
                    overlay.fill((255, 240, 120, alpha))
                    for r, c in matches:
                        rect = pygame.Rect(
                            offset_x + c * CELL_SIZE,
                            offset_y + r * CELL_SIZE,
                            CELL_SIZE,
                            CELL_SIZE
                        )
                        screen.blit(overlay, rect)
                        pygame.draw.rect(screen, (255, 255, 255), rect, 2)
                pygame.display.flip()
                await asyncio.sleep(0.02)
        else:
            start = pygame.time.get_ticks()
            while True:
                handle_window_events()
                elapsed = pygame.time.get_ticks() - start
                t = 1.0 if POP_DURATION_MS <= 0 else min(1.0, elapsed / POP_DURATION_MS)
                if POP_FEEL == "heavy":
                    hold = max(0.0, min(0.6, POP_HOLD))
                    if t <= hold:
                        k = 0.0
                    else:
                        tt = (t - hold) / max(1e-6, 1.0 - hold)
                        k = ease_in_out_cubic(tt)
                else:
                    k = ease_out_cubic(t)
                pop_scale = {(r, c): max(0.0, 1.0 - k) for (r, c) in matches}
                draw_board(pop_scale=pop_scale)
                pygame.display.flip()
                if t >= 1.0:
                    break
                if sys.platform == "emscripten":
                    await asyncio.sleep(0)
                else:
                    clock.tick(ANIM_FPS)
    else:
        draw_board()
        pygame.display.flip()
        if sys.platform == "emscripten":
            await asyncio.sleep(0)
        else:
            pygame.time.delay(100)

    # 动画完成后统一消除
    for r, c in matches:
        board[r][c] = None

    # 下落补齐
    missing_per_col = [0] * COLS
    for c in range(COLS):
        col = [board[r][c] for r in range(ROWS)]
        new_col = [cell for cell in col if cell is not None]
        missing = ROWS - len(new_col)
        missing_per_col[c] = missing
        new_cells = [random_block() for _ in range(missing)]
        full_col = new_cells + new_col  # 从上到下
        for r in range(ROWS):
            board[r][c] = full_col[r]

    # 新方块弹入缓动效果
    if ENABLE_POP_ANIM and ENABLE_SPAWN_ANIM:
        # 弹入动画，简单向下移动显示
        start = pygame.time.get_ticks()
        while True:
            handle_window_events()
            elapsed = pygame.time.get_ticks() - start
            t = 1.0 if SPAWN_DURATION_MS <= 0 else min(1.0, elapsed / SPAWN_DURATION_MS)
            k = ease_out_cubic(t)
            offsets = {}
            for c in range(COLS):
                missing = missing_per_col[c]
                if missing <= 0:
                    continue
                offset_y = int((1.0 - k) * CELL_SIZE)
                for r in range(missing):
                    offsets[(r, c)] = (0, -offset_y)
            draw_board(offsets=offsets)
            pygame.display.flip()
            if t >= 1.0:
                break
            if sys.platform == "emscripten":
                await asyncio.sleep(0)
            else:
                clock.tick(ANIM_FPS)

def swap(a, b):
    (r1, c1), (r2, c2) = a, b
    board[r1][c1], board[r2][c2] = board[r2][c2], board[r1][c1]

def random_move_blocks():
    # 随机移动部分普通方块，避免炸弹移动
    moves = []
    count = 10  # 尝试移动10次
    for _ in range(count):
        r = random.randint(0, ROWS-1)
        c = random.randint(0, COLS-1)
        block = board[r][c]
        if block is None:
            continue
        # if block.is_bomb:
        #     continue
        # 找邻近空位或非炸弹块交换
        neighbors = []
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                nb = board[nr][nc]
                if nb is not None:
                    # if not nb.is_bomb:
                    neighbors.append((nr,nc))
        if neighbors:
            nr, nc = random.choice(neighbors)
            moves.append(((r,c),(nr,nc)))
    for a,b in moves:
        swap(a,b)

# ================== 主循环 ==================
font_moves = pygame.font.SysFont(None, 36)
moves_text_surface = None
score_text_surface = None
_moves_text_last = None
_score_text_last = None

def update_moves_text():
    global moves_text_surface, _moves_text_last
    if _moves_text_last == moves_left and moves_text_surface is not None:
        return
    _moves_text_last = moves_left
    moves_text_surface = font_moves.render(f"剩余步数: {moves_left}", True, (255, 255, 255))

def update_score_text():
    global score_text_surface, _score_text_last
    if _score_text_last == score and score_text_surface is not None:
        return
    _score_text_last = score
    score_text_surface = font_moves.render(f"总分: {score}", True, (255, 255, 255))

update_moves_text()
update_score_text()

async def handle_pointer(x, y):
    global selected, moves_left, processing, pending_matches, pending_groups
    if processing:
        return
    if y < TOP_MARGIN:
        return
    board_w = CELL_SIZE * COLS
    board_h = CELL_SIZE * ROWS
    offset_x = (WIDTH - board_w) // 2
    offset_y = TOP_MARGIN + (HEIGHT - TOP_MARGIN - board_h) // 2

    r = (y - offset_y) // CELL_SIZE
    c = (x - offset_x) // CELL_SIZE
    if r >= ROWS or c >= COLS or r < 0 or c < 0:
        return

    if not selected:
        selected = (r, c)
        return

    r0, c0 = selected
    if abs(r - r0) + abs(c - c0) == 1:
        swap(selected, (r, c))
        matches, groups = find_matches_with_groups()
        if matches:
            moves_left -= 1
            update_moves_text()
            pending_matches = matches
            pending_groups = groups
            processing = True
        else:
            swap(selected, (r, c))
    selected = None

async def process_cascade_step():
    global processing, pending_matches, pending_groups
    if not processing:
        return
    if pending_matches:
        await remove_and_drop(pending_matches, pending_groups)
        pending_matches, pending_groups = find_matches_with_groups()
        if not pending_matches and ENABLE_RANDOM_MOVE:
            random_move_blocks()
            pending_matches, pending_groups = find_matches_with_groups()
    if not pending_matches:
        processing = False

async def show_error(message):
    font = pygame.font.SysFont(None, 24)
    lines = []
    for raw in str(message).splitlines():
        if not raw:
            lines.append("")
            continue
        while len(raw) > 80:
            lines.append(raw[:80])
            raw = raw[80:]
        lines.append(raw)
    screen.fill((10, 10, 12))
    y = 20
    for line in lines[:20]:
        surf = font.render(line, True, (240, 90, 90))
        screen.blit(surf, (20, y))
        y += 26
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        await asyncio.sleep(0.1)

async def main():
    global running, WIDTH, HEIGHT, screen, selected, moves_left
    running = True
    user_quit = False
    try:
        while running:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.VIDEORESIZE:
                    WIDTH, HEIGHT = event.w, event.h
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                    recalc_layout()
                    rebuild_scaled_assets()
                if event.type == pygame.QUIT:
                    running = False
                    user_quit = True

                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    await handle_pointer(x, y)

                if event.type == pygame.FINGERDOWN:
                    x = int(event.x * WIDTH)
                    y = int(event.y * HEIGHT)
                    await handle_pointer(x, y)

            if moves_left <= 0:
                running = False

            if processing:
                await process_cascade_step()

            draw_board()
            pygame.display.flip()
            await asyncio.sleep(0)

        if not user_quit:
            await show_end_screen()
    except Exception:
        await show_error(traceback.format_exc())

# 游戏结束提示
end_font_title = None
end_font_stat = None
end_font_hint = None
end_bg_raw = None
end_bg_scaled = None
end_bg_pos = (0, 0)

def load_cjk_font(size):
    for name in [
        "PingFang SC",
        "Hiragino Sans GB",
        "Heiti SC",
        "Songti SC",
        "STHeiti",
        "Arial Unicode MS",
        "Noto Sans CJK SC",
        "Source Han Sans SC",
        "Microsoft YaHei",
        "SimHei",
    ]:
        path = pygame.font.match_font(name)
        if path:
            return pygame.font.Font(path, size)
    return pygame.font.SysFont(None, size)

def rebuild_end_fonts():
    global end_font_title, end_font_stat, end_font_hint
    title_size = max(72, min(140, int(min(WIDTH, HEIGHT) * 0.14)))
    stat_size = max(30, min(56, int(min(WIDTH, HEIGHT) * 0.06)))
    hint_size = max(20, min(32, int(min(WIDTH, HEIGHT) * 0.035)))
    end_font_title = load_cjk_font(title_size)
    end_font_stat = load_cjk_font(stat_size)
    end_font_hint = load_cjk_font(hint_size)

def rebuild_end_background():
    global end_bg_raw, end_bg_scaled, end_bg_pos
    if end_bg_raw is None:
        try:
            end_bg_raw = pygame.image.load(str(ASSET_DIR / "images/2.jpg")).convert()
        except Exception:
            end_bg_raw = pygame.Surface((1, 1))
            end_bg_raw.fill((20, 20, 24))
    bw, bh = end_bg_raw.get_size()
    if bw <= 0 or bh <= 0:
        end_bg_scaled = pygame.Surface((WIDTH, HEIGHT))
        end_bg_scaled.fill((20, 20, 24))
        end_bg_pos = (0, 0)
        return
    scale = max(WIDTH / bw, HEIGHT / bh)
    sw, sh = max(1, int(bw * scale)), max(1, int(bh * scale))
    end_bg_scaled = pygame.transform.smoothscale(end_bg_raw, (sw, sh))
    end_bg_pos = ((WIDTH - sw) // 2, (HEIGHT - sh) // 2)

async def show_end_screen():
    global WIDTH, HEIGHT, screen
    rebuild_end_fonts()
    rebuild_end_background()
    end_start = pygame.time.get_ticks()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                recalc_layout()
                rebuild_scaled_assets()
                rebuild_end_fonts()
                rebuild_end_background()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    pygame.quit()
                    return

        screen.blit(end_bg_scaled, end_bg_pos)

        elapsed = pygame.time.get_ticks() - end_start
        t = min(1.0, elapsed / 420)
        k = ease_out_cubic(t)
        overlay_alpha = int(110 * k)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, overlay_alpha))
        screen.blit(overlay, (0, 0))

        cx = WIDTH // 2
        title_y = int(HEIGHT * 0.25)
        score_y = int(HEIGHT * 0.42)

        title = end_font_title.render("游戏结束", True, (255, 240, 200))
        title_shadow = end_font_title.render("游戏结束", True, (0, 0, 0))
        title_rect = title.get_rect(center=(cx, title_y))
        screen.blit(title_shadow, title_rect.move(2, 2))
        screen.blit(title, title_rect)

        score_text = end_font_stat.render(f"分数: {score}", True, (245, 245, 245))
        score_shadow = end_font_stat.render(f"分数: {score}", True, (0, 0, 0))
        score_rect = score_text.get_rect(center=(cx, score_y))
        screen.blit(score_shadow, score_rect.move(2, 2))
        screen.blit(score_text, score_rect)

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)


asyncio.run(main())
