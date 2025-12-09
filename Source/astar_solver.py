# giai hashiwokakero bang A*
# tham khao: https://en.wikipedia.org/wiki/A*_search_algorithm

from hashiwokakero import Puzzle, PuzzleState, Island
import heapq
import time


class AStarNode:
    # node trong cay tim kiem
    
    def __init__(self, state, g_cost, h_cost, parent=None):
        self.state = state
        self.g = g_cost   # chi phi tu dau
        self.h = h_cost   # uoc luong
        self.f = g_cost + h_cost
        self.parent = parent
    
    def __lt__(self, other):
        # so sanh de dung trong heap
        if self.f == other.f:
            return self.h < other.h
        return self.f < other.f


class AStarSolver:
    # giai bang A*, heuristic = tong cau thieu / 2
    
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.time_spent = 0
        self.nodes_explored = 0
        self.nodes_generated = 0
    
    def calc_heuristic(self, state):
        # h(n) = tong cau con thieu chia 2
        # vi moi cau noi 2 dao nen chia 2
        tong = 0
        for isl in self.puzzle.islands:
            hien_tai = state.get_total_bridges(isl, self.puzzle.neighbors[isl])
            thieu = isl.value - hien_tai
            if thieu > 0:
                tong = tong + thieu
        return (tong + 1) // 2
    
    def generate_children(self, state):
        # sinh cac trang thai con
        result = []
        
        # tim dao dau tien chua du cau
        for isl in self.puzzle.islands:
            hien_tai = state.get_total_bridges(isl, self.puzzle.neighbors[isl])
            if hien_tai >= isl.value:
                continue
            
            # thu them cau den tung lang gieng
            for nb in self.puzzle.neighbors[isl]:
                nb_hien_tai = state.get_total_bridges(nb, self.puzzle.neighbors[nb])
                if nb_hien_tai >= nb.value:
                    continue  # lang gieng da du cau
                
                so_cau = state.get_bridge_count(isl, nb)
                if so_cau >= 2:
                    continue  # da co 2 cau roi
                
                # tao state moi
                new_state = state.copy()
                new_state.add_bridge(isl, nb, 1)
                
                # check hop le
                if self._check_bridge_ok(state, isl, nb):
                    result.append(new_state)
            
            break  # chi xet 1 dao thoi de giam branching
        
        return result
    
    def _check_bridge_ok(self, state, isl1, isl2):
        # kiem tra cau moi khong giao cau cu
        for key, cnt in state.bridges.items():
            if cnt > 0:
                if self.puzzle.bridges_cross(isl1, isl2, key[0], key[1]):
                    return False
        return True
    
    def solve(self):
        t1 = time.time()
        self.nodes_explored = 0
        self.nodes_generated = 0
        
        # tao node ban dau
        init = PuzzleState()
        h = self.calc_heuristic(init)
        start_node = AStarNode(init, 0, h)
        
        # open list va closed set
        open_list = [start_node]
        heapq.heapify(open_list)
        closed = set()
        g_vals = {}
        g_vals[init] = 0
        
        while len(open_list) > 0:
            cur = heapq.heappop(open_list)
            self.nodes_explored = self.nodes_explored + 1
            
            # kiem tra goal
            if self.puzzle.is_solution(cur.state):
                self.time_spent = time.time() - t1
                return cur.state
            
            # da xet roi thi bo qua
            if cur.state in closed:
                continue
            closed.add(cur.state)
            
            # sinh con
            children = self.generate_children(cur.state)
            for child in children:
                self.nodes_generated = self.nodes_generated + 1
                
                if child in closed:
                    continue
                
                if not self.puzzle.is_valid(child):
                    continue
                
                g = cur.g + 1
                h = self.calc_heuristic(child)
                
                # kiem tra co duong tot hon ko
                if child in g_vals:
                    if g_vals[child] <= g:
                        continue
                
                g_vals[child] = g
                new_node = AStarNode(child, g, h, cur)
                heapq.heappush(open_list, new_node)
        
        # khong tim thay
        self.time_spent = time.time() - t1
        return None
    
    def get_stats(self):
        return {
            "time": self.time_spent,
            "nodes_explored": self.nodes_explored,
            "nodes_generated": self.nodes_generated,
            "algorithm": "A*"
        }


def solve_astar(puzzle):
    s = AStarSolver(puzzle)
    kq = s.solve()
    return kq, s.time_spent, s.get_stats()
