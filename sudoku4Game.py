import numpy as np
import pandas as pd
import pygame

# Initialize Pygame
pygame.init()

# Window settings
WIDTH = 400
HEIGHT = 500
GRID_SIZE = 4
CELL_SIZE = WIDTH // GRID_SIZE
LINE_WIDTH = 2
BUTTON_HEIGHT = 80

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
GREEN = (0, 200, 0)
RED = (200, 0, 0)  # Added for "Can't solve" state

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("4x4 Sudoku Solver")
font = pygame.font.Font(None, 40)
button_font = pygame.font.Font(None, 50)

class SudokuHistory:
    def __init__(self):
        self.location = []
        self.is_empty = []
        self.loop = []
        self.num_input = []
        self.num_valid = []
        self.move = []
        self.next_location = []

    def add_record(self, location, is_empty, loop, num_input, num_valid, move, next_location):
        self.location.append(location)
        self.is_empty.append(is_empty)
        self.loop.append(loop)
        self.num_input.append(num_input)
        self.num_valid.append(num_valid)
        self.move.append(move)
        self.next_location.append(next_location)
        
    def to_csv(self, path):
        df = pd.DataFrame({
            "location": self.location,
            "is_empty": self.is_empty,
            "loop": self.loop, 
            "num_input": self.num_input,
            "num_valid": self.num_valid,
            "move": self.move, 
            "next_location": self.next_location
        })
        df.to_csv(path, index=False)

def is_safe(mat: np.ndarray, row, col, num):
    if num in mat[row, :]:
        return False
    if num in mat[:, col]:
        return False 
    startRow, startCol = row - row % 2, col - col % 2
    if num in mat[startRow:startRow+2, startCol:startCol+2]:
        return False
    return True

def solve_sudoku(mat, row, col, history: SudokuHistory, loop=0):
    if row == 4:
        return True, mat, history
    if col == 4:
        return solve_sudoku(mat, row + 1, 0, history, loop)
    if mat[row][col] != 0:
        history.add_record((row, col), False, None, None, None, 1, (row, col + 1))
        return solve_sudoku(mat, row, col + 1, history, loop)
    
    for num in range(1, 5):
        valid = is_safe(mat, row, col, num)
        history.add_record((row, col), True, loop, num, valid, None, None)
        
        if valid:
            mat[row][col] = num
            history.add_record((row, col), True, loop, num, True, 1, (row, col + 1))
            solvable, mat, history = solve_sudoku(mat, row, col + 1, history, loop + 1)
            if solvable:
                return True, mat, history
            mat[row][col] = 0
            history.add_record((row, col), True, loop, num, True, -1, (row, col))
    
    prev_col = col - 1 if col > 0 else 3
    prev_row = row if col > 0 else row - 1
    if prev_row >= 0:
        history.add_record((row, col), True, loop, None, False, -1, (prev_row, prev_col))
    return False, mat, history

def draw_grid(mat):
    screen.fill(WHITE)
    
    for i in range(GRID_SIZE + 1):
        thickness = LINE_WIDTH * 2 if i % 2 == 0 else LINE_WIDTH
        pygame.draw.line(screen, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, WIDTH), thickness)
        pygame.draw.line(screen, BLACK, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), thickness)

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if mat[i][j] != 0:
                text = font.render(str(mat[i][j]), True, BLUE)
                text_rect = text.get_rect(center=(j * CELL_SIZE + CELL_SIZE//2, 
                                                i * CELL_SIZE + CELL_SIZE//2))
                screen.blit(text, text_rect)

def draw_button(state):
    button_rect = pygame.Rect(100, HEIGHT - BUTTON_HEIGHT - 10, 200, BUTTON_HEIGHT)
    if state == "unsolved":
        pygame.draw.rect(screen, GREEN, button_rect)
        text = button_font.render("Solve", True, WHITE)
    elif state == "solved":
        pygame.draw.rect(screen, GRAY, button_rect)
        text = button_font.render("Solved", True, WHITE)
    else:  # can't solve
        pygame.draw.rect(screen, RED, button_rect)
        text = button_font.render("Can't solve", True, WHITE)
    
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)
    return button_rect

def main():
    original_mat = np.array([
        [1, 1, 0, 0],
        [0, 2, 0, 0],
        [0, 0, 0, 3],
        [0, 0, 4, 0]
    ])
    
    current_mat = original_mat.copy()
    history = SudokuHistory()
    state = "unsolved"  # Can be "unsolved", "solved", or "cant_solve"
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and state == "unsolved":
                if button_rect.collidepoint(event.pos):
                    solvable, current_mat, history = solve_sudoku(original_mat.copy(), 0, 0, history)
                    if solvable:
                        state = "solved"
                        history.to_csv("sudoku.csv")
                    else:
                        state = "cant_solve"
        
        draw_grid(current_mat)
        button_rect = draw_button(state)
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()