import sys
from algorithm import a_star, q_learning, dfs, and_or_search, steepest_ascent_hill_climbing, beam_search
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
from PyQt6.uic import loadUi
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtGui import QPainter, QPixmap, QImage, QPen, QColor
from PyQt6.QtCore import Qt, QUrl, QTimer

import os
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"

class MazeWidget(QWidget):
    def __init__(self, parent=None, map_index=0):
        super().__init__(parent)

        self.map_index =  map_index
        self.current_algorithm = None
        self.auto_solving = False  # Trạng thái tự động giải
        self.game_over = False  # Thêm biến trạng thái game_over
        
       # Initialize footstep sound with QMediaPlayer
        self.step_player = QMediaPlayer(self)
        step_audio_output = QAudioOutput(self)  # Create a separate QAudioOutput for step_player
        self.step_player.setAudioOutput(step_audio_output)
        # Set footstep sound source (MP3)
        self.step_player.setSource(QUrl.fromLocalFile("music\\footstep.mp3"))

        # Khởi tạo âm thanh thắng
        self.win_sound = QMediaPlayer(self)
        win_audio_output = QAudioOutput(self)
        self.win_sound.setAudioOutput(win_audio_output)
        self.win_sound.setSource(QUrl.fromLocalFile("music\\game_win.mp3"))

        # Cài đặt kích thước mê cung và hình ảnh
        self.maze_size = 25
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

        # Tạo mê cung và đặt vị trí người chơi
        self.create_and_draw_maze(self.map_index)
        self.player_pos = [1, 0]
        
        # Gọi auto_solve ngay sau khi mê cung được tạo
        QTimer.singleShot(500, self.auto_solve)  # Gọi sau 500ms để đảm bảo giao diện được load
        self.setFocus()

    def create_and_draw_maze(self, size):
        self.maze = self.generate_maze(map_index)
        self.update()  # Gọi lại paintEvent để vẽ mê cung

    def generate_maze(self, map_index):
        # Mặc định sẵn 3 mê cung
        maze_list = [
            [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [2, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0],
            [0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0],
            [0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
            [0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0],
            [0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0],
            [0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0],
            [0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0],
            [0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0],
            [0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0],
            [0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0],
            [0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0],
            [0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0],
            [0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0],
            [0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0],
            [0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0],
            [0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0],
            [0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0],
            [0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0]], # map 1
            
            [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [2, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0],
            [0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0],
            [0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0],
            [0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0],
            [0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0],
            [0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0],
            [0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0],
            [0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0],
            [0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0],
            [0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0],
            [0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0],
            [0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0],
            [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0],
            [0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0]], # map 2
            
            [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [2, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0],
            [0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
            [0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0],
            [0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0],
            [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0],
            [0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0],
            [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0],
            [0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0],
            [0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0]] # map 3
        ]

        selected_maze = maze_list[map_index]
        
        return selected_maze

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
                elif self.maze[row][col] == 1:  # W
                    painter.fillRect(x, y, self.cell_size, self.cell_size, QColor("#edb934"))
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

    def auto_solve(self):
        self.auto_solving = True  # Bắt đầu tự động giải
        start = tuple(self.player_pos)
        goal = None
        
        # Tìm vị trí đích (3)
        for row in range(self.maze_size):
            for col in range(self.maze_size):
                if self.maze[row][col] == 3:
                    goal = (row, col)
                    break
            if goal:
                break
        
        if not goal:
            print("Không tìm thấy đích.")
            return
        
        path = self.current_algorithm(self.maze, self.maze_size, start, goal)
        if not path:
            print("Không có đường đi đến đích.")
            return
        
        # Di chuyển người chơi theo đường đi
        self.move_player_along_path(path)        
    
    def move_player_along_path(self, path):
        # Di chuyển người chơi từng bước trên đường đi
        for i in range(len(path) - 1):
            if not self.auto_solving:  # Kiểm tra trạng thái dừng
                return

            current_pos = path[i]
            next_pos = path[i + 1]

            # Xác định hướng di chuyển
            dx = next_pos[1] - current_pos[1]  # Sự thay đổi theo cột (x)
            dy = next_pos[0] - current_pos[0]  # Sự thay đổi theo hàng (y)

            if dx == 1:  # Di chuyển sang phải
                self.current_player_image = self.player_images["right"]
            elif dx == -1:  # Di chuyển sang trái
                self.current_player_image = self.player_images["left"]
            elif dy == 1:  # Di chuyển xuống
                self.current_player_image = self.player_images["down"]
            elif dy == -1:  # Di chuyển lên
                self.current_player_image = self.player_images["up"]

            # Cập nhật vị trí người chơi
            self.player_pos = list(next_pos)

            self.step_player.play()

            # Vẽ lại giao diện
            self.update()
            QCoreApplication.processEvents()  # Cập nhật giao diện

            # Nghỉ giữa các bước
            QThread.msleep(300)  # 300ms giữa mỗi bước di chuyển

        # Đảm bảo người chơi đứng ở vị trí cuối cùng (đích)
        self.player_pos = list(path[-1])
        self.update()  # Vẽ lại lần cuối
        self.win_game()

    def stop_auto_solve(self):
        self.auto_solving = False  # Dừng tự động giải
    
    def win_game(self):
        self.game_over = True  # Ngăn người chơi di chuyển
            
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
        self.maze_size = 25  # Kích thước mặc định của mê cung
        self.map_index = 0

        # Lưu trữ trạng thái âm nhạc
        self.music_playing = True

        # Set volume through QAudioOutput
        audio_output.setVolume(0.3)  # Adjust volume (value from 0.0 to 1.0)

    def change_ui_map(self):
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
        btn_map1 = new_widget.findChild(QPushButton, "btnMap1")
        btn_map2 = new_widget.findChild(QPushButton, "btnMap2")
        btn_map3 = new_widget.findChild(QPushButton, "btnMap3")

        if btn_map1:
            btn_map1.clicked.connect(lambda: self.change_ui_algorithm(0))
        if btn_map2:
            btn_map2.clicked.connect(lambda: self.change_ui_algorithm(1))
        if btn_map3:
            btn_map3.clicked.connect(lambda: self.change_ui_algorithm(2))
    
        self.setCentralWidget(new_widget)
        self.update()

    def change_ui_algorithm(self, map_index):  
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
        loadUi("ui\\algorithm.ui", new_widget)
        
        self.map_index = map_index

        # Gắn sự kiện cho từng nút
        btn_Dfs = new_widget.findChild(QPushButton, "btnDfs")
        btn_AStar = new_widget.findChild(QPushButton, "btnAStar")
        btn_Aos = new_widget.findChild(QPushButton, "btnAos")
        btn_Sahc = new_widget.findChild(QPushButton, "btnSahc")
        btn_Backtracking = new_widget.findChild(QPushButton, "btnBacktracking")
        btn_QLearning = new_widget.findChild(QPushButton, "btnQLearning")

        if btn_Dfs:
            btn_Dfs.clicked.connect(lambda: self.start_game_with_level(dfs))
        if btn_AStar:
            btn_AStar.clicked.connect(lambda: self.start_game_with_level(a_star))
        if btn_Aos:
            btn_Aos.clicked.connect(lambda: self.start_game_with_level(and_or_search))
        if btn_Sahc:
            btn_Sahc.clicked.connect(lambda: self.start_game_with_level(steepest_ascent_hill_climbing))
        if btn_QLearning:
            btn_QLearning.clicked.connect(lambda: self.start_game_with_level(q_learning))

        # Tìm nút btnBack
        self.btnBack = new_widget.findChild(QPushButton, "btnBack")
        self.btnBack.clicked.connect(self.change_ui_map)

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

    def start_game_with_level(self, algorithm):
        # Xóa widget Win
        if hasattr(self, 'win_game_widget') and self.win_game_widget:
            self.win_game_widget.hide()
            self.win_game_widget.deleteLater()
            self.win_game_widget = None

        # Xóa centralWidget cũ nếu tồn tại
        if self.centralWidget():
            self.centralWidget().deleteLater()

        self.algorithm = algorithm

        # Pass the spawn time to the maze widget
        self.change_ui()

    def change_ui(self, spawn_time):
        # Tạo một widget mới từ main.ui
        new_widget = QWidget(self)
        loadUi("ui\\main.ui", new_widget)

        # Tìm mazeWidgetPlaceholder trong main.ui
        maze_widget_placeholder = new_widget.findChild(QWidget, "mazeWidget")
        if not maze_widget_placeholder:
            raise RuntimeError("Widget 'mazeWidget' không tồn tại trong main.ui!")

        # Tạo MazeWidget với kích thước tương ứng
        maze_widget = MazeWidget(maze_widget_placeholder, map_index=self.map_index)
        maze_widget.maze_size = self.maze_size  # Gán kích thước mê cung
        maze_widget.current_algorithm = self.algorithm
        maze_widget.create_and_draw_maze(self.map_index)  # Tạo mê cung với map_index
        maze_widget.setGeometry(0, 0, maze_widget_placeholder.width(), maze_widget_placeholder.height())
        maze_widget.show()

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

        self.setCentralWidget(new_widget)
    
    def recreate_maze(self, maze_widget, spawn_time):
        if not isinstance(maze_widget, MazeWidget):
            raise ValueError("Provided widget is not a valid MazeWidget instance.")
        
        maze_widget.create_and_draw_maze(maze_widget.maze_size)

        # Đặt lại vị trí người chơi
        maze_widget.player_pos = [1, 0]
            
        # Gọi auto_solve ngay sau khi mê cung được tạo
        maze_widget.stop_auto_solve()
        QTimer.singleShot(500, maze_widget.auto_solve)  # Gọi sau 500ms để đảm bảo giao diện được load
        self.setFocus()

        maze_widget.update()
        # Cập nhật lại hướng nhân vật
        maze_widget.current_player_image = maze_widget.player_images["right"]  # Ví dụ, hướng ban đầu là "right"
        
    def show_win_game(self):
        self.win_game_widget = QWidget(self)
        loadUi("ui\\win.ui", self.win_game_widget)
        
        # Căn giữa widget trên cửa sổ chính
        main_window_rect = self.contentsRect()
        widget_rect = self.win_game_widget.contentsRect()
        widget_rect.moveCenter(main_window_rect.center())
        self.win_game_widget.setGeometry(widget_rect)
        
        # Kết nối các nút
        btn_again = self.win_game_widget.findChild(QPushButton, "btnAgain")
        btn_new_map = self.win_game_widget.findChild(QPushButton, "btnNewMap")
        btn_new_algorithm = self.win_game_widget.findChild(QPushButton, "btnNewAlgorithm")

        if btn_again:
            btn_again.clicked.connect(lambda: self.start_game_with_level(self.maze_size, self.algorithm))
        if btn_new_map:
            btn_new_map.clicked.connect(self.change_ui_map)
        if btn_new_algorithm:
           btn_new_algorithm.clicked.connect(lambda: self.change_ui_algorithm(self.maze_size))
            
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
