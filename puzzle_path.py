import sys
import random
from algorithm import greedy_best_first_search, a_star
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
from PyQt6.uic import loadUi
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QSoundEffect
from PyQt6.QtGui import QPainter, QPixmap, QImage, QPen
from PyQt6.QtCore import Qt, QUrl, QTimer
import os
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"

class MazeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.dog_movement_timer = None
        # Ensure spawn_timer is created here
        self.spawn_timer = QTimer(self)
        self.dog_spawn_time = 5000  # Example time
        
        self.game_over = False  # Thêm biến trạng thái game_over
        
        self.hint_path = []  # Lưu đường dẫn gợi ý

        self.player_history = []  # Lịch sử vị trí người chơi

       # Initialize footstep sound with QMediaPlayer
        self.step_player = QMediaPlayer(self)
        step_audio_output = QAudioOutput(self)  # Create a separate QAudioOutput for step_player
        self.step_player.setAudioOutput(step_audio_output)
        # Set footstep sound source (MP3)
        self.step_player.setSource(QUrl.fromLocalFile("music\\footstep.mp3"))

        # Initialize dog appearance sound with QMediaPlayer
        self.appear_dog = QMediaPlayer(self)
        dog_audio_output = QAudioOutput(self)  # Create a separate QAudioOutput for appear_dog
        self.appear_dog.setAudioOutput(dog_audio_output)
        # Set dog appearance sound source (MP3)
        self.appear_dog.setSource(QUrl.fromLocalFile("music\\wolf-howling.mp3"))

        # Khởi tạo âm thanh thắng
        self.win_sound = QMediaPlayer(self)
        win_audio_output = QAudioOutput(self)
        self.win_sound.setAudioOutput(win_audio_output)
        self.win_sound.setSource(QUrl.fromLocalFile("music\\game_win.mp3"))

        # Khởi tạo âm thanh thua
        self.lose_sound = QMediaPlayer(self)
        lose_audio_output = QAudioOutput(self)
        self.lose_sound.setAudioOutput(lose_audio_output)
        self.lose_sound.setSource(QUrl.fromLocalFile("music\\game_over.mp3"))

        # Cài đặt kích thước mê cung và hình ảnh
        self.maze_size = 21
        self.maze = []
        self.wall_image = QPixmap("image\\wall.png")
        self.player_images = {
            "up": QImage("image\\actor_up.png"),
            "down": QImage("image\\actor_down.png"),
            "left": QImage("image\\actor_left.png"),
            "right": QImage("image\\actor_right.png"),
        }
        self.current_player_image = self.player_images["right"]  # Mặc định là hướng phải

        self.goal_image = QPixmap("image\\goal.png")
        self.start_image = QPixmap("image\\start.png")
        self.cell_size = 30

        self.dog_images = {
            "up": QImage("image\\dog_up.png"),
            "down": QImage("image\\dog_down.png"),
            "left": QImage("image\\dog_left.png"),
            "right": QImage("image\\dog_right.png"),
        }
        self.dog_image = self.dog_images["down"]  # Mặc định là hướng xuống

        self.dog_pos = None  # Vị trí ban đầu của con chó

        # Tạo mê cung và đặt vị trí người chơi
        self.create_and_draw_maze(self.maze_size)
        self.player_pos = [1, 0]
        self.setFocus()  # Đảm bảo widget nhận sự kiện bàn phím

    def spawn_dog(self):
        # Lấy vị trí ngẫu nhiên trong mê cung mà người chơi đã đi qua
        if not self.player_history:
            # Nếu chưa có lịch sử, chọn vị trí bắt đầu mặc định
            self.dog_pos = [1, 1]
        else:
            # Chọn ngẫu nhiên một vị trí từ lịch sử người chơi
            row, col = random.choice(self.player_history)
            self.dog_pos = [row, col]

        # Phát âm thanh khi con chó xuất hiện (khi spawn_dog được gọi)
        self.appear_dog.play()
        
        self.update()  # Vẽ lại mê cung sau khi con chó được spawn.

        self.update_dog_path()
    
    def update_dog_path(self):
        if self.dog_pos and not self.game_over:
            self.find_path(self.dog_pos[0], self.dog_pos[1])  # Find path from dog's current position to player's position

    def find_path(self, row, col):
        if self.game_over:  # Không tìm đường nếu trò chơi đã kết thúc
            return
    
        player_goal = self.player_pos
        start = (row, col)
        goal = (player_goal[0], player_goal[1])
        path = a_star(self.maze, self.maze_size, start, goal)

        if path:
            # Dừng tiến trình di chuyển cũ nếu đang chạy
            if self.dog_movement_timer:
                self.dog_movement_timer.stop()
                self.dog_movement_timer.deleteLater()
                self.dog_movement_timer = None

            # Di chuyển con chó qua từng bước của con đường
            def move_dog(path_steps, index=0):
                if index < len(path_steps) and not self.game_over:
                    # Lấy vị trí hiện tại và vị trí tiếp theo
                    current_pos = list(path_steps[index])
                    next_pos = list(path_steps[index + 1]) if index + 1 < len(path_steps) else current_pos
                    
                    # Cập nhật vị trí con chó
                    self.dog_pos = current_pos
                    self.update()  # Vẽ lại mê cung và con chó
                    
                    if self.dog_pos == self.player_pos:
                        self.gameOver()
                        return
                    
                    # Xác định hướng di chuyển và chọn ảnh phù hợp
                    if next_pos[0] < current_pos[0]:
                        self.dog_image = self.dog_images["up"]
                    elif next_pos[0] > current_pos[0]:
                        self.dog_image = self.dog_images["down"]
                    elif next_pos[1] < current_pos[1]:
                        self.dog_image = self.dog_images["left"]
                    elif next_pos[1] > current_pos[1]:
                        self.dog_image = self.dog_images["right"]
                    
                    # Tạo tiến trình mới cho bước tiếp theo
                    self.dog_movement_timer = QTimer(self)
                    self.dog_movement_timer.setSingleShot(True)
                    self.dog_movement_timer.timeout.connect(lambda: move_dog(path_steps, index + 1))
                    self.dog_movement_timer.start(1000)  # 1000ms delay giữa các bước
                else:
                    self.dog_movement_timer = None  # Reset timer khi hoàn thành di chuyển

            # Bắt đầu di chuyển con chó qua từng bước
            move_dog(path)
        else:
            print("No path available for the dog.")

    def set_dog_spawn_time(self, time):
        self.dog_spawn_time = time
        self.spawn_timer.setInterval(self.dog_spawn_time)
        # Trigger the dog spawn once based on the level's spawn time
        self.spawn_timer.singleShot(self.dog_spawn_time, self.spawn_dog)

    def reset_dog_movement(self, spawn_time):
        self.game_over = False  # Đặt lại trạng thái game_over khi reset
        
        # 1. Dừng và xóa timer di chuyển của con chó
        if self.dog_movement_timer:
            self.dog_movement_timer.stop()
            self.dog_movement_timer.deleteLater()
            self.dog_movement_timer = None

        # 2. Dừng và xóa spawn_timer (nếu đang chạy)
        if self.spawn_timer:
            self.spawn_timer.stop()
            self.spawn_timer.deleteLater()
            self.spawn_timer = None

        # 3. Xóa trạng thái và hình ảnh con chó
        self.dog_pos = None
        self.dog_image = self.dog_images["down"]  # Hình ảnh mặc định
        self.update()  # Vẽ lại giao diện

        # 4. Tạo lại spawn_timer và đặt lại thời gian spawn
        self.spawn_timer = QTimer(self)
        self.spawn_timer.setSingleShot(True)  # Chỉ chạy một lần
        self.spawn_timer.timeout.connect(self.spawn_dog)
        self.spawn_timer.start(spawn_time)  # Đặt thời gian spawn

    def create_and_draw_maze(self, size):
        self.maze = self.generate_maze(size)
        self.update()  # Gọi lại paintEvent để vẽ mê cung

    def generate_maze(self, size):
        # Khởi tạo mê cung
        maze = [[0 for _ in range(size)] for _ in range(size)]
        
        # Giá trị 1: lối đi, 0: tường
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

        # Vẽ đường dẫn gợi ý (nếu có)
        if self.hint_path:
            painter.setPen(QPen(Qt.GlobalColor.yellow, 5, Qt.PenStyle.SolidLine))
            for i in range(len(self.hint_path) - 1):
                start_pos = self.hint_path[i]
                end_pos = self.hint_path[i + 1]
                start_x = start_pos[1] * self.cell_size + self.cell_size // 2
                start_y = start_pos[0] * self.cell_size + self.cell_size // 2
                end_x = end_pos[1] * self.cell_size + self.cell_size // 2
                end_y = end_pos[0] * self.cell_size + self.cell_size // 2
                painter.drawLine(start_x, start_y, end_x, end_y)
        
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
        if self.game_over:  # Không xử lý phím nếu trò chơi đã kết thúc
            return
        
        if event.key() == Qt.Key.Key_Up:
            self.current_player_image = self.player_images["up"]
            self.move_player(0, -1)
        elif event.key() == Qt.Key.Key_Down:
            self.current_player_image = self.player_images["down"]
            self.move_player(0, 1)
        elif event.key() == Qt.Key.Key_Left:
            self.current_player_image = self.player_images["left"]
            self.move_player(-1, 0)
        elif event.key() == Qt.Key.Key_Right:
            self.current_player_image = self.player_images["right"]
            self.move_player(1, 0)
        
        self.update_dog_path()
    
    def move_player(self, dx, dy):
        new_pos = [self.player_pos[0] + dy, self.player_pos[1] + dx]
        if self.is_valid_move(new_pos[0], new_pos[1]):
            self.player_pos = new_pos
            self.player_history.append(tuple(self.player_pos))  # Lưu vị trí vào lịch sử
            self.update()
            
            # Play the footstep sound using QMediaPlayer
            self.step_player.play()
            
            # Kiểm tra xem người chơi có đến đích không
            if self.maze[self.player_pos[0]][self.player_pos[1]] == 3:
                self.win_game()

    def is_valid_move(self, row, col):
        if row < 0 or col < 0 or row >= len(self.maze) or col >= len(self.maze[row]):
            return False
        return self.maze[row][col] in (1, 2, 3)
    
    def toggle_hint(self, checked):
        if checked and not self.game_over:
            # Tính đường dẫn gợi ý từ player_pos đến đích
            start = tuple(self.player_pos)
            goal = None
            # Tìm vị trí đích
            for row in range(self.maze_size):
                for col in range(self.maze_size):
                    if self.maze[row][col] == 3:  # Đích
                        goal = (row, col)
                        break
                if goal:
                    break
            if goal:
                self.hint_path = greedy_best_first_search(self.maze, self.maze_size, start, goal)
            else:
                self.hint_path = []  # Không tìm thấy đích
        else:
            self.hint_path = []  # Xóa đường dẫn gợi ý khi tắt
        self.update()  # Vẽ lại để hiển thị/xóa gợi ý
    
    def gameOver(self):
        self.game_over = True  # Đặt trạng thái game_over
        if self.dog_movement_timer:
            self.dog_movement_timer.stop()
            self.dog_movement_timer.deleteLater()
            self.dog_movement_timer = None
        if self.spawn_timer:
            self.spawn_timer.stop()
            self.spawn_timer.deleteLater()
            self.spawn_timer = None   
            
        # Phát âm thanh thắng
        self.lose_sound.play() 
            
        # Gọi hàm hiển thị Game Over từ MyWindow
        main_window = self.window()  # Lấy QMainWindow (MyWindow)
        if isinstance(main_window, MyWindow):
            main_window.show_game_over()
    
    def win_game(self):
        self.game_over = True  # Ngăn người chơi di chuyển
        if self.dog_movement_timer:
            self.dog_movement_timer.stop()
            self.dog_movement_timer.deleteLater()
            self.dog_movement_timer = None
        if self.spawn_timer:
            self.spawn_timer.stop()
            self.spawn_timer.deleteLater()
            self.spawn_timer = None
            
        # Phát âm thanh thắng
        self.win_sound.play()
        
        # Gọi hàm hiển thị Win từ MyWindow
        main_window = self.window()
        if isinstance(main_window, MyWindow):
            main_window.show_win_game()
    
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("ui\\start.ui", self)

        # Thiết lập âm thanh nền
        self.player = QMediaPlayer(self)
        audio_output = QAudioOutput(self)
        self.player.setAudioOutput(audio_output)

        audio_url = QUrl.fromLocalFile("music\\game_music.mp3")
        self.player.setSource(audio_url)
        self.player.play()

        # Kết nối tín hiệu statusChanged để kiểm tra khi nào âm thanh kết thúc
        self.player.mediaStatusChanged.connect(self.handle_media_status_changed)

        self.btnStart.clicked.connect(self.change_ui_des)  # Kết nối nút start
        self.maze_size = 21  # Kích thước mặc định của mê cung (sẽ thay đổi theo lựa chọn)

        # Lưu trữ trạng thái âm nhạc
        self.music_playing = True

        # Set volume through QAudioOutput
        audio_output.setVolume(0.3)  # Adjust volume (value from 0.0 to 1.0)

    def change_ui_des(self):
        # Tạo một widget mới từ description.ui
        new_widget = QWidget(self)
        # Tải và hiển thị giao diện của description.ui vào widget mới
        loadUi("ui\\description.ui", new_widget)

        # Kết nối nút Next với hành động chuyển qua UI của level
        btn_next = new_widget.findChild(QPushButton, "btnNext")
        if btn_next:
            btn_next.clicked.connect(self.change_ui_level)  # Chuyển qua UI của level

        # Đặt widget mới làm widget trung tâm của QMainWindow
        self.setCentralWidget(new_widget)

    def change_ui_level(self):
        # Xóa widget Game Over nếu tồn tại
        if hasattr(self, 'game_over_widget') and self.game_over_widget:
            self.game_over_widget.hide()
            self.game_over_widget.deleteLater()
            self.game_over_widget = None
            
        # Xóa widget Win
        if hasattr(self, 'win_game_widget') and self.win_game_widget:
            self.win_game_widget.hide()
            self.win_game_widget.deleteLater()
            self.win_game_widget = None

        # Xóa centralWidget cũ nếu tồn tại
        if self.centralWidget():
            self.centralWidget().deleteLater()
        
        # Tạo một widget mới từ level.ui
        new_widget = QWidget(self)
        loadUi("ui\\level.ui", new_widget)

        # Gắn sự kiện cho từng nút
        btn_easy = new_widget.findChild(QPushButton, "btnEasy")
        btn_medium = new_widget.findChild(QPushButton, "btnMedium")
        btn_hard = new_widget.findChild(QPushButton, "btnHard")
        btn_expert = new_widget.findChild(QPushButton, "btnExpert")

        if btn_easy:
            btn_easy.clicked.connect(lambda: self.start_game_with_level(21))
        if btn_medium:
            btn_medium.clicked.connect(lambda: self.start_game_with_level(31))
        if btn_hard:
            btn_hard.clicked.connect(lambda: self.start_game_with_level(41))
        if btn_expert:
            btn_expert.clicked.connect(lambda: self.start_game_with_level(51))

        # Tìm nút btnBack
        self.btnBack = new_widget.findChild(QPushButton, "btnBack")
        self.btnBack.clicked.connect(self.change_ui_des)

        self.setCentralWidget(new_widget)
        self.update()

    def handle_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.player.play()  # Phát lại nhạc khi kết thúc

    def toggle_music(self):
        if self.music_playing:
            self.player.pause()  # Tạm dừng nhạc
        else:
            self.player.play()  # Phát nhạc
        self.music_playing = not self.music_playing  # Đảo trạng thái nhạc

    def start_game_with_level(self, maze_size):
        # Xóa widget Game Over nếu tồn tại
        if hasattr(self, 'game_over_widget') and self.game_over_widget:
            self.game_over_widget.hide()
            self.game_over_widget.deleteLater()
            self.game_over_widget = None
            
        # Xóa widget Win
        if hasattr(self, 'win_game_widget') and self.win_game_widget:
            self.win_game_widget.hide()
            self.win_game_widget.deleteLater()
            self.win_game_widget = None

        # Xóa centralWidget cũ nếu tồn tại
        if self.centralWidget():
            self.centralWidget().deleteLater()
            
        self.maze_size = maze_size  # Lưu kích thước mê cung
        spawn_time = 0  # Default spawn time

        # Set spawn time for each level
        if self.maze_size == 21:  # Easy level
            spawn_time = 5000  # 5 seconds
        elif self.maze_size == 31:  # Medium level
            spawn_time = 6000  # 6 seconds
        elif self.maze_size == 41:  # Hard level
            spawn_time = 7000  # 7 seconds
        elif self.maze_size == 51:  # Expert level
            spawn_time = 8000  # 8 seconds

        # Pass the spawn time to the maze widget
        self.change_ui(spawn_time)  # Modify to pass spawn_time to the UI change

    def change_ui(self, spawn_time):
        # Tạo một widget mới từ main.ui
        new_widget = QWidget(self)
        loadUi("ui\\main.ui", new_widget)

        # Tìm mazeWidgetPlaceholder trong main.ui
        maze_widget_placeholder = new_widget.findChild(QWidget, "mazeWidget")
        if not maze_widget_placeholder:
            raise RuntimeError("Widget 'mazeWidget' không tồn tại trong main.ui!")

        # Tạo MazeWidget với kích thước tương ứng
        maze_widget = MazeWidget(maze_widget_placeholder)
        maze_widget.maze_size = self.maze_size  # Gán kích thước mê cung
        maze_widget.create_and_draw_maze(self.maze_size)  # Tạo mê cung
        maze_widget.setGeometry(0, 0, maze_widget_placeholder.width(), maze_widget_placeholder.height())
        maze_widget.show()

        # Pass spawn time to MazeWidget
        maze_widget.set_dog_spawn_time(spawn_time)

        # Đảm bảo widget được vẽ lại
        self.update()

        # Tìm nút btnMusic
        self.btnMusic = new_widget.findChild(QPushButton, "btnMusic")
        if not self.btnMusic:
            raise RuntimeError("btnMusic không được tìm thấy trong main.ui!")
        else:
            self.btnMusic.clicked.connect(self.toggle_music)
            self.btnMusic.clicked.connect(lambda: maze_widget.setFocus())

        # Tìm nút btnBack
        self.btnBack = new_widget.findChild(QPushButton, "btnBack")
        self.btnBack.clicked.connect(self.change_ui_level)

        # Tìm nút btnReNew
        self.btnReNew = new_widget.findChild(QPushButton, "btnReNew")
        if self.btnReNew:
            self.btnReNew.clicked.connect(lambda: self.recreate_maze(maze_widget, spawn_time))
            self.btnReNew.clicked.connect(lambda: maze_widget.setFocus())
            
        # Tìm nút btnHint
        self.btnHint = new_widget.findChild(QPushButton, "btnHint")
        if self.btnHint:
            self.btnHint.clicked.connect(lambda checked: maze_widget.toggle_hint(checked))
            self.btnHint.clicked.connect(lambda: maze_widget.setFocus())

        self.setCentralWidget(new_widget)
    
    def recreate_maze(self, maze_widget, spawn_time):
        if not isinstance(maze_widget, MazeWidget):
            raise ValueError("Provided widget is not a valid MazeWidget instance.")
        
        maze_widget.create_and_draw_maze(maze_widget.maze_size)

        maze_widget.player_pos = [1, 0]
        
        # Xóa đường dẫn gợi ý
        maze_widget.hint_path = []  # Xóa hint_path
        if hasattr(self, 'btnHint') and self.btnHint:
            self.btnHint.setChecked(False)  # Tắt nút btnHint

        maze_widget.update()
        # Cập nhật lại hướng nhân vật
        maze_widget.current_player_image = maze_widget.player_images["right"]  # Ví dụ, hướng ban đầu là "right"

        maze_widget.reset_dog_movement(spawn_time)
        
    def show_game_over(self):
        self.game_over_widget = QWidget(self)
        loadUi("ui\\Gameover.ui", self.game_over_widget)
        
        # Căn giữa widget trên cửa sổ chính
        main_window_rect = self.contentsRect()
        widget_rect = self.game_over_widget.contentsRect()
        widget_rect.moveCenter(main_window_rect.center())
        self.game_over_widget.setGeometry(widget_rect)
        
        # Kết nối các nút
        btn_continue = self.game_over_widget.findChild(QPushButton, "btnContinue")
        btn_new_level = self.game_over_widget.findChild(QPushButton, "btnNewLevel")

        if btn_continue:
            btn_continue.clicked.connect(lambda: self.start_game_with_level(self.maze_size))
        if btn_new_level:
            btn_new_level.clicked.connect(self.change_ui_level)
            
        # Vô hiệu hóa các nút bên dưới
        if hasattr(self, 'btnMusic'):
            self.btnMusic.setEnabled(False)
        if hasattr(self, 'btnBack'):
            self.btnBack.setEnabled(False)
        if hasattr(self, 'btnHint'):
            self.btnHint.setEnabled(False)
        if hasattr(self, 'btnReNew'):
            self.btnReNew.setEnabled(False)
        
        self.game_over_widget.show()
        
    def show_win_game(self):
        self.win_game_widget = QWidget(self)
        loadUi("ui\\win.ui", self.win_game_widget)
        
        # Căn giữa widget trên cửa sổ chính
        main_window_rect = self.contentsRect()
        widget_rect = self.win_game_widget.contentsRect()
        widget_rect.moveCenter(main_window_rect.center())
        self.win_game_widget.setGeometry(widget_rect)
        
        # Kết nối các nút
        btn_continue = self.win_game_widget.findChild(QPushButton, "btnContinue")
        btn_new_level = self.win_game_widget.findChild(QPushButton, "btnNewLevel")

        if btn_continue:
            btn_continue.clicked.connect(lambda: self.start_game_with_level(self.maze_size))
        if btn_new_level:
            btn_new_level.clicked.connect(self.change_ui_level)
            
        # Vô hiệu hóa các nút bên dưới
        if hasattr(self, 'btnMusic'):
            self.btnMusic.setEnabled(False)
        if hasattr(self, 'btnBack'):
            self.btnBack.setEnabled(False)
        if hasattr(self, 'btnHint'):
            self.btnHint.setEnabled(False)
        if hasattr(self, 'btnReNew'):
            self.btnReNew.setEnabled(False)
        
        self.win_game_widget.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
