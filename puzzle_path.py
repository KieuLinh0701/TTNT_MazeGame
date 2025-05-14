import sys
import pandas as pd
from datetime import datetime
from algorithm import dfs, a_star, and_or_search, steepest_ascent_hill_climbing, backtracking, q_learning
from PyQt6.uic import loadUi
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtGui import QPainter, QPixmap, QImage, QPen, QColor
from PyQt6.QtCore import Qt, QUrl, QTimer, QCoreApplication, QThread
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel

import os
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"

class MazeWidget(QWidget):
    def __init__(self, parent=None, map_index=0, lbl_time=None):
        super().__init__(parent)

        self.map_index =  map_index # Chỉ số của mê cung
        self.current_algorithm = None # Thuật toán hiện tại
        self.auto_solving = False  # Trạng thái tự động giải
        self.game_over = False  # Trạng thái game_over
        
        self.step_count = 0  # Đếm số bước đi
        self.lbl_time = lbl_time       
        self.time_elapsed = 0  # Thời gian đã trôi qua (tính bằng giây)
        self.timer = QTimer(self)  # Timer để đếm thời gian
        self.timer.timeout.connect(self.update_time)  # Kết nối với hàm cập nhật thời gian
        self.time_started = False  # Trạng thái bắt đầu đếm thời gian
        
       # Khởi tạo âm thanh bước chân
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

        self.show_path = True  # Cờ để hiển thị đường đi (mặc định là True)
        self.path = None  # Lưu đường đi từ start đến goal

        # Tạo mê cung và đặt vị trí người chơi
        self.create_and_draw_maze(self.map_index)
        self.player_pos = [1, 0]
        
        # Gọi auto_solve ngay sau khi mê cung được tạo
        QTimer.singleShot(1000, self.auto_solve)  # Gọi sau 1000ms để đảm bảo giao diện được load
        self.setFocus()

    def create_and_draw_maze(self, size):
        self.maze = self.generate_maze(self.map_index)
        self.time_elapsed = 0  # Đặt lại thời gian khi tạo mê cung mới
        self.step_count = 0  # Đặt lại số bước đi
        self.time_started = False  # Đặt lại trạng thái thời gian
        self.timer.stop()  # Dừng timer nếu đang chạy
        self.update_time_label()  # Cập nhật nhãn thời gian
        self.path = None  # Đặt lại path
        self.update()  # Gọi lại paintEvent để vẽ mê cung

    def toggle_path(self):
        """Đảo trạng thái hiển thị đường đi và cập nhật giao diện."""
        self.show_path = not self.show_path
        main_window = self.window()
        if isinstance(main_window, QMainWindow):
            btn_path = main_window.findChild(QPushButton, "btnPath")
            if btn_path:
                btn_path.setChecked(self.show_path)
        self.update()

    def generate_maze(self, map_index):
        # Mặc định sẵn 3 mê cung
        maze_list = [
            [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [2, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0],
            [0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0],
            [0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
            [0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0],
            [0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0],
            [0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0],
            [0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0],
            [0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0],
            [0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0],
            [0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0],
            [0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0],
            [0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0],
            [0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0],
            [0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0],
            [0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0],
            [0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0],
            [0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0]], # map 1
            
            [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [2, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0],
            [0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0],
            [0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0],
            [0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0],
            [0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0],
            [0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0],
            [0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0],
            [0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0],
            [0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0],
            [0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0],
            [0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0],
            [0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0],
            [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0],
            [0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0]], # map 2
            
            [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [2, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0],
            [0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
            [0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0],
            [0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0],
            [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0],
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
                
                if self.maze[row][col] == 0:  # Tường
                    painter.drawPixmap(x, y, self.cell_size, self.cell_size, self.wall_image)                    
                elif self.maze[row][col] == 1:  # Lối đi
                    painter.fillRect(x, y, self.cell_size, self.cell_size, QColor("#edb934"))
                elif self.maze[row][col] == 2:  # Điểm bắt đầu
                    painter.drawPixmap(x, y, self.cell_size, self.cell_size, self.start_image)
                elif self.maze[row][col] == 3:  # Điểm kết thúc
                    painter.drawPixmap(x, y, self.cell_size, self.cell_size, self.goal_image)

        # Vẽ đường đi nếu show_path là True và path tồn tại
        if self.show_path and self.path:
            painter.setPen(QPen(QColor("red"), 5, Qt.PenStyle.SolidLine))  # Đường đỏ, dày 5px
            for i in range(len(self.path) - 1):
                start_pos = self.path[i]
                end_pos = self.path[i + 1]
                start_x = start_pos[1] * self.cell_size + self.cell_size // 2
                start_y = start_pos[0] * self.cell_size + self.cell_size // 2
                end_x = end_pos[1] * self.cell_size + self.cell_size // 2
                end_y = end_pos[0] * self.cell_size + self.cell_size // 2
                painter.drawLine(start_x, start_y, end_x, end_y)   
        
        # Vẽ người chơi
        scaled_image = self.current_player_image.scaled(
            self.cell_size, self.cell_size,
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
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
        
        self.path = self.current_algorithm(self.maze, self.maze_size, start, goal)
        if not self.path:
            print("Không có đường đi đến đích.")
            self.auto_solving = False
            return
        
        # Di chuyển người chơi theo đường đi
        self.move_player_along_path(self.path)        
    
    def move_player_along_path(self, path):
        if not self.time_started:
            self.time_started = True
            self.timer.start(100)  # cập nhật thời gian mỗi 100ms

        self.path = path
        self.step_index = 0
        self.step_count = 0
        self._move_step()
    def _move_step(self):
        if self.step_index >= len(self.path) - 1:
            self.win_game()
            return

        current_pos = self.path[self.step_index]
        next_pos = self.path[self.step_index + 1]

        dx = next_pos[1] - current_pos[1]
        dy = next_pos[0] - current_pos[0]

        if dx == 1:
            self.current_player_image = self.player_images["right"]
        elif dx == -1:
            self.current_player_image = self.player_images["left"]
        elif dy == 1:
            self.current_player_image = self.player_images["down"]
        elif dy == -1:
            self.current_player_image = self.player_images["up"]

        self.player_pos = list(next_pos)
        self.step_count += 1
        self.update()
        self.step_player.play()
        self.step_index += 1

        QTimer.singleShot(300, self._move_step)  # gọi lại chính nó sau 300ms

    def stop_auto_solve(self):
        self.auto_solving = False  # Dừng tự động giải
        self.timer.stop()  # Dừng timer khi dừng giải tự động
        self.time_started = False
    
    def win_game(self):
        self.game_over = True  # Ngăn người chơi di chuyển
        self.timer.stop()  # Dừng timer khi đến đích
        self.time_started = False
            
        # Phát âm thanh thắng
        self.win_sound.play()
        
        # Gọi hàm hiển thị Win từ MyWindow
        main_window = self.window()
        if isinstance(main_window, MyWindow):
            self.save_to_excel(self.current_algorithm, self.map_index) #lưu vào Excel
            main_window.show_win_game()

    def update_time(self):
        self.time_elapsed += 100  # tăng 100ms mỗi lần gọi (vì timer mỗi 100ms)
        self.update_time_label()

    def update_time_label(self):
        total_ms = self.time_elapsed
        minutes = total_ms // 60000
        seconds = (total_ms % 60000) // 1000
        centiseconds = (total_ms % 1000) // 10  # 2 chữ số mili giây: 0–99

        time_text = f"{minutes:02d}:{seconds:02d}.{centiseconds:02d}"
        print("Updating time:", time_text)

        if self.lbl_time:
            self.lbl_time.setText(time_text)

    def save_to_excel(self, algorithm, map_index):
        # Xác định tên thuật toán
        algorithm_name = (
            "DFS" if algorithm == dfs else
            "A*" if algorithm == a_star else
            "Q-Learning" if algorithm == q_learning else
            "And-Or Search" if algorithm == and_or_search else
            "Steepest Ascent Hill Climbing" if algorithm == steepest_ascent_hill_climbing else
            "Backtracking" if algorithm == backtracking else
            "Unknown"
        )
        
        # Xác định tên map dựa trên map_index
        map_name = (
            "Map 1" if map_index == 0 else
            "Map 2" if map_index == 1 else
            "Map 3" if map_index == 2 else
            "Unknown"
        )
        
        # Lấy thời gian hiện tại
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
       
        # Định dạng thời gian đến đích
        total_ms = self.time_elapsed
        minutes = total_ms // 60000
        seconds = (total_ms % 60000) // 1000
        centiseconds = (total_ms % 1000) // 10
        time_to_goal = f"{minutes:02d}:{seconds:02d}.{centiseconds:02d}"
        
        # Tạo dữ liệu để lưu
        data = {
            "DateTime": [current_time],
            "Algorithm": [algorithm_name],
            "Maze": [map_name],
            "TimeToGoal": [time_to_goal],
            "Steps": [self.step_count]
        }
        df = pd.DataFrame(data)
        # Lưu vào file Excel
        excel_file = "game_records.xlsx"
        try:
            # Nếu file đã tồn tại, đọc và nối dữ liệu
            if os.path.exists(excel_file):
                existing_df = pd.read_excel(excel_file, engine='openpyxl')  # Chỉ định engine để đọc
                df = pd.concat([existing_df, df], ignore_index=True)
            
            # Ghi dữ liệu vào file Excel
            df.to_excel(excel_file, index=False, engine='openpyxl')  # Chỉ định engine để ghi
            print(f"Saved game record to {excel_file}")
        except Exception as e:
            print(f"Error saving to Excel: {e}")


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

        self.btnStart.clicked.connect(self.change_ui_map)  # Kết nối nút start
        self.maze_size = 25  # Kích thước mặc định của mê cung
        self.map_index = 0
        self.lblTime = None  # Thêm tham chiếu đến lblTime

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
            btn_Dfs.clicked.connect(lambda: self.start_game_with_algorithm(dfs))
        if btn_AStar:
            btn_AStar.clicked.connect(lambda: self.start_game_with_algorithm(a_star))
        if btn_Aos:
            btn_Aos.clicked.connect(lambda: self.start_game_with_algorithm(and_or_search))
        if btn_Sahc:
            btn_Sahc.clicked.connect(lambda: self.start_game_with_algorithm(steepest_ascent_hill_climbing))
        if btn_Backtracking:
            btn_Backtracking.clicked.connect(lambda: self.start_game_with_algorithm(backtracking))
        if btn_QLearning:
            btn_QLearning.clicked.connect(lambda: self.start_game_with_algorithm(q_learning))

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

    def start_game_with_algorithm(self, algorithm):
        # Xóa widget Win
        if hasattr(self, 'win_game_widget') and self.win_game_widget:
            self.win_game_widget.hide()
            self.win_game_widget.deleteLater()
            self.win_game_widget = None

        # Xóa centralWidget cũ nếu tồn tại
        if self.centralWidget():
            self.centralWidget().deleteLater()

        self.algorithm = algorithm
        self.change_ui()

    def change_ui(self):
        # Tạo một widget mới từ main.ui
        new_widget = QWidget(self)
        loadUi("ui\\main.ui", new_widget)

        # Tìm mazeWidgetPlaceholder trong main.ui
        maze_widget_placeholder = new_widget.findChild(QWidget, "mazeWidget")
        if not maze_widget_placeholder:
            raise RuntimeError("Widget 'mazeWidget' không tồn tại trong main.ui!")

        # Gán self.lblTime trước
        self.lblTime = new_widget.findChild(QLabel, "lblTime")
        if not self.lblTime:
            raise RuntimeError("lblTime không được tìm thấy trong main.ui!")

        # Tạo MazeWidget với kích thước tương ứng
        maze_widget = MazeWidget(maze_widget_placeholder, map_index=self.map_index, lbl_time=self.lblTime)
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
        self.btnBack.clicked.connect(self.change_ui_algorithm)
        self.btnBack.clicked.connect(maze_widget.stop_auto_solve)

        # Tìm nút btnPath
        self.btnPath = new_widget.findChild(QPushButton, "btnPath")
        if self.btnPath:
            self.btnPath.clicked.connect(maze_widget.toggle_path)
            self.btnPath.setChecked(maze_widget.show_path)

        self.setCentralWidget(new_widget)
    
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
        btn_show_path = self.win_game_widget.findChild(QPushButton, "btnPath")

        if btn_again:
            btn_again.clicked.connect(lambda: self.start_game_with_algorithm(self.algorithm))
        if btn_new_map:
            btn_new_map.clicked.connect(self.change_ui_map)
        if btn_new_algorithm:
           btn_new_algorithm.clicked.connect(lambda: self.change_ui_algorithm(self.map_index))
        if btn_show_path:
            btn_show_path.clicked.connect(self.hide_win_game)
            
        # Vô hiệu hóa các nút bên dưới
        if hasattr(self, 'btnMusic'):
            self.btnMusic.setEnabled(False)
        if hasattr(self, 'btnBack'):
            self.btnBack.setEnabled(False)
        if hasattr(self, 'btnPath'):
            self.btnPath.setEnabled(False)

        # Tìm label thời gian
        lbl_result_time = self.win_game_widget.findChild(QLabel, "label_result_time")
        maze_widget = self.centralWidget().findChild(MazeWidget)
        if lbl_result_time and maze_widget:
            total_ms = maze_widget.time_elapsed
            minutes = total_ms // 60000
            seconds = (total_ms % 60000) // 1000
            centiseconds = (total_ms % 1000) // 10

            lbl_result_time.setText(f"Arrived the goal in {minutes:02d}:{seconds:02d}.{centiseconds:02d} seconds")
        
        self.win_game_widget.show()

    def hide_win_game(self):
        """Ẩn win_game_widget và kích hoạt lại các nút."""
        if self.win_game_widget:
            self.win_game_widget.hide()
            self.win_game_widget.deleteLater()
            self.win_game_widget = None
        
        if hasattr(self, 'btnMusic'):
            self.btnMusic.setEnabled(True)
        if hasattr(self, 'btnBack'):
            self.btnBack.setEnabled(True)
        if hasattr(self, 'btnPath'):
            self.btnPath.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
