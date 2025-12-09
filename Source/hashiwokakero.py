"""
hashiwokakero puzzle structure
"""
from dataclasses import dataclass, field
from enum import Enum
import copy


class Direction(Enum):
    """4 huong di chuyen"""
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)


@dataclass
class Island:
    """1 dao trong puzzle"""
    row: int
    col: int
    value: int  # so cau can noi
    
    def __hash__(self):
        return hash((self.row, self.col))
    
    def __eq__(self, other):
        if not isinstance(other, Island):
            return False
        return self.row == other.row and self.col == other.col
    
    def __repr__(self):
        return "Island(%d, %d, %d)" % (self.row, self.col, self.value)


@dataclass  
class Bridge:
    """cau noi 2 dao"""
    island1: Island
    island2: Island
    count: int  # 1 hoac 2 cau
    
    def __post_init__(self):
        # dam bao island1 luon o tren/trai hon island2
        if (self.island1.row, self.island1.col) > (self.island2.row, self.island2.col):
            temp = self.island1
            self.island1 = self.island2
            self.island2 = temp
    
    def is_horizontal(self):
        return self.island1.row == self.island2.row
    
    def is_vertical(self):
        return self.island1.col == self.island2.col
    
    def get_cells(self):
        """lay cac o ma cau di qua (khong tinh 2 dao)"""
        cells = []
        if self.is_horizontal():
            c = self.island1.col + 1
            while c < self.island2.col:
                cells.append((self.island1.row, c))
                c += 1
        else:
            r = self.island1.row + 1
            while r < self.island2.row:
                cells.append((r, self.island1.col))
                r += 1
        return cells
    
    def __hash__(self):
        return hash((self.island1.row, self.island1.col, 
                     self.island2.row, self.island2.col))
    
    def __eq__(self, other):
        if not isinstance(other, Bridge):
            return False
        return self.island1 == other.island1 and self.island2 == other.island2


@dataclass
class PuzzleState:
    """trang thai cua puzzle - luu cac cau da noi"""
    bridges: dict = field(default_factory=dict)
    
    def copy(self):
        new_state = PuzzleState()
        new_state.bridges = dict(self.bridges)
        return new_state
    
    def add_bridge(self, isl1, isl2, count=1):
        """them cau giua 2 dao"""
        # sap xep de key nhat quan
        if (isl1.row, isl1.col) < (isl2.row, isl2.col):
            key = (isl1, isl2)
        else:
            key = (isl2, isl1)
        
        if key in self.bridges:
            self.bridges[key] = self.bridges[key] + count
        else:
            self.bridges[key] = count
    
    def get_bridge_count(self, isl1, isl2):
        """dem so cau giua 2 dao"""
        if (isl1.row, isl1.col) < (isl2.row, isl2.col):
            key = (isl1, isl2)
        else:
            key = (isl2, isl1)
        
        if key in self.bridges:
            return self.bridges[key]
        return 0
    
    def get_total_bridges(self, island, neighbor_list):
        """tong so cau noi voi 1 dao"""
        total = 0
        for nb in neighbor_list:
            total += self.get_bridge_count(island, nb)
        return total
    
    def __hash__(self):
        items = []
        for k, v in self.bridges.items():
            items.append((k[0].row, k[0].col, k[1].row, k[1].col, v))
        items.sort()
        return hash(tuple(items))
    
    def __eq__(self, other):
        if not isinstance(other, PuzzleState):
            return False
        return self.bridges == other.bridges
    
    def __lt__(self, other):
        # can cho heapq
        return hash(self) < hash(other)


class Puzzle:
    """class chinh bieu dien puzzle hashiwokakero"""
    
    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        if len(grid) > 0:
            self.cols = len(grid[0])
        else:
            self.cols = 0
        self.islands = []
        self.island_map = {}  # (row, col) -> Island
        self.neighbors = {}   # Island -> list cac dao ke
        
        self._parse_grid()
        self._find_neighbors()
    
    def _parse_grid(self):
        """tim tat ca cac dao trong grid"""
        for r in range(self.rows):
            for c in range(self.cols):
                val = self.grid[r][c]
                if val > 0:
                    isl = Island(r, c, val)
                    self.islands.append(isl)
                    self.island_map[(r, c)] = isl
    
    def _find_neighbors(self):
        """tim cac dao ke theo 4 huong"""
        for isl in self.islands:
            self.neighbors[isl] = []
            
            # duyet 4 huong
            for direction in Direction:
                dr, dc = direction.value
                r = isl.row + dr
                c = isl.col + dc
                
                # di theo huong do den khi gap dao hoac ra ngoai
                while r >= 0 and r < self.rows and c >= 0 and c < self.cols:
                    if (r, c) in self.island_map:
                        self.neighbors[isl].append(self.island_map[(r, c)])
                        break
                    r = r + dr
                    c = c + dc
    
    def get_possible_bridges(self):
        """lay tat ca cac cap dao co the noi cau"""
        bridge_set = set()
        for isl in self.islands:
            for nb in self.neighbors[isl]:
                if (isl.row, isl.col) < (nb.row, nb.col):
                    bridge_set.add((isl, nb))
                else:
                    bridge_set.add((nb, isl))
        return list(bridge_set)
    
    def bridges_cross(self, start1, end1, start2, end2):
        """kiem tra 2 cau co giao nhau khong"""
        # 1 ngang 1 doc moi co the giao
        if start1.row == end1.row:  # cau 1 ngang
            if start2.col == end2.col:  # cau 2 doc
                h_row = start1.row
                h_c1 = min(start1.col, end1.col)
                h_c2 = max(start1.col, end1.col)
                v_col = start2.col
                v_r1 = min(start2.row, end2.row)
                v_r2 = max(start2.row, end2.row)
                
                # giao nhau neu diem giao nam trong ca 2 doan
                if h_c1 < v_col and v_col < h_c2:
                    if v_r1 < h_row and h_row < v_r2:
                        return True
                    
        elif start1.col == end1.col:  # cau 1 doc
            if start2.row == end2.row:  # cau 2 ngang
                return self.bridges_cross(start2, end2, start1, end1)
        
        return False
    
    def bridge_crosses_island(self, start, end):
        """kiem tra cau co di qua dao khac khong"""
        if start.row == end.row:
            # cau ngang
            c1 = min(start.col, end.col)
            c2 = max(start.col, end.col)
            for c in range(c1 + 1, c2):
                if (start.row, c) in self.island_map:
                    return True
        else:
            # cau doc
            r1 = min(start.row, end.row)
            r2 = max(start.row, end.row)
            for r in range(r1 + 1, r2):
                if (r, start.col) in self.island_map:
                    return True
        return False
    
    def is_connected(self, state):
        """BFS kiem tra tat ca dao co lien thong khong"""
        if len(self.islands) == 0:
            return True
        
        visited = set()
        queue = [self.islands[0]]
        visited.add(self.islands[0])
        
        while len(queue) > 0:
            current = queue.pop(0)
            for nb in self.neighbors[current]:
                if nb not in visited:
                    # chi di duoc neu co cau
                    if state.get_bridge_count(current, nb) > 0:
                        visited.add(nb)
                        queue.append(nb)
        
        return len(visited) == len(self.islands)
    
    def is_valid(self, state):
        """kiem tra trang thai co hop le khong"""
        # kiem tra so cau khong vuot qua
        for isl in self.islands:
            cnt = state.get_total_bridges(isl, self.neighbors[isl])
            if cnt > isl.value:
                return False
        
        # kiem tra cau khong giao nhau
        bridge_list = []
        for key, cnt in state.bridges.items():
            if cnt > 0:
                bridge_list.append(key)
        
        for i in range(len(bridge_list)):
            for j in range(i + 1, len(bridge_list)):
                b1 = bridge_list[i]
                b2 = bridge_list[j]
                if self.bridges_cross(b1[0], b1[1], b2[0], b2[1]):
                    return False
        
        return True
    
    def is_solution(self, state):
        """kiem tra day co phai loi giai day du khong"""
        # moi dao phai co dung so cau
        for isl in self.islands:
            cnt = state.get_total_bridges(isl, self.neighbors[isl])
            if cnt != isl.value:
                return False
        
        # phai lien thong
        if not self.is_connected(state):
            return False
        
        # khong co cau giao nhau
        return self.is_valid(state)
    
    def state_to_output(self, state):
        """chuyen state thanh output grid"""
        output = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                row.append('0')
            output.append(row)
        
        # dat cac dao
        for isl in self.islands:
            output[isl.row][isl.col] = str(isl.value)
        
        # dat cac cau
        for key, cnt in state.bridges.items():
            if cnt == 0:
                continue
            
            i1, i2 = key
            
            if i1.row == i2.row:
                # cau ngang
                if cnt == 1:
                    symbol = '-'
                else:
                    symbol = '='
                c1 = min(i1.col, i2.col)
                c2 = max(i1.col, i2.col)
                for c in range(c1 + 1, c2):
                    output[i1.row][c] = symbol
            else:
                # cau doc
                if cnt == 1:
                    symbol = '|'
                else:
                    symbol = '$'
                r1 = min(i1.row, i2.row)
                r2 = max(i1.row, i2.row)
                for r in range(r1 + 1, r2):
                    output[r][i1.col] = symbol
        
        return output
    
    @staticmethod
    def from_file(filepath):
        """doc puzzle tu file"""
        grid = []
        f = open(filepath, 'r')
        for line in f:
            line = line.strip()
            if line != "":
                parts = line.split(',')
                row = []
                for p in parts:
                    row.append(int(p))
                grid.append(row)
        f.close()
        return Puzzle(grid)
    
    def __repr__(self):
        return "Puzzle(%dx%d, %d islands)" % (self.rows, self.cols, len(self.islands))
