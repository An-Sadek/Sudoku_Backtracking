import os
import random

import pygame
import numpy as np
from enum import Enum
from solver import SudokuSolver, SudokuHistory


class Color(Enum):

    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0) 

    SCREEN = (230, 240, 255) # Xanh dương nhạt
    GRID_LINE = (0, 50, 100) # Xanh dương đậm

    INACTIVE = (120, 120, 120) # Xám
    ACTIVE = (70, 180, 70) # Xanh lục
    QUIT = (180, 70, 70) # Đỏ đậm
    WIN = (50, 150, 50) # Xanh lục đậm
    SELECTED = (100, 150, 255) # Xanh dương


class SudokuGame:

    def __init__(self, 
            path: str, 
            cell_size: int = 60, 
            button_height: int = 50,
            button_width: int = 120,
            button_spacing: int = 20
    ):
        """
        Đọc đường dẫn của các câu đố sudoku có sẵn
        Chuyển câu đố sang dạng bảng
        Khởi tạo các biến
        Khởi tạo game
            path: Đường dẫn đến ngân hàng câu đố
            cell_size: Kích thước mỗi ô trong bảng câu đố
            button_height: Chiều dài của nút bấm
            button_width: Chiều rộng của nút bấm
            button_spacing: Khoảng cách của nút bấm
        """
        # Kiểm tra file có tồn tại hay không
        assert os.path.exists(path)

        # Đọc toàn bộ câu đố
        with open(path, "r") as file:
            self.grids = file.readlines()

        # Khởi tạo các biến
        """
        locked: Bảng 9x9 các phần từ boolean. Phần tử mang giá trị True khi phần tử đố là gợi ý (số khác 0)
        solved: Giá trị boolean thể hiện câu đố đã được giải hay chưa. Giá trị khởi tạo là False
        won: Giá trị boolean thể hiện người chơi đã chiến thắng. Giá trị khởi tạo là False
        history: Là lớp SudokuHistory lưu lại quá trình giải của backtracking. Lớp SudokuHistory được khởi tạo sẽ là rỗng.
        selected_cell: Là tuple vị trí (x, y) của ô đã chọn. Giá trị khởi tạo là None và khi không chọn vào ô sẽ là None.
        """
        self.locked: tuple[int] = None
        self.solved: bool = None
        self.won: bool = None
        self.history: SudokuHistory = None
        self.selected_cell: tuple[int] = None

        # Khởi tạo trạng thái mặc định trừ mat
        self.reset()
        self.solver = SudokuSolver()
        # mat khởi tạo và locked sẽ là ma trận sử dụng trong bài báo cáo
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
        self.locked = [[True if self.mat[i][j] != 0 else False for j in range(9)] for i in range(9)]

        # Khởi tạo game, tạo screen, lưu thuộc tính
        pygame.init()

        self.cell_size = cell_size
        self.button_height = button_height
        self.button_width = button_width
        self.button_spacing = button_spacing

        self.screen_width = cell_size * 9
        self.total_buttons_width = self.button_width * 3 + self.button_spacing * 2
        self.button_x_start = (self.screen_width - self.total_buttons_width) // 2
        self.button_y_start = self.cell_size * 9 + 40

        self.screen_height = cell_size * 9 + 100
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.screen.fill(Color.SCREEN.value)

    def reset(self) -> None:
        """
        Reset lại trạng thái bằng cách lấy một bảng sudoku ngẫu nhiên
        """
        txt_line = random.choice(self.grids).strip() # Lấy một dòng ngẫu nhiên
        parts = txt_line.split() # Tách ra từng phần, do mỗi cột cách nhau bởi dấu cách
        self.mat = self.load_grid(parts[1]) # Lấy giá trị thứ 2, chỉ số 1 là câu đố sudoku

        # Đặt lại các giá trị
        self.locked = [[True if self.mat[i][j] != 0 else False for j in range(9)] for i in range(9)]
        self.solved = False
        self.won = False
        self.history = SudokuHistory()
        self.selected_cell = None

    def load_grid(self, txt_grid: str) -> np.array:
        """
        Các bảng sudoku được viết theo kiểu chuỗi, 
        trong đó ma trận là dữ liệu ở giữa là chuỗi gồm 81 số.
        Chuyển về dạng ma trận (1, 81), dùng reshape để chuyển vè dạng bảng 9 x 9.
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
            selected_cell: tuple[int]=None
    ) -> None:
        """
        Vẽ bảng câu đố, bao gồm tô màu các ô gợi ý, vẽ đường phân chia
            screen: Tạo màn hình từ pygame với kích thước width x height
            mat: Ma trận sudoku được lấy từ self.grid
            locked: Ma trận boolean các số đã được gợi ý
            cell_size: Kích thước mỗi ô
            selected_cell: Vị trí ô hiện tại đang chọn (x, y)
        """
        # Tô màu cho ô, màu xám nếu thuộc ô gợi ý
        for i in range(9):
            for j in range(9):
                color = Color.GRAY.value if locked[i][j] else Color.WHITE.value
                pygame.draw.rect(
                    screen, 
                    color, 
                    (j * cell_size, i * cell_size, cell_size, cell_size)
                )

        # Vẽ các đường phân chia
        for i in range(10):
            thickness = 4 if i % 3 == 0 else 1 # Đường chia cắt các khối dày hơn

            # Vẽ theo trục tung Oy
            pygame.draw.line(
                screen, # Màn hình
                Color.GRID_LINE.value, # Chọn màu
                (i * cell_size, 0), # Toạ độ đầu
                (i * cell_size, 9 * cell_size), # Toạ độ cuối
                thickness # Độ dày của đường
            )
            
            # Vẽ theo trung hoành Ox
            pygame.draw.line(
                screen, 
                Color.GRID_LINE.value, 
                (0, i * cell_size), 
                (9 * cell_size, i * cell_size), 
                thickness
            )
        
        # Vẽ đường viền cho ô đang được chọn (trừ ô gợi ý)
        if selected_cell and not locked[selected_cell[0]][selected_cell[1]]:
            i, j = selected_cell
            pygame.draw.rect(screen, Color.SELECTED.value, (j * cell_size, i * cell_size, cell_size, cell_size), 4)
        
        # Tạo font chữ
        font = pygame.font.Font(None, 40)

        for i in range(9):
            for j in range(9):
                if mat[i][j] != 0:
                    num = mat[i][j]
                    if locked[i][j]:
                        color = Color.BLACK.value  # Các ô gợi ý có chữ đen
                    else:
                        color = Color.GREEN.value # Các ô trống có chữ màu lục

                    text = font.render(str(num), True, color)
                    text_rect = text.get_rect(center=(j * cell_size + cell_size / 2, i * cell_size + cell_size / 2))
                    screen.blit(text, text_rect)

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
            screen: Màn hình game
            text: Nội dung nút bấm
            x, y: Toạ độ của nút bấm
            w, h: Chiều dài, chiều rộng của nút
            inactive_color: Màu sắc nếu không được rê chuột vào nút
            active_color: Màu sắc nếu được rê chuột vào nút
            text_color: Màu chữ
        """
        # Lấy vị trí chuột
        mouse = pygame.mouse.get_pos()

        # Kiểm tra xem được nhấn chưa
        click = pygame.mouse.get_pressed()

        # Chọn màu cho nút khi chưa được và được rê chuột vào
        is_in_area = x + w > mouse[0] > x and y + h > mouse[1] > y
        color = active_color if is_in_area else inactive_color
        pygame.draw.rect(screen, color, (x, y, w, h), border_radius=10)
        font = pygame.font.Font(None, 36)

        # Tạo text 
        text_surf = font.render(text, True, text_color)

        # Tạo rect
        text_rect = text_surf.get_rect(center=(x + w / 2, y + h / 2))
        screen.blit(text_surf, text_rect) # Hiện lên surface

        return click[0] == 1 and is_in_area

    def run(self) -> None:
        """
        Chạy game
        """
        pygame.display.set_caption("Sudoku Game")

        # Bắt đầu game
        running = True

        while running:

            # Lấy các event
            for event in pygame.event.get():

                # Thoát game bằng nút X
                if event.type == pygame.QUIT:
                    running = False
                    
                # Nếu chưa thắng trò chơi
                if not self.won:

                    # Lấy vị trí chuột nếu bấm vào ô
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = pygame.mouse.get_pos()

                        # Nếu bấm chuột trong phạm vi 9 ô lấy chỉ số
                        if y < self.cell_size * 9:
                            i, j = y // self.cell_size, x // self.cell_size
                            if not self.locked[i][j]:
                                self.selected_cell = (i, j) # Lấy chỉ số của ô trong ma trận
                        else:
                            self.selected_cell = None

                    # Nhận giá trị từ bàn phím hoặc xoá
                    elif event.type == pygame.KEYDOWN and self.selected_cell:
                        i, j = self.selected_cell

                        # Xoá giá trị bằng delete hoặc backspace
                        if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                            self.mat[i][j] = 0

                        # Nhập số vào từ bàn phím
                        elif event.unicode.isdigit() and int(event.unicode) in range(1, 10):
                            num = int(event.unicode)
                            self.mat[i][j] = num

            # Vẽ bảng
            self.draw_board(self.screen, self.mat, self.locked, self.cell_size, self.selected_cell)

            # Hiện thông báo chiến thắng
            if not self.won and self.is_board_complete_and_valid(self.mat, self.locked):
                self.solved = True
                self.won = True

            if self.won:
                font = pygame.font.Font(None, 100)
                win_text = font.render("You Win!", True, Color.WIN.value)
                text_rect = win_text.get_rect(center=(self.screen_width / 2, self.cell_size*9 / 3))
                self.screen.blit(win_text, text_rect)


            if not self.solved:

                # Vẽ nút "Solve", nếu bấm vào thì giải luôn
                if self.draw_button(
                    self.screen, "Solve", 
                    self.button_x_start, self.button_y_start, 
                    self.button_width, self.button_height,
                    Color.INACTIVE.value, Color.ACTIVE.value
                ):
                    # Giải câu đố bằng hàm solve_sudoku
                    solvable = self.solver.solve_sudoku(self.mat, 0, 0, self.history)
                    if solvable:
                        self.solved = True
                    
                    self.history.to_csv("history.csv")

            # Nếu giải rồi thì huỷ nút Solve
            else:
                self.draw_button(self.screen, "Solved!", self.button_x_start, self.button_y_start, 
                            self.button_width, self.button_height,
                            Color.ACTIVE.value, Color.ACTIVE.value, Color.WHITE.value)

            # Nút làm mới bảng
            if self.draw_button(
                self.screen, "New", 
                self.button_x_start + self.button_width + self.button_spacing, 
                self.button_y_start, self.button_width, self.button_height, 
                Color.INACTIVE.value, Color.ACTIVE.value
            ):
                self.reset()

            # Nút thoát game "Quit"
            if self.draw_button(
                self.screen, 
                "Quit", 
                self.button_x_start + (self.button_width + self.button_spacing) * 2, 
                self.button_y_start,
                self.button_width, self.button_height, 
                Color.INACTIVE.value, Color.QUIT.value
            ):
                running = False
            
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    game = SudokuGame("easy.txt")
    game.run()