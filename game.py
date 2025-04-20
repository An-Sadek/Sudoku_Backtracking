import os
import pygame
import random

import numpy as np
from enum import Enum
from solver import SudokuSolver, SudokuHistory


class Color(Enum):

    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    WHITE = (255, 255, 255)

    RED = (255, 0, 0)
    GREEN = (0, 255, 0) 

    SCREEN = (230, 240, 255)
    GRID_LINE = (0, 50, 100)

    INACTIVE = (120, 120, 120)
    ACTIVE = (70, 180, 70)
    ERROR = (180, 70, 70)
    WIN = (50, 150, 50)
    SELECTED = (100, 150, 255)


class SudokuGame:

    def __init__(self, 
            path: str, 
            cell_size: int = 60, 
            button_height: int = 50
    ):
        """
        Đọc đường dẫn của các câu đố sudoku có sẵn
        Khởi tạo câu đó
        Khởi tạo game
        """
        # Kiểm tra file có tồn tại hay không
        assert os.path.exists(path)

        # Đọc toàn bộ câu đố
        with open(path, "r") as file:
            self.grids = file.readlines()

        # Khởi tạo các biến
        self.locked = None
        self.solved = None
        self.failed = None
        self.won = None
        self.lives = None
        self.history = None
        self.selected_cell = None

        # Khởi tạo trạng thái mặc định trừ mat
        self.reset()
        self.solver = SudokuSolver()
        # mat khởi tạo sẽ là ma trận sử dụng trong bài báo cáo
        self.mat = np.array([
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ], dtype=int)

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

    def reset(self) -> None:
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

    def load_grid(self, txt_grid: str) -> np.array:
        """
        Các bảng sudoku được viết theo kiểu chuỗi, 
        trong đó ma trận là dữ liệu ở giữa là chuỗi gồm 81 số
        """
        mat = np.array([int(num) for num in txt_grid]).reshape(9, 9)
        return mat
    
    def is_board_complete_and_valid(self, 
            mat: np.array, 
            locked: list[list[bool]]
    ) -> bool:
        """
        Kiểm tra sudoku đã được giải hay chưa
        """
        for i in range(9):
            for j in range(9):
                if mat[i][j] == 0 or (not locked[i][j] and not self.solver.is_safe(mat, i, j, mat[i][j])):
                    return False
        return True
    
    def draw_board(self, 
            screen: pygame.surface.Surface, 
            mat: np.array, 
            locked: list[list[bool]], 
            cell_size: int, 
            selected_cell: tuple[int]=None, 
            lives: int=3
    ) -> None:
        """
        Vẽ bảng, bao gồm tô màu các ô gợi ý, vẽ đường phân chia
            screen: Tạo màn hình từ pygame với kích thước width x heigh
            mat: Ma trận sudoku được lấy từ self.grid
            locked: Ma trận boolean các số đã được gợi ý
            cell_size: Kích thước mỗi ô
            selected_cell: Vị trí ô hiện tại đang chọn (x, y)
            lives: Số mạng còn lại của người chơi
        """
        screen.fill(Color.SCREEN.value)

        # Nền xám cho gợi ý 
        for i in range(9):
            for j in range(9):
                color = Color.GRAY.value if locked[i][j] else Color.WHITE.value
                pygame.draw.rect(screen, color, (j * cell_size, i * cell_size, cell_size, cell_size))

        # Vẽ các đường phân chia
        for i in range(10):
            thickness = 4 if i % 3 == 0 else 1 # Đường chia cắt các khối dày hơn
            pygame.draw.line(screen, Color.GRID_LINE.value, (i * cell_size, 0), (i * cell_size, 9 * cell_size), thickness)
            pygame.draw.line(screen, Color.GRID_LINE.value, (0, i * cell_size), (9 * cell_size, i * cell_size), thickness)
        
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

    def draw_button(self, 
            screen: pygame.surface.Surface, 
            text: str, 
            x: int, y: int, 
            w: int, h: int, 
            inactive_color, active_color, 
            text_color=Color.WHITE.value
    ) -> bool:
        """
        Vẽ các nút bấm vào, trả về giá trị True nếu bấm vào
            screen
            text: Nội dung nút bấm
            x, y: Toạ độ của nút bấm
            w, h: Chiều dài, chiều rộng của nút
            inactive_color: Màu sắc nếu không được rê chuột vào nút
            active_color: Màu sắc nếu được rê chuột vào nút
            text_color: Màu chữ
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

    def run(self) -> None:
        """
        Chạy game
        """
        pygame.display.set_caption("Sudoku Game")

        mat = self.mat
        locked = [[True if mat[i][j] != 0 else False for j in range(9)] for i in range(9)]

        # Bắt đầu game
        running = True

        while running:

            # Lấy các event
            for event in pygame.event.get():

                # Thoát game bằng nút X
                if event.type == pygame.QUIT:
                    running = False
                    
                if not self.failed and not self.won:

                    # Lấy vị trí chuột nếu bấm vào ô
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = pygame.mouse.get_pos()
                        if y < self.cell_size * 9:
                            i, j = y // self.cell_size, x // self.cell_size
                            if not locked[i][j]:
                                self.selected_cell = (i, j) # Lấy chỉ số của ô trong ma trận
                        else:
                            self.selected_cell = None

                    # Nhận giá trị từ bàn phím hoặc xoá
                    elif event.type == pygame.KEYDOWN and self.selected_cell:
                        i, j = self.selected_cell

                        # Xoá giá trị bằng delete hoặc backspace
                        if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                            mat[i][j] = 0

                        # Nhập số vào từ bàn phím
                        elif event.unicode.isdigit() and int(event.unicode) in range(1, 10):
                            num = int(event.unicode)
                            if self.solver.is_safe(mat, i, j, num):
                                mat[i][j] = num
                            else:
                                mat[i][j] = num
                                self.lives -= 1
                                if self.lives <= 0: # Đánh dấu là thua nếu hết mạng
                                    self.failed = True

            # Vẽ bảng
            self.draw_board(self.screen, mat, locked, self.cell_size, self.selected_cell, self.lives)

            # Nếu hết mạng hiện thông báo thua
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
                    # Reset lại lịch sử
                    self.history = SudokuHistory() 

                    # Phải copy ra để không thay đổi ma trận
                    result = mat.copy()
                    solvable = self.solver.solve_sudoku(result, 0, 0, self.history)
                    if solvable:
                        mat = result
                        self.solved = True
                        if self.failed:
                            self.failed = False
                    
                    self.history.to_csv("history.csv")

            # Nếu giải rồi thì huỷ nút Solve
            else:
                self.draw_button(self.screen, "Solved!", self.button_x_start, self.button_y, 
                            self.button_width, self.button_height,
                            Color.ACTIVE.value, Color.ACTIVE.value, Color.WHITE.value)

            # Nút làm mới bảng
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

            # Nút thoát game "Quit"
            if self.draw_button(
                self.screen, 
                "Quit", 
                self.button_x_start + (self.button_width + self.button_spacing) * 2, 
                self.button_y,
                self.button_width, self.button_height, 
                Color.INACTIVE.value, Color.ERROR.value
            ):
                running = False

            
            # Hiện thông báo chiến thắng
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