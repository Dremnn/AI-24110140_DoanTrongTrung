"""
8-PUZZLE — Giao diện Đồ họa 3 Panel (Pygame Dark Mode)
Có thể chạy độc lập: py puzzle8/app.py
Hoặc chạy thông qua Menu chính: py main.py
"""
import sys
import pygame
from common.ui import (
    WINDOW_W, WINDOW_H, LEFT_W, RIGHT_W, CENTER_X, CENTER_W, RIGHT_X,
    BG, PANEL_BG, CARD_BG, LINE, TEXT, MUTED,
    CYAN, CYAN_BG, PURPLE, PURPLE_BG, GOLD, GOLD_BG, GREEN, GREEN_BG,
    AMBER, AMBER_BG, RED, RED_BG,
    Button, Slider, load_font, draw_aa_circle, ease_out_cubic
)
from puzzle8.solver import (
    GOAL, bfs, dfs, ucs, is_solvable, shuffle_state, calculate_cost, ACTION_COSTS
)

# Màu ô số trong Dark Theme
BOARD_FRAME = (26, 32, 44)
BOARD_WELL = (15, 20, 28)
TILE_NORMAL = (35, 45, 60)
TILE_NORMAL_EDGE = (70, 85, 110)
TILE_CORRECT = (16, 68, 50)
TILE_CORRECT_EDGE = (52, 211, 153)
TILE_MOVING = (14, 116, 144)
TILE_MOVING_EDGE = (56, 189, 248)


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


class Puzzle8App:
    ROW_H = 58

    def __init__(self, screen=None):
        if screen is None:
            pygame.init()
            pygame.display.set_caption("8-Puzzle — BFS, DFS & UCS (Pygame Dark Mode)")
            self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
            self.own_screen = True
        else:
            self.screen = screen
            self.own_screen = False

        self.clock = pygame.time.Clock()

        # Font chữ
        self.f_title = load_font(21, "bold")
        self.f_head = load_font(15, "semibold")
        self.f_text = load_font(14, "regular")
        self.f_small = load_font(12, "regular")
        self.f_tiny = load_font(11, "bold")
        self.f_mini = load_font(10, "bold")
        self.f_tile = load_font(46, "bold")

        self.algo = "BFS"  # "BFS" | "DFS" | "UCS"
        self.depth_limit = 25
        self.shuffle_n = 14
        self.start = shuffle_state(self.shuffle_n)
        self.board = self.start
        self.compare_cache = {"BFS": None, "DFS": None, "UCS": None}

        # Nút điều hướng quay lại Menu chính
        self.b_back = Button((20, 16, 120, 36), "⬅ Menu", MUTED, CARD_BG)

        # Nút chọn 3 thuật toán
        self.b_bfs = Button((20, 92, 80, 38), "BFS", CYAN, CYAN_BG)
        self.b_dfs = Button((110, 92, 80, 38), "DFS", PURPLE, PURPLE_BG)
        self.b_ucs = Button((200, 92, 80, 38), "UCS", GOLD, GOLD_BG)

        # Chỉnh độ sâu DFS & số bước trộn
        self.b_lim_m = Button((168, 172, 38, 34), "-", PURPLE, PURPLE_BG)
        self.b_lim_p = Button((242, 172, 38, 34), "+", PURPLE, PURPLE_BG)

        self.b_sh_m = Button((168, 218, 38, 34), "-", AMBER, AMBER_BG)
        self.b_sh_p = Button((242, 218, 38, 34), "+", AMBER, AMBER_BG)

        self.speed = Slider((20, 314, 260, 10), 1, 100, 62, AMBER)

        self.b_shuffle = Button((20, 368, 260, 42), "Trộn bàn cờ ngẫu nhiên", AMBER, AMBER_BG)
        self.b_run = Button((20, 422, 260, 46), "Bắt đầu giải", GREEN, GREEN_BG)
        self.b_pause = Button((20, 478, 125, 40), "Tạm dừng", CYAN, CYAN_BG)
        self.b_reset = Button((155, 478, 125, 40), "Đặt lại", RED, RED_BG)

        self.reset_run(clear_cache=True)

    def board_rect(self):
        size = 336
        return pygame.Rect(CENTER_X + (CENTER_W - size) // 2, 118, size, size)

    def reset_run(self, clear_cache=False):
        self.mode = "idle"  # idle | search | solve | done
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
            self.compare_cache = {"BFS": None, "DFS": None, "UCS": None}

        self.status = "Sẵn sàng — Chọn thuật toán (BFS/DFS/UCS) rồi bấm Bắt đầu giải."

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
        self.status = f"{self.algo}: Đang tìm kiếm trong không gian trạng thái..."
        self.draw()
        pygame.display.flip()

        if self.algo == "BFS":
            self.result = bfs(self.start)
        elif self.algo == "DFS":
            self.result = dfs(self.start, self.depth_limit)
        else:  # UCS
            self.result = ucs(self.start)

        self.compare_cache[self.algo] = self.result
        self.mode = "search"
        cost_txt = f" (Tổng chi phí: {self.result['total_cost']})" if self.result["found"] else ""
        self.add_log(f"Bắt đầu duyệt {self.algo}", f"Số node: {len(self.result['expanded'])}{cost_txt}", None, True)
        self.status = f"{self.algo}: Đang duyệt các Node..."

    def begin_solve_step(self, step_idx):
        path = self.result["path"]
        acts = self.result["actions"]
        prev_st = path[step_idx]
        next_st = path[step_idx + 1]
        act_name = acts[step_idx]
        act_cost = ACTION_COSTS.get(act_name, 1)

        self.board = next_st
        self.trigger_slide(prev_st, next_st)
        moved_val = self.slide_tile_val
        self.add_log(
            f"Bước {step_idx + 1}/{len(acts)}: Trượt số {moved_val}",
            f"Ô trống {act_name} (Cost: {act_cost})",
            next_st,
            True,
        )
        self.status = f"Lời giải — Bước {step_idx + 1}/{len(acts)}: Trượt số {moved_val} (Ô trống {act_name}, chi phí={act_cost})"

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
                s, d_or_c = exp[self.idx]
                self.idx += 1
                self.board = s
                correct_cnt = sum(1 for i in range(8) if s[i] == GOAL[i])
                metric_name = "Cost" if self.algo == "UCS" else "Độ sâu"
                self.add_log(f"Node #{self.idx}  ({metric_name} {d_or_c})", f"Đúng vị trí: {correct_cnt}/8 ô", s, False)

            if self.idx >= len(exp):
                if self.result["found"]:
                    self.mode = "solve"
                    self.sol_idx = 0
                    self.board = self.start
                    acts = self.result["actions"]
                    cost = self.result["total_cost"]
                    self.add_log("Đã tìm thấy đích!", f"{len(acts)} bước • Tổng chi phí = {cost}", None, True)
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
                    self.status = f"Hoàn thành! {self.algo} đã giải xong sau {len(acts)} bước trượt (Chi phí = {self.result['total_cost']})."

    def on_click(self, pos):
        # Nút quay lại Menu
        if self.b_back.hit(pos):
            return "MENU"

        busy = self.mode in ("search", "solve")
        if self.b_bfs.hit(pos) and not busy:
            self.algo = "BFS"
        elif self.b_dfs.hit(pos) and not busy:
            self.algo = "DFS"
        elif self.b_ucs.hit(pos) and not busy:
            self.algo = "UCS"
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
        return None

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
        pygame.draw.rect(self.screen, PANEL_BG, (0, 0, LEFT_W, WINDOW_H))
        pygame.draw.line(self.screen, LINE, (LEFT_W, 0), (LEFT_W, WINDOW_H), 2)

        self.b_back.draw(self.screen, self.f_small)

        self.draw_text("8-PUZZLE LAB", (150, 24), self.f_title, AMBER)
        self.draw_text("1. Chọn thuật toán", (20, 68), self.f_head, TEXT)

        busy = self.mode in ("search", "solve")
        self.b_bfs.active = self.algo == "BFS"
        self.b_dfs.active = self.algo == "DFS"
        self.b_ucs.active = self.algo == "UCS"

        for b in (self.b_bfs, self.b_dfs, self.b_ucs, self.b_lim_m, self.b_lim_p,
                  self.b_sh_m, self.b_sh_p, self.b_shuffle, self.b_run):
            b.enabled = not busy
        self.b_pause.enabled = busy
        self.b_pause.text = "Tiếp tục" if self.paused else "Tạm dừng"

        # Hiển thị chú thích chi phí UCS
        cost_tip = "Chi phí: Lên/Xuống=1, Trái/Phải=2"
        self.draw_text(cost_tip, (20, 138), self.f_tiny, GOLD if self.algo == "UCS" else MUTED)

        self.draw_text("Giới hạn sâu (DFS):", (20, 178), self.f_text, MUTED)
        self.draw_text(str(self.depth_limit), (224, 189), self.f_head, PURPLE, True)

        self.draw_text("Số bước trộn:", (20, 224), self.f_text, MUTED)
        self.draw_text(str(self.shuffle_n), (224, 235), self.f_head, AMBER, True)

        self.draw_text(f"2. Tốc độ mô phỏng: {int(self.speed.value)}%", (20, 280), self.f_head, TEXT)
        self.draw_text("Chậm", (20, 332), self.f_small, MUTED)
        self.draw_text("Nhanh", (238, 332), self.f_small, MUTED)

        for b in (self.b_bfs, self.b_dfs, self.b_ucs, self.b_lim_m, self.b_lim_p,
                  self.b_sh_m, self.b_sh_p, self.b_shuffle, self.b_run, self.b_pause, self.b_reset):
            b.draw(self.screen, self.f_text)
        self.speed.draw(self.screen)

        # Khung Đích & Chú thích
        info_card = pygame.Rect(16, 536, LEFT_W - 32, 194)
        pygame.draw.rect(self.screen, CARD_BG, info_card, border_radius=12)
        pygame.draw.rect(self.screen, LINE, info_card, 1, border_radius=12)
        self.draw_text("Trạng thái Đích (Goal):", (28, 548), self.f_head, TEXT)
        draw_mini_board(self.screen, GOAL, 32, 578, 72, self.f_mini, True)

        self.draw_text("Chú thích màu ô:", (120, 576), self.f_small, TEXT)
        pygame.draw.rect(self.screen, TILE_CORRECT, (120, 602, 16, 16), border_radius=4)
        pygame.draw.rect(self.screen, TILE_CORRECT_EDGE, (120, 602, 16, 16), 1, border_radius=4)
        self.draw_text("Đúng vị trí đích", (144, 601), self.f_small, GREEN)

        pygame.draw.rect(self.screen, TILE_NORMAL, (120, 626, 16, 16), border_radius=4)
        pygame.draw.rect(self.screen, TILE_NORMAL_EDGE, (120, 626, 16, 16), 1, border_radius=4)
        self.draw_text("Chưa đúng vị trí", (144, 625), self.f_small, MUTED)

        self.draw_text("• Click ô cạnh ô trống để tự trượt.", (28, 666), self.f_small, MUTED)
        self.draw_text("• Bấm ESC để về Menu chọn game.", (28, 686), self.f_small, MUTED)

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
        algo_color = CYAN if self.algo == "BFS" else (PURPLE if self.algo == "DFS" else GOLD)
        algo_bg = CYAN_BG if self.algo == "BFS" else (PURPLE_BG if self.algo == "DFS" else GOLD_BG)
        st_bg = GREEN_BG if self.mode == "done" else (algo_bg if self.mode in ("search", "solve") else PANEL_BG)
        st_border = GREEN if self.mode == "done" else (algo_color if self.mode in ("search", "solve") else LINE)
        st_fg = GREEN if self.mode == "done" else (algo_color if self.mode in ("search", "solve") else TEXT)
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
        card1 = pygame.Rect(CENTER_X + 26, 478, CENTER_W - 52, 86)
        pygame.draw.rect(self.screen, PANEL_BG, card1, border_radius=14)
        pygame.draw.rect(self.screen, LINE, card1, 1, border_radius=14)

        shown = self.idx if res else 0
        total = len(res["expanded"]) if res else 0
        algo_col = CYAN if self.algo == "BFS" else (PURPLE if self.algo == "DFS" else GOLD)

        items = [
            ("Thuật toán", self.algo, algo_col),
            ("Node duyệt", f"{shown} / {total}" if res else "—", TEXT),
            ("Số bước", f"{len(res['actions'])} bước" if (res and res["found"]) else "—", GREEN),
            ("Tổng Cost", f"{res['total_cost']}" if (res and res["found"]) else "—", GOLD),
            ("Thời gian", f"{res['time'] * 1000:.1f} ms" if res else "—", AMBER),
        ]
        col_w = card1.w // len(items)
        for idx, (label, val, col) in enumerate(items):
            cx = card1.x + col_w * idx + col_w // 2
            self.draw_text(label, (cx, card1.y + 18), self.f_small, MUTED, True)
            self.draw_text(val, (cx, card1.y + 44), self.f_head, col, True)

        # Thanh tiến trình
        if res and total > 0:
            prog_bg = pygame.Rect(card1.x + 16, card1.bottom - 10, card1.w - 32, 4)
            pygame.draw.rect(self.screen, (35, 42, 54), prog_bg, border_radius=2)
            ratio = (self.sol_idx / max(1, len(res["actions"]))) if self.mode in ("solve", "done") else (shown / total)
            prog_fill = pygame.Rect(prog_bg.x, prog_bg.y, int(prog_bg.w * min(1.0, ratio)), 4)
            pygame.draw.rect(self.screen, GREEN if self.mode in ("solve", "done") else algo_col, prog_fill, border_radius=2)

        # Bảng so sánh 3 thuật toán: BFS, DFS, UCS
        card2 = pygame.Rect(CENTER_X + 26, 576, CENTER_W - 52, 152)
        pygame.draw.rect(self.screen, PANEL_BG, card2, border_radius=14)
        pygame.draw.rect(self.screen, LINE, card2, 1, border_radius=14)
        self.draw_text("SO SÁNH 3 THUẬT TOÁN: BFS vs DFS vs UCS (TRÊN CÙNG BÀN CỜ)",
                       (card2.x + 18, card2.y + 11), self.f_head, TEXT)

        col_3w = (card2.w - 48) // 3
        algos = [
            ("BFS", CYAN, CYAN_BG, "Queue (Ít bước nhất)"),
            ("DFS", PURPLE, PURPLE_BG, f"Stack (Giới hạn {self.depth_limit})"),
            ("UCS", GOLD, GOLD_BG, "Priority (Tối ưu Cost)"),
        ]

        for idx, (name, col, bg_col, desc) in enumerate(algos):
            bx = card2.x + 14 + idx * (col_3w + 10)
            by = card2.y + 36
            box = pygame.Rect(bx, by, col_3w, 102)
            pygame.draw.rect(self.screen, bg_col, box, border_radius=10)
            pygame.draw.rect(self.screen, col, box, 1, border_radius=10)

            self.draw_text(name, (bx + 10, by + 6), self.f_head, col)
            self.draw_text(desc, (bx + 10, by + 26), self.f_tiny, MUTED)

            data = self.compare_cache[name]
            if data:
                steps_txt = f"{len(data['actions'])} bước" if data["found"] else "Không thấy"
                cost_txt = f"Cost: {data['total_cost']}" if data["found"] else "Cost: —"
                self.draw_text(f"• Duyệt: {len(data['expanded'])} node", (bx + 10, by + 46), self.f_small, TEXT)
                self.draw_text(f"• {steps_txt}  |  {cost_txt}", (bx + 10, by + 66), self.f_small, GREEN if data["found"] else RED)
                self.draw_text(f"• {data['time']*1000:.1f} ms", (bx + 10, by + 84), self.f_tiny, MUTED)
            else:
                self.draw_text("Chưa chạy thử.", (bx + 10, by + 58), self.f_small, MUTED)

    def draw_right(self):
        pygame.draw.rect(self.screen, PANEL_BG, (RIGHT_X, 0, RIGHT_W, WINDOW_H))
        pygame.draw.line(self.screen, LINE, (RIGHT_X, 0), (RIGHT_X, WINDOW_H), 2)

        self.draw_text("CÁC NODE & BƯỚC GIẢI", (RIGHT_X + 20, 22), self.f_title, PURPLE)
        self.draw_text("Tự cuộn mới nhất • Lăn chuột để xem lại", (RIGHT_X + 20, 52), self.f_small, MUTED)

        top, bottom = 84, WINDOW_H - 14
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
            pygame.draw.rect(self.screen, LINE, (WINDOW_W - 10, bar_y, 5, bar_h), border_radius=3)

    def draw(self):
        self.screen.fill(BG)
        self.draw_left()
        self.draw_center()
        self.draw_right()

    def run(self):
        """Vòng lặp chạy khi chạy độc lập."""
        while True:
            dt = self.clock.tick(60) / 1000.0
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    return "MENU"
                self.speed.handle(e)
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    action = self.on_click(e.pos)
                    if action == "MENU":
                        return "MENU"
                if e.type == pygame.MOUSEWHEEL and pygame.mouse.get_pos()[0] > RIGHT_X:
                    self.scroll += e.y * 2
            self.update(dt)
            self.draw()
            pygame.display.flip()


if __name__ == "__main__":
    app = Puzzle8App()
    app.run()
