"""
8-PUZZLE — Thuật toán tìm kiếm không gian trạng thái:
- BFS (Breadth-First Search - Hàng đợi Queue)
- DFS (Depth-First Search - Ngăn xếp Stack có giới hạn độ sâu)
- UCS (Uniform Cost Search - Hàng đợi ưu tiên Priority Queue)

Quy định chi phí bước đi (Action Costs):
- Trái (Left) / Phải (Right): cost = 2
- Lên (Up) / Xuống (Down): cost = 1
"""
import heapq
import random
import time
from collections import deque

GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)

# (Tên hành động, delta_r, delta_c, cost)
# Ô trống trượt Lên/Xuống cost=1; Trái/Phải cost=2
MOVES = (
    ("Lên", -1, 0, 1),
    ("Xuống", 1, 0, 1),
    ("Trái", 0, -1, 2),
    ("Phải", 0, 1, 2),
)

ACTION_COSTS = {
    "Lên": 1,
    "Xuống": 1,
    "Trái": 2,
    "Phải": 2,
}


def neighbors(state):
    """Sinh các (hành_động, trạng_thái_mới, chi_phí_bước) khi trượt ô trống."""
    z = state.index(0)
    r, c = divmod(z, 3)
    for name, dr, dc, cost in MOVES:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            n_idx = nr * 3 + nc
            lst = list(state)
            lst[z], lst[n_idx] = lst[n_idx], lst[z]
            yield name, tuple(lst), cost


def is_solvable(state):
    """Kiểm tra tính giải được dựa trên số cặp nghịch thế (inversions)."""
    arr = [x for x in state if x != 0]
    inv = sum(1 for i in range(len(arr)) for j in range(i + 1, len(arr)) if arr[i] > arr[j])
    return inv % 2 == 0


def calculate_cost(actions):
    """Tính tổng chi phí theo chuỗi hành động."""
    return sum(ACTION_COSTS.get(a, 1) for a in actions)


def build_result(parent, expanded, found, t0):
    """Truy vết chuỗi trạng thái và hành động từ GOAL ngược về xuất phát."""
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
    total_cost = calculate_cost(actions)
    return {
        "expanded": expanded,
        "path": states,
        "actions": actions,
        "total_cost": total_cost,
        "found": found,
        "time": time.time() - t0,
    }


def bfs(start):
    """
    BFS (Breadth-First Search):
    - Hàng đợi (Queue - FIFO).
    - Luôn tìm ra đường đi có SỐ BƯỚC ÍT NHẤT.
    """
    t0 = time.time()
    parent = {start: None}
    queue = deque([(start, 0)])
    expanded = []

    while queue:
        s, d = queue.popleft()
        expanded.append((s, d))
        if s == GOAL:
            return build_result(parent, expanded, True, t0)
        for act, nxt, _ in neighbors(s):
            if nxt not in parent:
                parent[nxt] = (s, act)
                queue.append((nxt, d + 1))

    return build_result(parent, expanded, False, t0)


def dfs(start, limit=25, cap=250000):
    """
    DFS (Depth-First Search):
    - Ngăn xếp (Stack - LIFO) có Giới hạn độ sâu (Depth Limit).
    - Cắm sâu theo một nhánh ngẫu nhiên tới khi chạm ngõ cụt thì quay lui.
    """
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

        for act, nxt, _ in reversed(list(neighbors(s))):
            nd = d + 1
            if nxt not in best_depth or best_depth[nxt] > nd:
                best_depth[nxt] = nd
                parent[nxt] = (s, act)
                stack.append((nxt, nd))

    return build_result(parent, expanded, False, t0)


def ucs(start):
    """
    UCS (Uniform Cost Search):
    - Hàng đợi ưu tiên (Priority Queue / Min-Heap qua heapq).
    - Luôn mở rộng nút có TỔNG CHI PHÍ g(n) NHỎ NHẤT.
    - Đảm bảo tìm ra đường đi có TỔNG CHI PHÍ TỐI ƯU NHẤT (với Trái/Phải=2, Lên/Xuống=1).
    """
    t0 = time.time()
    counter = 0  # Tie-breaker để tránh so sánh tuple state khi cost bằng nhau
    pq = [(0, counter, start)]
    cost_so_far = {start: 0}
    parent = {start: None}  # state -> (parent_state, action)
    expanded = []

    while pq:
        current_cost, _, s = heapq.heappop(pq)

        # Bỏ qua nếu đã tìm thấy đường đi khác tới s với chi phí thấp hơn
        if current_cost > cost_so_far.get(s, float("inf")):
            continue

        expanded.append((s, current_cost))
        if s == GOAL:
            return build_result(parent, expanded, True, t0)

        for act, nxt, step_cost in neighbors(s):
            new_cost = current_cost + step_cost
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                parent[nxt] = (s, act)
                counter += 1
                heapq.heappush(pq, (new_cost, counter, nxt))

    return build_result(parent, expanded, False, t0)


def shuffle_state(n_moves):
    """Trộn bàn cờ bằng cách trượt ngẫu nhiên từ GOAL -> đảm bảo 100% giải được."""
    s, prev = GOAL, None
    for _ in range(n_moves):
        opts = [nxt for _, nxt, _ in neighbors(s) if nxt != prev]
        prev, s = s, random.choice(opts)
    return s if s != GOAL else shuffle_state(n_moves)
