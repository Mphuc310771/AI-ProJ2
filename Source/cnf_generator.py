"""
sinh cac menh de CNF cho hashiwokakero
chuyen bai toan sang dang SAT de giai bang pysat
"""
from itertools import combinations, product
from hashiwokakero import Puzzle, Island, PuzzleState


class CNFGenerator:
    """
    tao cac menh de CNF cho puzzle
    
    cach ma hoa bien:
    - moi cap dao ke nhau co 2 bien: b1 va b2
    - b1 = true neu co it nhat 1 cau
    - b2 = true neu co 2 cau
    
    cac rang buoc:
    1. b2 => b1 (co 2 cau thi phai co 1 cau)
    2. tong so cau moi dao = gia tri cua dao
    3. cac cau khong duoc giao nhau
    """
    
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.var_counter = 0
        self.var_map = {}     # (island1, island2, level) -> bien SAT
        self.reverse_map = {}
        self.clauses = []
        
        self._create_variables()
    
    def _create_variables(self):
        """tao bien SAT cho moi cau co the co"""
        possible = self.puzzle.get_possible_bridges()
        
        for island1, island2 in possible:
            # bien cho 1 cau
            self.var_counter += 1
            key1 = (island1, island2, 1)
            self.var_map[key1] = self.var_counter
            self.reverse_map[self.var_counter] = key1
            
            # bien cho 2 cau
            self.var_counter += 1
            key2 = (island1, island2, 2)
            self.var_map[key2] = self.var_counter
            self.reverse_map[self.var_counter] = key2
    
    def get_var(self, island1, island2, level):
        """lay bien SAT cho cau giua 2 dao"""
        # sap xep de key nhat quan
        if (island1.row, island1.col) < (island2.row, island2.col):
            key = (island1, island2, level)
        else:
            key = (island2, island1, level)
        
        if key in self.var_map:
            return self.var_map[key]
        return 0
    
    def generate_all(self):
        """sinh tat ca cac menh de CNF"""
        self.clauses = []
        
        self._add_implication_clauses()
        self._add_degree_clauses()
        self._add_crossing_clauses()
        
        # bo menh de trung
        unique_clauses = []
        seen = set()
        for clause in self.clauses:
            t = tuple(sorted(clause))
            if t not in seen:
                seen.add(t)
                unique_clauses.append(clause)
        
        self.clauses = unique_clauses
        return self.clauses
    
    def _add_implication_clauses(self):
        """b2 => b1 tuong duong voi: not b2 OR b1"""
        possible = self.puzzle.get_possible_bridges()
        
        for island1, island2 in possible:
            var1 = self.get_var(island1, island2, 1)
            var2 = self.get_var(island1, island2, 2)
            
            if var1 != 0 and var2 != 0:
                self.clauses.append([-var2, var1])
    
    def _add_degree_clauses(self):
        """voi moi dao, tong so cau phai bang gia tri cua dao"""
        for island in self.puzzle.islands:
            neighbors = self.puzzle.neighbors[island]
            target = island.value
            n = len(neighbors)
            
            if n == 0:
                if target > 0:
                    # khong co lang gieng ma can cau -> vo nghiem
                    self.clauses.append([])
                continue
            
            # lay bien cho moi lang gieng
            bridge_vars = []
            for neighbor in neighbors:
                v1 = self.get_var(island, neighbor, 1)
                v2 = self.get_var(island, neighbor, 2)
                bridge_vars.append((v1, v2))
            
            # tim cac to hop ma tong = target
            valid_combos = []
            for combo in product(range(3), repeat=n):
                total = 0
                for x in combo:
                    total += x
                if total == target:
                    valid_combos.append(combo)
            
            if len(valid_combos) == 0:
                self.clauses.append([])  # vo nghiem
                continue
            
            self._encode_valid_combos(bridge_vars, valid_combos)
    
    def _encode_valid_combos(self, bridge_vars, valid_combos):
        """ma hoa: phai thoa man dung 1 trong cac to hop hop le"""
        n = len(bridge_vars)
        
        # tao bien phu cho moi to hop
        aux_vars = []
        for i in range(len(valid_combos)):
            self.var_counter += 1
            aux_vars.append(self.var_counter)
        
        # it nhat 1 to hop phai dung
        self.clauses.append(list(aux_vars))
        
        # moi bien phu => cau hinh cau tuong ung
        for i in range(len(valid_combos)):
            aux_var = aux_vars[i]
            combo = valid_combos[i]
            
            for j in range(n):
                count = combo[j]
                var1, var2 = bridge_vars[j]
                
                if count == 0:
                    self.clauses.append([-aux_var, -var1])
                elif count == 1:
                    self.clauses.append([-aux_var, var1])
                    self.clauses.append([-aux_var, -var2])
                else:  # count == 2
                    self.clauses.append([-aux_var, var2])
        
        # loai bo cac cau hinh khong hop le
        for config in product(range(3), repeat=n):
            # xem config nay co match voi combo nao khong
            matched = False
            for combo in valid_combos:
                if combo == config:
                    matched = True
                    break
            
            if not matched:
                # tao menh de block config nay
                blocking = []
                for j in range(n):
                    count = config[j]
                    var1, var2 = bridge_vars[j]
                    if count == 0:
                        blocking.append(var1)
                    elif count == 1:
                        blocking.append(-var1)
                        blocking.append(var2)
                    else:
                        blocking.append(-var2)
                
                if len(blocking) > 0:
                    self.clauses.append(blocking)
    
    def _add_crossing_clauses(self):
        """hai cau giao nhau khong the cung ton tai"""
        possible = self.puzzle.get_possible_bridges()
        
        for i in range(len(possible)):
            for j in range(i + 1, len(possible)):
                b1 = possible[i]
                b2 = possible[j]
                
                if self.puzzle.bridges_cross(b1[0], b1[1], b2[0], b2[1]):
                    v1 = self.get_var(b1[0], b1[1], 1)
                    v2 = self.get_var(b2[0], b2[1], 1)
                    
                    if v1 != 0 and v2 != 0:
                        self.clauses.append([-v1, -v2])
    
    def decode(self, model):
        """chuyen ket qua SAT thanh PuzzleState"""
        state = PuzzleState()
        
        true_vars = set()
        for v in model:
            if v > 0:
                true_vars.add(v)
        
        for v in true_vars:
            if v in self.reverse_map:
                island1, island2, level = self.reverse_map[v]
                if level == 2:
                    state.bridges[(island1, island2)] = 2
                elif level == 1:
                    v2 = self.get_var(island1, island2, 2)
                    if v2 not in true_vars:
                        state.bridges[(island1, island2)] = 1
        
        return state
    
    def to_dimacs(self):
        """xuat ra format DIMACS"""
        lines = []
        lines.append("p cnf %d %d" % (self.var_counter, len(self.clauses)))
        for clause in self.clauses:
            line = ""
            for lit in clause:
                line += str(lit) + " "
            line += "0"
            lines.append(line)
        return "\n".join(lines)
    
    def get_stats(self):
        return {
            "num_vars": self.var_counter,
            "num_clauses": len(self.clauses),
            "num_islands": len(self.puzzle.islands),
            "num_bridges": len(self.puzzle.get_possible_bridges())
        }
