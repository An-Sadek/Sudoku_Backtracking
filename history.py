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