"""
CHƯƠNG TRÌNH CHÍNH — TRỰC QUAN HÓA THUẬT TOÁN TÌM KIẾM AI (Pygame Dark Mode)
Khởi chạy:
    cd "d:\\UTE\\AI\\HW games"
    python main.py (hoặc .\run.bat)

Hỗ trợ 2 bài toán kinh điển:
1. 8-Puzzle (Trượt số 3×3) — BFS, DFS, UCS (L/R=2, U/D=1)
2. Vacuum World (2 phòng A, B) — BFS, DFS, UCS (Suck=2, L/R=1)

Bấm ESC hoặc nút [⬅ Menu] để quay lại màn hình chọn game bất cứ lúc nào.
"""
import sys
import os

# Thêm thư mục gốc vào sys.path để các module import nhau dễ dàng
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import pygame
from common.ui import WINDOW_W, WINDOW_H
from menu import MainMenu
from puzzle8.app import Puzzle8App
from vacuum.app import VacuumApp


def main():
    pygame.init()
    pygame.display.set_caption("AI Search Lab — 8-Puzzle & Vacuum World (BFS • DFS • UCS)")
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()

    state = "MENU"  # "MENU" | "PUZZLE8" | "VACUUM"

    menu = MainMenu(screen)
    p8_app = None
    vac_app = None

    while True:
        dt = clock.tick(60) / 1000.0

        if state == "MENU":
            action = menu.run_frame(dt)
            if action == "PUZZLE8":
                p8_app = Puzzle8App(screen)
                state = "PUZZLE8"
            elif action == "VACUUM":
                vac_app = VacuumApp(screen)
                state = "VACUUM"

        elif state == "PUZZLE8":
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    state = "MENU"
                    break
                p8_app.speed.handle(e)
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    nav = p8_app.on_click(e.pos)
                    if nav == "MENU":
                        state = "MENU"
                        break
                if e.type == pygame.MOUSEWHEEL and pygame.mouse.get_pos()[0] > 960:
                    p8_app.scroll += e.y * 2

            if state == "PUZZLE8":
                p8_app.update(dt)
                p8_app.draw()
                pygame.display.flip()

        elif state == "VACUUM":
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    state = "MENU"
                    break
                vac_app.speed.handle(e)
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    nav = vac_app.on_click(e.pos)
                    if nav == "MENU":
                        state = "MENU"
                        break
                if e.type == pygame.MOUSEWHEEL and pygame.mouse.get_pos()[0] > 960:
                    vac_app.scroll += e.y * 2

            if state == "VACUUM":
                vac_app.update(dt)
                vac_app.draw()
                pygame.display.flip()


if __name__ == "__main__":
    main()
