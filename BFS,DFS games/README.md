# Bài tập Lớn AI — 8-Puzzle & Vacuum World (Pygame Dark Mode)

Dự án mô phỏng và trực quan hóa 2 bài toán tìm kiếm không gian trạng thái kinh điển trong môn **Trí tuệ Nhân tạo (AI)** bằng Python & Pygame với giao diện **Dark Theme**, hỗ trợ **High-DPI** sắc nét và bố cục 3 Panel trực quan.

---

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

---

## 2. Bố cục giao diện 3 Panel (Giao diện Dark Theme)

Cả hai ứng dụng đều được thiết kế theo bố cục 3 cột hiện đại:

1. **Panel Trái (Bảng điều khiển):**
   - Chọn thuật toán: **BFS (Queue)** hoặc **DFS (Stack)**.
   - Nút chỉnh tốc độ mô phỏng (Slider từ Chậm đến Nhanh).
   - Nút **Bắt đầu chạy**, **Tạm dừng / Tiếp tục**, **Đặt lại**.
   - Cấu hình chuyên biệt:
     - Ở **8-Puzzle**: Chỉnh số bước trộn ngẫu nhiên và giới hạn độ sâu (Depth Limit) cho DFS.
     - Ở **Vacuum World**: Chuyển đổi ưu tiên hành động (**Ưu tiên Suck trước** / **Ưu tiên di chuyển L/R trước**), đổi phòng xuất phát, tạo phòng ngẫu nhiên.

2. **Panel Giữa (Khu vực chính mô phỏng game):**
   - **8-Puzzle:** Bàn cờ 3×3 với hiệu ứng trượt ô số mượt mà (`ease-out cubic`). Ô số nào đã về đúng vị trí đích sẽ sáng màu xanh ngọc. Hỗ trợ click chuột trực tiếp để tự chơi thử.
   - **Vacuum World:** Hai phòng thí nghiệm A & B với hành lang nối. Robot có ăng-ten, mắt LED, hiệu ứng chùm lốc xoáy xanh neon và hạt bụi bị hút thu nhỏ xoáy vào miệng robot, bung hiệu ứng lấp lánh (sparkles) khi phòng sạch.
   - Thống kê thời gian thực & **Bảng so sánh trực tiếp BFS vs DFS** trên cùng trạng thái ban đầu.

3. **Panel Phải (Lịch sử các Node & Bước giải):**
   - Hiển thị danh sách các Node được mở rộng trong quá trình tìm kiếm kèm ảnh thu nhỏ của trạng thái.
   - Khi tìm thấy đích, hiển thị chi tiết từng bước hành động của lời giải.
   - Tự động cuộn xuống dưới, hỗ trợ dùng con lăn chuột để xem lại lịch sử.

---

## 3. Lý thuyết và Áp dụng Thuật toán

### 🧩 Bài toán 1: 8-Puzzle
- **Không gian trạng thái:** Hoán vị của 9 ô ($9! / 2 = 181.440$ trạng thái giải được).
- **BFS (Queue - FIFO):** Luôn tìm ra đường đi ngắn nhất (ít bước trượt nhất) để đưa bàn cờ về trạng thái đích `(1, 2, 3, 4, 5, 6, 7, 8, _)`.
- **DFS (Stack - LIFO có Depth Limit):** Đi sâu vào một nhánh cho tới khi chạm giới hạn độ sâu thì quay lui (Backtracking). Lời giải thường dài hơn BFS (ví dụ: BFS giải 12 bước thì DFS giải 22–24 bước).

### 🧹 Bài toán 2: Vacuum World (2 phòng A, B)
- **Không gian trạng thái:** 8 trạng thái `(Vị trí Robot, Tình trạng phòng A, Tình trạng phòng B)`.
- **Hành động:** `Suck` (Hút bụi), `Left` (Sang trái), `Right` (Sang phải).
- **Thứ tự ưu tiên hành động:** Mặc định ưu tiên `Suck` trước giúp cả BFS và DFS giải quyết ngay phòng đang đứng trước khi di chuyển, cho ra lời giải tối ưu `Suck -> Right -> Suck` (3 bước) chỉ sau khi duyệt 4–6 node.
