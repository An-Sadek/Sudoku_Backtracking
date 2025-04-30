from typing import Tuple

import time
import numpy as np
from history import SudokuHistory


class SudokuSolver:

    def __init__(self):
        pass 

    def is_safe(self, 
            mat: np.array, 
            row: int, 
            col: int, 
            num: int
    ) -> bool:
        """
        Kiểm tra giá trị đầu vào có trùng với giá trị units không
        """
        # Kiểm tra hàng
        if num in mat[row, :]:
            return False
        
        # Kiểm tra cột
        if num in mat[:, col]:
            return False
        
        # Kiểm tra khối
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        if num in mat[start_row:start_row + 3, start_col:start_col + 3]:
            return False
        
        return True

    def solve_sudoku(self, 
            mat: np.array, 
            row: int, 
            col: int, 
            history: SudokuHistory
    ) -> bool:
        """
        Giải sudoku, trả về kết quả fail nếu thời gian vượt quá quy định
        Hoặc không giải được do cấu hình
        """

        # Nếu đạt tới hàng thứ 10 (index 9) thì hoàn thành
        if row == 9:
            return True
        
        # Nếu vượt cột thì xuống hàng tiếp
        if col == 9:
            return self.solve_sudoku(mat, row + 1, 0, history)
        
        # Bỏ qua những giá trị không rỗng
        if mat[row][col] != 0:
            history.add_record((row, col), False, None, None, 1, (row, col + 1))
            return self.solve_sudoku(mat, row, col + 1, history)
        
        # Duyệt từng giá trị
        for num in range(1, 10):

            # Kiểm tra giá trị hợp lệ
            valid = self.is_safe(mat, row, col, num)
            history.add_record((row, col), True, num, valid, None, None)

            # Nếu hợp lệ
            if valid:
                mat[row][col] = num
                history.add_record((row, col), None, None, None, 1, (row, col + 1))
                solvable = self.solve_sudoku(mat, row, col + 1, history)

                # Nếu đã giải xong thì trả về True
                if solvable:
                    return True
                
                # Nếu chưa giải xong thì backtracking
                mat[row][col] = 0
                history.add_record((row, col), None, None, None, -1, (row, col))

        # Lưu lịch sử, không ảnh hướng đến giải thuật
        prev_col = col - 1 if col > 0 else 8
        prev_row = row if col > 0 else row - 1
        if prev_row >= 0:
            history.add_record((row, col), None, None, None, -1, (prev_row, prev_col))

        # Trả về False
        return False
        
    
if __name__ == "__main__":
    mat = np.array([
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

    history = SudokuHistory()
    solver = SudokuSolver()
    solvable = solver.solve_sudoku(mat, 0, 0, history)
    print(mat)
    history.to_csv("history.csv")

