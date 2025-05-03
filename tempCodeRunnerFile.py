class MazeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Ensure spawn_timer is created here
        self.spawn_timer = QTimer(self)
        self.dog_spawn_time = 5000  # Example time

       # Initialize footstep sound with QMediaPlayer
        self.step_player = QMediaPlayer(self)
        step_audio_output = QAudioOutput(self)  # Create a separate QAudioOutput for step_player
        self.step_player.setAudioOutput(step_audio_output)

        # Set footstep sound source (MP3)
        self.step_player.setSource(QUrl.fromLocalFile("C:/TTNT_MazeGame/music/footstep.mp3"))

        # Initialize dog appearance sound with QMediaPlayer
        self.appear_dog = QMediaPlayer(self)
        dog_audio_output = QAudioOutput(self)  # Create a separate QAudioOutput for appear_dog
        self.appear_dog.setAudioOutput(dog_audio_output)

        # Set dog appearance sound source (MP3)
        self.appear_dog.setSource(QUrl.fromLocalFile("C:/TTNT_MazeGame/music/wolf-howling.mp3"))

        # Cài đặt kích thước mê cung và hình ảnh
        self.maze_size = 21
        self.maze = []
        self.wall_image = QPixmap("C:/TTNT_MazeGame/image/wall.png")
        self.player_images = {
            "up": QImage("C:/TTNT_MazeGame/image/actor_up.png"),
            "down": QImage("C:/TTNT_MazeGame/image/actor_down.png"),
            "left": QImage("C:/TTNT_MazeGame/image/actor_left.png"),
            "right": QImage("C:/TTNT_MazeGame/image/actor_right.png"),
        }
        self.current_player_image = self.player_images["right"]  # Mặc định là hướng phải

        self.goal_image = QPixmap("C:/TTNT_MazeGame/image/goal.png")
        self.start_image = QPixmap("C:/TTNT_MazeGame/image/start.png")
        self.cell_size = 30

        self.dog_images = {
            "up": QImage("C:/TTNT_MazeGame/image/dog_up.png"),
            "down": QImage("C:/TTNT_MazeGame/image/dog_down.png"),
            "left": QImage("C:/TTNT_MazeGame/image/dog_left.png"),
            "right": QImage("C:/TTNT_MazeGame/image/dog_right.png"),
        }
        self.dog_image = self.dog_images["down"]  # Mặc định là hướng xuống

        self.dog_pos = None  # Vị trí ban đầu của con chó

        # Tạo mê cung và đặt vị trí người chơi
        self.create_and_draw_maze(self.maze_size)
        self.player_pos = [1, 0]
        self.setFocus()  # Đảm bảo widget nhận sự kiện bàn phím

    def spawn_dog(self):

        # Lấy vị trí ngẫu nhiên trong mê cung (có thể thay đổi theo yêu cầu)
        row, col = random.randint(1, self.maze_size-2), random.randint(1, self.maze_size-2)
        while self.maze[row][col] != 1:  # Ensure it's not a wall
            row, col = random.randint(1, self.maze_size-2), random.randint(1, self.maze_size-2)

        self.dog_pos = [row, col]  # Lưu vị trí con chó.
        self.update()  # Vẽ lại mê cung sau khi con chó được spawn.

        self.update_dog_path()
    
    def update_dog_path(self):
        if self.dog_pos:
            self.find_path(self.dog_pos[0], self.dog_pos[1])  # Find path from dog's current position to player's position

    def find_path(self, row, col):
        player_goal = self.player_pos
        start = (row, col)
        goal = (player_goal[0], player_goal[1])
        path = self.a_star(start, goal)

        if path:
            # Di chuyển con chó qua từng bước của con đường
            def move_dog(path_steps, index=0):
                if index < len(path_steps):
                    # Lấy vị trí hiện tại và vị trí tiếp theo
                    current_pos = list(path_steps[index])
                    next_pos = list(path_steps[index + 1]) if index + 1 < len(path_steps) else current_pos
                    
                    # Cập nhật vị trí con chó
                    self.dog_pos = current_pos
                    self.update()  # Vẽ lại mê cung và con chó
                    
                    # Xác định hướng di chuyển và chọn ảnh phù hợp
                    if next_pos[0] < current_pos[0]:
                        self.dog_image = self.dog_images["up"]
                    elif next_pos[0] > current_pos[0]:
                        self.dog_image = self.dog_images["down"]
                    elif next_pos[1] < current_pos[1]:
                        self.dog_image = self.dog_images["left"]
                    elif next_pos[1] > current_pos[1]:
                        self.dog_image = self.dog_images["right"]
                    
                    # Đặt độ trễ cho mỗi bước di chuyển
                    QTimer.singleShot(500, lambda: move_dog(path_steps, index + 1))  # 300ms delay giữa các bước

            # Bắt đầu di chuyển con chó qua từng bước
            move_dog(path)

        else:
            print("No path available for the dog.")


    def set_dog_spawn_time(self, time):
        self.dog_spawn_time = time
        self.spawn_timer.setInterval(self.dog_spawn_time)
        # Trigger the dog spawn once based on the level's spawn time
        self.spawn_timer.singleShot(self.dog_spawn_time, self.spawn_dog)

    # Hàm heuristic: Tính khoảng cách Manhattan
    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    # A* tìm đường đi từ start_pos đến goal_pos
    def a_star(self, start_pos, goal_pos):
        open_list = PriorityQueue()
        counter = 0  # Bộ đếm để phân biệt thứ tự các phần tử
        open_list.put((0, counter, start_pos))
        counter += 1
        came_from = {}
        g_score = {start_pos: 0}
        f_score = {start_pos: self.manhattan_distance(start_pos, goal_pos)}
        
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
                if 0 <= neighbor[0] < len(self.maze) and 0 <= neighbor[1] < len(self.maze[0]):
                    if self.maze[neighbor[0]][neighbor[1]] not in (1, 2, 3):
                        continue
                    tentative_g_score = g_score[current] + 1
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + self.manhattan_distance(neighbor, goal_pos)
                        counter += 1
                        open_list.put((f_score[neighbor], counter, neighbor))
        
        print("Không tìm thấy đường đi!")
        return None
    
    def reset_dog_movement(self, spawn_time):
        # Dừng tất cả các hành động di chuyển của con chó cũ
        self.spawn_timer.stop()  # Dừng timer nếu có
        
        # Xóa vị trí con chó hiện tại và đặt lại hình ảnh mặc định
        self.dog_pos = None
        self.dog_image = self.dog_images["down"]  # Mặc định là hướng xuống
        
        # Cập nhật lại giao diện sau khi reset
        self.update()

        # Gọi lại phương thức spawn_dog để con chó xuất hiện lại từ đầu
        self.set_dog_spawn_time(spawn_time)

        # Phát lại âm thanh khi con chó xuất hiện
        self.appear_dog.play()

        # Đảm bảo con chó bắt đầu di chuyển từ đầu sau khi spawn lại
        self.spawn_dog()


    def create_and_draw_maze(self, size):
        self.maze = self.generate_maze(size)
        self.update()  # Gọi lại paintEvent để vẽ mê cung

    def generate_maze(self, size):
        # Khởi tạo mê cung
        maze = [[0 for _ in range(size)] for _ in range(size)]
        
        # Gía trị 1: lối đi, 0: tường
        # Bao quanh mê cung bằng tường (giá trị 0)
        for i in range(size):
            maze[0][i] = 0  # Hàng trên cùng
            maze[size - 1][i] = 0  # Hàng dưới cùng
            maze[i][0] = 0  # Cột bên trái
            maze[i][size - 1] = 0  # Cột bên phải

        # Điểm bắt đầu mê cung
        start = (1, 0)
        stack = [start]
        maze[start[1]][start[0]] = 1

        # duyệt mê cung bằng dfs
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while stack:
            x, y = stack[-1]
            random.shuffle(directions)
            moved = False
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 1 <= nx < size - 1 and 1 <= ny < size - 1 and maze[ny][nx] == 0:
                    count = sum(
                        maze[ny + dy2][nx + dx2] == 1
                        for dx2, dy2 in directions
                        if 0 <= nx + dx2 < size and 0 <= ny + dy2 < size
                    )
                    if count <= 1:
                        maze[ny][nx] = 1
                        stack.append((nx, ny))
                        moved = True
                        break
            if not moved:
                stack.pop()

        # Đặt điểm bắt đầu
        maze[1][0] = 2  # Start
        maze[0][1] = 0
        
        # Đặt điểm kết thúc tại hàng cuối (size - 1)
        end_row = size - 1
        for col in range(size - 2, 0, -1):  # Duyệt từ phải qua trái
            if maze[end_row - 1][col] == 1:  # Kiểm tra ô phía trên là lối đi
                maze[end_row][col] = 3  # Đặt điểm kết thúc
                break

        return maze

    def resizeEvent(self, event):
        self.cell_size = min(self.width() // self.maze_size, self.height() // self.maze_size)
        self.update()

    def paintEvent(self, event):
        if not self.maze:
            return

        painter = QPainter(self)
        painter.setPen(QPen(Qt.GlobalColor.white, 2, Qt.PenStyle.SolidLine))

        for row in range(self.maze_size):
            for col in range(self.maze_size):
                x = col * self.cell_size
                y = row * self.cell_size
                
                if self.maze[row][col] == 0:  # Wall
                    painter.drawPixmap(x, y, self.cell_size, self.cell_size, self.wall_image)
                elif self.maze[row][col] == 2:  # Start
                    painter.drawPixmap(x, y, self.cell_size, self.cell_size, self.start_image)
                elif self.maze[row][col] == 3:  # End
                    painter.drawPixmap(x, y, self.cell_size, self.cell_size, self.goal_image)

        # Vẽ người chơi
        scaled_image = self.current_player_image.scaled(
            self.cell_size, self.cell_size,
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        player_x = self.player_pos[1] * self.cell_size + (self.cell_size - scaled_image.width()) // 2
        player_y = self.player_pos[0] * self.cell_size + (self.cell_size - scaled_image.height()) // 2
        painter.drawImage(player_x, player_y, scaled_image)

        # Vẽ con chó (nếu có)
        if self.dog_pos:
            # Lấy hình ảnh của con chó theo hướng hiện tại
            dog_image = self.dog_image  # Corrected here

            # Scale the dog image to fit the cell size
            scaled_dog_image = dog_image.scaled(
                self.cell_size, self.cell_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            dog_x = self.dog_pos[1] * self.cell_size + (self.cell_size - scaled_dog_image.width()) // 2
            dog_y = self.dog_pos[0] * self.cell_size + (self.cell_size - scaled_dog_image.height()) // 2
            painter.drawImage(dog_x, dog_y, scaled_dog_image)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            self.current_player_image = self.player_images["up"]
            self.move_player(0, -1)
            self.update_dog_path()
        elif event.key() == Qt.Key.Key_Down:
            self.current_player_image = self.player_images["down"]
            self.move_player(0, 1)
            self.update_dog_path()
        elif event.key() == Qt.Key.Key_Left:
            self.current_player_image = self.player_images["left"]
            self.move_player(-1, 0)
            self.update_dog_path()
        elif event.key() == Qt.Key.Key_Right:
            self.current_player_image = self.player_images["right"]
            self.move_player(1, 0)
            self.update_dog_path()
    
    def move_player(self, dx, dy):
        new_pos = [self.player_pos[0] + dy, self.player_pos[1] + dx]
        if self.is_valid_move(new_pos[0], new_pos[1]):
            self.player_pos = new_pos
            self.update()
            
            # Play the footstep sound using QMediaPlayer
            self.step_player.play()

    def is_valid_move(self, row, col):
        if row < 0 or col < 0 or row >= len(self.maze) or col >= len(self.maze[row]):
            return False
        return self.maze[row][col] in (1, 2, 3)
