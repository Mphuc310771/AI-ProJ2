from hashiwokakero import Puzzle, PuzzleState, Island
import time


class BacktrackingSolver:
    
    def __init__(self, puzzle, timeout_seconds=None):
        self.puzzle = puzzle
        self.tg_chay = 0
        self.dem_node = 0
        self.dem_quay_lui = 0
        self.loi_giai = None
        self._start_time = None
        self._timeout_seconds = timeout_seconds
        self.timed_out = False
    
    def solve(self):
        t1 = time.time()
        self.dem_node = 0
        self.dem_quay_lui = 0
        self.loi_giai = None
        self._start_time = t1
        self.timed_out = False
        
        # lay danh sach cac cap dao co the noi
        ds_cau = self.puzzle.get_possible_bridges()
        
        # sap xep de duyet dao it lua chon truoc (toi uu)
        ds_cau = self._sap_xep_cau(ds_cau)
        
        state = PuzzleState()
        self._quay_lui(state, ds_cau, 0)
        
        self.tg_chay = time.time() - t1
        return self.loi_giai
    
    def _sap_xep_cau(self, ds_cau):
        # tinh so lua chon cua moi dao
        dem = {}
        for d in self.puzzle.islands:
            dem[d] = len(self.puzzle.neighbors[d])
        
        # sap xep: uu tien cap dao ma ca 2 deu co it lua chon
        def tinh_diem(cap):
            d1, d2 = cap
            return dem[d1] + dem[d2]
        
        return sorted(ds_cau, key=tinh_diem)
    
    def _quay_lui(self, state, ds_cau, vi_tri):
        # da tim duoc thi dung
        if self.loi_giai is not None:
            return True
        
        self.dem_node += 1
        # Kiểm tra timeout
        if self._timeout_seconds is not None and self._start_time is not None:
            if time.time() - self._start_time > self._timeout_seconds:
                self.timed_out = True
                self.dem_quay_lui += 1
                return False
        
        # cat tia som neu khong kha thi
        if not self._kha_thi(state):
            self.dem_quay_lui += 1
            return False
        
        # het cau de duyet -> kiem tra loi giai
        if vi_tri >= len(ds_cau):
            if self.puzzle.is_solution(state):
                self.loi_giai = state.copy()
                return True
            self.dem_quay_lui += 1
            return False
        
        dao1, dao2 = ds_cau[vi_tri]
        
        # thu 0, 1, 2 cau cho cap nay
        for so_cau in [0, 1, 2]:
            # kiem tra co the them so cau nay khong
            if so_cau > 0 and not self._co_the_them(state, dao1, dao2, so_cau):
                continue
            
            # kiem tra cat nhau
            if so_cau > 0 and self._bi_cat(state, dao1, dao2):
                continue
            
            # tao state moi va tiep tuc
            st_moi = state.copy()
            if so_cau > 0:
                st_moi.bridges[(dao1, dao2)] = so_cau
            
            if self._quay_lui(st_moi, ds_cau, vi_tri + 1):
                return True
        
        self.dem_quay_lui += 1
        return False
    
    def _kha_thi(self, state):
        # kiem tra moi dao co the dat yeu cau khong
        for dao in self.puzzle.islands:
            hien_tai = state.get_total_bridges(dao, self.puzzle.neighbors[dao])
            
            # qua so cau yeu cau
            if hien_tai > dao.value:
                return False
            
            con_thieu = dao.value - hien_tai
            
            # dem so cau con co the them
            co_the_them = 0
            for nb in self.puzzle.neighbors[dao]:
                da_co = state.get_bridge_count(dao, nb)
                con_cho = 2 - da_co
                
                # kiem tra dao ke con cho bao nhieu
                nb_hien = state.get_total_bridges(nb, self.puzzle.neighbors[nb])
                nb_con = nb.value - nb_hien
                
                them = min(con_cho, nb_con)
                if them > 0:
                    co_the_them += them
            
            # khong du cho de dap ung yeu cau
            if co_the_them < con_thieu:
                return False
        
        return True
    
    def _co_the_them(self, state, d1, d2, so_cau):
        # kiem tra 2 dao con cho phep them so_cau cau nua khong
        c1 = state.get_total_bridges(d1, self.puzzle.neighbors[d1])
        c2 = state.get_total_bridges(d2, self.puzzle.neighbors[d2])
        
        return (c1 + so_cau <= d1.value) and (c2 + so_cau <= d2.value)
    
    def _bi_cat(self, state, d1, d2):
        # kiem tra cau moi co cat cau nao da co khong
        for key, cnt in state.bridges.items():
            if cnt > 0:
                if self.puzzle.bridges_cross(d1, d2, key[0], key[1]):
                    return True
        return False
    
    def get_stats(self):
        return {
            "time": self.tg_chay,
            "nodes": self.dem_node,
            "backtracks": self.dem_quay_lui,
            "algorithm": "Backtracking",
            "timed_out": getattr(self, 'timed_out', False),
            "timeout_seconds": self._timeout_seconds
        }


def solve_backtracking(puzzle, timeout_seconds=60):
    solver = BacktrackingSolver(puzzle, timeout_seconds=timeout_seconds)
    kq = solver.solve()
    return kq, solver.tg_chay, solver.get_stats()
