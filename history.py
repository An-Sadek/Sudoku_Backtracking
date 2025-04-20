import pandas as pd


class SudokuHistory:

    def __init__(self):
        
        self.location = []
        self.is_empty = []
        self.num_input = []
        self.num_valid = []
        self.move = []
        self.next_location = []

    def add_record(self, 
            location: tuple[int], 
            is_empty: bool, 
            num_input: int, 
            num_valid: bool, 
            move: int, 
            next_location: tuple[int]
    ) -> None:
        """
            location: Danh sách vị trí hiện tại đang xét
            is_empty: Xét vị trí hiện tại có trống hay không
            num_input: Giá trị đầu vào của ô đang xét
            num_valid: Giá trị đầu vào hợp lệ (không trùng số của hàng, cột, ma trận con)
            move: Di chuyển đến ô tiếp theo, hoặc không di chuyển, hoặc lùi lại sang ô phía trước
            next_location: Ô tiếp theo sẽ di chuyển đến
        """
        self.location.append(location)
        self.is_empty.append(is_empty)
        self.num_input.append(num_input)
        self.num_valid.append(num_valid)
        self.move.append(move)
        self.next_location.append(next_location)

    def to_csv(self, path: str) -> pd.DataFrame:
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
    
