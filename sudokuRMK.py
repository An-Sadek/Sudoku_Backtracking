import numpy as np
import pandas as pd
import random
import os
import time
import pygame 


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

class SudokuGame:

    def __init__(self, path):
        """
        Đọc đường dẫn của các câu đố sudoku có sãnư
        Khởi tạo câu đó
        Khởi tạo game
        """
        assert os.path.exists(path)
        with open(path, "r") as file:
            self.grids = file.readlines()

        self.grid = None
        self.reset()
        self.solver = SudokuSolver()

        pygame.init()

    def reset(self):
        txt_line = random.choice(self.grids).strip()
        parts = txt_line.split()
        self.grid = self.load_grid(parts[1])

    def load_grid(self, txt_grid: str):
        # Convert the 81-character string to a 9x9 numpy array
        mat = np.array([int(num) for num in txt_grid]).reshape(9, 9)
        return mat
    
    def is_board_complete_and_valid(self, mat, locked):
        for i in range(9):
            for j in range(9):
                if mat[i][j] == 0 or (not locked[i][j] and not self.solver.is_safe(mat, i, j, mat[i][j])):
                    return False
        return True
    
    def draw_board(self, screen, mat, locked, cell_size, selected_cell=None, lives=3):
        screen.fill((230, 240, 255))
        for i in range(9):
            for j in range(9):
                color = (200, 200, 200) if locked[i][j] else (255, 255, 255)
                pygame.draw.rect(screen, color, (j * cell_size, i * cell_size, cell_size, cell_size))
        for i in range(10):
            thickness = 4 if i % 3 == 0 else 1
            pygame.draw.line(screen, (0, 50, 100), (i * cell_size, 0), (i * cell_size, 9 * cell_size), thickness)
            pygame.draw.line(screen, (0, 50, 100), (0, i * cell_size), (9 * cell_size, i * cell_size), thickness)
        if selected_cell and not locked[selected_cell[0]][selected_cell[1]]:
            i, j = selected_cell
            pygame.draw.rect(screen, (100, 150, 255), (j * cell_size, i * cell_size, cell_size, cell_size), 4)
        font = pygame.font.Font(None, 40)
        for i in range(9):
            for j in range(9):
                if mat[i][j] != 0:
                    num = mat[i][j]
                    if locked[i][j]:
                        color = (0, 0, 0)  # Black for initial numbers
                    else:
                        color = (0, 255, 0) if self.solver.is_safe(mat, i, j, num) else (255, 0, 0)  # Green for correct, red for incorrect
                    text = font.render(str(num), True, color)
                    text_rect = text.get_rect(center=(j * cell_size + cell_size / 2, i * cell_size + cell_size / 2))
                    screen.blit(text, text_rect)
        font = pygame.font.Font(None, 36)
        lives_text = font.render(f"Lives: {lives}", True, (0, 0, 0))
        screen.blit(lives_text, (10, cell_size * 9 + 5))

    def draw_button(self, screen, text, x, y, w, h, inactive_color, active_color, text_color=(255, 255, 255)):
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
        """
        Hàm chạy game
        """
        cell_size = 60
        button_height = 50
        screen_width = cell_size * 9
        screen_height = cell_size * 9 + button_height * 2 + 20
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Sudoku Game")

        mat = self.grid.copy()
        locked = [[True if mat[i][j] != 0 else False for j in range(9)] for i in range(9)]

        # Colors
        INACTIVE_COLOR = (120, 120, 120)
        ACTIVE_COLOR = (70, 180, 70)
        ERROR_COLOR = (180, 70, 70)
        WIN_COLOR = (50, 150, 50)

        # Game state
        running = True
        solved = False
        failed = False
        won = False
        selected_cell = None
        lives = 3
        history = SudokuHistory()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if not failed and not won:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = pygame.mouse.get_pos()
                        if y < cell_size * 9:
                            i, j = y // cell_size, x // cell_size
                            if not locked[i][j]:
                                selected_cell = (i, j)
                        else:
                            selected_cell = None
                    elif event.type == pygame.KEYDOWN and selected_cell:
                        i, j = selected_cell
                        if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                            mat[i][j] = 0
                        elif event.unicode.isdigit() and int(event.unicode) in range(1, 10):
                            num = int(event.unicode)
                            if self.solver.is_safe(mat, i, j, num):
                                mat[i][j] = num
                            else:
                                mat[i][j] = num
                                lives -= 1
                                if lives <= 0:
                                    failed = True

            self.draw_board(screen, mat, locked, cell_size, selected_cell, lives)

            button_width = 120
            button_height = 40
            button_spacing = 20
            total_buttons_width = button_width * 3 + button_spacing * 2
            button_x_start = (screen_width - total_buttons_width) // 2
            button_y = cell_size * 9 + 30

            if failed and not solved:
                font = pygame.font.Font(None, 100)
                game_over_text = font.render("Game Over", True, ERROR_COLOR)
                text_rect = game_over_text.get_rect(center=(screen_width / 2, screen_height / 3))
                screen.blit(game_over_text, text_rect)

            if not solved:
                if self.draw_button(screen, "Solve", button_x_start, button_y, button_width, button_height,
                                   INACTIVE_COLOR, ACTIVE_COLOR):
                    solvable, result = self.solver.is_solvable(mat)
                    if solvable:
                        mat = result
                        solved = True
                        if failed:
                            failed = False
                        history.to_csv("sudoku_history.csv")
            else:
                self.draw_button(screen, "Solved!", button_x_start, button_y, button_width, button_height,
                                ACTIVE_COLOR, ACTIVE_COLOR, (255, 255, 255))

            if self.draw_button(screen, "New", button_x_start + button_width + button_spacing, button_y,
                               button_width, button_height, INACTIVE_COLOR, ACTIVE_COLOR):
                self.reset()
                mat = self.grid.copy()
                locked = [[True if mat[i][j] != 0 else False for j in range(9)] for i in range(9)]
                solved = False
                failed = False
                won = False
                lives = 3
                history = SudokuHistory()
                selected_cell = None

            if self.draw_button(screen, "Quit", button_x_start + (button_width + button_spacing) * 2, button_y,
                               button_width, button_height, INACTIVE_COLOR, ERROR_COLOR):
                running = False

            if not won and not failed and self.is_board_complete_and_valid(mat, locked):
                won = True

            if won:
                font = pygame.font.Font(None, 100)
                win_text = font.render("You Win!", True, WIN_COLOR)
                text_rect = win_text.get_rect(center=(screen_width / 2, screen_height / 3))
                screen.blit(win_text, text_rect)

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = SudokuGame("easy.txt")
    game.run()