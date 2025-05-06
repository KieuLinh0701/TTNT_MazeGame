from heapq import heappush, heappop
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