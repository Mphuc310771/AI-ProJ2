from dataclasses import dataclass, field
from enum import Enum


class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)


@dataclass
class Island:
    row: int
    col: int
    value: int
    
    def __hash__(self):
        return hash((self.row, self.col))
    
    def __eq__(self, khac):
        if not isinstance(khac, Island):
            return False
        return self.row == khac.row and self.col == khac.col
    
    def __repr__(self):
        return "Island(%d,%d,val=%d)" % (self.row, self.col, self.value)


@dataclass  
class Bridge:
    island1: Island
    island2: Island
    count: int
    
    def __post_init__(self):
        # sap xep de island1 luon nho hon island2
        if (self.island1.row, self.island1.col) > (self.island2.row, self.island2.col):
            tmp = self.island1
            self.island1 = self.island2
            self.island2 = tmp
    
    def is_horizontal(self):
        return self.island1.row == self.island2.row
    
    def is_vertical(self):
        return self.island1.col == self.island2.col
    
    def get_cells(self):
        # tra ve danh sach cac o ma cau di qua (ko tinh 2 dau)
        ds = []
        if self.is_horizontal():
            c = self.island1.col + 1
            while c < self.island2.col:
                ds.append((self.island1.row, c))
                c += 1
        else:
            r = self.island1.row + 1
            while r < self.island2.row:
                ds.append((r, self.island1.col))
                r += 1
        return ds
    
    def __hash__(self):
        return hash((self.island1.row, self.island1.col, 
                     self.island2.row, self.island2.col))
    
    def __eq__(self, khac):
        if not isinstance(khac, Bridge):
            return False
        return self.island1 == khac.island1 and self.island2 == khac.island2


@dataclass
class PuzzleState:
    bridges: dict = field(default_factory=dict)
    
    def copy(self):
        st = PuzzleState()
        st.bridges = dict(self.bridges)
        return st
    
    def add_bridge(self, d1, d2, so_cau=1):
        # dam bao thu tu nhat quan
        if (d1.row, d1.col) < (d2.row, d2.col):
            k = (d1, d2)
        else:
            k = (d2, d1)
        
        if k in self.bridges:
            self.bridges[k] += so_cau
        else:
            self.bridges[k] = so_cau
    
    def get_bridge_count(self, d1, d2):
        if (d1.row, d1.col) < (d2.row, d2.col):
            k = (d1, d2)
        else:
            k = (d2, d1)
        return self.bridges.get(k, 0)
    
    def get_total_bridges(self, dao, ds_neighbor):
        tong = 0
        for nb in ds_neighbor:
            tong += self.get_bridge_count(dao, nb)
        return tong
    
    def __hash__(self):
        items = []
        for k, v in self.bridges.items():
            items.append((k[0].row, k[0].col, k[1].row, k[1].col, v))
        items.sort()
        return hash(tuple(items))
    
    def __eq__(self, khac):
        if not isinstance(khac, PuzzleState):
            return False
        return self.bridges == khac.bridges
    
    def __lt__(self, khac):
        return hash(self) < hash(khac)


class Puzzle:
    
    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if len(grid) > 0 else 0
        self.islands = []
        self.island_map = {}
        self.neighbors = {}
        
        self._doc_grid()
        self._tim_neighbor()
    
    def _doc_grid(self):
        # duyet qua grid de tim cac dao
        for r in range(self.rows):
            for c in range(self.cols):
                v = self.grid[r][c]
                if v > 0:
                    dao = Island(r, c, v)
                    self.islands.append(dao)
                    self.island_map[(r, c)] = dao
    
    def _tim_neighbor(self):
        # voi moi dao, tim cac dao ke theo 4 huong
        for dao in self.islands:
            self.neighbors[dao] = []
            
            for huong in Direction:
                dr, dc = huong.value
                r, c = dao.row + dr, dao.col + dc
                
                # di theo huong cho den khi gap dao hoac ra ngoai
                while 0 <= r < self.rows and 0 <= c < self.cols:
                    if (r, c) in self.island_map:
                        self.neighbors[dao].append(self.island_map[(r, c)])
                        break
                    r += dr
                    c += dc
    
    def get_possible_bridges(self):
        # lay tat ca cap dao co the noi cau
        ds = set()
        for dao in self.islands:
            for nb in self.neighbors[dao]:
                if (dao.row, dao.col) < (nb.row, nb.col):
                    ds.add((dao, nb))
                else:
                    ds.add((nb, dao))
        return list(ds)
    
    def bridges_cross(self, s1, e1, s2, e2):
        # kiem tra 2 cau co cat nhau khong
        # cau 1: s1 -> e1, cau 2: s2 -> e2
        
        # truong hop cau 1 ngang, cau 2 doc
        if s1.row == e1.row and s2.col == e2.col:
            row_h = s1.row
            c_min = min(s1.col, e1.col)
            c_max = max(s1.col, e1.col)
            
            col_v = s2.col
            r_min = min(s2.row, e2.row)
            r_max = max(s2.row, e2.row)
            
            # cat khi cot cua cau doc nam giua 2 dau cau ngang
            # va hang cua cau ngang nam giua 2 dau cau doc
            if c_min < col_v < c_max and r_min < row_h < r_max:
                return True
        
        # truong hop cau 1 doc, cau 2 ngang -> swap roi goi lai
        if s1.col == e1.col and s2.row == e2.row:
            return self.bridges_cross(s2, e2, s1, e1)
        
        return False
    
    def bridge_crosses_island(self, dau, cuoi):
        # kiem tra cau co di qua dao nao khong
        if dau.row == cuoi.row:
            c1, c2 = min(dau.col, cuoi.col), max(dau.col, cuoi.col)
            for c in range(c1 + 1, c2):
                if (dau.row, c) in self.island_map:
                    return True
        else:
            r1, r2 = min(dau.row, cuoi.row), max(dau.row, cuoi.row)
            for r in range(r1 + 1, r2):
                if (r, dau.col) in self.island_map:
                    return True
        return False
    
    def is_connected(self, state):
        # kiem tra tat ca dao co lien thong qua cau khong (BFS)
        if len(self.islands) == 0:
            return True
        
        da_tham = set()
        hang_doi = [self.islands[0]]
        da_tham.add(self.islands[0])
        
        while hang_doi:
            hien_tai = hang_doi.pop(0)
            for nb in self.neighbors[hien_tai]:
                if nb not in da_tham and state.get_bridge_count(hien_tai, nb) > 0:
                    da_tham.add(nb)
                    hang_doi.append(nb)
        
        return len(da_tham) == len(self.islands)
    
    def is_valid(self, state):
        # kiem tra trang thai hop le (chua vuot qua so cau yeu cau, ko cat nhau)
        for dao in self.islands:
            so_cau = state.get_total_bridges(dao, self.neighbors[dao])
            if so_cau > dao.value:
                return False
        
        # lay danh sach cac cau dang co
        ds_cau = []
        for k, cnt in state.bridges.items():
            if cnt > 0:
                ds_cau.append(k)
        
        # kiem tra tung cap cau xem co cat nhau ko
        for i in range(len(ds_cau)):
            for j in range(i + 1, len(ds_cau)):
                c1, c2 = ds_cau[i], ds_cau[j]
                if self.bridges_cross(c1[0], c1[1], c2[0], c2[1]):
                    return False
        
        return True
    
    def is_solution(self, state):
        # kiem tra da giai xong chua
        for dao in self.islands:
            so_cau = state.get_total_bridges(dao, self.neighbors[dao])
            if so_cau != dao.value:
                return False
        
        if not self.is_connected(state):
            return False
        
        return self.is_valid(state)
    
    def state_to_output(self, state):
        # chuyen state thanh dang output de hien thi
        out = []
        for r in range(self.rows):
            dong = ['0'] * self.cols
            out.append(dong)
        
        # dien so dao
        for dao in self.islands:
            out[dao.row][dao.col] = str(dao.value)
        
        # ve cau
        for k, cnt in state.bridges.items():
            if cnt == 0:
                continue
            
            d1, d2 = k
            
            if d1.row == d2.row:
                # cau ngang
                ky_hieu = '-' if cnt == 1 else '='
                c1, c2 = min(d1.col, d2.col), max(d1.col, d2.col)
                for c in range(c1 + 1, c2):
                    out[d1.row][c] = ky_hieu
            else:
                # cau doc
                ky_hieu = '|' if cnt == 1 else '$'
                r1, r2 = min(d1.row, d2.row), max(d1.row, d2.row)
                for r in range(r1 + 1, r2):
                    out[r][d1.col] = ky_hieu
        
        return out
    
    @staticmethod
    def from_file(duong_dan):
        grid = []
        with open(duong_dan, 'r') as f:
            for dong in f:
                dong = dong.strip()
                if dong:
                    parts = dong.split(',')
                    hang = [int(p.strip()) for p in parts]
                    grid.append(hang)
        return Puzzle(grid)
    
    def __repr__(self):
        return "Puzzle(%dx%d, %d dao)" % (self.rows, self.cols, len(self.islands))
