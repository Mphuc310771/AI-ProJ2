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
        
        # giai
        solution = hashi.solve()
        
        self.time_spent = time.time() - t1
        
        if solution is None:
            return None
        
        # chuyen ket qua ve PuzzleState
        state = self._convert_to_state(solution)
        return state
    
    def _convert_to_state(self, solution_bridges):
        """Chuyen ket qua tu HashiCNF ve PuzzleState"""
        state = PuzzleState()
        
        for b in solution_bridges:
            r1, c1 = b['u']
            r2, c2 = b['v']
            count = b['count']
            
            # tim island tu toa do
            isl1 = self.puzzle.island_map.get((r1, c1))
            isl2 = self.puzzle.island_map.get((r2, c2))
            
            if isl1 and isl2:
                state.add_bridge(isl1, isl2, count)
        
        return state
    
    def get_stats(self):
        kq = dict(self.stats)
        kq["time"] = self.time_spent
        return kq


def solve_sat(puzzle):
    s = SATSolver(puzzle)
    kq = s.solve()
    return kq, s.time_spent, s.get_stats()
