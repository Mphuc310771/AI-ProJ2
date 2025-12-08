"""
Giải Hashiwokakero bằng PySAT
"""
from pysat.solvers import Glucose3
from hashiwokakero import Puzzle, PuzzleState
from cnf_generator import CNFGenerator
import time


class SATSolver:
    """Dùng thư viện pysat để giải"""
    
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.cnf_gen = CNFGenerator(puzzle)
        self.thoi_gian = 0
        self.stats = {}
    
    def solve(self):
        """Giải puzzle, trả về PuzzleState nếu tìm được, None nếu không"""
        start = time.time()
        
        # sinh mệnh đề CNF
        clauses = self.cnf_gen.sinh_tat_ca_menh_de()
        self.stats = self.cnf_gen.get_stats()
        
        # tạo solver và thêm các mệnh đề
        solver = Glucose3()
        for clause in clauses:
            if clause:  # bỏ qua mệnh đề rỗng
                solver.add_clause(clause)
        
        # giải
        if solver.solve():
            model = solver.get_model()
            state = self.cnf_gen.giai_ma_ket_qua(model)
            
            # kiểm tra liên thông
            if not self.puzzle.is_connected(state):
                state = self._tim_loi_giai_lien_thong(solver)
            
            self.thoi_gian = time.time() - start
            solver.delete()
            return state
        
        self.thoi_gian = time.time() - start
        solver.delete()
        return None
    
    def _tim_loi_giai_lien_thong(self, solver):
        """
        Nếu lời giải không liên thông, thử tìm lời giải khác
        Cách làm: block lời giải hiện tại và giải lại
        """
        max_tries = 1000
        
        for _ in range(max_tries):
            model = solver.get_model()
            if model is None:
                return None
            
            state = self.cnf_gen.giai_ma_ket_qua(model)
            
            if self.puzzle.is_connected(state):
                return state
            
            # block lời giải này
            block = [-lit for lit in model if abs(lit) <= len(self.cnf_gen.var_map)]
            solver.add_clause(block)
            
            if not solver.solve():
                return None
        
        return None
    
    def get_dimacs(self):
        return self.cnf_gen.to_dimacs()
    
    def get_stats(self):
        s = self.stats.copy()
        s["thoi_gian"] = self.thoi_gian
        return s


def solve_with_pysat(puzzle):
    """Hàm tiện ích để giải puzzle"""
    solver = SATSolver(puzzle)
    solution = solver.solve()
    return solution, solver.thoi_gian, solver.get_stats()
