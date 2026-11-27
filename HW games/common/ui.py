"""
Module dùng chung cho các game: Khởi tạo High-DPI, Bảng màu Dark Mode,
Font chữ chuẩn Windows, và các Component UI (Button, Slider, Khử răng cưa).
"""
import ctypes
import os
import pygame
from pygame import gfxdraw

# Kích hoạt High-DPI Windows để chữ và nét vẽ nét 1:1, không bị kéo giãn mờ
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# Kích thước chuẩn cửa sổ
WINDOW_W = 1320
WINDOW_H = 750

LEFT_W = 300
RIGHT_W = 360
CENTER_X = LEFT_W
CENTER_W = WINDOW_W - LEFT_W - RIGHT_W
RIGHT_X = WINDOW_W - RIGHT_W

# Bảng màu Dark Theme Cyber / Obsidian
BG = (13, 17, 23)              # Nền chính đen chì
PANEL_BG = (22, 27, 34)        # Nền panel sẫm
CARD_BG = (30, 36, 46)         # Thẻ nổi
LINE = (48, 54, 61)            # Đường viền phân cách
TEXT = (240, 246, 252)         # Chữ trắng sáng
MUTED = (139, 148, 158)        # Chữ xám bạc

# Màu sắc thuật toán & trạng thái
CYAN = (56, 189, 248)          # BFS - Xanh lơ
CYAN_BG = (15, 38, 58)

PURPLE = (168, 85, 247)        # DFS - Tím neon
PURPLE_BG = (42, 22, 66)

GOLD = (250, 204, 21)          # UCS - Vàng ánh kim
GOLD_BG = (58, 48, 14)

GREEN = (52, 211, 153)         # Xanh ngọc phát quang / Đích
GREEN_BG = (16, 48, 36)

AMBER = (251, 191, 36)         # Vàng hổ phách
AMBER_BG = (58, 42, 14)

RED = (248, 113, 113)          # Đỏ cam (Reset / Cảnh báo)
RED_BG = (56, 20, 24)

# Hàm vẽ khử răng cưa mượt mà
def draw_aa_circle(surf, color, center, radius):
    x, y, r = int(center[0]), int(center[1]), int(radius)
    if r <= 0:
        return
    c = (color[0], color[1], color[2])
    gfxdraw.filled_circle(surf, x, y, r, c)
    gfxdraw.aacircle(surf, x, y, r, c)


def draw_aa_ellipse(surf, color, rect):
    x, y, w, h = int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3])
    rx, ry = max(1, w // 2), max(1, h // 2)
    cx, cy = x + rx, y + ry
    c = (color[0], color[1], color[2])
    gfxdraw.filled_ellipse(surf, cx, cy, rx, ry, c)
    gfxdraw.aaellipse(surf, cx, cy, rx, ry, c)


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


def ease_in_out(t):
    t = max(0.0, min(1.0, t))
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2


def ease_out_cubic(t):
    t = max(0.0, min(1.0, t))
    return 1.0 - pow(1.0 - t, 3)


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
    def __init__(self, rect, vmin, vmax, value, color=AMBER):
        self.rect = pygame.Rect(rect)
        self.vmin, self.vmax, self.value = vmin, vmax, value
        self.color = color
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
        pygame.draw.rect(surf, self.color, fill, border_radius=5)
        cx = int(self.rect.x + self.rect.w * t)
        draw_aa_circle(surf, self.color, (cx, self.rect.centery), 10)
        draw_aa_circle(surf, (255, 255, 255), (cx, self.rect.centery), 4)
