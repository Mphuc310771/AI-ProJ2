"""
Giải Hashiwokakero bằng thuật toán A*
"""
from hashiwokakero import Puzzle, PuzzleState, Island
import heapq
import time


class Node:
    """Node trong cây tìm kiếm A*"""
    
    def __init__(self, state, g, h, parent=None):
        self.state = state
        self.g = g  # chi phí từ đầu
        self.h = h  # ước lượng đến đích
        self.f = g + h
        self.parent = parent
    
    def __lt__(self, other):
        # ưu tiên f nhỏ, nếu bằng thì ưu tiên h nhỏ
        if self.f == other.f:
            return self.h < other.h
        return self.f < other.f


class AStarSolver:
    """
    Giải bằng A*
    
    Heuristic: tổng số cầu còn thiếu / 2
    (chia 2 vì mỗi cầu nối 2 đảo)
    """
    
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.thoi_gian = 0
        self.nodes_explored = 0
        self.nodes_generated = 0
    
    def _tinh_heuristic(self, state):
        """
        h(n) = tổng số cầu còn thiếu / 2
        Đây là admissible vì mỗi cầu kết nối 2 đảo
        """
        total = 0
        for island in self.puzzle.islands:
            current = state.get_island_bridge_count(island, self.puzzle.neighbors[island])
            needed = island.value - current
            if needed > 0:
                total += needed
        return (total + 1) // 2
    
    def _sinh_trang_thai_con(self, state):
        """Sinh các trạng thái con bằng cách thêm 1 cầu"""
        children = []
        
        # tìm đảo đầu tiên chưa đủ cầu
        for island in self.puzzle.islands:
            current = state.get_island_bridge_count(island, self.puzzle.neighbors[island])
            if current >= island.value:
                continue
            
            # thử thêm cầu đến mỗi láng giềng
            for neighbor in self.puzzle.neighbors[island]:
                # láng giềng còn chỗ không?
                neighbor_current = state.get_island_bridge_count(neighbor, self.puzzle.neighbors[neighbor])
                if neighbor_current >= neighbor.value:
                    continue
                
                # đã có 2 cầu rồi?
                bridge_count = state.get_bridge_count(island, neighbor)
                if bridge_count >= 2:
                    continue
                
                # tạo trạng thái mới
                new_state = state.copy()
                new_state.add_bridge(island, neighbor, 1)
                
                # kiểm tra hợp lệ
                if self._kiem_tra_hop_le(state, island, neighbor):
                    children.append(new_state)
            
            break  # chỉ xét đảo đầu tiên để giảm branching
        
        return children
    
    def _kiem_tra_hop_le(self, state, island1, island2):
        """Kiểm tra thêm cầu có hợp lệ không (không giao cầu khác)"""
        for (i1, i2), count in state.bridges.items():
            if count > 0:
                if self.puzzle.bridges_cross(island1, island2, i1, i2):
                    return False
        return True
    
    def solve(self):
        """Chạy A*"""
        start = time.time()
        self.nodes_explored = 0
        self.nodes_generated = 0
        
        # khởi tạo
        init_state = PuzzleState()
        h = self._tinh_heuristic(init_state)
        start_node = Node(init_state, 0, h)
        
        open_list = [start_node]
        heapq.heapify(open_list)
        
        closed_set = set()
        g_values = {init_state: 0}
        
        while open_list:
            current = heapq.heappop(open_list)
            self.nodes_explored += 1
            
            # tìm thấy goal?
            if self.puzzle.is_solution(current.state):
                self.thoi_gian = time.time() - start
                return current.state
            
            if current.state in closed_set:
                continue
            closed_set.add(current.state)
            
            # sinh các trạng thái con
            for child_state in self._sinh_trang_thai_con(current.state):
                self.nodes_generated += 1
                
                if child_state in closed_set:
                    continue
                
                if not self.puzzle.is_valid_state(child_state):
                    continue
                
                g = current.g + 1
                h = self._tinh_heuristic(child_state)
                
                # đã có đường tốt hơn?
                if child_state in g_values and g_values[child_state] <= g:
                    continue
                
                g_values[child_state] = g
                child_node = Node(child_state, g, h, current)
                heapq.heappush(open_list, child_node)
        
        self.thoi_gian = time.time() - start
        return None
    
    def get_stats(self):
        return {
            "thoi_gian": self.thoi_gian,
            "nodes_explored": self.nodes_explored,
            "nodes_generated": self.nodes_generated,
            "algorithm": "A*"
        }


def solve_with_astar(puzzle):
    solver = AStarSolver(puzzle)
    solution = solver.solve()
    return solution, solver.thoi_gian, solver.get_stats()
