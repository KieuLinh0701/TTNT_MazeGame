import sys
import random
from algorithm import a_star, q_learning, dfs
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel
from PyQt6.uic import loadUi
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtGui import QPainter, QPixmap, QImage, QPen, QColor
from PyQt6.QtCore import Qt, QUrl, QTimer, QCoreApplication, QThread

import os
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"

class MazeWidget(QWidget):
    def __init__(self, parent=None, lbl_time=None):
        super().__init__(parent)
        self.lbl_time = lbl_time  # Lưu tham chiếu đến lblTime
        if self.lbl_time is None:
            print("Warning: lbl_time is None in MazeWidget")  # Thêm debug

        self.current_algorithm = None
        self.auto_solving = False  # Trạng thái tự động giải
        self.game_over = False  # Thêm biến trạng thái game_over
        self.time_elapsed = 0  # Thời gian đã trôi qua (tính bằng giây)
        self.timer = QTimer(self)  # Timer để đếm thời gian
        self.timer.timeout.connect(self.update_time)  # Kết nối với hàm cập nhật thời gian
        self.time_started = False  # Trạng thái bắt đầu đếm thời gian
        
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
        
        self.setFocus()

    def create_and_draw_maze(self, size):
        self.maze = self.generate_maze(size)
        self.time_elapsed = 0  # Đặt lại thời gian khi tạo mê cung mới
        self.time_started = False  # Đặt lại trạng thái thời gian
        self.timer.stop()  # Dừng timer nếu đang chạy
        self.update_time_label()  # Cập nhật nhãn thời gian
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
        
        if self.current_algorithm is None:
            print("Error: No algorithm set for auto_solve.")
            return
        
        path = self.current_algorithm(self.maze, self.maze_size, start, goal)
        if not path:
            print("Không có đường đi đến đích.")
            return
        
        # Di chuyển người chơi theo đường đi
        self.move_player_along_path(path)

    def move_player_along_path(self, path):
        # Bắt đầu đồng hồ ngay trước khi di chuyển
        if not self.time_started:
            self.time_started = True
            self.timer.start(1000) #Cập nhật mỗi giây
 
        # Di chuyển người chơi từng bước trên đường đi
        for i in range(len(path) - 1):
            if not self.auto_solving:
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
            QThread.msleep(300)  # 200ms giữa mỗi bước di chuyển

        # Đảm bảo người chơi đứng ở vị trí cuối cùng (đích)
        self.player_pos = list(path[-1])
        self.update()  # Vẽ lại lần cuối
        self.win_game()


    def stop_auto_solve(self):
        self.auto_solving = False  # Dừng tự động giải
        self.timer.stop()  # Dừng timer khi dừng giải tự động
        self.time_started = False

    def set_algorithm(self, algorithm_name):
        if algorithm_name in (dfs, a_star, q_learning):
            self.current_algorithm = algorithm_name
            print("Algorithm set to:", "DFS" if algorithm_name == dfs else "A*" if algorithm_name == a_star else "Q-Learning")
        else:
            print("Warning: Invalid algorithm provided, setting to None")
            self.current_algorithm = None

    def win_game(self):
        self.game_over = True  # Ngăn người chơi di chuyển
        self.timer.stop()  # Dừng timer khi đến đích
        self.time_started = False
            
        # Phát âm thanh thắng
        self.win_sound.play()
        
        # Gọi hàm hiển thị Win từ MyWindow
        main_window = self.window()
        if isinstance(main_window, MyWindow):
            main_window.show_win_game()

    def update_time(self):
        self.time_elapsed += 1
        self.update_time_label()

    def update_time_label(self):
        minutes = self.time_elapsed // 60
        seconds = self.time_elapsed % 60
        time_text = f"{minutes:02d} : {seconds:02d}"
        print("Updating time:", time_text)  # Thêm debug
        if self.lbl_time:  # Kiểm tra nếu lbl_time tồn tại
            self.lbl_time.setText(time_text)
    
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
        self.lblTime = None  # Thêm tham chiếu đến lblTime
        self.algorithm = None  # Khai báo thuộc tính algorithm

    def change_ui_level(self):
            
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
            btn_easy.clicked.connect(lambda: self.change_ui_algorithm(21))
        if btn_medium:
            btn_medium.clicked.connect(lambda: self.change_ui_algorithm(31))
        if btn_hard:
            btn_hard.clicked.connect(lambda: self.change_ui_algorithm(41))
        if btn_expert:
            btn_expert.clicked.connect(lambda: self.change_ui_algorithm(51))

        self.setCentralWidget(new_widget)
        self.update()

    def change_ui_algorithm(self, size):  
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

        # Gắn sự kiện cho từng nút
        btn_Dfs = new_widget.findChild(QPushButton, "btnDfs")
        btn_AStar = new_widget.findChild(QPushButton, "btnAStar")
        btn_QLearning = new_widget.findChild(QPushButton, "btnQLearning")

        if btn_Dfs:
            btn_Dfs.clicked.connect(lambda: self.start_game_with_level(size, dfs))
        if btn_AStar:
            btn_AStar.clicked.connect(lambda: self.start_game_with_level(size, a_star))
        if btn_QLearning:
            btn_QLearning.clicked.connect(lambda: self.start_game_with_level(size, q_learning))

        # Tìm nút btnBack
        self.btnBack = new_widget.findChild(QPushButton, "btnBack")
        self.btnBack.clicked.connect(self.change_ui_level)

        print("Algorithm set in change_ui_algorithm:", self.algorithm)  # Thêm debug

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

    def start_game_with_level(self, maze_size, algorithm):
        # Xóa widget Win
        if hasattr(self, 'win_game_widget') and self.win_game_widget:
            self.win_game_widget.hide()
            self.win_game_widget.deleteLater()
            self.win_game_widget = None

        # Xóa centralWidget cũ nếu tồn tại
        if self.centralWidget():
            self.centralWidget().deleteLater()
            
        self.maze_size = maze_size  # Lưu kích thước mê cung
        self.algorithm = algorithm  # Gán thuật toán
        print("Algorithm set in start_game_with_level:", self.algorithm)  # Thêm debug
        
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
        
        # Gán self.lblTime trước
        self.lblTime = new_widget.findChild(QLabel, "lblTime")
        if not self.lblTime:
            raise RuntimeError("lblTime không được tìm thấy trong main.ui!")
        print("lblTime found:", self.lblTime)

        # Tạo MazeWidget với kích thước tương ứng
        maze_widget = MazeWidget(maze_widget_placeholder, self.lblTime)
        maze_widget.maze_size = self.maze_size  # Gán kích thước mê cung
        maze_widget.current_algorithm = self.algorithm
        maze_widget.set_algorithm(self.algorithm)  # Gán thuật toán
        print("Algorithm in change_ui:", self.algorithm)  # Thêm debug
        maze_widget.create_and_draw_maze(self.maze_size)  # Tạo mê cung
        QTimer.singleShot(500, maze_widget.auto_solve)  # Gọi sau khi mọi thứ sẵn sàng
        maze_widget.setGeometry(0, 0, maze_widget_placeholder.width(), maze_widget_placeholder.height())
        maze_widget.show()

        # Đảm bảo widget được vẽ lại
        self.update()

        # Tìm và lưu lblTime
        self.lblTime = new_widget.findChild(QLabel, "lblTime")
        if not self.lblTime:
            raise RuntimeError("lblTime không được tìm thấy trong main.ui!")
        print("lblTime found:", self.lblTime)  # Thêm debug

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
        self.btnBack.clicked.connect(maze_widget.stop_auto_solve)

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
        btn_continue = self.win_game_widget.findChild(QPushButton, "btnContinue")
        btn_new_level = self.win_game_widget.findChild(QPushButton, "btnNewLevel")
        btn_new_algorithm = self.win_game_widget.findChild(QPushButton, "btnNewAlgorithm")

        if btn_continue:
            btn_continue.clicked.connect(lambda: self.start_game_with_level(self.maze_size, self.algorithm))
        if btn_new_level:
            btn_new_level.clicked.connect(self.change_ui_level)
        if btn_new_algorithm:
           btn_new_algorithm.clicked.connect(lambda: self.change_ui_algorithm(self.maze_size))
            
        # Vô hiệu hóa các nút bên dưới
        if hasattr(self, 'btnMusic'):
            self.btnMusic.setEnabled(False)
        if hasattr(self, 'btnBack'):
            self.btnBack.setEnabled(False)
        if hasattr(self, 'btnReNew'):
            self.btnReNew.setEnabled(False)

        # Tìm label thời gian
        lbl_result_time = self.win_game_widget.findChild(QLabel, "label_result_time")
        if lbl_result_time:
            minutes = self.centralWidget().findChild(MazeWidget).time_elapsed // 60
            seconds = self.centralWidget().findChild(MazeWidget).time_elapsed % 60
            lbl_result_time.setText(f"{minutes:02d} : {seconds:02d}")

        
        self.win_game_widget.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())