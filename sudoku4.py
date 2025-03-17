import numpy as np
import pandas as pd


class SudokuHistory:
	def __init__(self):
		self.location = []
		self.is_empty = []
		self.loop = []
		self.num_input = []
		self.num_valid = []
		self.move = []
		self.next_location = []

	def __getitem__(self, idx):
		return (
			self.location[idx],
			self.is_empty[idx],
			self.loop[idx],
			self.num_input[idx],
			self.num_valid[idx],
			self.move[idx],
			self.next_location[idx]
		)

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

			# Backtracking
			mat[row][col] = 0
			history.add_record((row, col), True, loop, num, True, -1, (row, col))

	# If no number works, backtrack to the previous position
	prev_col = col - 1 if col > 0 else 3
	prev_row = row if col > 0 else row - 1
	if prev_row >= 0:  # Ensure we don't backtrack out of bounds
		history.add_record((row, col), True, loop, None, False, -1, (prev_row, prev_col))
	return False, mat, history


if __name__ == "__main__":
	history = SudokuHistory()
	# mat = np.zeros((4, 4), dtype=int)
	mat = np.array([
		[1, 0, 0, 0],
		[0, 2, 0, 0],
		[0, 0, 0, 3],
		[0, 0, 4, 0]
	])

	solvable, result, history = solve_sudoku(mat, 0, 0, history)
	
	print(result)
	
	for i in range(len(history.location)):
		print(f"Step {i}: Location {history.location[i]}, Input {history.num_input[i]}, Valid {history.num_valid[i]}, Move {history.move[i]}, Next {history.next_location[i]}")

	history.to_csv("history.csv")