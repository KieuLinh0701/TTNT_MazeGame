import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
from PyQt6.uic import loadUi
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtGui import QPainter, QPixmap, QImage, QPen
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
import os
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"

class MazeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Cài đặt kích thước mê cung và hình ảnh
        self.maze_size = 21
        self.maze = []
        self.wall_image = QPixmap("C:/TTNT_MazeGame/image/wall.png")
        self.player_image = QImage("C:/TTNT_MazeGame/image/actor.png")
        self.goal_image = QPixmap("C:/TTNT_MazeGame/image/goal.png")
        self.start_image = QPixmap("C:/TTNT_MazeGame/image/start.png")
        self.cell_size = 30

        # Tạo mê cung và đặt vị trí người chơi
        self.create_and_draw_maze(self.maze_size)
        self.player_pos = [1, 0]
        self.setFocus()  # Đảm bảo widget nhận sự kiện bàn phím

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
        scaled_image = self.player_image.scaled(
            self.cell_size, self.cell_size,
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        player_x = self.player_pos[1] * self.cell_size + (self.cell_size - scaled_image.width()) // 2
        player_y = self.player_pos[0] * self.cell_size + (self.cell_size - scaled_image.height()) // 2
        painter.drawImage(player_x, player_y, scaled_image)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            self.move_player(0, -1)
        elif event.key() == Qt.Key.Key_Down:
            self.move_player(0, 1)
        elif event.key() == Qt.Key.Key_Left:
            self.move_player(-1, 0)
        elif event.key() == Qt.Key.Key_Right:
            self.move_player(1, 0)
    
    def move_player(self, dx, dy):
        new_pos = [self.player_pos[0] + dy, self.player_pos[1] + dx]
        if self.is_valid_move(new_pos[0], new_pos[1]):
            self.player_pos = new_pos
            self.update()

    def is_valid_move(self, row, col):
        if row < 0 or col < 0 or row >= len(self.maze) or col >= len(self.maze[row]):
            return False
        return self.maze[row][col] in (1, 2, 3)

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("C:/TTNT_MazeGame/ui/start.ui", self)

        # Thiết lập âm thanh nền
        self.player = QMediaPlayer(self)
        audio_output = QAudioOutput(self)
        self.player.setAudioOutput(audio_output)

        audio_url = QUrl.fromLocalFile("C:/TTNT_MazeGame/music/game_music.mp3")
        self.player.setSource(audio_url)
        self.player.play()

        # Kết nối tín hiệu statusChanged để kiểm tra khi nào âm thanh kết thúc
        self.player.mediaStatusChanged.connect(self.handle_media_status_changed)

        self.btnStart.clicked.connect(self.change_ui) # Kết nối tín hiệu clicked với phương thức changeUi

        # Lưu trữ trạng thái âm nhạc
        self.music_playing = True

        # Set volume through QAudioOutput
        audio_output.setVolume(0.5)  # Adjust volume (value from 0.0 to 1.0)

    def handle_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.player.play()  # Phát lại nhạc khi kết thúc

    def toggle_music(self):
        if self.music_playing:
            self.player.pause()  # Tạm dừng nhạc
        else:
            self.player.play()  # Phát nhạc
        self.music_playing = not self.music_playing  # Đảo trạng thái nhạc

    def change_ui(self):
        # Tạo một widget mới từ main.ui
        new_widget = QWidget(self)
        loadUi("C:/TTNT_MazeGame/ui/main.ui", new_widget)
        
        # Đặt widget mới làm central widget
        self.setCentralWidget(new_widget)
        
        # Tìm mazeWidget trong UI mới
        self.mazeWidgetPlaceholder = new_widget.findChild(QWidget, "mazeWidget")
        if not self.mazeWidgetPlaceholder:
            raise RuntimeError("Widget 'mazeWidget' không tồn tại trong main.ui!")
        
        # Tạo MazeWidget và thiết lập kích thước phù hợp
        self.mazeWidget = MazeWidget(self.mazeWidgetPlaceholder)
        self.mazeWidget.setGeometry(0, 0, self.mazeWidgetPlaceholder.width(), self.mazeWidgetPlaceholder.height())
        self.mazeWidget.show()

        # Tìm nút btnMusic
        self.btnMusic = new_widget.findChild(QPushButton, "btnMusic")
        if not self.btnMusic:
            raise RuntimeError("btnMusic không được tìm thấy trong main.ui!")
        else:
            self.btnMusic.clicked.connect(self.toggle_music)

        # Đảm bảo cửa sổ chính có kích thước giống như trong UI
        self.resize(self.size())

        # Đảm bảo mọi widget được vẽ lại
        self.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())