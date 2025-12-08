"""
Hashiwokakero Puzzle Solver
@author: [Tên của bạn]
@date: December 2024

Module chính để biểu diễn puzzle Hashiwokakero
"""
from typing import List, Tuple, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import copy


class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)


@dataclass
class Island:
    """Đảo trong puzzle - lưu vị trí và số cầu cần nối"""
    row: int
    col: int
    value: int
    
    def __hash__(self):
        return hash((self.row, self.col))
    
    def __eq__(self, other):
        if not isinstance(other, Island):
            return False
        return self.row == other.row and self.col == other.col
    
    def __repr__(self):
        return f"Island({self.row}, {self.col}, {self.value})"


@dataclass
class Bridge:
    """Cầu nối 2 đảo"""
    island1: Island
    island2: Island
    count: int  # 1 hoặc 2
    
    def __post_init__(self):
        # đảm bảo island1 luôn ở trên/trái hơn island2
        if (self.island1.row, self.island1.col) > (self.island2.row, self.island2.col):
            self.island1, self.island2 = self.island2, self.island1
    
    def is_horizontal(self):
        return self.island1.row == self.island2.row
    
    def is_vertical(self):
        return self.island1.col == self.island2.col
    
    def get_cells(self):
        """Lấy tất cả các ô mà cầu đi qua (không tính 2 đảo ở đầu)"""
        cells = []
        if self.is_horizontal():
            for c in range(self.island1.col + 1, self.island2.col):
                cells.append((self.island1.row, c))
        else:
            for r in range(self.island1.row + 1, self.island2.row):
                cells.append((r, self.island1.col))
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
    """Trạng thái của puzzle - dùng cho các thuật toán tìm kiếm"""
    bridges: Dict[Tuple[Island, Island], int] = field(default_factory=dict)
    
    def copy(self):
        new_state = PuzzleState()
        new_state.bridges = dict(self.bridges)
        return new_state
    
    def add_bridge(self, island1, island2, count=1):
        """Thêm cầu giữa 2 đảo"""
        # sắp xếp để key nhất quán
        if (island1.row, island1.col) < (island2.row, island2.col):
            key = (island1, island2)
        else:
            key = (island2, island1)
        self.bridges[key] = self.bridges.get(key, 0) + count
    
    def get_bridge_count(self, island1, island2):
        """Đếm số cầu giữa 2 đảo"""
        if (island1.row, island1.col) < (island2.row, island2.col):
            key = (island1, island2)
        else:
            key = (island2, island1)
        return self.bridges.get(key, 0)
    
    def get_island_bridge_count(self, island, neighbors):
        """Tổng số cầu nối với 1 đảo"""
        total = 0
        for neighbor in neighbors:
            total += self.get_bridge_count(island, neighbor)
        return total
    
    def __hash__(self):
        return hash(tuple(sorted((k[0].row, k[0].col, k[1].row, k[1].col, v) 
                                  for k, v in self.bridges.items())))
    
    def __eq__(self, other):
        if not isinstance(other, PuzzleState):
            return False
        return self.bridges == other.bridges
    
    def __lt__(self, other):
        # cần cho heapq
        return hash(self) < hash(other)


class Puzzle:
    """
    Class chính biểu diễn puzzle Hashiwokakero
    Đọc input, tìm các đảo lân cận, kiểm tra solution
    """
    
    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if grid else 0
        self.islands = []
        self.island_map = {}  # (r,c) -> Island
        self.neighbors = {}   # Island -> [Island láng giềng]
        
        self._parse_grid()
        self._find_neighbors()
    
    def _parse_grid(self):
        # tìm tất cả các đảo trong grid
        for r in range(self.rows):
            for c in range(self.cols):
                val = self.grid[r][c]
                if val > 0:
                    island = Island(r, c, val)
                    self.islands.append(island)
                    self.island_map[(r, c)] = island
    
    def _find_neighbors(self):
        """
        Tìm các đảo lân cận theo 4 hướng
        Láng giềng = đảo gần nhất theo hướng ngang/dọc (không bị chặn bởi đảo khác)
        """
        for island in self.islands:
            self.neighbors[island] = []
            
            # duyệt 4 hướng
            for direction in Direction:
                dr, dc = direction.value
                r, c = island.row + dr, island.col + dc
                
                # đi theo hướng đó đến khi gặp đảo hoặc ra ngoài
                while 0 <= r < self.rows and 0 <= c < self.cols:
                    if (r, c) in self.island_map:
                        self.neighbors[island].append(self.island_map[(r, c)])
                        break
                    r += dr
                    c += dc
    
    def get_possible_bridges(self):
        """Lấy tất cả các cặp đảo có thể nối cầu"""
        bridges = set()
        for island in self.islands:
            for neighbor in self.neighbors[island]:
                # đảm bảo không trùng (A,B) và (B,A)
                if (island.row, island.col) < (neighbor.row, neighbor.col):
                    bridges.add((island, neighbor))
                else:
                    bridges.add((neighbor, island))
        return list(bridges)
    
    def bridges_cross(self, b1_start, b1_end, b2_start, b2_end):
        """Kiểm tra 2 cầu có giao nhau không"""
        # 1 ngang 1 dọc mới có thể giao
        if b1_start.row == b1_end.row:  # b1 ngang
            if b2_start.col == b2_end.col:  # b2 dọc
                h_row = b1_start.row
                h_c1 = min(b1_start.col, b1_end.col)
                h_c2 = max(b1_start.col, b1_end.col)
                v_col = b2_start.col
                v_r1 = min(b2_start.row, b2_end.row)
                v_r2 = max(b2_start.row, b2_end.row)
                
                # giao nhau nếu điểm giao nằm trong cả 2 đoạn
                if h_c1 < v_col < h_c2 and v_r1 < h_row < v_r2:
                    return True
                    
        elif b1_start.col == b1_end.col:  # b1 dọc
            if b2_start.row == b2_end.row:  # b2 ngang
                # đổi vai trò và gọi lại
                return self.bridges_cross(b2_start, b2_end, b1_start, b1_end)
        
        return False
    
    def bridge_crosses_island(self, start, end):
        """Kiểm tra cầu có đi qua đảo khác không"""
        if start.row == end.row:
            # cầu ngang
            c1, c2 = min(start.col, end.col), max(start.col, end.col)
            for c in range(c1 + 1, c2):
                if (start.row, c) in self.island_map:
                    return True
        else:
            # cầu dọc
            r1, r2 = min(start.row, end.row), max(start.row, end.row)
            for r in range(r1 + 1, r2):
                if (r, start.col) in self.island_map:
                    return True
        return False
    
    def is_connected(self, state):
        """BFS kiểm tra tất cả đảo có liên thông không"""
        if not self.islands:
            return True
        
        visited = set()
        queue = [self.islands[0]]
        visited.add(self.islands[0])
        
        while queue:
            current = queue.pop(0)
            for neighbor in self.neighbors[current]:
                if neighbor not in visited:
                    # chỉ đi được nếu có cầu
                    if state.get_bridge_count(current, neighbor) > 0:
                        visited.add(neighbor)
                        queue.append(neighbor)
        
        return len(visited) == len(self.islands)
    
    def is_valid_state(self, state):
        """Kiểm tra trạng thái có hợp lệ không (chưa hoàn thành)"""
        # kiểm tra số cầu không vượt quá
        for island in self.islands:
            count = state.get_island_bridge_count(island, self.neighbors[island])
            if count > island.value:
                return False
        
        # kiểm tra cầu không giao nhau
        bridge_list = []
        for (i1, i2), count in state.bridges.items():
            if count > 0:
                bridge_list.append((i1, i2))
        
        for i in range(len(bridge_list)):
            for j in range(i + 1, len(bridge_list)):
                b1, b2 = bridge_list[i], bridge_list[j]
                if self.bridges_cross(b1[0], b1[1], b2[0], b2[1]):
                    return False
        
        return True
    
    def is_solution(self, state):
        """Kiểm tra đây có phải solution hoàn chỉnh không"""
        # mỗi đảo phải có đúng số cầu
        for island in self.islands:
            count = state.get_island_bridge_count(island, self.neighbors[island])
            if count != island.value:
                return False
        
        # phải liên thông
        if not self.is_connected(state):
            return False
        
        # không có cầu giao nhau
        return self.is_valid_state(state)
    
    def state_to_output(self, state):
        """Chuyển state thành output format"""
        output = [['0' for _ in range(self.cols)] for _ in range(self.rows)]
        
        # đặt các đảo
        for island in self.islands:
            output[island.row][island.col] = str(island.value)
        
        # đặt các cầu
        for (i1, i2), count in state.bridges.items():
            if count == 0:
                continue
            
            if i1.row == i2.row:
                # cầu ngang
                symbol = '-' if count == 1 else '='
                c1, c2 = min(i1.col, i2.col), max(i1.col, i2.col)
                for c in range(c1 + 1, c2):
                    output[i1.row][c] = symbol
            else:
                # cầu dọc
                symbol = '|' if count == 1 else '$'
                r1, r2 = min(i1.row, i2.row), max(i1.row, i2.row)
                for r in range(r1 + 1, r2):
                    output[r][i1.col] = symbol
        
        return output
    
    @staticmethod
    def from_file(filepath):
        """Đọc puzzle từ file"""
        grid = []
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    row = [int(x) for x in line.split(',')]
                    grid.append(row)
        return Puzzle(grid)
    
    @staticmethod
    def output_to_string(output):
        lines = []
        for row in output:
            lines.append(str(row))
        return '\n'.join(lines)
    
    def __repr__(self):
        return f"Puzzle({self.rows}x{self.cols}, {len(self.islands)} islands)"
