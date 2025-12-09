# SAT solver dung pysat
# chuyen bai toan sang CNF roi giai

from pysat.solvers import Glucose3
from hashiwokakero import Puzzle, PuzzleState
from cnf_generator import CNFGenerator
import time


class SATSolver:
    # dung pysat de giai
    
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.gen = CNFGenerator(puzzle)
        self.time_spent = 0
        self.stats = {}
    
    def solve(self):
        t1 = time.time()
        
        # sinh cnf
        cac_menh_de = self.gen.generate_all()
        self.stats = self.gen.get_stats()
        
        # tao solver
        solver = Glucose3()
        for md in cac_menh_de:
            if len(md) > 0:
                solver.add_clause(md)
        
        # giai
        if solver.solve():
            model = solver.get_model()
            state = self.gen.decode(model)
            
            # kiem tra lien thong
            if not self.puzzle.is_connected(state):
                # thu tim loi giai khac
                state = self._tim_loi_giai_lien_thong(solver)
            
            self.time_spent = time.time() - t1
            solver.delete()
            return state
        
        self.time_spent = time.time() - t1
        solver.delete()
        return None
    
    def _tim_loi_giai_lien_thong(self, solver):
        # neu loi giai ko lien thong thi block va thu lai
        max_lan = 1000
        
        for lan in range(max_lan):
            model = solver.get_model()
            if model == None:
                return None
            
            state = self.gen.decode(model)
            
            if self.puzzle.is_connected(state):
                return state
            
            # block loi giai nay
            block = []
            for lit in model:
                if abs(lit) <= len(self.gen.var_map):
                    block.append(-lit)
            solver.add_clause(block)
            
            if not solver.solve():
                return None
        
        return None
    
    def get_dimacs(self):
        return self.gen.to_dimacs()
    
    def get_stats(self):
        kq = dict(self.stats)
        kq["time"] = self.time_spent
        return kq


def solve_sat(puzzle):
    s = SATSolver(puzzle)
    kq = s.solve()
    return kq, s.time_spent, s.get_stats()
