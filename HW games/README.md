# AI Search Lab — 8-Puzzle & Vacuum World
Trực quan hóa thuật toán tìm kiếm không gian trạng thái trong Trí tuệ Nhân tạo với giao diện Dark Theme hiện đại trên Pygame.

---

## 📁 Cấu trúc thư mục (HW games)

```text
d:\UTE\AI\HW games\
├── common/                  # Các thành phần giao diện & tiện ích chung
│   ├── __init__.py
│   └── ui.py                # Bảng màu Dark Mode, Anti-aliasing, Button, Slider, Typography
│
├── puzzle8/                 # Module Bài toán 8-Puzzle (Trượt số 3×3)
│   ├── __init__.py
│   ├── solver.py            # Thuật toán BFS, DFS, UCS (Tách biệt logic thuật toán)
│   └── app.py               # Giao diện Pygame 3 panel, animation mượt mà, so sánh 3 thuật toán
│
├── vacuum/                  # Module Bài toán Thế giới máy hút bụi (Vacuum World 2 phòng A & B)
│   ├── __init__.py
│   ├── solver.py            # Thuật toán BFS, DFS, UCS (Tách biệt logic thuật toán)
│   └── app.py               # Giao diện Pygame robot LED, vortex hút bụi, so sánh trực quan
│
├── menu.py                  # Màn hình Menu chọn game (2 Card tương tác hiệu ứng phát sáng)
├── main.py                  # File chạy chính kết nối toàn bộ hệ thống
├── run.bat                  # Script khởi chạy 1-click tiện lợi
└── requirements.txt         # Thư viện yêu cầu (pygame)
```

---

## 🚀 Cách khởi chạy

Mở terminal hoặc PowerShell tại thư mục `d:\UTE\AI\HW games`:

### Cách 1: Chạy file tiện ích (Khuyên dùng)
Double click vào file `run.bat` hoặc gõ trong terminal:
```powershell
.\run.bat
```

### Cách 2: Chạy trực tiếp bằng Python
```powershell
# Chạy với Python 3.12 (nơi đã cài pygame):
& "C:\Users\trong\AppData\Local\Programs\Python\Python312\python.exe" main.py

# Hoặc nếu python trong terminal đã nhận thư viện pygame:
python main.py
```

---

## 🧠 Các thuật toán đã triển khai

| Thuật toán | Cấu trúc dữ liệu | Mục tiêu tối ưu | Tính chất |
| :--- | :--- | :--- | :--- |
| **BFS** (Breadth-First Search) | Hàng đợi (Queue FIFO) | Số bước đi ít nhất ($d$) | Hoàn chỉnh, tối ưu về số bước |
| **DFS** (Depth-First Search) | Ngăn xếp (Stack LIFO) | Đi sâu theo nhánh | Giới hạn độ sâu để tránh chu trình |
| **UCS** (Uniform Cost Search) | Hàng đợi ưu tiên (Priority Queue) | **Tổng chi phí nhỏ nhất ($g(n)$)** | Tối ưu về chi phí tích lũy |

### Quy định chi phí (Action Costs):
1. **8-Puzzle:**
   - Trượt **Trái (Left)** / **Phải (Right)**: $\text{cost} = 2$
   - Trượt **Lên (Up)** / **Xuống (Down)**: $\text{cost} = 1$
   - *Đặc điểm:* UCS sẽ ưu tiên trượt theo chiều dọc (chi phí 1) trước chiều ngang (chi phí 2), đảm bảo tổng chi phí đến đích là thấp nhất.

2. **Vacuum World:**
   - Hành động **Hút bụi (Suck)**: $\text{cost} = 2$
   - Hành động **Sang trái (Left)** / **Sang phải (Right)**: $\text{cost} = 1$
   - *Đặc điểm:* Khi ưu tiên di chuyển trước hút bụi, DFS đi vòng 4 bước tốn chi phí 6; trong khi BFS và UCS chọn chuỗi hành động 3 bước tối ưu với chi phí 5.

---