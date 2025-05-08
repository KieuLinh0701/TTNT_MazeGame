import sys
import random
from algorithm import greedy_best_first_search, a_star
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
from PyQt6.uic import loadUi
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QSoundEffect
from PyQt6.QtGui import QPainter, QPixmap, QImage, QPen
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, QUrl, QTimer
import os
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"

class MazeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
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
    
    def move_player(self, dx, dy):
        new_pos = [self.player_pos[0] + dy, self.player_pos[1] + dx]
        if self.is_valid_move(new_pos[0], new_pos[1]):
            self.player_pos = new_pos        
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
    
    def gameOver(self):
        self.game_over = True  # Đặt trạng thái game_over
            
        # Phát âm thanh thắng
        self.lose_sound.play() 
            
        # Gọi hàm hiển thị Game Over từ MyWindow
        main_window = self.window()  # Lấy QMainWindow (MyWindow)
        if isinstance(main_window, MyWindow):
            main_window.show_game_over()
    
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

        self.btnStart.clicked.connect(self.change_ui_level)  # Kết nối nút start
        self.maze_size = 21  # Kích thước mặc định của mê cung (sẽ thay đổi theo lựa chọn)

        # Lưu trữ trạng thái âm nhạc
        self.music_playing = True

        # Set volume through QAudioOutput
        audio_output.setVolume(0.3)  # Adjust volume (value from 0.0 to 1.0)

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

        # Pass the spawn time to the maze widget
        self.change_ui()  # Modify to pass spawn_time to the UI change

    def change_ui(self):
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
            self.btnReNew.clicked.connect(lambda: self.recreate_maze(maze_widget))
            self.btnReNew.clicked.connect(lambda: maze_widget.setFocus())

        self.setCentralWidget(new_widget)
    
    def recreate_maze(self, maze_widget):
        if not isinstance(maze_widget, MazeWidget):
            raise ValueError("Provided widget is not a valid MazeWidget instance.")
        
        maze_widget.create_and_draw_maze(maze_widget.maze_size)

        # Đặt lại vị trí người chơi
        maze_widget.player_pos = [1, 0]
            
        # Xóa đường dẫn gợi ý
        maze_widget.hint_path = []  # Xóa hint_path
        if hasattr(self, 'btnHint') and self.btnHint:
            self.btnHint.setChecked(False)  # Tắt nút btnHint

        maze_widget.update()
        # Cập nhật lại hướng nhân vật
        maze_widget.current_player_image = maze_widget.player_images["right"]  # Ví dụ, hướng ban đầu là "right"
        
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