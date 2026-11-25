## 1. Yêu cầu cài đặt & Khởi chạy

### Cài đặt thư viện:
```powershell
pip install pygame
```

### Khởi chạy chương trình:
Chạy bằng Python 3.12 (khuyên dùng lệnh `py` trên Windows):

- **Bài 1 — 8-Puzzle (Trượt số 3×3):**
  ```powershell
  cd d:\UTE\AI
  py puzzle8.py
  ```

- **Bài 2 — Vacuum World (Máy hút bụi 2 phòng A & B):**
  ```powershell
  cd d:\UTE\AI
  py vacuum.py
  ```

## 2. Lý thuyết và Áp dụng Thuật toán

### Bài toán 1: 8-Puzzle
- **Không gian trạng thái:** Hoán vị của 9 ô ($9! / 2 = 181.440$ trạng thái giải được).
- **BFS (Queue - FIFO):** Luôn tìm ra đường đi ngắn nhất (ít bước trượt nhất) để đưa bàn cờ về trạng thái đích `(1, 2, 3, 4, 5, 6, 7, 8, _)`.
- **DFS (Stack - LIFO có Depth Limit):** Đi sâu vào một nhánh cho tới khi chạm giới hạn độ sâu thì quay lui (Backtracking). Lời giải thường dài hơn BFS (ví dụ: BFS giải 12 bước thì DFS giải 22–24 bước).

### Bài toán 2: Vacuum World (2 phòng A, B)
- **Không gian trạng thái:** 8 trạng thái `(Vị trí Robot, Tình trạng phòng A, Tình trạng phòng B)`.
- **Hành động:** `Suck` (Hút bụi), `Left` (Sang trái), `Right` (Sang phải).
- **Thứ tự ưu tiên hành động:** Mặc định ưu tiên `Suck` trước giúp cả BFS và DFS giải quyết ngay phòng đang đứng trước khi di chuyển, cho ra lời giải tối ưu `Suck -> Right -> Suck` (3 bước) chỉ sau khi duyệt 4–6 node.
