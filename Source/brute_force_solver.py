"""
Giải Hashiwokakero bằng Brute-force (vét cạn)
Chậm nhất nhưng đảm bảo tìm được nghiệm nếu có
"""
from hashiwokakero import Puzzle, PuzzleState
from itertools import product
import time


class BruteForceSolver:
    """
    Vét cạn tất cả các tổ hợp cầu có thể
    Số tổ hợp = 3^n với n là số cặp đảo có thể nối
    """
    
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.thoi_gian = 0
        self.so_config_da_thu = 0
    
    def solve(self):
        """Thử tất cả các tổ hợp"""
        start = time.time()
        self.so_config_da_thu = 0
        
        possible = self.puzzle.get_possible_bridges()
        n = len(possible)
        
        # cảnh báo nếu quá lớn
        if n > 20:
            print(f"Cảnh báo: {n} cặp đảo = {3**n} tổ hợp, sẽ rất lâu!")
        
        # thử từng tổ hợp
        for config in product(range(3), repeat=n):
            self.so_config_da_thu += 1
            
            # tạo state từ config
            state = PuzzleState()
            for i, count in enumerate(config):
                if count > 0:
                    island1, island2 = possible[i]
                    state.bridges[(island1, island2)] = count
            
            # kiểm tra
            if self.puzzle.is_solution(state):
                self.thoi_gian = time.time() - start
                return state
            
            # in tiến độ
            if self.so_config_da_thu % 100000 == 0:
                elapsed = time.time() - start
                print(f"Đã thử {self.so_config_da_thu} tổ hợp ({elapsed:.1f}s)...")
        
        self.thoi_gian = time.time() - start
        return None
    
    def get_stats(self):
        n = len(self.puzzle.get_possible_bridges())
        return {
            "thoi_gian": self.thoi_gian,
            "so_config_da_thu": self.so_config_da_thu,
            "tong_so_config": 3 ** n,
            "so_cap_dao": n,
            "algorithm": "Brute-force"
        }


def solve_with_bruteforce(puzzle):
    solver = BruteForceSolver(puzzle)
    solution = solver.solve()
    return solution, solver.thoi_gian, solver.get_stats()
