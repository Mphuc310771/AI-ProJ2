from pysat.solvers import Glucose3
from hashiwokakero import Puzzle, PuzzleState
from cnf_generator import HashiCNF
import time


class SATSolver:
    
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.tg_chay = 0
        self.thong_ke = {}
    
    def solve(self):
        t1 = time.time()
        
        hashi = HashiCNF(self.puzzle.grid)
        cnf = hashi.generate_cnf()
        
        self.thong_ke = {
            'so_dao': len(hashi.islands),
            'so_cau_tiem_nang': len(hashi.bridges),
            'so_bien': cnf.nv,
            'so_menh_de': len(cnf.clauses)
        }
        
        solver = Glucose3()
        for menh_de in cnf.clauses:
            if len(menh_de) > 0:
                solver.add_clause(menh_de)
        
        if solver.solve():
            model = solver.get_model()
            state = self._giai_ma(model, hashi)
            
            # kiem tra lien thong, neu chua thi tim tiep
            if not self.puzzle.is_connected(state):
                state = self._tim_lien_thong(solver, hashi)
            
            self.tg_chay = time.time() - t1
            solver.delete()
            return state
        
        self.tg_chay = time.time() - t1
        solver.delete()
        return None
    
    def _giai_ma(self, model, hashi):
        # chuyen model SAT thanh PuzzleState
        state = PuzzleState()
        tap_model = set(model)
        
        for b in hashi.bridges:
            idx = b['idx']
            v1 = hashi.var_pool[(idx, 1)]
            v2 = hashi.var_pool[(idx, 2)]
            
            so_cau = 0
            if v2 in tap_model:
                so_cau = 2
            elif v1 in tap_model:
                so_cau = 1
            
            if so_cau > 0:
                r1, c1 = b['u']['r'], b['u']['c']
                r2, c2 = b['v']['r'], b['v']['c']
                
                dao1 = self.puzzle.island_map.get((r1, c1))
                dao2 = self.puzzle.island_map.get((r2, c2))
                
                if dao1 and dao2:
                    state.add_bridge(dao1, dao2, so_cau)
        
        return state
    
    def _tim_lien_thong(self, solver, hashi):
        # thu nhieu loi giai de tim cai lien thong
        so_lan_thu = 1000
        
        for _ in range(so_lan_thu):
            model = solver.get_model()
            if model is None:
                return None
            
            state = self._giai_ma(model, hashi)
            
            if self.puzzle.is_connected(state):
                return state
            
            # block loi giai hien tai va tim tiep
            block_clause = []
            for lit in model:
                if abs(lit) <= len(hashi.var_pool):
                    block_clause.append(-lit)
            
            solver.add_clause(block_clause)
            
            if not solver.solve():
                return None
        
        return None
    
    def get_stats(self):
        kq = dict(self.thong_ke)
        kq["time"] = self.tg_chay
        return kq

def solve_sat(puzzle):
    solver = SATSolver(puzzle)
    kq = solver.solve()
    return kq, solver.tg_chay, solver.get_stats()
