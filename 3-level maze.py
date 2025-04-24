import sys
import random
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt

class MazeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("C:\\TTNT\\test ck\\newmaze.ui", self)
        self.widget.setFixedSize(600, 600)

        # Gán nút
        self.pushButton_3.clicked.connect(lambda: self.create_and_draw_maze(30))  # Easy
        self.pushButton_2.clicked.connect(lambda: self.create_and_draw_maze(40))  # Medium
        self.pushButton.clicked.connect(lambda: self.create_and_draw_maze(50))    # Hard

        self.maze = []
        self.maze_size = 0

        # Kích hoạt redraw khi cần
        self.widget.paintEvent = self.paint_maze

# vẽ mê cung
    def create_and_draw_maze(self, size):
        self.maze_size = size
        self.maze = self.generate_maze(size)
        self.widget.update()  # gọi lại paintEvent

# tạo mê theo kích thước
    def generate_maze(self, size):
        maze = [[1 for _ in range(size)] for _ in range(size)]

        start = (1, 1)
        stack = [start]
        maze[start[1]][start[0]] = 0

        directions = [(-1,0),(1,0),(0,-1),(0,1)]

        while stack:
            x, y = stack[-1]
            random.shuffle(directions)
            moved = False
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 1 <= nx < size - 1 and 1 <= ny < size - 1 and maze[ny][nx] == 1:
                    count = sum(
                        maze[ny + dy2][nx + dx2] == 0
                        for dx2, dy2 in directions
                        if 0 <= nx + dx2 < size and 0 <= ny + dy2 < size
                    )
                    if count <= 1:
                        maze[ny][nx] = 0
                        stack.append((nx, ny))
                        moved = True
                        break
            if not moved:
                stack.pop()

        maze[1][1] = 2  # Start
        for i in range(size-2, 0, -1):
            for j in range(size-2, 0, -1):
                if maze[i][j] == 0:
                    maze[i][j] = 3
                    return maze
        
        return maze
 # tô màu cho các ô
    def paint_maze(self, event):
        if not self.maze:
            return
        painter = QPainter(self.widget)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.widget.width()
        h = self.widget.height()
        cell_size = min(w, h) // self.maze_size

        for row in range(self.maze_size):
            for col in range(self.maze_size):
                value = self.maze[row][col]
                if value == 1:
                    color = QColor("black")
                elif value == 0:
                    color = QColor("white")
                elif value == 2:
                    color = QColor("green")
                elif value == 3:
                    color = QColor("red")
                else:
                    color = QColor("gray")

                painter.fillRect(col * cell_size, row * cell_size, cell_size, cell_size, color)
                painter.drawRect(col * cell_size, row * cell_size, cell_size, cell_size)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MazeApp()
    window.show()
    sys.exit(app.exec())
