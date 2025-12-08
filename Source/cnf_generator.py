"""
Module sinh CNF cho Hashiwokakero
Chuyển bài toán sang dạng SAT để giải bằng pysat
"""
from typing import List, Tuple, Dict
from itertools import combinations, product
from hashiwokakero import Puzzle, Island, PuzzleState


class CNFGenerator:
    """
    Tạo các mệnh đề CNF cho puzzle
    
    Cách mã hóa biến:
    - Mỗi cặp đảo kề nhau có 2 biến: b1 và b2
    - b1 = true nếu có ít nhất 1 cầu
    - b2 = true nếu có 2 cầu
    
    Các ràng buộc:
    1. b2 => b1 (có 2 cầu thì phải có 1 cầu)
    2. Tổng số cầu mỗi đảo = giá trị của đảo
    3. Các cầu không được giao nhau
    """
    
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.var_counter = 0
        self.var_map = {}  # (island1, island2, level) -> biến SAT
        self.reverse_var_map = {}
        self.clauses = []
        
        self._tao_bien()
    
    def _tao_bien(self):
        """Tạo biến SAT cho mỗi cầu có thể có"""
        possible = self.puzzle.get_possible_bridges()
        
        for island1, island2 in possible:
            # biến cho 1 cầu
            self.var_counter += 1
            key1 = (island1, island2, 1)
            self.var_map[key1] = self.var_counter
            self.reverse_var_map[self.var_counter] = key1
            
            # biến cho 2 cầu
            self.var_counter += 1
            key2 = (island1, island2, 2)
            self.var_map[key2] = self.var_counter
            self.reverse_var_map[self.var_counter] = key2
    
    def get_var(self, island1, island2, level):
        """Lấy biến SAT cho cầu giữa 2 đảo"""
        # sắp xếp để key nhất quán
        if (island1.row, island1.col) < (island2.row, island2.col):
            key = (island1, island2, level)
        else:
            key = (island2, island1, level)
        return self.var_map.get(key, 0)
    
    def sinh_tat_ca_menh_de(self):
        """Sinh tất cả các mệnh đề CNF"""
        self.clauses = []
        
        self._sinh_rang_buoc_b2_suy_ra_b1()
        self._sinh_rang_buoc_so_cau()
        self._sinh_rang_buoc_giao_nhau()
        
        # bỏ mệnh đề trùng
        unique = []
        seen = set()
        for clause in self.clauses:
            t = tuple(sorted(clause))
            if t not in seen:
                seen.add(t)
                unique.append(clause)
        
        self.clauses = unique
        return self.clauses
    
    def _sinh_rang_buoc_b2_suy_ra_b1(self):
        """b2 => b1 tương đương với: not b2 OR b1"""
        possible = self.puzzle.get_possible_bridges()
        
        for island1, island2 in possible:
            var1 = self.get_var(island1, island2, 1)
            var2 = self.get_var(island1, island2, 2)
            
            if var1 and var2:
                self.clauses.append([-var2, var1])
    
    def _sinh_rang_buoc_so_cau(self):
        """
        Với mỗi đảo, tổng số cầu phải bằng giá trị của đảo
        Dùng cách liệt kê tất cả tổ hợp hợp lệ
        """
        for island in self.puzzle.islands:
            neighbors = self.puzzle.neighbors[island]
            target = island.value
            n = len(neighbors)
            
            if n == 0:
                if target > 0:
                    # không có láng giềng mà cần cầu -> vô nghiệm
                    self.clauses.append([])
                continue
            
            # lấy biến cho mỗi láng giềng
            bridge_vars = []
            for neighbor in neighbors:
                v1 = self.get_var(island, neighbor, 1)
                v2 = self.get_var(island, neighbor, 2)
                bridge_vars.append((v1, v2))
            
            # tìm các tổ hợp mà tổng = target
            # mỗi cầu có thể là 0, 1 hoặc 2
            valid_combos = []
            for combo in product(range(3), repeat=n):
                if sum(combo) == target:
                    valid_combos.append(combo)
            
            if not valid_combos:
                self.clauses.append([])  # vô nghiệm
                continue
            
            self._ma_hoa_cac_to_hop(bridge_vars, valid_combos)
    
    def _ma_hoa_cac_to_hop(self, bridge_vars, valid_combos):
        """
        Mã hóa: phải thỏa mãn đúng 1 trong các tổ hợp hợp lệ
        """
        n = len(bridge_vars)
        
        # tạo biến phụ cho mỗi tổ hợp
        aux_vars = []
        for _ in valid_combos:
            self.var_counter += 1
            aux_vars.append(self.var_counter)
        
        # ít nhất 1 tổ hợp phải đúng
        self.clauses.append(aux_vars[:])
        
        # mỗi biến phụ => cấu hình cầu tương ứng
        for aux_var, combo in zip(aux_vars, valid_combos):
            for i, count in enumerate(combo):
                var1, var2 = bridge_vars[i]
                
                if count == 0:
                    self.clauses.append([-aux_var, -var1])
                elif count == 1:
                    self.clauses.append([-aux_var, var1])
                    self.clauses.append([-aux_var, -var2])
                else:  # count == 2
                    self.clauses.append([-aux_var, var2])
        
        # loại bỏ các cấu hình không hợp lệ
        for config in product(range(3), repeat=n):
            # xem config này có match với combo nào không
            matched = any(combo == config for combo in valid_combos)
            
            if not matched:
                # tạo mệnh đề block config này
                blocking = []
                for i, count in enumerate(config):
                    var1, var2 = bridge_vars[i]
                    if count == 0:
                        blocking.append(var1)
                    elif count == 1:
                        blocking.append(-var1)
                        blocking.append(var2)
                    else:
                        blocking.append(-var2)
                
                if blocking:
                    self.clauses.append(blocking)
    
    def _sinh_rang_buoc_giao_nhau(self):
        """Hai cầu giao nhau không thể cùng tồn tại"""
        possible = self.puzzle.get_possible_bridges()
        
        for i in range(len(possible)):
            for j in range(i + 1, len(possible)):
                b1, b2 = possible[i], possible[j]
                
                if self.puzzle.bridges_cross(b1[0], b1[1], b2[0], b2[1]):
                    v1 = self.get_var(b1[0], b1[1], 1)
                    v2 = self.get_var(b2[0], b2[1], 1)
                    
                    if v1 and v2:
                        self.clauses.append([-v1, -v2])
    
    def giai_ma_ket_qua(self, model):
        """Chuyển kết quả SAT thành PuzzleState"""
        state = PuzzleState()
        
        true_vars = set(v for v in model if v > 0)
        
        for var in true_vars:
            if var in self.reverse_var_map:
                island1, island2, level = self.reverse_var_map[var]
                if level == 2:
                    state.bridges[(island1, island2)] = 2
                elif level == 1:
                    v2 = self.get_var(island1, island2, 2)
                    if v2 not in true_vars:
                        state.bridges[(island1, island2)] = 1
        
        return state
    
    def to_dimacs(self):
        """Xuất ra format DIMACS"""
        lines = [f"p cnf {self.var_counter} {len(self.clauses)}"]
        for clause in self.clauses:
            lines.append(" ".join(map(str, clause)) + " 0")
        return "\n".join(lines)
    
    def get_stats(self):
        return {
            "so_bien": self.var_counter,
            "so_menh_de": len(self.clauses),
            "so_dao": len(self.puzzle.islands),
            "so_cau_co_the": len(self.puzzle.get_possible_bridges())
        }
