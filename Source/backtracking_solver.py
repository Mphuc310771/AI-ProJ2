"""
Giải Hashiwokakero bằng Backtracking (quay lui)
Hiệu quả hơn brute-force nhờ cắt tỉa
"""
from hashiwokakero import Puzzle, PuzzleState, Island
import time


class BacktrackingSolver:
    """
    Thuật toán quay lui với cắt tỉa:
    - Dừng sớm khi đảo có quá nhiều cầu
    - Dừng sớm khi đảo không thể đạt đủ cầu
    - Dừng sớm khi cầu giao nhau
    """
    
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.thoi_gian = 0
        self.nodes = 0
        self.backtracks = 0
        self.ket_qua = None
    
    def solve(self):
        start = time.time()
        self.nodes = 0
        self.backtracks = 0
        self.ket_qua = None
        
        possible = self.puzzle.get_possible_bridges()
        init_state = PuzzleState()
        
        self._backtrack(init_state, possible, 0)
        
        self.thoi_gian = time.time() - start
        return self.ket_qua
    
    def _backtrack(self, state, bridges, idx):
        """Đệ quy quay lui"""
        if self.ket_qua is not None:
            return True
        
        self.nodes += 1
        
        # cắt tỉa: kiểm tra có khả thi không
        if not self._co_kha_thi(state):
            self.backtracks += 1
            return False
        
        # đã gán hết các cầu?
        if idx >= len(bridges):
            if self.puzzle.is_solution(state):
                self.ket_qua = state.copy()
                return True
            self.backtracks += 1
            return False
        
        island1, island2 = bridges[idx]
        
        # thử 0, 1, 2 cầu
        for count in range(3):
            if count > 0:
                if not self._co_the_them_cau(state, island1, island2, count):
                    continue
            
            new_state = state.copy()
            if count > 0:
                new_state.bridges[(island1, island2)] = count
            
            # kiểm tra giao nhau
            if count > 0 and self._bi_giao(state, island1, island2):
                continue
            
            if self._backtrack(new_state, bridges, idx + 1):
                return True
        
        self.backtracks += 1
        return False
    
    def _co_kha_thi(self, state):
        """Kiểm tra có thể dẫn đến lời giải không"""
        for island in self.puzzle.islands:
            current = state.get_island_bridge_count(island, self.puzzle.neighbors[island])
            
            # quá nhiều cầu rồi
            if current > island.value:
                return False
            
            # còn thiếu bao nhiêu?
            needed = island.value - current
            
            # có đủ chỗ không?
            available = 0
            for neighbor in self.puzzle.neighbors[island]:
                now = state.get_bridge_count(island, neighbor)
                can_add = 2 - now
                
                # láng giềng còn chỗ không?
                neighbor_current = state.get_island_bridge_count(neighbor, self.puzzle.neighbors[neighbor])
                neighbor_space = neighbor.value - neighbor_current
                can_add = min(can_add, neighbor_space)
                
                available += max(0, can_add)
            
            if available < needed:
                return False
        
        return True
    
    def _co_the_them_cau(self, state, island1, island2, count):
        """Kiểm tra có thể thêm 'count' cầu không"""
        c1 = state.get_island_bridge_count(island1, self.puzzle.neighbors[island1])
        c2 = state.get_island_bridge_count(island2, self.puzzle.neighbors[island2])
        
        if c1 + count > island1.value:
            return False
        if c2 + count > island2.value:
            return False
        
        return True
    
    def _bi_giao(self, state, island1, island2):
        """Kiểm tra cầu mới có giao cầu cũ không"""
        for (i1, i2), cnt in state.bridges.items():
            if cnt > 0:
                if self.puzzle.bridges_cross(island1, island2, i1, i2):
                    return True
        return False
    
    def get_stats(self):
        return {
            "thoi_gian": self.thoi_gian,
            "nodes": self.nodes,
            "backtracks": self.backtracks,
            "algorithm": "Backtracking"
        }


def solve_with_backtracking(puzzle):
    solver = BacktrackingSolver(puzzle)
    solution = solver.solve()
    return solution, solver.thoi_gian, solver.get_stats()
