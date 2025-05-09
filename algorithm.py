from heapq import heappush, heappop
import random
from queue import PriorityQueue

def manhattan_distance(pos1, pos2):
    """Tính khoảng cách Manhattan giữa hai điểm."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def greedy_best_first_search(maze, maze_size, start, goal):
    """Tìm đường từ start đến goal bằng Greedy Best-First Search."""
    frontier = []
    heappush(frontier, (manhattan_distance(start, goal), start))
    came_from = {start: None}
    visited = set()

    while frontier:
        _, current = heappop(frontier)
        if current == goal:
            # Tái tạo đường dẫn
            path = []
            while current is not None:
                path.append(current)
                current = came_from[current]
            return path[::-1]  # Đảo ngược đường dẫn

        visited.add(current)
        row, col = current

        # Kiểm tra các láng giềng (lên, xuống, trái, phải)
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            next_row, next_col = row + dr, col + dc
            next_pos = (next_row, next_col)
            if (0 <= next_row < maze_size and
                0 <= next_col < maze_size and
                next_pos not in visited and
                maze[next_row][next_col] in (1, 3)):  # Đường đi hoặc đích
                heappush(frontier, (manhattan_distance(next_pos, goal), next_pos))
                came_from[next_pos] = current

    return []  # Không tìm thấy đường dẫn

def a_star(maze, maze_size, start_pos, goal_pos):
    """Tìm đường từ start_pos đến goal_pos bằng thuật toán A*."""
    open_list = PriorityQueue()
    counter = 0  # Bộ đếm để phân biệt thứ tự các phần tử
    open_list.put((0, counter, start_pos))
    counter += 1
    came_from = {}
    g_score = {start_pos: 0}
    f_score = {start_pos: manhattan_distance(start_pos, goal_pos)}
    
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while not open_list.empty():
        _, _, current = open_list.get()
        if current == goal_pos:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
        
        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < maze_size and 0 <= neighbor[1] < maze_size:
                if maze[neighbor[0]][neighbor[1]] not in (1, 2, 3):
                    continue
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + manhattan_distance(neighbor, goal_pos)
                    counter += 1
                    open_list.put((f_score[neighbor], counter, neighbor))
    
    print("Không tìm thấy đường đi!")
    return None

def q_learning(maze, maze_size, start, goal, episodes = 1000):
    q_table = {}
    learning_rate = 0.1
    discount_factor = 0.9
    epsilon = 0.1
    actions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    def is_valid_move(pos):
        row, col = pos
        if row < 0 or col < 0 or row >= maze_size or col >= maze_size:
            return False
        return maze[row][col] in (1, 2, 3)
    
    def get_reward(pos):
        row, col = pos
        if row < 0 or col < 0 or row >= maze_size or col >= maze_size:
            return -10
        if maze[row][col] == 0:
            return -10
        if maze[row][col] == 3:
            return 100
        return -1
    # Huấn luyện Q-table qua nhiều episode
    for episode in range(episodes):
        current_pos = start
        epsilon = max(0.01, epsilon * 0.995)  # Giảm epsilon theo thời gian

        while current_pos != goal:
            current_state = current_pos
            if current_state not in q_table:
                q_table[current_state] = {a: 0 for a in actions}

            # Chọn hành động (epsilon-greedy)
            if random.random() < epsilon:
                action = random.choice(actions)
            else:
                action = max(q_table[current_state], key=q_table[current_state].get)
            # Trong quá trình học, policy này thay đổi dần theo q-table nên không cố định

            # Thực hiện hành động
            dx, dy = action
            next_pos = (current_pos[0] + dy, current_pos[1] + dx)
            reward = get_reward(next_pos)

            # Cập nhật Q-table
            next_state = next_pos if is_valid_move(next_pos) else current_pos
            if next_state not in q_table:
                q_table[next_state] = {a: 0 for a in actions}
            
            current_q = q_table[current_state][action]
            max_next_q = max(q_table[next_state].values())
            new_q = current_q + learning_rate * (
                reward + discount_factor * max_next_q - current_q
            )
            q_table[current_state][action] = new_q

            # Di chuyển đến trạng thái tiếp theo nếu hợp lệ
            if is_valid_move(next_pos):
                current_pos = next_pos

            # Thoát nếu đến đích
            if current_pos == goal:
                break
    # Tái tạo đường đi sử dụng Q-table
    path = [start]
    current_pos = start
    visited = set([start])
    max_steps = maze_size * maze_size  # Giới hạn bước để tránh vòng lặp vô hạn

    while current_pos != goal and len(path) < max_steps:
        if current_pos not in q_table:
            return []  # Không tìm thấy đường đi
        action = max(q_table[current_pos], key=q_table[current_pos].get) #ở đây là policy, chọn hành động có q-value cao nhất
        dx, dy = action
        next_pos = (current_pos[0] + dy, current_pos[1] + dx)
        if not is_valid_move(next_pos) or next_pos in visited:
            return []  # Không tìm thấy đường đi
        path.append(next_pos)
        visited.add(next_pos)
        current_pos = next_pos

    if current_pos == goal:
        return path
    return []  # Không tìm thấy đường đi