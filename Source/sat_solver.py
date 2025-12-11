# SAT solver dung pysat
# chuyen bai toan sang CNF roi giai

from pysat.solvers import Glucose3
from hashiwokakero import Puzzle, PuzzleState
from cnf_generator import HashiCNF
import time


class SATSolver:
    # dung pysat de giai
    
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.time_spent = 0
        self.stats = {}
    
    def solve(self):
        t1 = time.time()
        
        # chuyen puzzle thanh grid
        grid = self.puzzle.grid
        
        # tao HashiCNF va sinh cnf
        hashi = HashiCNF(grid)
        cnf = hashi.generate_cnf()
        
        self.stats = {
            'so_dao': len(hashi.islands),
            'so_cau_tiem_nang': len(hashi.bridges),
            'so_bien': cnf.nv,
            'so_menh_de': len(cnf.clauses)
        }
        
        # giai bang Glucose3
        solver = Glucose3()
        for clause in cnf.clauses:
            if len(clause) > 0:
                solver.add_clause(clause)
        
        if solver.solve():
            model = solver.get_model()
            state = self._decode_model(model, hashi)
            
            # kiem tra lien thong
            if not self.puzzle.is_connected(state):
                state = self._tim_lien_thong(solver, hashi)
            
            self.time_spent = time.time() - t1
            solver.delete()
            return state
        
        self.time_spent = time.time() - t1
        solver.delete()
        return None
    
    def _decode_model(self, model, hashi):
        # chuyen SAT model ve PuzzleState
        state = PuzzleState()
        model_set = set(model)
        
        for b in hashi.bridges:
            idx = b['idx']
            v1 = hashi.var_pool[(idx, 1)]
            v2 = hashi.var_pool[(idx, 2)]
            
            count = 0
            if v2 in model_set:
                count = 2
            elif v1 in model_set:
                count = 1
            
            if count > 0:
                r1 = b['u']['r']
                c1 = b['u']['c']
                r2 = b['v']['r']
                c2 = b['v']['c']
                
                isl1 = self.puzzle.island_map.get((r1, c1))
                isl2 = self.puzzle.island_map.get((r2, c2))
                
                if isl1 and isl2:
                    state.add_bridge(isl1, isl2, count)
        
        return state
    
    def _tim_lien_thong(self, solver, hashi):
        # neu ko lien thong thi block va thu lai
        max_lan = 1000
        
        for lan in range(max_lan):
            model = solver.get_model()
            if model is None:
                return None
            
            state = self._decode_model(model, hashi)
            
            if self.puzzle.is_connected(state):
                return state
            
            # block loi giai nay
            block = []
            for lit in model:
                if abs(lit) <= len(hashi.var_pool):
                    block.append(-lit)
            solver.add_clause(block)
            
            if not solver.solve():
                return None
        
        return None
    
    def get_stats(self):
        kq = dict(self.stats)
        kq["time"] = self.time_spent
        return kq


def solve_sat(puzzle):
    s = SATSolver(puzzle)
    kq = s.solve()
    return kq, s.time_spent, s.get_stats()
