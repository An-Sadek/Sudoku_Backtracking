import pandas as pd


class SudokuHistory:

    def __init__(self):
        
        self.location = []
        self.is_empty = []
        self.num_input = []
        self.num_valid = []
        self.move = []
        self.next_location = []

    def add_record(self, location, is_empty, num_input, num_valid, move, next_location):
        """
            Location: Danh sách vị trí hiện tại đang xét\n
            Is empty: Xét vị trí hiện tại có trống hay không\n
            Num input: Giá trị đầu vào của ô đang xét\n
            Num valid: Giá trị đầu vào hợp lệ (không trùng số của hàng, cột, ma trận con)\n
            Move: Di chuyển đến ô tiếp theo, hoặc không di chuyển, hoặc lùi lại sang ô phía trước\n
            Next location: Ô tiếp theo sẽ di chuyển đến\n
        """
        self.location.append(location)
        self.is_empty.append(is_empty)
        self.num_input.append(num_input)
        self.num_valid.append(num_valid)
        self.move.append(move)
        self.next_location.append(next_location)

    def to_csv(self, path):
        """
        Lưu lịch sử về trong trường hợp mở rộng chương trình
        """
        df = pd.DataFrame({
            "location": self.location,
            "is_empty": self.is_empty,
            "num_input": self.num_input,
            "num_valid": self.num_valid,
            "move": self.move,
            "next_location": self.next_location
        })
        df.to_csv(path, index=False)
        return df
    
import time


class SudokuSolver:

    def __init__(self):
        pass 

    def is_safe(self, mat, row, col, num):
        """
        Kiểm tra giá trị đầu vào có trùng với giá trị units không
        """
        # Kiểm tra hàng
        if num in mat[row, :]:
            return False
        
        # Kiểm tra cột
        if num in mat[:, col]:
            return False
        
        # Kiểm tra
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        if num in mat[start_row:start_row + 3, start_col:start_col + 3]:
            return False
        
        return True

    def solve_sudoku(self, mat, row, col, history: SudokuHistory, timeout=20):
        """
        Giải sudoku, trả về kết quả fail nếu thời gian vượt quá quy định
        Hoặc không giải được do cấu hình
        """
        start_time = time.time()

        # Nếu đạt tới hàng thứ 10 (index 9) thì hoàn thành
        if row == 9:
            return True, mat, history
        
        # Nếu vượt cột thì xuống hàng tiếp
        if col == 9:
            return self.solve_sudoku(mat, row + 1, 0, history, timeout)
        
        # Bỏ qua những giá trị không rỗng
        if mat[row][col] != 0:
            history.add_record((row, col), False, None, None, 1, (row, col + 1))
            return self.solve_sudoku(mat, row, col + 1, history, timeout)
        
        # Duyệt từng giá trị
        for num in range(1, 10):
            
            # Huỷ chương trình nếu giải quá lâu
            if time.time() - start_time > timeout:
                return False, mat, history  

            # Kiểm tra giá trị hợp lệ
            valid = self.is_safe(mat, row, col, num)
            history.add_record((row, col), True, num, valid, None, None)

            # Nếu hợp lệ
            if valid:
                mat[row][col] = num
                history.add_record((row, col), True, num, True, 1, (row, col + 1))
                solvable, mat, history = self.solve_sudoku(mat, row, col + 1, history, timeout)

                # Nếu đã giải xong thì trả về True
                if solvable:
                    return True, mat, history
                
                # Nếu chưa giải xong thì backtracking
                mat[row][col] = 0
                history.add_record((row, col), True, num, True, -1, (row, col))

        # Lưu lịch sử, không ảnh hướng đến giải thuật
        prev_col = col - 1 if col > 0 else 8
        prev_row = row if col > 0 else row - 1
        if prev_row >= 0:
            history.add_record((row, col), True, None, False, -1, (prev_row, prev_col))

        # Backtracking tiếp
        return False, mat, history

    def is_solvable(self, mat, timeout=20):
        """
        Kiểm tra xem ma trận đầu vào có giải được không
        """
        history = SudokuHistory()
        solvable, solved_mat, history = self.solve_sudoku(mat.copy(), 0, 0, history, timeout)
        if solvable:
            return True, solved_mat
        else:
            return False, "Grid is unsolvable or timed out"
        
import os
import pygame
import random

import numpy as np
from enum import Enum


class Color(Enum):

    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    WHITE = (255, 255, 255)

    RED = (255, 0, 0)
    GREEN = (0, 255, 0) 

    INACTIVE = (120, 120, 120)
    ACTIVE = (70, 180, 70)
    ERROR = (180, 70, 70)
    WIN = (50, 150, 50)
    SELECTED = (100, 150, 255)


class SudokuGame:

    def __init__(self, path, cell_size = 60, button_height = 50):
        """
        Đọc đường dẫn của các câu đố sudoku có sẵn
        Khởi tạo câu đó
        Khởi tạo game
        """
        assert os.path.exists(path)
        with open(path, "r") as file:
            self.grids = file.readlines()

        # Khởi tạo các biến
        self.grid = None
        self.locked = None
        self.solved = None
        self.failed = None
        self.won = None
        self.lives = None
        self.history = None
        self.selected_cell = None

        # Reset về trạng thái mặc định
        self.reset()
        self.solver = SudokuSolver()

        # Khởi tạo game
        pygame.init()

        self.cell_size = cell_size
        self.button_height = button_height
        self.screen_width = cell_size * 9
        self.screen_height = cell_size * 9 + button_height * 2 + 20
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        # Khởi tạo các nút bấm
        self.button_width = 120
        self.button_height = 40
        self.button_spacing = 20
        self.total_buttons_width = self.button_width * 3 + self.button_spacing * 2
        self.button_x_start = (self.screen_width - self.total_buttons_width) // 2
        self.button_y = self.cell_size * 9 + 30

    def reset(self):
        """
        Reset lại trạng thái bằng cách lấy một bảng sudoku ngẫu nhiên
        """
        txt_line = random.choice(self.grids).strip()
        parts = txt_line.split()
        self.mat = self.load_grid(parts[1])

        self.locked = [[True if self.mat[i][j] != 0 else False for j in range(9)] for i in range(9)]
        self.solved = False
        self.failed = False
        self.won = False
        self.lives = 3
        self.history = SudokuHistory()
        self.selected_cell = None

    def load_grid(self, txt_grid: str):
        """
        Các bảng sudoku được viết theo kiểu chuỗi, 
        trong đó ma trận là dữ liệu ở giữa là chuỗi gồm 81 số
        """
        mat = np.array([int(num) for num in txt_grid]).reshape(9, 9)
        return mat
    
    def is_board_complete_and_valid(self, mat, locked):
        """
        Kiểm tra sudoku đã được giải hay chưa
        """
        for i in range(9):
            for j in range(9):
                if mat[i][j] == 0 or (not locked[i][j] and not self.solver.is_safe(mat, i, j, mat[i][j])):
                    return False
        return True
    
    def draw_board(self, 
        screen, 
        mat, 
        locked, 
        cell_size, 
        selected_cell=None, 
        lives=3
    ):
        """
        Vẽ các 
            screen: Tạo màn hình từ pygame với kích thước width x heigh
            mat: Ma trận sudoku được lấy từ self.grid
            locked: Ma trận boolean các số đã được gợi ý
            cell_size: Kích thước mỗi ô
            selected_cell: Vị trí ô hiện tại đang chọn (x, y)
            lives: Số mạng còn lại của người chơi
        """
        screen.fill((230, 240, 255))

        # Nền xám cho gợi ý 
        for i in range(9):
            for j in range(9):
                color = Color.GRAY.value if locked[i][j] else Color.WHITE.value
                pygame.draw.rect(screen, color, (j * cell_size, i * cell_size, cell_size, cell_size))

        # Vẽ các đường phân chia
        for i in range(10):
            thickness = 4 if i % 3 == 0 else 1 # Đường chia cắt các khối dày hơn
            pygame.draw.line(screen, (0, 50, 100), (i * cell_size, 0), (i * cell_size, 9 * cell_size), thickness)
            pygame.draw.line(screen, (0, 50, 100), (0, i * cell_size), (9 * cell_size, i * cell_size), thickness)
        
        # Vẽ đường viền cho ô đang được chọn (trừ ô gợi ý)
        if selected_cell and not locked[selected_cell[0]][selected_cell[1]]:
            i, j = selected_cell
            pygame.draw.rect(screen, Color.SELECTED.value, (j * cell_size, i * cell_size, cell_size, cell_size), 4)
        
        font = pygame.font.Font(None, 40)

        for i in range(9):
            for j in range(9):
                if mat[i][j] != 0:
                    num = mat[i][j]
                    if locked[i][j]:
                        color = Color.BLACK.value  # Các ô không phải gợi ý có chữ đen
                    
                    else:
                        color = Color.GREEN.value
                    text = font.render(str(num), True, color)
                    text_rect = text.get_rect(center=(j * cell_size + cell_size / 2, i * cell_size + cell_size / 2))
                    screen.blit(text, text_rect)
        font = pygame.font.Font(None, 36)
        lives_text = font.render(f"Lives: {lives}", True, Color.BLACK.value)
        screen.blit(lives_text, (10, cell_size * 9 + 5))

    def draw_button(self, screen, text, x, y, w, h, inactive_color, active_color, text_color=Color.WHITE.value):
        """
        Thêm các nút bấm vào, trả về giá trị True nếu bấm vào
            screen
            text: Nội dung nút bấm
            x, y: Toạ độ của nút bấm
            w, h: Chiều dài, chiều rộng của nút

        """
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        color = active_color if (x + w > mouse[0] > x and y + h > mouse[1] > y) else inactive_color
        pygame.draw.rect(screen, color, (x, y, w, h), border_radius=10)
        font = pygame.font.Font(None, 36)
        text_surf = font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=(x + w / 2, y + h / 2))
        screen.blit(text_surf, text_rect)

        return click[0] == 1 and x + w > mouse[0] > x and y + h > mouse[1] > y


    def run(self):
        pygame.display.set_caption("Sudoku Game")

        mat = self.mat
        locked = [[True if mat[i][j] != 0 else False for j in range(9)] for i in range(9)]

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if not self.failed and not self.won:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = pygame.mouse.get_pos()
                        if y < self.cell_size * 9:
                            i, j = y // self.cell_size, x // self.cell_size
                            if not locked[i][j]:
                                self.selected_cell = (i, j)
                        else:
                            self.selected_cell = None
                    elif event.type == pygame.KEYDOWN and self.selected_cell:
                        i, j = self.selected_cell
                        if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                            mat[i][j] = 0
                        elif event.unicode.isdigit() and int(event.unicode) in range(1, 10):
                            num = int(event.unicode)
                            if self.solver.is_safe(mat, i, j, num):
                                mat[i][j] = num
                            else:
                                mat[i][j] = num
                                self.lives -= 1
                                if self.lives <= 0:
                                    self.failed = True

            self.draw_board(self.screen, mat, locked, self.cell_size, self.selected_cell, self.lives)

            if self.failed and not self.solved:
                font = pygame.font.Font(None, 100)
                game_over_text = font.render("Game Over", True, Color.RED.value)
                text_rect = game_over_text.get_rect(center=(self.screen_width / 2, self.screen_height / 3))
                self.screen.blit(game_over_text, text_rect)

            if not self.solved:
                # Vẽ nút "Solve", nếu bấm vào thì giải luôn
                if self.draw_button(
                    self.screen, "Solve", 
                    self.button_x_start, self.button_y, 
                    self.button_width, self.button_height,
                    Color.INACTIVE.value, Color.ACTIVE.value
                ):
                    # Modified solving process to include history
                    self.history = SudokuHistory()  # Reset history before solving
                    solvable, result, history = self.solver.solve_sudoku(mat.copy(), 0, 0, self.history)
                    if solvable:
                        mat = result
                        self.solved = True
                        if self.failed:
                            self.failed = False
                        # Export to CSV immediately after solving
                        try:
                            self.history.to_csv("sudoku_history.csv")
                            print("History exported to sudoku_history.csv")
                        except Exception as e:
                            print(f"Failed to export CSV: {e}")
            else:
                self.draw_button(self.screen, "Solved!", self.button_x_start, self.button_y, 
                            self.button_width, self.button_height,
                            Color.ACTIVE.value, Color.ACTIVE.value, Color.WHITE.value)

            # Rest of your code remains the same...
            if self.draw_button(
                self.screen, "New", 
                self.button_x_start + self.button_width + self.button_spacing, 
                self.button_y, self.button_width, self.button_height, 
                Color.INACTIVE.value, Color.ACTIVE.value
            ):
                self.reset()
                mat = self.mat
                locked = [[True if mat[i][j] != 0 else False for j in range(9)] for i in range(9)]
                self.solved = False

            if self.draw_button(
                self.screen, 
                "Quit", 
                self.button_x_start + (self.button_width + self.button_spacing) * 2, 
                self.button_y,
                self.button_width, self.button_height, 
                Color.INACTIVE.value, Color.ERROR.value
            ):
                running = False

            if not self.won and not self.failed and self.is_board_complete_and_valid(mat, locked):
                self.won = True

            if self.won:
                font = pygame.font.Font(None, 100)
                win_text = font.render("You Win!", True, Color.WIN.value)
                text_rect = win_text.get_rect(center=(self.screen_width / 2, self.screen_height / 3))
                self.screen.blit(win_text, text_rect)

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    game = SudokuGame("easy.txt")
    game.run()