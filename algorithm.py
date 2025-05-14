from queue import PriorityQueue
import random

def dfs(maze, size, start, goal):
    stack = [start]  
    cameFrom = {}  # Lưu lại đường đi
    visited = set()  # Theo dõi các ô đã thăm

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Các hướng di chuyển

    while stack:
        current = stack.pop()  # Lấy ra phần tử cuối cùng trong stack
        if current == goal:
            path = []
            while current in cameFrom:
                path.append(current)
                current = cameFrom[current]
            path.append(start)
            path.reverse()
            return path

        if current in visited:
            continue
        visited.add(current)  # Đánh dấu ô đã thăm

        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < size and 0 <= neighbor[1] < size:
                if maze[neighbor[0]][neighbor[1]] in (1, 2, 3):  # Chỉ di chuyển vào ô có lối đi
                    if neighbor not in visited:
                        cameFrom[neighbor] = current
                        stack.append(neighbor)  # Thêm hàng xóm vào stack để duyệt sau

    return None

def manhattan_distance(pos1, pos2):
    """Tính khoảng cách Manhattan giữa hai điểm."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def a_star(maze, mazeSize, start, goal):
    """Tìm đường từ start_pos đến goal_pos bằng thuật toán A*."""
    openList = PriorityQueue()
    counter = 0  # Bộ đếm để phân biệt thứ tự các phần tử
    openList.put((0, counter, start))
    counter += 1
    cameFrom = {}
    gScore = {start: 0}
    fScore = {start: manhattan_distance(start, goal)}
    
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    while not openList.empty():
        _, _, current = openList.get()
        if current == goal:
            path = []
            while current in cameFrom:
                path.append(current)
                current = cameFrom[current]
            path.append(start)
            path.reverse()
            return path
        
        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < mazeSize and 0 <= neighbor[1] < mazeSize:
                if maze[neighbor[0]][neighbor[1]] not in (1, 2, 3):
                    continue
                tentativeGScore = gScore[current] + 1
                if neighbor not in gScore or tentativeGScore < gScore[neighbor]:
                    cameFrom[neighbor] = current
                    gScore[neighbor] = tentativeGScore
                    fScore[neighbor] = tentativeGScore + manhattan_distance(neighbor, goal)
                    counter += 1
                    openList.put((fScore[neighbor], counter, neighbor))
    return None

def and_or_search(maze, maze_size, start_pos, goal_pos):
    """Tìm đường từ start_pos đến goal_pos bằng thuật toán And-Or Search."""
    def search(node, visited, came_from):
        if node == goal_pos:
            return [node]
        
        if node in visited:
            return None
        visited.add(node)
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            neighbor = (node[0] + dx, node[1] + dy)
            if 0 <= neighbor[0] < maze_size and 0 <= neighbor[1] < maze_size:
                if maze[neighbor[0]][neighbor[1]] in (1, 2, 3) and neighbor not in visited:
                    came_from[neighbor] = node
                    result = search(neighbor, visited, came_from)
                    if result:
                        result.append(node)
                        return result
        
        return None

    came_from = {}
    visited = set()
    path = search(start_pos, visited, came_from)
    
    if path:
        path.reverse()  # Đảo ngược để có đường đi từ start đến goal
        return path
    
    print("Không tìm thấy đường đi!")
    return None

def steepest_ascent_hill_climbing(maze, maze_size, start_pos, goal_pos):
    """Tìm đường từ start_pos đến goal_pos bằng thuật toán Steepest-Ascent Hill-Climbing."""
    current = start_pos
    came_from = {current: None}
    visited = set([current])
    stack = [current]  # Stack để backtrack
    
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    while current != goal_pos:
        neighbors = []
        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < maze_size and 0 <= neighbor[1] < maze_size:
                if maze[neighbor[0]][neighbor[1]] in (1, 2, 3) and neighbor not in visited:
                    neighbors.append(neighbor)
        
        if neighbors:
            # Chọn hàng xóm có heuristic tốt nhất
            best_neighbor = min(neighbors, key=lambda pos: manhattan_distance(pos, goal_pos))
            visited.add(best_neighbor)
            came_from[best_neighbor] = current
            current = best_neighbor
            stack.append(current)
        elif stack:  # Backtrack nếu không có hàng xóm hợp lệ
            stack.pop()  # Bỏ node hiện tại
            if stack:
                current = stack[-1]  # Quay lại node trước đó
            else:
                print("Không tìm thấy đường đi (bị kẹt)!")
                return None
        else:
            print("Không tìm thấy đường đi (bị kẹt)!")
            return None
    
    # Xây dựng đường đi
    path = [current]
    while current in came_from and came_from[current] is not None:
        current = came_from[current]
        path.append(current)
    path.reverse()
    
    return path

def backtracking(maze, maze_size, start_pos, goal_pos):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    path = []        # Lưu đường đi đúng (kết quả)
    visited = set()  # Ghi nhớ các ô đã đi qua để không bị lặp lại

    def is_valid(cell):
        """Kiểm tra ô có hợp lệ để đi không"""
        r, c = cell
        return (
            0 <= r < maze_size and 0 <= c < maze_size and
            maze[r][c] in (1, 2, 3) and                     
            cell not in visited                 
        )

    def backtrack(current):
        """Hàm đệ quy chính của thuật toán Backtracking"""
        if current == goal_pos:
            path.append(current)  # Thêm ô đích vào đường đi
            return True           # Đã đến đích, kết thúc

        visited.add(current)  # Đánh dấu đã đi qua
        path.append(current)  # Thêm vào đường đi hiện tại

        for dr, dc in directions:
            next_cell = (current[0] + dr, current[1] + dc)
            if is_valid(next_cell):
                if backtrack(next_cell):  # Đệ quy: thử đi tiếp
                    return True           # Nếu tìm được đường đi thì kết thúc luôn

        # Không đi được đâu → quay lui: loại ô hiện tại ra khỏi đường đi
        path.pop()
        visited.remove(current)
        return False

    # Bắt đầu tìm đường từ ô start_pos
    if backtrack(start_pos):
        return path  # Trả về đường đi đúng nếu tìm được
    else:
        print("Không tìm thấy đường đi với Backtracking.")
        return []  # Không có đường đi đến đích

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

import random