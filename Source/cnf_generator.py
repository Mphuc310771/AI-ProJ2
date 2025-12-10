# CNF Generator cho Hashiwokakero
# Chuyen bai toan sang dang CNF de giai bang SAT solver

from pysat.formula import CNF
from pysat.card import CardEnc
from pysat.solvers import Glucose3
from hashiwokakero import Puzzle, PuzzleState, Island
import collections


class CNFGenerator:
    """
    Sinh menh de CNF tu puzzle Hashiwokakero
    """
    
    def __init__(self, puzzle):
        """
        Khoi tao voi puzzle dau vao
        :param puzzle: Puzzle object tu hashiwokakero.py
        """
        self.puzzle = puzzle
        self.bridges = []  # Danh sach cac cau noi tiem nang
        self.var_map = {}  # Anh xa (bridge_idx, count) -> var_id
        self.reverse_map = {}  # var_id -> (bridge_idx, count)
        self.cnf = CNF()
        self.stats = {}
        
        # Tim tat ca cau noi tiem nang
        self._find_bridges()
        
        # Tao bien logic
        self._allocate_variables()
    
    def _find_bridges(self):
        """
        Lay danh sach cac cap dao co the noi cau
        """
        possible = self.puzzle.get_possible_bridges()
        for idx, (isl1, isl2) in enumerate(possible):
            # Xac dinh loai cau (ngang/doc)
            if isl1.row == isl2.row:
                btype = 'horizontal'
            else:
                btype = 'vertical'
            
            self.bridges.append({
                'idx': idx,
                'island1': isl1,
                'island2': isl2,
                'type': btype
            })
    
    def _allocate_variables(self):
        """
        Moi cau noi co 2 bien logic:
        - x_{i,1}: Cau i co it nhat 1 net
        - x_{i,2}: Cau i co 2 net
        """
        var_counter = 1
        for b in self.bridges:
            idx = b['idx']
            self.var_map[(idx, 1)] = var_counter
            self.var_map[(idx, 2)] = var_counter + 1
            self.reverse_map[var_counter] = (idx, 1)
            self.reverse_map[var_counter + 1] = (idx, 2)
            var_counter += 2
    
    def generate_all(self):
        """
        Sinh tat ca menh de CNF dua tren luat choi
        Tra ve danh sach cac menh de
        """
        self.cnf = CNF()
        
        # 1. Rang buoc nhat quan (Consistency)
        # Neu co 2 cau thi bat buoc phai co 1 cau
        # x_{i,2} -> x_{i,1}  <=>  -x_{i,2} v x_{i,1}
        for b in self.bridges:
            idx = b['idx']
            var_1 = self.var_map[(idx, 1)]
            var_2 = self.var_map[(idx, 2)]
            self.cnf.append([-var_2, var_1])
        
        # 2. Rang buoc khong cat nhau (No Crossing)
        horizontals = [b for b in self.bridges if b['type'] == 'horizontal']
        verticals = [b for b in self.bridges if b['type'] == 'vertical']
        
        cnt_crossing = 0
        for h in horizontals:
            for v in verticals:
                # Kiem tra giao nhau ve mat hinh hoc
                h_row = h['island1'].row
                h_c1 = min(h['island1'].col, h['island2'].col)
                h_c2 = max(h['island1'].col, h['island2'].col)
                
                v_col = v['island1'].col
                v_r1 = min(v['island1'].row, v['island2'].row)
                v_r2 = max(v['island1'].row, v['island2'].row)
                
                # Cat nhau neu: h_c1 < v_col < h_c2 && v_r1 < h_row < v_r2
                if h_c1 < v_col < h_c2 and v_r1 < h_row < v_r2:
                    # 2 cau khong the cung ton tai
                    # -(h AND v) <=> -h OR -v
                    h_var = self.var_map[(h['idx'], 1)]
                    v_var = self.var_map[(v['idx'], 1)]
                    self.cnf.append([-h_var, -v_var])
                    cnt_crossing += 1
        
        # 3. Rang buoc so luong cau tai moi dao (Island Capacity)
        # Tong so cau noi vao dao phai bang gia tri cua dao
        for island in self.puzzle.islands:
            connected_vars = []
            
            # Tim tat ca cau noi vao dao nay
            for b in self.bridges:
                if b['island1'] == island or b['island2'] == island:
                    # Lay ca bien 1 cau va bien 2 cau
                    # Tong = x_1 + x_2
                    # Cau don: x_1=1, x_2=0 => Tong=1
                    # Cau doi: x_1=1, x_2=1 => Tong=2
                    connected_vars.append(self.var_map[(b['idx'], 1)])
                    connected_vars.append(self.var_map[(b['idx'], 2)])
            
            # Dung CardEnc de tao rang buoc: Tong == island.value
            if len(connected_vars) > 0:
                clauses = CardEnc.equals(
                    lits=connected_vars, 
                    bound=island.value, 
                    top_id=self.cnf.nv
                )
                self.cnf.extend(clauses)
        
        # Luu thong ke
        self.stats = {
            'so_dao': len(self.puzzle.islands),
            'so_cau_tiem_nang': len(self.bridges),
            'so_bien': self.cnf.nv,
            'so_menh_de': len(self.cnf.clauses),
            'so_rang_buoc_cat': cnt_crossing
        }
        
        return self.cnf.clauses
    
    def decode(self, model):
        """
        Chuyen ket qua SAT model thanh PuzzleState
        """
        state = PuzzleState()
        model_set = set(model)
        
        for b in self.bridges:
            idx = b['idx']
            v1 = self.var_map[(idx, 1)]
            v2 = self.var_map[(idx, 2)]
            
            count = 0
            if v2 in model_set:
                count = 2
            elif v1 in model_set:
                count = 1
            
            if count > 0:
                state.add_bridge(b['island1'], b['island2'], count)
        
        return state
    
    def get_stats(self):
        """Tra ve thong ke"""
        return self.stats
    
    def to_dimacs(self):
        """Xuat CNF ra dinh dang DIMACS"""
        lines = []
        lines.append("c Hashiwokakero CNF")
        lines.append("c So dao: %d" % len(self.puzzle.islands))
        lines.append("c So cau tiem nang: %d" % len(self.bridges))
        lines.append("p cnf %d %d" % (self.cnf.nv, len(self.cnf.clauses)))
        
        for clause in self.cnf.clauses:
            line = " ".join(str(x) for x in clause) + " 0"
            lines.append(line)
        
        return "\n".join(lines)


class HashiCNF:
    """
    Class doc lap de giai Hashiwokakero bang CNF/SAT
    Co the su dung truc tiep voi ma tran dau vao
    """
    
    def __init__(self, grid):
        """
        Khoi tao voi ma tran dau vao
        :param grid: List[List[int]], 0 la o trong, so > 0 la dao
        """
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.islands = []
        self.bridges = []
        self.var_pool = {}
        self.cnf = CNF()
        
        # Tim dao
        self._find_islands()
        
        # Tim cau noi tiem nang
        self._find_potential_bridges()
        
        # Tao bien logic
        self._allocate_variables()
    
    def _find_islands(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] > 0:
                    self.islands.append({
                        'r': r, 'c': c, 'val': self.grid[r][c], 'id': len(self.islands)
                    })
    
    def _find_potential_bridges(self):
        """
        Tim cac cap dao co the noi voi nhau
        Chi quet ben phai va ben duoi de tranh trung lap
        """
        for i, u in enumerate(self.islands):
            # Quet hang ngang (tim ben phai)
            for c in range(u['c'] + 1, self.cols):
                val = self.grid[u['r']][c]
                if val > 0:
                    v = next(isl for isl in self.islands if isl['r'] == u['r'] and isl['c'] == c)
                    self.bridges.append({
                        'u': u, 'v': v,
                        'type': 'horizontal',
                        'idx': len(self.bridges)
                    })
                    break
            
            # Quet hang doc (tim ben duoi)
            for r in range(u['r'] + 1, self.rows):
                val = self.grid[r][u['c']]
                if val > 0:
                    v = next(isl for isl in self.islands if isl['r'] == r and isl['c'] == u['c'])
                    self.bridges.append({
                        'u': u, 'v': v,
                        'type': 'vertical',
                        'idx': len(self.bridges)
                    })
                    break
    
    def _allocate_variables(self):
        """
        Moi cau noi i se co 2 bien logic:
        - x_{i,1}: Cau i co it nhat 1 net
        - x_{i,2}: Cau i co 2 net
        """
        var_counter = 1
        for b in self.bridges:
            self.var_pool[(b['idx'], 1)] = var_counter
            self.var_pool[(b['idx'], 2)] = var_counter + 1
            var_counter += 2
    
    def generate_cnf(self):
        """
        Sinh cac menh de CNF dua tren luat choi
        """
        # 1. Rang buoc nhat quan
        for b in self.bridges:
            idx = b['idx']
            var_1 = self.var_pool[(idx, 1)]
            var_2 = self.var_pool[(idx, 2)]
            self.cnf.append([-var_2, var_1])
        
        # 2. Rang buoc khong cat nhau
        horizontals = [b for b in self.bridges if b['type'] == 'horizontal']
        verticals = [b for b in self.bridges if b['type'] == 'vertical']
        
        for h in horizontals:
            for v in verticals:
                if (h['u']['c'] < v['u']['c'] < h['v']['c']) \
                    and (v['u']['r'] < h['u']['r'] < v['v']['r']):
                    h_var = self.var_pool[(h['idx'], 1)]
                    v_var = self.var_pool[(v['idx'], 1)]
                    self.cnf.append([-h_var, -v_var])
        
        # 3. Rang buoc so luong cau tai moi dao
        for island in self.islands:
            connected_vars = []
            
            for b in self.bridges:
                if b['u'] == island or b['v'] == island:
                    connected_vars.append(self.var_pool[(b['idx'], 1)])
                    connected_vars.append(self.var_pool[(b['idx'], 2)])
            
            clauses = CardEnc.equals(
                lits=connected_vars, 
                bound=island['val'], 
                top_id=self.cnf.nv
            )
            self.cnf.extend(clauses)
        
        return self.cnf
    
    def _get_connected_component(self, current_bridges, start_node_idx=0):
        """
        Dung BFS de tim nhom dao lien thong
        """
        adj = collections.defaultdict(list)
        for b in current_bridges:
            u_id = next(isl['id'] for isl in self.islands if (isl['r'], isl['c']) == b['u'])
            v_id = next(isl['id'] for isl in self.islands if (isl['r'], isl['c']) == b['v'])
            adj[u_id].append(v_id)
            adj[v_id].append(u_id)
        
        visited = set()
        queue = collections.deque([start_node_idx])
        visited.add(start_node_idx)
        
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if v not in visited:
                    visited.add(v)
                    queue.append(v)
        
        return visited
    
    def solve(self):
        """
        Giai lap (Iterative Solving) de xu ly tinh lien thong
        """
        with Glucose3(bootstrap_with=self.cnf) as solver:
            while True:
                if not solver.solve():
                    return None
                
                model = solver.get_model()
                solution_bridges = self._parse_model(model)
                
                visited_islands = self._get_connected_component(solution_bridges, start_node_idx=0)
                
                if len(visited_islands) == len(self.islands):
                    return solution_bridges
                
                # Them rang buoc lien thong
                cut_bridges_vars = []
                for b in self.bridges:
                    u_id = b['u']['id']
                    v_id = b['v']['id']
                    
                    if (u_id in visited_islands and v_id not in visited_islands) or \
                            (u_id not in visited_islands and v_id in visited_islands):
                        var_id = self.var_pool[(b['idx'], 1)]
                        cut_bridges_vars.append(var_id)
                
                if not cut_bridges_vars:
                    return None
                
                solver.add_clause(cut_bridges_vars)
    
    def _parse_model(self, model):
        """
        Chuyen ket qua SAT model ve dang de doc
        """
        result_bridges = []
        model_set = set(model)
        
        for b in self.bridges:
            idx = b['idx']
            v1 = self.var_pool[(idx, 1)]
            v2 = self.var_pool[(idx, 2)]
            
            count = 0
            if v2 in model_set:
                count = 2
            elif v1 in model_set:
                count = 1
            
            if count > 0:
                result_bridges.append({
                    'u': (b['u']['r'], b['u']['c']),
                    'v': (b['v']['r'], b['v']['c']),
                    'count': count,
                    'type': b['type']
                })
        
        return result_bridges
    
    def format_output(self, solution_bridges):
        """
        Tao ma tran string ket qua
        """
        output_grid = [["0" for _ in range(self.cols)] for _ in range(self.rows)]
        
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] > 0:
                    output_grid[r][c] = str(self.grid[r][c])
        
        for bridge in solution_bridges:
            r1, c1 = bridge['u']
            r2, c2 = bridge['v']
            count = bridge['count']
            b_type = bridge['type']
            
            if b_type == 'horizontal':
                symbol = "-" if count == 1 else "="
                start_c, end_c = min(c1, c2), max(c1, c2)
                for c in range(start_c + 1, end_c):
                    output_grid[r1][c] = symbol
            else:
                symbol = "|" if count == 1 else "$"
                start_r, end_r = min(r1, r2), max(r1, r2)
                for r in range(start_r + 1, end_r):
                    output_grid[r][c1] = symbol
        
        return output_grid


# Vi du su dung
if __name__ == "__main__":
    sample_grid = [
        [0, 2, 0, 5, 0, 0, 2],
        [0, 0, 0, 0, 0, 0, 0],
        [4, 0, 2, 0, 2, 0, 4],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 5, 0, 2, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [4, 0, 0, 0, 0, 0, 3]
    ]
    
    solver = HashiCNF(sample_grid)
    cnf = solver.generate_cnf()
    
    print("Da sinh %d menh de CNF." % len(cnf.clauses))
    print("Tong so bien: %d" % cnf.nv)
    
    solution = solver.solve()
    if solution:
        formatted_grid = solver.format_output(solution)
        for row in formatted_grid:
            print(row)
    else:
        print("Khong tim thay loi giai.")
