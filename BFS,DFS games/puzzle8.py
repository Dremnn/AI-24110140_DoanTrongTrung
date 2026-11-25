"""
8-PUZZLE — Trực quan hóa BFS & DFS (Pygame Dark Mode)
Bố cục 3 panel:  [ Điều khiển ]  [ Bàn cờ 8-Puzzle ]  [ Các Node & Bước giải ]
Chạy:  py puzzle8.py
"""
import ctypes
import os
import random
import sys
import time
from collections import deque

# Bật chế độ High-DPI chuẩn Windows để hình vẽ và font chữ nét căng 1:1, không bị Windows kéo giãn mờ
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

import pygame
from pygame import gfxdraw

# ----------------------------------------------------------------------------
# 1. THUẬT TOÁN TÌM KIẾM (BFS & DFS)
# ----------------------------------------------------------------------------
GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
MOVES = (
    ("Lên", -1, 0),
    ("Xuống", 1, 0),
    ("Trái", 0, -1),
    ("Phải", 0, 1),
)


def neighbors(state):
    """Sinh các (hành_động, trạng_thái_mới) hợp lệ khi trượt ô trống."""
    z = state.index(0)
    r, c = divmod(z, 3)
    for name, dr, dc in MOVES:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            n_idx = nr * 3 + nc
            lst = list(state)
            lst[z], lst[n_idx] = lst[n_idx], lst[z]
            yield name, tuple(lst)


def is_solvable(state):
    arr = [x for x in state if x != 0]
    inv = sum(1 for i in range(len(arr)) for j in range(i + 1, len(arr)) if arr[i] > arr[j])
    return inv % 2 == 0


def build_result(parent, expanded, found, t0):
    states, actions = [], []
    if found:
        cur = GOAL
        while cur is not None:
            states.append(cur)
            p_info = parent[cur]
            if p_info is None:
                break
            actions.append(p_info[1])
            cur = p_info[0]
        states.reverse()
        actions.reverse()
    return {
        "expanded": expanded,
        "path": states,
        "actions": actions,
        "found": found,
        "time": time.time() - t0,
    }


def bfs(start):
    """BFS (Queue - FIFO) -> luôn tìm ra chuỗi bước trượt ngắn nhất."""
    t0 = time.time()
    parent = {start: None}
    queue = deque([(start, 0)])
    expanded = []

    while queue:
        s, d = queue.popleft()
        expanded.append((s, d))
        if s == GOAL:
            return build_result(parent, expanded, True, t0)
        for act, nxt in neighbors(s):
            if nxt not in parent:
                parent[nxt] = (s, act)
                queue.append((nxt, d + 1))

    return build_result(parent, expanded, False, t0)


def dfs(start, limit=25, cap=250000):
    """DFS (Stack - LIFO có Depth Limit) -> đi sâu theo nhánh."""
    t0 = time.time()
    best_depth = {start: 0}
    parent = {start: None}
    stack = [(start, 0)]
    expanded = []

    while stack:
        s, d = stack.pop()
        if best_depth.get(s, 10 ** 9) < d:
            continue
        expanded.append((s, d))
        if s == GOAL:
            return build_result(parent, expanded, True, t0)
        if len(expanded) >= cap:
            break
        if d >= limit:
            continue

        for act, nxt in reversed(list(neighbors(s))):
            nd = d + 1
            if nxt not in best_depth or best_depth[nxt] > nd:
                best_depth[nxt] = nd
                parent[nxt] = (s, act)
                stack.append((nxt, nd))

    return build_result(parent, expanded, False, t0)


def shuffle_state(n_moves):
    """Trộn bàn cờ bằng cách trượt ngẫu nhiên từ GOAL -> luôn giải được 100%."""
    s, prev = GOAL, None
    for _ in range(n_moves):
        opts = [nxt for _, nxt in neighbors(s) if nxt != prev]
        prev, s = s, random.choice(opts)
    return s if s != GOAL else shuffle_state(n_moves)


# ----------------------------------------------------------------------------
# 2. HỆ THỐNG MÀU DARK THEME & KHỬ RĂNG CƯA
# ----------------------------------------------------------------------------
W, H = 1320, 750
LEFT_W, RIGHT_W = 300, 360
CENTER_X, CENTER_W = LEFT_W, W - LEFT_W - RIGHT_W
RIGHT_X = W - RIGHT_W

# Bảng màu Dark Cyber / Obsidian sang trọng
BG = (13, 17, 23)              # Đen chì sâu
PANEL_BG = (22, 27, 34)        # Panel sẫm
CARD_BG = (30, 36, 46)         # Thẻ nền nổi
LINE = (48, 54, 61)            # Đường viền phân cách
TEXT = (240, 246, 252)         # Chữ trắng sáng
MUTED = (139, 148, 158)        # Chữ phụ màu xám bạc

CYAN = (56, 189, 248)          # Xanh lơ (BFS)
CYAN_BG = (15, 38, 58)
PURPLE = (168, 85, 247)        # Tím neon (DFS)
PURPLE_BG = (42, 22, 66)
GREEN = (52, 211, 153)         # Xanh ngọc phát quang
GREEN_BG = (16, 48, 36)
AMBER = (251, 191, 36)         # Vàng hổ phách
AMBER_BG = (58, 42, 14)
RED = (248, 113, 113)
RED_BG = (56, 20, 24)

BOARD_FRAME = (26, 32, 44)
BOARD_WELL = (15, 20, 28)

# Màu ô số ở chế độ Dark Mode
TILE_NORMAL = (35, 45, 60)
TILE_NORMAL_EDGE = (70, 85, 110)
TILE_CORRECT = (16, 68, 50)
TILE_CORRECT_EDGE = (52, 211, 153)
TILE_MOVING = (14, 116, 144)
TILE_MOVING_EDGE = (56, 189, 248)


def draw_aa_circle(surf, color, center, radius):
    x, y, r = int(center[0]), int(center[1]), int(radius)
    if r <= 0:
        return
    c = (color[0], color[1], color[2])
    gfxdraw.filled_circle(surf, x, y, r, c)
    gfxdraw.aacircle(surf, x, y, r, c)


def load_font(size, weight="regular"):
    win_fonts = "C:/WINDOWS/Fonts"
    candidates = {
        "regular": ["segoeui.ttf", "verdana.ttf", "tahoma.ttf"],
        "semibold": ["seguisb.ttf", "segoeuib.ttf", "verdanab.ttf"],
        "bold": ["segoeuib.ttf", "verdanab.ttf", "tahomabd.ttf"],
    }.get(weight, ["segoeui.ttf"])

    for fname in candidates:
        path = os.path.join(win_fonts, fname)
        if os.path.exists(path):
            return pygame.font.Font(path, size)
    return pygame.font.SysFont("verdana", size, bold=(weight != "regular"))


def ease_out_cubic(t):
    t = max(0.0, min(1.0, t))
    return 1.0 - pow(1.0 - t, 3)


# ----------------------------------------------------------------------------
# 3. COMPONENT GIAO DIỆN DARK MODE
# ----------------------------------------------------------------------------
class Button:
    def __init__(self, rect, text, color=CYAN, bg_active=CYAN_BG):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.bg_active = bg_active
        self.active = False
        self.enabled = True

    def draw(self, surf, font):
        hover = self.rect.collidepoint(pygame.mouse.get_pos()) and self.enabled
        if not self.enabled:
            bg, fg, border = (20, 24, 30), (75, 85, 99), (35, 42, 52)
        elif self.active:
            bg, fg, border = self.bg_active, self.color, self.color
        else:
            bg = (28, 35, 45) if hover else (22, 28, 36)
            fg = (255, 255, 255) if hover else self.color
            border = self.color if hover else LINE

        pygame.draw.rect(surf, bg, self.rect, border_radius=10)
        pygame.draw.rect(surf, border, self.rect, 2 if (self.active or hover) else 1, border_radius=10)
        img = font.render(self.text, True, fg)
        surf.blit(img, img.get_rect(center=self.rect.center))

    def hit(self, pos):
        return self.enabled and self.rect.collidepoint(pos)


class Slider:
    def __init__(self, rect, vmin, vmax, value):
        self.rect = pygame.Rect(rect)
        self.vmin, self.vmax, self.value = vmin, vmax, value
        self.drag = False

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.inflate(0, 24).collidepoint(event.pos):
                self.drag = True
        if event.type == pygame.MOUSEBUTTONUP:
            self.drag = False
        if self.drag and event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            t = (event.pos[0] - self.rect.x) / self.rect.w
            self.value = self.vmin + max(0.0, min(1.0, t)) * (self.vmax - self.vmin)

    def draw(self, surf):
        pygame.draw.rect(surf, (35, 42, 54), self.rect, border_radius=5)
        t = (self.value - self.vmin) / (self.vmax - self.vmin)
        fill = pygame.Rect(self.rect.x, self.rect.y, int(self.rect.w * t), self.rect.h)
        pygame.draw.rect(surf, AMBER, fill, border_radius=5)
        cx = int(self.rect.x + self.rect.w * t)
        draw_aa_circle(surf, AMBER, (cx, self.rect.centery), 10)
        draw_aa_circle(surf, (255, 255, 255), (cx, self.rect.centery), 4)


def draw_mini_board(surf, state, x, y, size, font, highlight=False):
    cell = size / 3.0
    border = GREEN if highlight else LINE
    pygame.draw.rect(surf, border, (x - 2, y - 2, size + 4, size + 4), 1, border_radius=5)
    for i, v in enumerate(state):
        r, c = divmod(i, 3)
        rect = pygame.Rect(int(x + c * cell), int(y + r * cell), int(cell - 1), int(cell - 1))
        if v:
            in_place = (GOAL[i] == v)
            bg = TILE_CORRECT if in_place else TILE_NORMAL
            pygame.draw.rect(surf, bg, rect, border_radius=3)
            fg = (255, 255, 255) if in_place else (220, 230, 242)
            img = font.render(str(v), True, fg)
            surf.blit(img, img.get_rect(center=rect.center))
        else:
            pygame.draw.rect(surf, (15, 20, 28), rect, border_radius=3)


# ----------------------------------------------------------------------------
# 4. ỨNG DỤNG CHÍNH
# ----------------------------------------------------------------------------
class App:
    ROW_H = 58

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("8-Puzzle — Trực quan hóa BFS & DFS")
        self.screen = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()

        self.f_title = load_font(21, "bold")
        self.f_head = load_font(15, "semibold")
        self.f_text = load_font(14, "regular")
        self.f_small = load_font(12, "regular")
        self.f_mini = load_font(10, "bold")
        self.f_tile = load_font(46, "bold")

        self.algo = "BFS"
        self.depth_limit = 25
        self.shuffle_n = 14
        self.start = shuffle_state(self.shuffle_n)
        self.board = self.start
        self.compare_cache = {"BFS": None, "DFS": None}

        # Nút / slider
        self.b_bfs = Button((20, 98, 125, 40), "BFS (Queue)", CYAN, CYAN_BG)
        self.b_dfs = Button((155, 98, 125, 40), "DFS (Stack)", PURPLE, PURPLE_BG)

        self.b_lim_m = Button((168, 170, 38, 34), "-", PURPLE, PURPLE_BG)
        self.b_lim_p = Button((242, 170, 38, 34), "+", PURPLE, PURPLE_BG)

        self.b_sh_m = Button((168, 220, 38, 34), "-", AMBER, AMBER_BG)
        self.b_sh_p = Button((242, 220, 38, 34), "+", AMBER, AMBER_BG)

        self.speed = Slider((20, 314, 260, 10), 1, 100, 62)

        self.b_shuffle = Button((20, 368, 260, 42), "Trộn bàn cờ ngẫu nhiên", AMBER, AMBER_BG)
        self.b_run = Button((20, 422, 260, 46), "Bắt đầu giải", GREEN, GREEN_BG)
        self.b_pause = Button((20, 478, 125, 40), "Tạm dừng", CYAN, CYAN_BG)
        self.b_reset = Button((155, 478, 125, 40), "Đặt lại", RED, RED_BG)

        self.reset_run(clear_cache=True)

    def board_rect(self):
        size = 336
        return pygame.Rect(CENTER_X + (CENTER_W - size) // 2, 120, size, size)

    def reset_run(self, clear_cache=False):
        self.mode = "idle"
        self.result = None
        self.paused = False
        self.idx = 0
        self.sol_idx = 0
        self.accum = 0.0
        self.log = []
        self.scroll = 0
        self.board = self.start

        self.slide_tile_val = None
        self.slide_from_rc = (0, 0)
        self.slide_to_rc = (0, 0)
        self.slide_t = 1.0

        if clear_cache:
            self.compare_cache = {"BFS": None, "DFS": None}

        self.status = "Sẵn sàng — Click ô cạnh ô trống để tự trượt, hoặc chọn thuật toán rồi bấm Bắt đầu giải."

    def add_log(self, title, subtitle="", state=None, hl=False):
        self.log.append((title, subtitle, state, hl))
        if len(self.log) > 3500:
            self.log.pop(0)

    def trigger_slide(self, prev_state, next_state):
        z_prev = prev_state.index(0)
        z_next = next_state.index(0)
        moved_tile = prev_state[z_next]
        self.slide_tile_val = moved_tile
        self.slide_from_rc = divmod(z_next, 3)
        self.slide_to_rc = divmod(z_prev, 3)
        self.slide_t = 0.0

    def start_run(self):
        if self.mode in ("search", "solve"):
            return
        self.reset_run(clear_cache=False)
        self.status = f"{self.algo}: Đang tìm đường trong không gian trạng thái..."
        self.draw()
        pygame.display.flip()

        if self.algo == "BFS":
            self.result = bfs(self.start)
        else:
            self.result = dfs(self.start, self.depth_limit)

        self.compare_cache[self.algo] = self.result
        self.mode = "search"
        self.add_log(f"Bắt đầu duyệt {self.algo}", f"Tổng node sẽ duyệt: {len(self.result['expanded'])}", None, True)
        self.status = f"{self.algo}: Đang mô phỏng quá trình duyệt các Node..."

    def begin_solve_step(self, step_idx):
        path = self.result["path"]
        acts = self.result["actions"]
        prev_st = path[step_idx]
        next_st = path[step_idx + 1]
        act_name = acts[step_idx]

        self.board = next_st
        self.trigger_slide(prev_st, next_st)
        moved_val = self.slide_tile_val
        self.add_log(
            f"Bước {step_idx + 1}/{len(acts)}: Trượt số {moved_val}",
            f"Ô trống dịch {act_name}",
            next_st,
            True,
        )
        self.status = f"Đang chạy lời giải — Bước {step_idx + 1}/{len(acts)}: Trượt ô số {moved_val} (ô trống đi {act_name})"

    def update(self, dt):
        if self.mode == "idle" and self.slide_t < 1.0:
            self.slide_t = min(1.0, self.slide_t + dt / 0.16)
            if self.slide_t >= 1.0:
                self.slide_tile_val = None
            return

        if self.mode not in ("search", "solve") or self.paused:
            return

        v = self.speed.value
        if self.mode == "search":
            rate = 2.5 * (1000 ** ((v - 1) / 99.0))
            self.accum += rate * dt
            n = int(self.accum)
            self.accum -= n
            exp = self.result["expanded"]

            for _ in range(n):
                if self.idx >= len(exp):
                    break
                s, d = exp[self.idx]
                self.idx += 1
                self.board = s
                correct_cnt = sum(1 for i in range(8) if s[i] == GOAL[i])
                self.add_log(f"Node #{self.idx}  (sâu {d})", f"Đúng vị trí: {correct_cnt}/8 ô", s, False)

            if self.idx >= len(exp):
                if self.result["found"]:
                    self.mode = "solve"
                    self.sol_idx = 0
                    self.board = self.start
                    acts = self.result["actions"]
                    self.add_log("Tìm thấy đích!", f"Độ dài lời giải: {len(acts)} bước", None, True)
                    if len(acts) > 0:
                        self.begin_solve_step(0)
                    else:
                        self.mode = "done"
                        self.status = "Bàn cờ đã ở trạng thái đích ngay từ đầu (0 bước)!"
                else:
                    self.mode = "done"
                    reason = f"vượt giới hạn độ sâu {self.depth_limit}" if self.algo == "DFS" else "không tìm thấy"
                    self.status = f"{self.algo}: Không tìm thấy lời giải ({reason}). Hãy tăng giới hạn sâu!"
                    self.add_log("Không tìm thấy lời giải", f"Đã duyệt {len(exp)} node", None, True)

        elif self.mode == "solve":
            acts = self.result["actions"]
            step_duration = max(0.12, 0.72 - (v / 100.0) * 0.58)
            self.slide_t += dt / step_duration
            if self.slide_t >= 1.0:
                self.slide_t = 1.0
                self.slide_tile_val = None
                self.sol_idx += 1
                if self.sol_idx < len(acts):
                    self.begin_solve_step(self.sol_idx)
                else:
                    self.mode = "done"
                    self.status = f"Hoàn thành! {self.algo} đã giải xong 8-Puzzle sau {len(acts)} bước trượt."

    def on_click(self, pos):
        busy = self.mode in ("search", "solve")
        if self.b_bfs.hit(pos) and not busy:
            self.algo = "BFS"
        elif self.b_dfs.hit(pos) and not busy:
            self.algo = "DFS"
        elif self.b_lim_m.hit(pos) and not busy:
            self.depth_limit = max(5, self.depth_limit - 1)
        elif self.b_lim_p.hit(pos) and not busy:
            self.depth_limit = min(60, self.depth_limit + 1)
        elif self.b_sh_m.hit(pos) and not busy:
            self.shuffle_n = max(2, self.shuffle_n - 1)
        elif self.b_sh_p.hit(pos) and not busy:
            self.shuffle_n = min(35, self.shuffle_n + 1)
        elif self.b_shuffle.hit(pos) and not busy:
            self.start = shuffle_state(self.shuffle_n)
            self.reset_run(clear_cache=True)
        elif self.b_run.hit(pos):
            self.start_run()
        elif self.b_pause.hit(pos) and busy:
            self.paused = not self.paused
        elif self.b_reset.hit(pos):
            self.reset_run(clear_cache=False)
        elif not busy:
            self.click_tile(pos)

    def click_tile(self, pos):
        br = self.board_rect()
        if not br.collidepoint(pos):
            return
        c = (pos[0] - br.x) * 3 // br.w
        r = (pos[1] - br.y) * 3 // br.h
        i = r * 3 + c
        z = self.start.index(0)
        zr, zc = divmod(z, 3)
        if abs(zr - r) + abs(zc - c) == 1:
            prev_st = self.start
            s = list(self.start)
            s[z], s[i] = s[i], s[z]
            self.start = tuple(s)
            self.reset_run(clear_cache=True)
            self.trigger_slide(prev_st, self.start)

    def draw_text(self, s, pos, font=None, color=TEXT, center=False):
        img = (font or self.f_text).render(s, True, color)
        rect = img.get_rect(center=pos) if center else img.get_rect(topleft=pos)
        self.screen.blit(img, rect)

    def draw_left(self):
        pygame.draw.rect(self.screen, PANEL_BG, (0, 0, LEFT_W, H))
        pygame.draw.line(self.screen, LINE, (LEFT_W, 0), (LEFT_W, H), 2)

        self.draw_text("BẢNG ĐIỀU KHIỂN", (20, 22), self.f_title, AMBER)
        self.draw_text("1. Chọn thuật toán", (20, 68), self.f_head, TEXT)

        busy = self.mode in ("search", "solve")
        self.b_bfs.active = self.algo == "BFS"
        self.b_dfs.active = self.algo == "DFS"
        for b in (self.b_bfs, self.b_dfs, self.b_lim_m, self.b_lim_p,
                  self.b_sh_m, self.b_sh_p, self.b_shuffle, self.b_run):
            b.enabled = not busy
        self.b_pause.enabled = busy
        self.b_pause.text = "Tiếp tục" if self.paused else "Tạm dừng"

        self.draw_text("Giới hạn sâu (DFS):", (20, 176), self.f_text, MUTED)
        self.draw_text(str(self.depth_limit), (224, 187), self.f_head, PURPLE, True)

        self.draw_text("Số bước trộn:", (20, 226), self.f_text, MUTED)
        self.draw_text(str(self.shuffle_n), (224, 237), self.f_head, AMBER, True)

        self.draw_text(f"2. Tốc độ mô phỏng: {int(self.speed.value)}%", (20, 282), self.f_head, TEXT)
        self.draw_text("Chậm", (20, 332), self.f_small, MUTED)
        self.draw_text("Nhanh", (238, 332), self.f_small, MUTED)

        for b in (self.b_bfs, self.b_dfs, self.b_lim_m, self.b_lim_p, self.b_sh_m, self.b_sh_p,
                  self.b_shuffle, self.b_run, self.b_pause, self.b_reset):
            b.draw(self.screen, self.f_text)
        self.speed.draw(self.screen)

        info_card = pygame.Rect(16, 536, LEFT_W - 32, 194)
        pygame.draw.rect(self.screen, CARD_BG, info_card, border_radius=12)
        pygame.draw.rect(self.screen, LINE, info_card, 1, border_radius=12)
        self.draw_text("Trạng thái Đích (Goal):", (28, 548), self.f_head, TEXT)
        draw_mini_board(self.screen, GOAL, 32, 578, 72, self.f_mini, True)

        self.draw_text("Chú thích màu ô:", (120, 576), self.f_small, TEXT)
        pygame.draw.rect(self.screen, TILE_CORRECT, (120, 602, 16, 16), border_radius=4)
        pygame.draw.rect(self.screen, TILE_CORRECT_EDGE, (120, 602, 16, 16), 1, border_radius=4)
        self.draw_text("Đã đúng vị trí đích", (144, 601), self.f_small, GREEN)

        pygame.draw.rect(self.screen, TILE_NORMAL, (120, 626, 16, 16), border_radius=4)
        pygame.draw.rect(self.screen, TILE_NORMAL_EDGE, (120, 626, 16, 16), 1, border_radius=4)
        self.draw_text("Chưa đúng vị trí", (144, 625), self.f_small, MUTED)

        self.draw_text("• Click vào ô cạnh ô trống để", (28, 666), self.f_small, MUTED)
        self.draw_text("  tự di chuyển và thử nghiệm.", (28, 686), self.f_small, MUTED)

    def draw_single_tile(self, px, py, cell_size, val, is_correct, is_sliding=False):
        rect = pygame.Rect(int(px + 5), int(py + 5), int(cell_size - 10), int(cell_size - 10))
        if is_sliding:
            bg, edge = TILE_MOVING, TILE_MOVING_EDGE
        elif is_correct:
            bg, edge = TILE_CORRECT, TILE_CORRECT_EDGE
        else:
            bg, edge = TILE_NORMAL, TILE_NORMAL_EDGE

        pygame.draw.rect(self.screen, (10, 14, 20), rect.move(0, 4), border_radius=16)
        pygame.draw.rect(self.screen, bg, rect, border_radius=16)
        pygame.draw.rect(self.screen, edge, rect, 2 if (is_correct or is_sliding) else 1, border_radius=16)

        pygame.draw.line(self.screen, (min(255, edge[0] + 40), min(255, edge[1] + 40), min(255, edge[2] + 40)),
                         (rect.x + 12, rect.y + 3), (rect.right - 12, rect.y + 3), 1)

        self.draw_text(str(val), rect.center, self.f_tile, (255, 255, 255), True)

        if is_correct and not is_sliding:
            draw_aa_circle(self.screen, GREEN, (rect.right - 14, rect.top + 14), 5)
            draw_aa_circle(self.screen, (255, 255, 255), (rect.right - 14, rect.top + 14), 2)

    def draw_center(self):
        cx = CENTER_X + CENTER_W // 2
        self.draw_text("BÀI TOÁN 8-PUZZLE (TRƯỢT SỐ 3×3)", (cx, 32), self.f_title, TEXT, True)

        st_rect = pygame.Rect(CENTER_X + 26, 62, CENTER_W - 52, 40)
        st_bg = GREEN_BG if self.mode == "done" else (CYAN_BG if self.mode in ("search", "solve") else PANEL_BG)
        st_border = GREEN if self.mode == "done" else (CYAN if self.mode in ("search", "solve") else LINE)
        st_fg = GREEN if self.mode == "done" else (CYAN if self.mode in ("search", "solve") else TEXT)
        pygame.draw.rect(self.screen, st_bg, st_rect, border_radius=12)
        pygame.draw.rect(self.screen, st_border, st_rect, 1, border_radius=12)
        self.draw_text(self.status, st_rect.center, self.f_text, st_fg, True)

        br = self.board_rect()
        outer = br.inflate(28, 28)
        pygame.draw.rect(self.screen, (8, 12, 16), outer.move(0, 6), border_radius=24)
        pygame.draw.rect(self.screen, BOARD_FRAME, outer, border_radius=24)
        pygame.draw.rect(self.screen, LINE, outer, 2, border_radius=24)
        pygame.draw.rect(self.screen, BOARD_WELL, br.inflate(8, 8), border_radius=18)

        cell = br.w / 3.0
        for r in range(3):
            for c in range(3):
                slot = pygame.Rect(int(br.x + c * cell + 5), int(br.y + r * cell + 5),
                                   int(cell - 10), int(cell - 10))
                pygame.draw.rect(self.screen, (18, 24, 34), slot, border_radius=16)

        for i, v in enumerate(self.board):
            if v == 0 or (self.slide_tile_val == v and self.slide_t < 1.0):
                continue
            r, c = divmod(i, 3)
            self.draw_single_tile(br.x + c * cell, br.y + r * cell, cell, v, GOAL[i] == v, False)

        if self.slide_tile_val is not None and self.slide_t < 1.0:
            t = ease_out_cubic(self.slide_t)
            r0, c0 = self.slide_from_rc
            r1, c1 = self.slide_to_rc
            cur_r = r0 + (r1 - r0) * t
            cur_c = c0 + (c1 - c0) * t
            target_idx = r1 * 3 + c1
            self.draw_single_tile(
                br.x + cur_c * cell,
                br.y + cur_r * cell,
                cell,
                self.slide_tile_val,
                GOAL[target_idx] == self.slide_tile_val,
                True,
            )

        self.draw_stats_and_comparison()

    def draw_stats_and_comparison(self):
        res = self.result
        card1 = pygame.Rect(CENTER_X + 26, 480, CENTER_W - 52, 84)
        pygame.draw.rect(self.screen, PANEL_BG, card1, border_radius=14)
        pygame.draw.rect(self.screen, LINE, card1, 1, border_radius=14)

        shown = self.idx if res else 0
        total = len(res["expanded"]) if res else 0
        items = [
            ("Thuật toán", self.algo, CYAN if self.algo == "BFS" else PURPLE),
            ("Node đã duyệt", f"{shown} / {total}" if res else "—", TEXT),
            ("Số bước giải", f"{len(res['actions'])} bước" if (res and res["found"]) else "—", GREEN),
            ("Thời gian tính", f"{res['time'] * 1000:.1f} ms" if res else "—", AMBER),
        ]
        col_w = card1.w // len(items)
        for idx, (label, val, col) in enumerate(items):
            cx = card1.x + col_w * idx + col_w // 2
            self.draw_text(label, (cx, card1.y + 18), self.f_small, MUTED, True)
            self.draw_text(val, (cx, card1.y + 42), self.f_head, col, True)

        if res and total > 0:
            prog_bg = pygame.Rect(card1.x + 16, card1.bottom - 12, card1.w - 32, 5)
            pygame.draw.rect(self.screen, (35, 42, 54), prog_bg, border_radius=3)
            ratio = (self.sol_idx / max(1, len(res["actions"]))) if self.mode in ("solve", "done") else (shown / total)
            prog_fill = pygame.Rect(prog_bg.x, prog_bg.y, int(prog_bg.w * min(1.0, ratio)), 5)
            pygame.draw.rect(self.screen, GREEN if self.mode in ("solve", "done") else CYAN, prog_fill, border_radius=3)

        card2 = pygame.Rect(CENTER_X + 26, 578, CENTER_W - 52, 150)
        pygame.draw.rect(self.screen, PANEL_BG, card2, border_radius=14)
        pygame.draw.rect(self.screen, LINE, card2, 1, border_radius=14)
        self.draw_text("SO SÁNH BFS & DFS (TRÊN CÙNG BÀN CỜ BAN ĐẦU)", (card2.x + 18, card2.y + 12), self.f_head, TEXT)

        half_w = (card2.w - 44) // 2
        for idx, name in enumerate(("BFS", "DFS")):
            bx = card2.x + 16 + idx * (half_w + 12)
            by = card2.y + 40
            box = pygame.Rect(bx, by, half_w, 96)
            bg = CYAN_BG if name == "BFS" else PURPLE_BG
            col = CYAN if name == "BFS" else PURPLE
            pygame.draw.rect(self.screen, bg, box, border_radius=10)
            pygame.draw.rect(self.screen, col, box, 1, border_radius=10)

            data = self.compare_cache[name]
            self.draw_text(f"{name} ({'Queue - Ngắn nhất' if name == 'BFS' else f'Stack - Giới hạn {self.depth_limit}'})",
                           (bx + 12, by + 8), self.f_head, col)
            if data:
                steps_txt = f"{len(data['actions'])} bước" if data["found"] else "Không tìm thấy"
                self.draw_text(f"• Số node duyệt: {len(data['expanded'])} node", (bx + 12, by + 35), self.f_small, TEXT)
                self.draw_text(f"• Độ dài lời giải: {steps_txt}  ({data['time']*1000:.1f} ms)",
                               (bx + 12, by + 60), self.f_small, GREEN if data["found"] else RED)
            else:
                self.draw_text("Chưa chạy trên bàn cờ này.", (bx + 12, by + 44), self.f_small, MUTED)

    def draw_right(self):
        pygame.draw.rect(self.screen, PANEL_BG, (RIGHT_X, 0, RIGHT_W, H))
        pygame.draw.line(self.screen, LINE, (RIGHT_X, 0), (RIGHT_X, H), 2)

        self.draw_text("CÁC NODE & BƯỚC GIẢI", (RIGHT_X + 20, 22), self.f_title, PURPLE)
        self.draw_text("Tự cuộn mới nhất • lăn chuột để xem lại", (RIGHT_X + 20, 52), self.f_small, MUTED)

        top, bottom = 84, H - 14
        avail_h = bottom - top
        rows = avail_h // self.ROW_H
        total = len(self.log)
        max_scroll = max(0, total - rows)
        self.scroll = max(0, min(self.scroll, max_scroll))
        end = total - self.scroll
        start = max(0, end - rows)

        self.screen.set_clip(pygame.Rect(RIGHT_X + 4, top, RIGHT_W - 8, avail_h))
        for k, (title, sub, st, hl) in enumerate(self.log[start:end]):
            y = top + k * self.ROW_H
            card = pygame.Rect(RIGHT_X + 14, y + 2, RIGHT_W - 34, self.ROW_H - 6)
            is_latest = (start + k == total - 1) and self.scroll == 0

            if st is None:
                pygame.draw.rect(self.screen, AMBER_BG, card, border_radius=9)
                pygame.draw.rect(self.screen, AMBER, card, 1, border_radius=9)
                self.draw_text(title, (card.x + 12, card.y + 6), self.f_head, AMBER)
                if sub:
                    self.draw_text(sub, (card.x + 12, card.y + 28), self.f_small, TEXT)
            else:
                bg = GREEN_BG if hl else ((18, 38, 56) if is_latest else CARD_BG)
                border = GREEN if hl else (CYAN if is_latest else LINE)
                pygame.draw.rect(self.screen, bg, card, border_radius=9)
                pygame.draw.rect(self.screen, border, card, 2 if (hl or is_latest) else 1, border_radius=9)

                draw_mini_board(self.screen, st, card.x + 10, card.y + 5, 42, self.f_mini, hl)
                self.draw_text(title, (card.x + 64, card.y + 6), self.f_head, GREEN if hl else TEXT)
                self.draw_text(sub, (card.x + 64, card.y + 28), self.f_small, MUTED)
        self.screen.set_clip(None)

        if total > rows:
            bar_h = max(28, int(avail_h * rows / total))
            ratio = 1.0 - (self.scroll / max_scroll)
            bar_y = top + int((avail_h - bar_h) * ratio)
            pygame.draw.rect(self.screen, LINE, (W - 10, bar_y, 5, bar_h), border_radius=3)

    def draw(self):
        self.screen.fill(BG)
        self.draw_left()
        self.draw_center()
        self.draw_right()

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.speed.handle(e)
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    self.on_click(e.pos)
                if e.type == pygame.MOUSEWHEEL and pygame.mouse.get_pos()[0] > RIGHT_X:
                    self.scroll += e.y * 2
            self.update(dt)
            self.draw()
            pygame.display.flip()


if __name__ == "__main__":
    App().run()
