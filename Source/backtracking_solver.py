# backtracking solver cho hashiwokakero
# su dung ky thuat quay lui va cat tia

from hashiwokakero import Puzzle, PuzzleState, Island
import time


class BacktrackingSolver:
    # quay lui voi cat tia (pruning)
    
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.time_spent = 0
        self.dem_node = 0
        self.dem_backtrack = 0
        self.kq = None  # ket qua
    
    def solve(self):
        t1 = time.time()
        self.dem_node = 0
        self.dem_backtrack = 0
        self.kq = None
        
        # lay danh sach cac cap dao co the noi
        cac_cau = self.puzzle.get_possible_bridges()
        state = PuzzleState()
        
        # bat dau quay lui
        self._bt(state, cac_cau, 0)
        
        self.time_spent = time.time() - t1
        return self.kq
    
    def _bt(self, state, cac_cau, idx):
        # ham de quy chinh
        
        # da tim thay roi thi return
        if self.kq != None:
            return True
        
        self.dem_node = self.dem_node + 1
        
        # cat tia: kiem tra feasibility  
        if not self._check_feasible(state):
            self.dem_backtrack += 1
            return False
        
        # het cau de xet
        if idx >= len(cac_cau):
            if self.puzzle.is_solution(state):
                self.kq = state.copy()
                return True
            self.dem_backtrack += 1
            return False
        
        dao1, dao2 = cac_cau[idx]
        
        # thu lan luot 0, 1, 2 cau
        for so_cau in [0, 1, 2]:
            if so_cau > 0:
                if not self._co_the_them(state, dao1, dao2, so_cau):
                    continue
            
            state_moi = state.copy()
            if so_cau > 0:
                state_moi.bridges[(dao1, dao2)] = so_cau
            
            # check giao nhau
            if so_cau > 0:
                if self._bi_giao(state, dao1, dao2):
                    continue
            
            if self._bt(state_moi, cac_cau, idx + 1):
                return True
        
        self.dem_backtrack += 1
        return False
    
    def _check_feasible(self, state):
        # kiem tra state hien tai co kha thi ko
        for dao in self.puzzle.islands:
            hien_tai = state.get_total_bridges(dao, self.puzzle.neighbors[dao])
            
            if hien_tai > dao.value:
                return False  # qua nhieu cau
            
            thieu = dao.value - hien_tai
            
            # dem so cau con co the them
            con_them_duoc = 0
            for nb in self.puzzle.neighbors[dao]:
                da_co = state.get_bridge_count(dao, nb)
                them = 2 - da_co
                
                # lang gieng con bao nhieu cho?
                nb_hien_tai = state.get_total_bridges(nb, self.puzzle.neighbors[nb])
                nb_cho = nb.value - nb_hien_tai
                if nb_cho < them:
                    them = nb_cho
                
                if them > 0:
                    con_them_duoc = con_them_duoc + them
            
            if con_them_duoc < thieu:
                return False
        
        return True
    
    def _co_the_them(self, state, dao1, dao2, so_cau):
        # kiem tra co the them so_cau cau ko
        c1 = state.get_total_bridges(dao1, self.puzzle.neighbors[dao1])
        c2 = state.get_total_bridges(dao2, self.puzzle.neighbors[dao2])
        
        if c1 + so_cau > dao1.value:
            return False
        if c2 + so_cau > dao2.value:
            return False
        return True
    
    def _bi_giao(self, state, dao1, dao2):
        # check cau moi co giao cau cu ko
        for key, cnt in state.bridges.items():
            if cnt > 0:
                if self.puzzle.bridges_cross(dao1, dao2, key[0], key[1]):
                    return True
        return False
    
    def get_stats(self):
        return {
            "time": self.time_spent,
            "nodes": self.dem_node,
            "backtracks": self.dem_backtrack,
            "algorithm": "Backtracking"
        }


def solve_backtracking(puzzle):
    solver = BacktrackingSolver(puzzle)
    kq = solver.solve()
    return kq, solver.time_spent, solver.get_stats()
