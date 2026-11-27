"""
VACUUM WORLD (2 phòng A, B) — Thuật toán tìm kiếm không gian trạng thái:
- BFS (Breadth-First Search - Hàng đợi Queue)
- DFS (Depth-First Search - Ngăn xếp Stack)
- UCS (Uniform Cost Search - Hàng đợi ưu tiên Priority Queue)

Quy định chi phí bước đi (Action Costs):
- Hút bụi (Suck): cost = 2
- Sang trái (Left) / Sang phải (Right): cost = 1
"""
import heapq
import time
from collections import deque

ACTION_ORDERS = {
    "suck_first": ("Suck", "Left", "Right"),
    "move_first": ("Left", "Right", "Suck"),
}

ACTION_COSTS = {
    "Suck": 2,
    "Left": 1,
    "Right": 1,
}

ACTION_VI = {
    "Suck": "Hút bụi (Suck)",
    "Left": "Sang trái (Left)",
    "Right": "Sang phải (Right)",
}


def goal_test(state):
    """Đích: cả 2 phòng đều sạch (bụi_A = 0 và bụi_B = 0)."""
    return state[1] == 0 and state[2] == 0


def get_next_state(state, action):
    """Hàm chuyển trạng thái Result(s, a)."""
    pos, dust_a, dust_b = state
    if action == "Left":
        return (0, dust_a, dust_b)
    if action == "Right":
        return (1, dust_a, dust_b)
    # Suck
    if pos == 0:
        return (0, 0, dust_b)
    return (1, dust_a, 0)


def calculate_cost(actions):
    """Tính tổng chi phí theo chuỗi hành động."""
    return sum(ACTION_COSTS.get(a, 1) for a in actions)


def reconstruct(parent, goal_state, expanded, found, t0):
    """Truy vết chuỗi trạng thái và hành động từ đích ngược về ban đầu."""
    path, actions = [], []
    if found and goal_state is not None:
        cur = goal_state
        while cur is not None:
            path.append(cur)
            info = parent[cur]
            if info is None:
                break
            actions.append(info[1])
            cur = info[0]
        path.reverse()
        actions.reverse()
    total_cost = calculate_cost(actions)
    return {
        "expanded": expanded,
        "path": path,
        "actions": actions,
        "total_cost": total_cost,
        "found": found,
        "time": time.time() - t0,
    }


def bfs(start, actions_order=ACTION_ORDERS["suck_first"]):
    """BFS: Hàng đợi Queue -> tìm chuỗi hành động có SỐ BƯỚC ÍT NHẤT."""
    t0 = time.time()
    parent = {start: None}
    queue = deque([(start, 0)])
    expanded = []

    while queue:
        state, depth = queue.popleft()
        expanded.append((state, depth))
        if goal_test(state):
            return reconstruct(parent, state, expanded, True, t0)

        for act in actions_order:
            nxt = get_next_state(state, act)
            if nxt not in parent:
                parent[nxt] = (state, act)
                queue.append((nxt, depth + 1))

    return reconstruct(parent, None, expanded, False, t0)


def dfs(start, actions_order=ACTION_ORDERS["suck_first"]):
    """DFS: Ngăn xếp Stack -> đi sâu theo nhánh hành động ưu tiên."""
    t0 = time.time()
    parent = {}
    stack = [(start, 0, None)]
    expanded = []

    while stack:
        state, depth, p_info = stack.pop()
        if state in parent:
            continue
        parent[state] = p_info
        expanded.append((state, depth))
        if goal_test(state):
            return reconstruct(parent, state, expanded, True, t0)

        for act in reversed(actions_order):
            nxt = get_next_state(state, act)
            if nxt not in parent:
                stack.append((nxt, depth + 1, (state, act)))

    return reconstruct(parent, None, expanded, False, t0)


def ucs(start, actions_order=ACTION_ORDERS["suck_first"]):
    """
    UCS (Uniform Cost Search):
    - Hàng đợi ưu tiên (Priority Queue qua heapq).
    - Luôn mở rộng nút có TỔNG CHI PHÍ g(n) NHỎ NHẤT (với Suck=2, Left/Right=1).
    - Đảm bảo tìm ra chuỗi hành động có TỔNG CHI PHÍ THẤP NHẤT.
    """
    t0 = time.time()
    counter = 0
    pq = [(0, counter, start)]
    cost_so_far = {start: 0}
    parent = {start: None}  # state -> (parent_state, action)
    expanded = []

    while pq:
        current_cost, _, s = heapq.heappop(pq)
        if current_cost > cost_so_far.get(s, float("inf")):
            continue

        expanded.append((s, current_cost))
        if goal_test(s):
            return reconstruct(parent, s, expanded, True, t0)

        for act in actions_order:
            step_cost = ACTION_COSTS[act]
            nxt = get_next_state(s, act)
            new_cost = current_cost + step_cost
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                parent[nxt] = (s, act)
                counter += 1
                heapq.heappush(pq, (new_cost, counter, nxt))

    return reconstruct(parent, None, expanded, False, t0)
