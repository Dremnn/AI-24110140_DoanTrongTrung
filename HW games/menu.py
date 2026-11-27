"""
MENU CHÍNH — Trình chọn Game và Thuật toán AI (Pygame Dark Mode)
"""
import sys
import pygame
from common.ui import (
    WINDOW_W, WINDOW_H, BG, PANEL_BG, CARD_BG, LINE, TEXT, MUTED,
    CYAN, CYAN_BG, PURPLE, PURPLE_BG, GOLD, GOLD_BG, GREEN, GREEN_BG,
    AMBER, AMBER_BG, RED,
    Button, load_font, draw_aa_circle, draw_aa_ellipse
)


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.f_hero = load_font(34, "bold")
        self.f_sub = load_font(16, "regular")
        self.f_title = load_font(22, "bold")
        self.f_head = load_font(16, "semibold")
        self.f_body = load_font(14, "regular")
        self.f_small = load_font(13, "regular")
        self.f_tiny = load_font(12, "semibold")
        self.f_btn = load_font(16, "bold")

        # Kích thước 2 thẻ Game
        card_w, card_h = 560, 480
        gap = 48
        x0 = (WINDOW_W - (card_w * 2 + gap)) // 2
        y0 = 150

        self.rect_p8 = pygame.Rect(x0, y0, card_w, card_h)
        self.rect_vac = pygame.Rect(x0 + card_w + gap, y0, card_w, card_h)

        self.btn_p8 = Button((x0 + 40, y0 + card_h - 76, card_w - 80, 50),
                             "CHƠI 8-PUZZLE  ▶", CYAN, CYAN_BG)
        self.btn_vac = Button((x0 + card_w + gap + 40, y0 + card_h - 76, card_w - 80, 50),
                              "CHƠI VACUUM WORLD  ▶", GREEN, GREEN_BG)

        self.hover_p8 = False
        self.hover_vac = False
        self.time_sec = 0.0

    def draw_text(self, s, pos, font, color=TEXT, center=False):
        img = font.render(s, True, color)
        rect = img.get_rect(center=pos) if center else img.get_rect(topleft=pos)
        self.screen.blit(img, rect)

    def draw_p8_preview(self, cx, cy):
        """Vẽ biểu tượng thu nhỏ của 8-Puzzle."""
        size = 108
        r0 = pygame.Rect(cx - size // 2, cy - size // 2, size, size)
        pygame.draw.rect(self.screen, (20, 26, 36), r0, border_radius=12)
        pygame.draw.rect(self.screen, CYAN if self.hover_p8 else LINE, r0, 2, border_radius=12)

        cell = size / 3.0
        sample = [1, 2, 3, 8, 0, 4, 7, 6, 5]
        font = self.f_tiny
        for i, val in enumerate(sample):
            r, c = divmod(i, 3)
            cell_rect = pygame.Rect(int(r0.x + c * cell + 3), int(r0.y + r * cell + 3),
                                    int(cell - 6), int(cell - 6))
            if val != 0:
                bg = (16, 68, 50) if val in (1, 2, 3) else (35, 45, 60)
                edge = (52, 211, 153) if val in (1, 2, 3) else (70, 85, 110)
                pygame.draw.rect(self.screen, bg, cell_rect, border_radius=4)
                pygame.draw.rect(self.screen, edge, cell_rect, 1, border_radius=4)
                lbl = font.render(str(val), True, (255, 255, 255))
                self.screen.blit(lbl, lbl.get_rect(center=cell_rect.center))

    def draw_vac_preview(self, cx, cy):
        """Vẽ biểu tượng thu nhỏ của Vacuum Robot & 2 phòng."""
        w, h = 180, 80
        rx, ry = cx - w // 2, cy - h // 2

        # 2 phòng thu nhỏ
        for i in range(2):
            box = pygame.Rect(rx + i * 94, ry, 86, h)
            pygame.draw.rect(self.screen, (20, 32, 28) if i == 0 else (44, 30, 18), box, border_radius=8)
            col = GREEN if i == 0 else AMBER
            pygame.draw.rect(self.screen, col, box, 1, border_radius=8)
            self.draw_text(f"Phòng {'AB'[i]}", (box.x + 8, box.y + 6), self.f_tiny, col)

        # Robot nhỏ ở giữa phòng A
        bot_cx = rx + 43
        bot_cy = ry + 46
        draw_aa_circle(self.screen, CYAN, (bot_cx, bot_cy), 16)
        draw_aa_circle(self.screen, (255, 255, 255), (bot_cx - 4, bot_cy - 2), 3)
        draw_aa_circle(self.screen, (255, 255, 255), (bot_cx + 4, bot_cy - 2), 3)

        # Hạt bụi ở phòng B
        for bx, by in ((rx + 120, ry + 36), (rx + 150, ry + 48), (rx + 135, ry + 58)):
            draw_aa_circle(self.screen, AMBER, (bx, by), 4)

    def draw_card(self, rect, title, tag, tag_col, desc_lines, is_hover, border_glow):
        # Đổ bóng & nền card
        pygame.draw.rect(self.screen, (8, 12, 16), rect.move(0, 6), border_radius=20)
        pygame.draw.rect(self.screen, CARD_BG if is_hover else PANEL_BG, rect, border_radius=20)
        pygame.draw.rect(self.screen, border_glow if is_hover else LINE, rect, 2 if is_hover else 1, border_radius=20)

        # Badge tag
        badge_rect = pygame.Rect(rect.x + 36, rect.y + 28, 130, 28)
        pygame.draw.rect(self.screen, (tag_col[0] // 5, tag_col[1] // 5, tag_col[2] // 5), badge_rect, border_radius=14)
        pygame.draw.rect(self.screen, tag_col, badge_rect, 1, border_radius=14)
        self.draw_text(tag, badge_rect.center, self.f_tiny, tag_col, True)

        self.draw_text(title, (rect.x + 36, rect.y + 70), self.f_title, TEXT)

        # Các dòng mô tả tính năng
        for idx, line in enumerate(desc_lines):
            self.draw_text(line, (rect.x + 36, rect.y + 242 + idx * 24), self.f_body, MUTED)

    def draw(self):
        self.screen.fill(BG)

        # Header Hero
        cx = WINDOW_W // 2
        self.draw_text("TRỰC QUAN HÓA THUẬT TOÁN TÌM KIẾM AI", (cx, 46), self.f_hero, TEXT, True)
        self.draw_text("So sánh trực quan: BFS (Hàng đợi)  •  DFS (Ngăn xếp)  •  UCS (Chi phí tối ưu)",
                       (cx, 92), self.f_sub, CYAN, True)

        # 1. Card 8-Puzzle
        p8_lines = [
            "• Không gian trạng thái: 9! / 2 = 181.440 trạng thái.",
            "• BFS: Luôn tìm chuỗi trượt có số bước ít nhất.",
            "• DFS: Tìm kiếm theo chiều sâu với Depth Limit.",
            "• UCS: Chi phí Trái / Phải = 2, Lên / Xuống = 1.",
            "• Hoạt ảnh gạch số trượt mượt mà (ease-out cubic).",
        ]
        self.draw_card(self.rect_p8, "BÀI TOÁN 8-PUZZLE", "TRƯỢT SỐ 3×3", CYAN,
                       p8_lines, self.hover_p8, CYAN)
        self.draw_p8_preview(self.rect_p8.centerx, self.rect_p8.y + 168)
        self.btn_p8.draw(self.screen, self.f_btn)

        # 2. Card Vacuum World
        vac_lines = [
            "• Không gian trạng thái: 8 trạng thái mẫu kinh điển.",
            "• Môi trường 2 phòng thí nghiệm A & B và robot hút bụi.",
            "• BFS: Tìm chuỗi hành động có số bước ít nhất.",
            "• DFS: Tìm kiếm theo nhánh hành động ưu tiên.",
            "• UCS: Chi phí Hút bụi = 2, Di chuyển L / R = 1.",
            "• Hoạt ảnh lốc xoáy xanh neon hút bụi và phát sáng.",
        ]
        self.draw_card(self.rect_vac, "VACUUM WORLD", "ROBOT 2 PHÒNG", GREEN,
                       vac_lines, self.hover_vac, GREEN)
        self.draw_vac_preview(self.rect_vac.centerx, self.rect_vac.y + 168)
        self.btn_vac.draw(self.screen, self.f_btn)

        # Footer
        self.draw_text("Đồ án Trí tuệ Nhân tạo  •  Trường Đại học Sư phạm Kỹ thuật TP.HCM (HCMUTE)",
                       (cx, WINDOW_H - 44), self.f_small, MUTED, True)
        self.draw_text("Mẹo: Bấm ESC hoặc nút [⬅ Menu] trong khi chơi để quay lại Menu này bất cứ lúc nào.",
                       (cx, WINDOW_H - 22), self.f_tiny, (90, 105, 120), True)

    def handle_events(self):
        mpos = pygame.mouse.get_pos()
        self.hover_p8 = self.rect_p8.collidepoint(mpos)
        self.hover_vac = self.rect_vac.collidepoint(mpos)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.rect_p8.collidepoint(e.pos) or self.btn_p8.hit(e.pos):
                    return "PUZZLE8"
                if self.rect_vac.collidepoint(e.pos) or self.btn_vac.hit(e.pos):
                    return "VACUUM"
        return None

    def run_frame(self, dt):
        self.time_sec += dt
        action = self.handle_events()
        self.draw()
        pygame.display.flip()
        return action
