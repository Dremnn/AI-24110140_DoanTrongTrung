"""
VACUUM WORLD — Giao diện Đồ họa 3 Panel (Pygame Dark Mode)
Có thể chạy độc lập: py vacuum/app.py
Hoặc chạy thông qua Menu chính: py main.py
"""
import math
import random
import sys
import pygame
from common.ui import (
    WINDOW_W, WINDOW_H, LEFT_W, RIGHT_W, CENTER_X, CENTER_W, RIGHT_X,
    BG, PANEL_BG, CARD_BG, LINE, TEXT, MUTED,
    CYAN, CYAN_BG, PURPLE, PURPLE_BG, GOLD, GOLD_BG, GREEN, GREEN_BG,
    AMBER, AMBER_BG, RED, RED_BG,
    Button, Slider, load_font, draw_aa_circle, draw_aa_ellipse, ease_in_out
)
from vacuum.solver import (
    ACTION_ORDERS, ACTION_COSTS, ACTION_VI,
    bfs, dfs, ucs, calculate_cost
)

DUST_COLOR = (217, 119, 6)
DUST_GLOW = (245, 158, 11)


def describe_state(s):
    return f"Robot ở phòng {'AB'[s[0]]}  •  A: {'Bẩn' if s[1] else 'Sạch'}  |  B: {'Bẩn' if s[2] else 'Sạch'}"


def draw_mini_rooms(surf, state, x, y, font, highlight=False):
    for i in range(2):
        rx = x + i * 32
        rect = pygame.Rect(rx, y, 29, 36)
        is_dirty = state[1 + i] == 1
        bg = (48, 32, 18) if is_dirty else (18, 42, 34)
        border = GREEN if highlight else ((217, 119, 6) if is_dirty else (34, 197, 94))
        pygame.draw.rect(surf, bg, rect, border_radius=6)
        pygame.draw.rect(surf, border, rect, 2 if highlight else 1, border_radius=6)

        lbl = font.render("AB"[i], True, (250, 204, 21) if is_dirty else (110, 231, 183))
        surf.blit(lbl, (rx + 4, y + 2))

        if is_dirty:
            for dx, dy in ((18, 10), (22, 16), (15, 17)):
                draw_aa_circle(surf, AMBER, (rx + dx, y + dy), 2)
        if state[0] == i:
            draw_aa_circle(surf, CYAN, (rect.centerx, y + 25), 6)
            draw_aa_circle(surf, (255, 255, 255), (rect.centerx, y + 25), 2)


class VacuumApp:
    ROW_H = 56

    def __init__(self, screen=None):
        if screen is None:
            pygame.init()
            pygame.display.set_caption("Vacuum World — BFS, DFS & UCS (Pygame Dark Mode)")
            self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
            self.own_screen = True
        else:
            self.screen = screen
            self.own_screen = False

        self.clock = pygame.time.Clock()

        self.f_title = load_font(21, "bold")
        self.f_head = load_font(15, "semibold")
        self.f_text = load_font(14, "regular")
        self.f_small = load_font(12, "regular")
        self.f_tiny = load_font(11, "bold")
        self.f_room = load_font(22, "bold")

        self.algo = "BFS"  # "BFS" | "DFS" | "UCS"
        self.priority_mode = "suck_first"
        self.start = (0, 1, 1)
        self.state = self.start
        self.compare_cache = {"BFS": None, "DFS": None, "UCS": None}

        rng = random.Random(42)
        self.dust_Layout = [
            [(rng.uniform(0.18, 0.82), rng.uniform(0.54, 0.82), rng.randint(5, 9)) for _ in range(18)],
            [(rng.uniform(0.18, 0.82), rng.uniform(0.54, 0.82), rng.randint(5, 9)) for _ in range(18)],
        ]

        # Nút điều hướng quay lại Menu
        self.b_back = Button((20, 16, 120, 36), "⬅ Menu", MUTED, CARD_BG)

        # Nút chọn 3 thuật toán
        self.b_bfs = Button((20, 92, 80, 38), "BFS", CYAN, CYAN_BG)
        self.b_dfs = Button((110, 92, 80, 38), "DFS", PURPLE, PURPLE_BG)
        self.b_ucs = Button((200, 92, 80, 38), "UCS", GOLD, GOLD_BG)

        self.b_prio_suck = Button((20, 176, 260, 36), "Ưu tiên: Hút bụi (Suck) trước", GREEN, GREEN_BG)
        self.b_prio_move = Button((20, 218, 260, 36), "Ưu tiên: Di chuyển (L/R) trước", AMBER, AMBER_BG)

        self.speed = Slider((20, 314, 260, 10), 1, 100, 55, GREEN)

        self.b_random = Button((20, 368, 260, 40), "Môi trường ngẫu nhiên", AMBER, AMBER_BG)
        self.b_robot = Button((20, 416, 260, 40), "Đổi phòng xuất phát Robot", CYAN, CYAN_BG)
        self.b_run = Button((20, 474, 260, 46), "Bắt đầu chạy", GREEN, GREEN_BG)
        self.b_pause = Button((20, 528, 125, 40), "Tạm dừng", CYAN, CYAN_BG)
        self.b_reset = Button((155, 528, 125, 40), "Đặt lại", RED, RED_BG)

        self.sparkles = []
        self.time_sec = 0.0
        self.reset_run(clear_cache=True)

    def room_rect(self, i):
        w, h = 265, 295
        gap = 44
        x0 = CENTER_X + (CENTER_W - (2 * w + gap)) // 2
        return pygame.Rect(x0 + i * (w + gap), 152, w, h)

    def room_center_x(self, i):
        return float(self.room_rect(i).centerx)

    def reset_run(self, clear_cache=False):
        self.mode = "idle"
        self.result = None
        self.paused = False
        self.idx = 0
        self.sol_idx = 0
        self.accum = 0.0
        self.log = []
        self.scroll = 0
        self.state = self.start
        self.robot_x = self.room_center_x(self.start[0])
        self.robot_tilt = 0.0

        self.active_action = None
        self.step_from_state = self.start
        self.step_to_state = self.start
        self.step_t = 1.0
        self.sucking_room = -1
        self.sparkles.clear()

        if clear_cache:
            self.compare_cache = {"BFS": None, "DFS": None, "UCS": None}

        self.status = "Sẵn sàng — Click vào phòng A/B để thêm hoặc xóa bụi, rồi bấm Bắt đầu chạy."

    def add_log(self, title, subtitle="", state=None, hl=False):
        self.log.append((title, subtitle, state, hl))

    def spawn_sparkles(self, room_idx):
        r = self.room_rect(room_idx)
        rng = random.Random()
        for _ in range(22):
            ang = rng.uniform(0, math.tau)
            spd = rng.uniform(40, 130)
            self.sparkles.append([
                r.centerx + rng.uniform(-50, 50),
                r.centery + rng.uniform(-10, 60),
                math.cos(ang) * spd,
                math.sin(ang) * spd - 30,
                1.0,
            ])

    def start_run(self):
        if self.mode in ("search", "solve"):
            return
        self.reset_run(clear_cache=False)
        order = ACTION_ORDERS[self.priority_mode]

        if self.algo == "BFS":
            self.result = bfs(self.start, order)
        elif self.algo == "DFS":
            self.result = dfs(self.start, order)
        else:  # UCS
            self.result = ucs(self.start, order)

        self.compare_cache[self.algo] = self.result
        self.mode = "search"
        prio_txt = "Suck -> Left -> Right" if self.priority_mode == "suck_first" else "Left -> Right -> Suck"
        cost_txt = f" (Tổng chi phí: {self.result['total_cost']})" if self.result["found"] else ""
        self.add_log(f"Bắt đầu duyệt {self.algo}", f"Thứ tự: {prio_txt}{cost_txt}", None, True)
        self.status = f"{self.algo}: Đang mở rộng không gian trạng thái..."

    def begin_solve_step(self, step_index):
        acts = self.result["actions"]
        path = self.result["path"]
        self.active_action = acts[step_index]
        self.step_from_state = path[step_index]
        self.step_to_state = path[step_index + 1]
        self.step_t = 0.0

        room_idx = self.step_from_state[0]
        was_dirty = self.step_from_state[1 + room_idx] == 1
        self.sucking_room = room_idx if (self.active_action == "Suck" and was_dirty) else -1
        step_cost = ACTION_COSTS.get(self.active_action, 1)

        self.add_log(
            f"Bước {step_index + 1}: {ACTION_VI[self.active_action]}",
            f"{describe_state(self.step_to_state)}  (Cost: {step_cost})",
            self.step_to_state,
            True,
        )
        self.status = f"Đang thực hiện Bước {step_index + 1}/{len(acts)}: {ACTION_VI[self.active_action]} (Chi phí={step_cost})"

    def update(self, dt):
        self.time_sec += dt

        for sp in self.sparkles:
            sp[0] += sp[2] * dt
            sp[1] += sp[3] * dt
            sp[4] -= dt * 1.5
        self.sparkles = [sp for sp in self.sparkles if sp[4] > 0]

        if self.mode not in ("search", "solve") or self.paused:
            self.robot_tilt *= max(0.0, 1.0 - dt * 10)
            return

        v = self.speed.value
        if self.mode == "search":
            rate = 0.8 + (v / 100.0) * 4.5
            self.accum += rate * dt
            n = int(self.accum)
            self.accum -= n
            exp = self.result["expanded"]
            for _ in range(n):
                if self.idx < len(exp):
                    s, d_or_c = exp[self.idx]
                    self.idx += 1
                    metric = "Chi phí" if self.algo == "UCS" else "Độ sâu"
                    self.add_log(f"Node #{self.idx}  ({metric} {d_or_c})", describe_state(s), s, False)
                if self.idx >= len(exp):
                    if self.result["found"]:
                        self.mode = "solve"
                        self.sol_idx = 0
                        self.state = self.start
                        self.robot_x = self.room_center_x(self.start[0])
                        acts = self.result["actions"]
                        cost = self.result["total_cost"]
                        plan_str = " -> ".join(acts) if acts else "Đã sạch sẵn"
                        self.add_log("Tìm thấy đích!", f"Kế hoạch: {plan_str} • Chi phí = {cost}", None, True)
                        if len(acts) > 0:
                            self.begin_solve_step(0)
                        else:
                            self.mode = "done"
                            self.status = "Hoàn thành! Cả 2 phòng đã sạch ngay từ đầu (0 hành động)."
                    else:
                        self.mode = "done"
                        self.status = "Không tìm thấy lời giải."
                    break

        elif self.mode == "solve":
            acts = self.result["actions"]
            step_duration = max(0.28, 1.15 - (v / 100.0) * 0.85)
            self.step_t += dt / step_duration

            if self.step_t >= 1.0:
                self.step_t = 1.0
                if self.sucking_room != -1:
                    self.spawn_sparkles(self.sucking_room)
                self.sucking_room = -1
                self.state = self.step_to_state
                self.robot_x = self.room_center_x(self.state[0])
                self.robot_tilt = 0.0

                self.sol_idx += 1
                if self.sol_idx < len(acts):
                    self.begin_solve_step(self.sol_idx)
                else:
                    self.active_action = None
                    self.mode = "done"
                    self.status = f"Hoàn thành! {self.algo} dọn sạch cả 2 phòng sau {len(acts)} hành động (Tổng chi phí = {self.result['total_cost']})."
            else:
                eased = ease_in_out(self.step_t)
                x0 = self.room_center_x(self.step_from_state[0])
                x1 = self.room_center_x(self.step_to_state[0])
                self.robot_x = x0 + (x1 - x0) * eased
                if abs(x1 - x0) > 1:
                    direction = 1 if x1 > x0 else -1
                    self.robot_tilt = direction * math.sin(self.step_t * math.pi) * 8.0
                else:
                    self.robot_tilt = 0.0

    def on_click(self, pos):
        if self.b_back.hit(pos):
            return "MENU"

        busy = self.mode in ("search", "solve")
        if self.b_bfs.hit(pos) and not busy:
            self.algo = "BFS"
        elif self.b_dfs.hit(pos) and not busy:
            self.algo = "DFS"
        elif self.b_ucs.hit(pos) and not busy:
            self.algo = "UCS"
        elif self.b_prio_suck.hit(pos) and not busy:
            self.priority_mode = "suck_first"
            self.reset_run(clear_cache=True)
        elif self.b_prio_move.hit(pos) and not busy:
            self.priority_mode = "move_first"
            self.reset_run(clear_cache=True)
        elif self.b_random.hit(pos) and not busy:
            self.start = (random.randint(0, 1), random.randint(0, 1), random.randint(0, 1))
            if self.start[1] == 0 and self.start[2] == 0:
                self.start = (self.start[0], random.choice([0, 1]), 1)
            self.reset_run(clear_cache=True)
        elif self.b_robot.hit(pos) and not busy:
            self.start = (1 - self.start[0], self.start[1], self.start[2])
            self.reset_run(clear_cache=True)
        elif self.b_run.hit(pos):
            self.start_run()
        elif self.b_pause.hit(pos) and busy:
            self.paused = not self.paused
        elif self.b_reset.hit(pos):
            self.reset_run(clear_cache=False)
        elif not busy:
            for i in range(2):
                if self.room_rect(i).collidepoint(pos):
                    s = list(self.start)
                    s[1 + i] = 1 - s[1 + i]
                    self.start = tuple(s)
                    self.reset_run(clear_cache=True)
        return None

    def draw_text(self, s, pos, font=None, color=TEXT, center=False):
        img = (font or self.f_text).render(s, True, color)
        rect = img.get_rect(center=pos) if center else img.get_rect(topleft=pos)
        self.screen.blit(img, rect)

    def draw_left(self):
        pygame.draw.rect(self.screen, PANEL_BG, (0, 0, LEFT_W, WINDOW_H))
        pygame.draw.line(self.screen, LINE, (LEFT_W, 0), (LEFT_W, WINDOW_H), 2)

        self.b_back.draw(self.screen, self.f_small)

        self.draw_text("VACUUM LAB", (150, 24), self.f_title, GREEN)
        self.draw_text("1. Chọn thuật toán", (20, 68), self.f_head, TEXT)

        busy = self.mode in ("search", "solve")
        self.b_bfs.active = self.algo == "BFS"
        self.b_dfs.active = self.algo == "DFS"
        self.b_ucs.active = self.algo == "UCS"
        self.b_prio_suck.active = self.priority_mode == "suck_first"
        self.b_prio_move.active = self.priority_mode == "move_first"

        for b in (self.b_bfs, self.b_dfs, self.b_ucs, self.b_prio_suck, self.b_prio_move,
                  self.b_random, self.b_robot, self.b_run):
            b.enabled = not busy
        self.b_pause.enabled = busy
        self.b_pause.text = "Tiếp tục" if self.paused else "Tạm dừng"

        self.draw_text("Chi phí: Suck=2, Di chuyển L/R=1", (20, 136), self.f_tiny,
                       GOLD if self.algo == "UCS" else MUTED)

        self.draw_text("2. Thứ tự ưu tiên hành động", (20, 154), self.f_head, TEXT)
        self.draw_text(f"3. Tốc độ mô phỏng: {int(self.speed.value)}%", (20, 280), self.f_head, TEXT)
        self.draw_text("Chậm", (20, 332), self.f_small, MUTED)
        self.draw_text("Nhanh", (238, 332), self.f_small, MUTED)

        for b in (self.b_bfs, self.b_dfs, self.b_ucs, self.b_prio_suck, self.b_prio_move,
                  self.b_random, self.b_robot, self.b_run, self.b_pause, self.b_reset):
            b.draw(self.screen, self.f_text)
        self.speed.draw(self.screen)

        tip_rect = pygame.Rect(16, 588, LEFT_W - 32, 142)
        pygame.draw.rect(self.screen, CARD_BG, tip_rect, border_radius=12)
        pygame.draw.rect(self.screen, LINE, tip_rect, 1, border_radius=12)
        tips = [
            "Gợi ý tương tác:",
            "• Click vào phòng A hoặc B để thêm/xóa bụi.",
            "• UCS tìm chuỗi có Tổng Chi phí nhỏ nhất.",
            "• BFS tìm chuỗi có Số bước ít nhất.",
            "• Bấm ESC để quay lại Menu chọn game.",
        ]
        for k, line in enumerate(tips):
            f = self.f_head if k == 0 else self.f_small
            c = TEXT if k == 0 else MUTED
            self.draw_text(line, (26, 598 + k * 21), f, c)

    def draw_robot(self, cx, cy, is_sucking=False):
        if is_sucking:
            pulse = 0.5 + 0.5 * math.sin(self.time_sec * 18)
            cone_pts = [
                (cx - 24, cy + 32),
                (cx + 24, cy + 32),
                (cx + 68 + int(pulse * 10), cy + 122),
                (cx - 68 - int(pulse * 10), cy + 122),
            ]
            cone_surf = pygame.Surface((CENTER_W, WINDOW_H), pygame.SRCALPHA)
            shifted = [(x - CENTER_X, y) for x, y in cone_pts]
            pygame.draw.polygon(cone_surf, (56, 189, 248, 50), shifted)
            self.screen.blit(cone_surf, (CENTER_X, 0))

            for ring in range(3):
                rt = (self.time_sec * 2.8 + ring / 3.0) % 1.0
                ry = int(cy + 115 - rt * 78)
                rw = int(58 * (1.0 - rt * 0.6))
                draw_aa_ellipse(self.screen, CYAN, (cx - rw, ry - 6, rw * 2, 12))

        shadow_y = cy + 112
        draw_aa_ellipse(self.screen, (10, 14, 20), (cx - 58, shadow_y - 10, 116, 20))

        bob = int(math.sin(self.time_sec * (24 if is_sucking else 5)) * (3 if is_sucking else 1.5))
        ry = cy + bob
        shift = int(self.robot_tilt)

        nozzle_rect = pygame.Rect(cx - 26, ry + 34, 52, 14)
        pygame.draw.rect(self.screen, (30, 41, 59), nozzle_rect, border_radius=5)
        pygame.draw.rect(self.screen, CYAN if is_sucking else (71, 85, 105),
                         (cx - 20, ry + 44, 40, 5), border_radius=3)

        for wx in (cx - 46, cx + 34):
            pygame.draw.rect(self.screen, (15, 23, 42), (wx, ry + 26, 14, 20), border_radius=5)
            pygame.draw.rect(self.screen, (51, 65, 85), (wx, ry + 26, 14, 20), 1, border_radius=5)

        body = pygame.Rect(0, 0, 124, 78)
        body.center = (cx + shift, ry)
        pygame.draw.rect(self.screen, (30, 58, 138), body.move(0, 4), border_radius=24)
        pygame.draw.rect(self.screen, (2, 132, 199), body, border_radius=24)
        pygame.draw.rect(self.screen, (56, 189, 248), (body.x + 14, body.y + 6, body.w - 28, 8), border_radius=4)

        ant_x = body.centerx
        pygame.draw.line(self.screen, (100, 116, 139), (ant_x, body.top), (ant_x, body.top - 16), 3)
        ant_col = GREEN if is_sucking else AMBER
        draw_aa_circle(self.screen, ant_col, (ant_x, body.top - 18), 6)

        visor = pygame.Rect(0, 0, 88, 36)
        visor.center = (body.centerx, body.centery - 2)
        pygame.draw.rect(self.screen, (10, 15, 26), visor, border_radius=12)
        pygame.draw.rect(self.screen, (30, 41, 59), visor, 1, border_radius=12)

        for dx in (-20, 20):
            ex, ey = visor.centerx + dx, visor.centery - 1
            if is_sucking:
                pygame.draw.arc(self.screen, CYAN, (ex - 9, ey - 7, 18, 16), 0.2, math.pi - 0.2, 3)
            else:
                draw_aa_circle(self.screen, CYAN, (ex, ey), 7)
                draw_aa_circle(self.screen, (255, 255, 255), (ex - 2, ey - 2), 2)

        if self.mode == "solve" and self.active_action:
            cost = ACTION_COSTS.get(self.active_action, 1)
            tag_bg = GREEN_BG if self.active_action == "Suck" else CYAN_BG
            tag_border = GREEN if self.active_action == "Suck" else CYAN
            lbl = self.f_tiny.render(f"{self.active_action.upper()} (+{cost})", True, tag_border)
            tag_rect = lbl.get_rect(center=(body.centerx, body.top - 34)).inflate(16, 8)
            pygame.draw.rect(self.screen, tag_bg, tag_rect, border_radius=8)
            pygame.draw.rect(self.screen, tag_border, tag_rect, 1, border_radius=8)
            self.screen.blit(lbl, lbl.get_rect(center=tag_rect.center))

    def draw_room_dust(self, room_idx, rect):
        is_being_sucked = (self.mode == "solve" and self.sucking_room == room_idx)
        has_dust = (self.step_from_state[1 + room_idx] == 1) if is_being_sucked else (self.state[1 + room_idx] == 1)
        if not has_dust:
            return

        nozzle_x = self.robot_x
        nozzle_y = rect.y + 135
        t = ease_in_out(self.step_t) if is_being_sucked else 0.0

        for idx, (rx, ry, rad) in enumerate(self.dust_Layout[room_idx]):
            px = rect.x + rx * rect.w
            py = rect.y + ry * rect.h
            if is_being_sucked:
                local_t = max(0.0, min(1.0, (t * 1.25) - (idx % 5) * 0.05))
                swirl = math.sin(local_t * math.pi * 3 + idx) * (1.0 - local_t) * 22
                px = px + (nozzle_x - px) * local_t + swirl
                py = py + (nozzle_y - py) * local_t
                cur_r = max(1, int(rad * (1.0 - local_t * 0.9)))
                if local_t >= 0.98:
                    continue
            else:
                cur_r = rad

            draw_aa_circle(self.screen, DUST_COLOR, (px, py), cur_r)
            draw_aa_circle(self.screen, DUST_GLOW, (px - 1, py - 1), max(1, cur_r // 2))

    def draw_center(self):
        cx = CENTER_X + CENTER_W // 2
        self.draw_text("MÔ PHỎNG VACUUM WORLD (2 PHÒNG A & B)", (cx, 32), self.f_title, TEXT, True)

        st_rect = pygame.Rect(CENTER_X + 26, 62, CENTER_W - 52, 40)
        algo_col = CYAN if self.algo == "BFS" else (PURPLE if self.algo == "DFS" else GOLD)
        algo_bg = CYAN_BG if self.algo == "BFS" else (PURPLE_BG if self.algo == "DFS" else GOLD_BG)
        st_bg = GREEN_BG if self.mode == "done" else (algo_bg if self.mode in ("search", "solve") else PANEL_BG)
        st_border = GREEN if self.mode == "done" else (algo_col if self.mode in ("search", "solve") else LINE)
        st_fg = GREEN if self.mode == "done" else (algo_col if self.mode in ("search", "solve") else TEXT)
        pygame.draw.rect(self.screen, st_bg, st_rect, border_radius=12)
        pygame.draw.rect(self.screen, st_border, st_rect, 1, border_radius=12)
        self.draw_text(self.status, st_rect.center, self.f_text, st_fg, True)

        r0, r1 = self.room_rect(0), self.room_rect(1)
        corridor = pygame.Rect(r0.right - 6, r0.y + 88, r1.left - r0.right + 12, 110)
        pygame.draw.rect(self.screen, (18, 22, 30), corridor)
        pygame.draw.line(self.screen, LINE, (corridor.left, corridor.top), (corridor.right, corridor.top), 2)
        pygame.draw.line(self.screen, LINE, (corridor.left, corridor.bottom), (corridor.right, corridor.bottom), 2)

        for i in range(2):
            r = self.room_rect(i)
            is_dirty = self.state[1 + i] == 1
            pygame.draw.rect(self.screen, (8, 12, 16), r.move(0, 5), border_radius=18)
            pygame.draw.rect(self.screen, PANEL_BG, r, border_radius=18)

            floor_rect = pygame.Rect(r.x + 4, r.y + 145, r.w - 8, r.h - 149)
            floor_color = (36, 26, 18) if is_dirty else (16, 32, 28)
            pygame.draw.rect(self.screen, floor_color, floor_rect,
                             border_bottom_left_radius=15, border_bottom_right_radius=15)
            pygame.draw.line(self.screen, LINE, (r.x + 4, r.y + 145), (r.right - 4, r.y + 145), 1)

            robot_here = (abs(self.robot_x - r.centerx) < r.w * 0.45)
            border_col = CYAN if robot_here else LINE
            pygame.draw.rect(self.screen, border_col, r, 2 if robot_here else 1, border_radius=18)

            self.draw_text(f"PHÒNG {'AB'[i]}", (r.x + 18, r.y + 16), self.f_room, TEXT)
            badge_w, badge_h = 82, 26
            badge_rect = pygame.Rect(r.right - badge_w - 16, r.y + 16, badge_w, badge_h)
            badge_bg = AMBER_BG if is_dirty else GREEN_BG
            badge_fg = AMBER if is_dirty else GREEN
            pygame.draw.rect(self.screen, badge_bg, badge_rect, border_radius=13)
            pygame.draw.rect(self.screen, badge_fg, badge_rect, 1, border_radius=13)
            self.draw_text("CÓ BỤI" if is_dirty else "SẠCH", badge_rect.center, self.f_tiny, badge_fg, True)

            self.draw_room_dust(i, r)

        for sx, sy, _, _, life in self.sparkles:
            rad = max(2, int(5 * life))
            draw_aa_circle(self.screen, GREEN, (sx, sy), rad)
            draw_aa_circle(self.screen, (255, 255, 255), (sx, sy), max(1, rad // 2))

        is_sucking = (self.mode == "solve" and self.active_action == "Suck")
        self.draw_robot(int(self.robot_x), r0.y + 100, is_sucking=is_sucking)
        self.draw_stats_and_comparison()

    def draw_stats_and_comparison(self):
        res = self.result
        card1 = pygame.Rect(CENTER_X + 26, 470, CENTER_W - 52, 95)
        pygame.draw.rect(self.screen, PANEL_BG, card1, border_radius=14)
        pygame.draw.rect(self.screen, LINE, card1, 1, border_radius=14)

        acts_str = " -> ".join(res["actions"]) if (res and res["found"] and res["actions"]) else (
            "0 bước (Đã sạch)" if (res and res["found"]) else "—"
        )
        algo_col = CYAN if self.algo == "BFS" else (PURPLE if self.algo == "DFS" else GOLD)

        items = [
            ("Thuật toán", self.algo, algo_col),
            ("Node duyệt", f"{self.idx} / {len(res['expanded'])}" if res else "—", TEXT),
            ("Số hành động", f"{len(res['actions'])} bước" if (res and res["found"]) else "—", GREEN),
            ("Tổng Chi phí", f"{res['total_cost']}" if (res and res["found"]) else "—", GOLD),
        ]
        col_w = (card1.w - 20) // len(items)
        for idx, (label, val, col) in enumerate(items):
            cx = card1.x + 10 + col_w * idx + col_w // 2
            self.draw_text(label, (cx, card1.y + 18), self.f_small, MUTED, True)
            self.draw_text(val, (cx, card1.y + 42), self.f_head, col, True)

        pygame.draw.line(self.screen, LINE, (card1.x + 16, card1.y + 64), (card1.right - 16, card1.y + 64), 1)
        self.draw_text(f"Chuỗi hành động:  {acts_str}", (card1.centerx, card1.y + 79), self.f_small, TEXT, True)

        # Bảng so sánh 3 thuật toán: BFS, DFS, UCS
        card2 = pygame.Rect(CENTER_X + 26, 576, CENTER_W - 52, 152)
        pygame.draw.rect(self.screen, PANEL_BG, card2, border_radius=14)
        pygame.draw.rect(self.screen, LINE, card2, 1, border_radius=14)
        self.draw_text("SO SÁNH 3 THUẬT TOÁN: BFS vs DFS vs UCS (TRÊN MÔI TRƯỜNG NÀY)",
                       (card2.x + 18, card2.y + 11), self.f_head, TEXT)

        col_3w = (card2.w - 48) // 3
        algos = [
            ("BFS", CYAN, CYAN_BG, "Queue (Ít bước nhất)"),
            ("DFS", PURPLE, PURPLE_BG, "Stack (Theo nhánh sâu)"),
            ("UCS", GOLD, GOLD_BG, "Priority (Tối ưu Chi phí)"),
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
                plan = " -> ".join(data["actions"]) if data["actions"] else "0 bước"
                self.draw_text(f"• {plan}", (bx + 10, by + 84), self.f_tiny, MUTED)
            else:
                self.draw_text("Chưa chạy thử.", (bx + 10, by + 58), self.f_small, MUTED)

    def draw_right(self):
        pygame.draw.rect(self.screen, PANEL_BG, (RIGHT_X, 0, RIGHT_W, WINDOW_H))
        pygame.draw.line(self.screen, LINE, (RIGHT_X, 0), (RIGHT_X, WINDOW_H), 2)

        self.draw_text("CÁC NODE & BƯỚC GIẢI", (RIGHT_X + 20, 22), self.f_title, PURPLE)
        self.draw_text("Lăn chuột để xem lịch sử duyệt & hành động", (RIGHT_X + 20, 52), self.f_small, MUTED)

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
                    self.draw_text(sub, (card.x + 12, card.y + 27), self.f_small, TEXT)
            else:
                bg = GREEN_BG if hl else ((18, 38, 56) if is_latest else CARD_BG)
                border = GREEN if hl else (CYAN if is_latest else LINE)
                pygame.draw.rect(self.screen, bg, card, border_radius=9)
                pygame.draw.rect(self.screen, border, card, 2 if (hl or is_latest) else 1, border_radius=9)

                draw_mini_rooms(self.screen, st, card.x + 10, card.y + 7, self.f_tiny, hl)
                self.draw_text(title, (card.x + 82, card.y + 6), self.f_head, GREEN if hl else TEXT)
                self.draw_text(sub, (card.x + 82, card.y + 27), self.f_small, MUTED)
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
        """Vòng lặp khi chạy độc lập."""
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
    app = VacuumApp()
    app.run()
