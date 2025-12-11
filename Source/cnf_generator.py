from pysat.formula import CNF
from pysat.card import CardEnc


class HashiCNF:
    def __init__(self, grid):
        """
        Khởi tạo với ma trận đầu vào.
        :param grid: List[List[int]], 0 là ô trống, số > 0 là đảo.
        """
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.islands = [] # Danh sách các đảo (r, c, value)
        self.bridges = [] # Danh sách các cầu nối tiềm năng
        self.var_pool = {} # Ánh xạ biến logic: (bridge_index, count) -> var_id
        self.cnf = CNF()

        # 1. Tìm tất cả các đảo
        self._find_islands()

        # 2. Tìm tất cả các cầu nối tiềm năng (cạnh đồ thị)
        self._find_potential_bridges()

        # 3. Tạo biến logic cho CNF
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
        Tìm các cặp đảo có thể nối với nhau (thẳng hàng, không bị chặn).
        Chỉ quét bên phải và bên dưới của đảo đang xét để tránh trùng lặp.
        """
        for i, u in enumerate(self.islands):
            # Quét hàng ngang (tìm bên phải)
            for c in range(u['c'] + 1, self.cols):
                val = self.grid[u['r']][c]
                if val > 0: # Gặp đảo v
                    v = next(isl for isl in self.islands if isl['r'] == u['r'] and isl['c'] == c)
                    self.bridges.append({
                        'u': u, 'v': v,
                        'type': 'horizontal',
                        'idx': len(self.bridges)
                    })
                    break

            # Quét hàng dọc (tìm bên dưới)
            for r in range(u['r'] + 1, self.rows):
                val = self.grid[r][u['c']]
                if val > 0: # Gặp đảo v
                    v = next(isl for isl in self.islands if isl['r'] == r and isl['c'] == u['c'])
                    self.bridges.append({
                        'u': u, 'v': v,
                        'type': 'vertical',
                        'idx': len(self.bridges)
                    })
                    break

    def _allocate_variables(self):
        """
        Mỗi cầu nối tiềm năng i sẽ có 2 biến logic:
        - x_{i, 1}: Cầu i có ít nhất 1 nét (1 bridge).
        - x_{i, 2}: Cầu i co 2 nét (2 bridge).
        """
        var_counter = 1
        for b in self.bridges:
            self.var_pool[(b['idx'], 1)] = var_counter
            self.var_pool[(b['idx'], 2)] = var_counter + 1
            var_counter += 2

    def generate_cnf(self):
        """
        Tự động sinh các mệnh đề CNF dựa trên luật chơi.
        """
        # 1. Ràng buộc nhất quán (Consistency)
        # Nếu có 2 cầu (x_{i, 2}: True) thì bắt buộc phải có ít nhất 1 cầu (x_{i, 1}: True).
        # Logic: x_{i, 2} -> x_{i, 1} <=> - x_{i, 2} v x_{i, 1}
        for b in self.bridges:
            idx = b['idx']
            var_1 = self.var_pool[(idx, 1)]
            var_2 = self.var_pool[(idx, 2)]
            self.cnf.append([-var_2, var_1])

        # 2. Ràng buộc không cắt nhau (No Crossing)
        # Cầu ngang và cầu dọc không được cắt nhau.
        horizontals = [b for b in self.bridges if b['type'] == 'horizontal']
        verticals = [b for b in self.bridges if b['type'] == 'vertical']

        for horizontal_bridge in horizontals:
            for vertical_bridge in verticals:
                # Kiểm tra giao nhau về mặt hình học
                # h đi từ (r, c1) đến (r, c2)
                # v đi từ (r1, c) đến (r2, c)
                # Cắt nhau nếu: c1 < c < c2 && r1 < r < r2
                if (horizontal_bridge['u']['c'] < vertical_bridge['u']['c'] < horizontal_bridge['v']['c']) \
                    and (vertical_bridge['u']['r'] < horizontal_bridge['u']['r'] < vertical_bridge['v']['r']):
                    # Nếu 2 cầu cắt nhau, chúng không thể cùng tồn tại.
                    # Chỉ cần xét biến "có ít nhất 1 cầu" (var_1).
                    # Logic: - (h_1 AND v_1) <=> - h_1 OR - v_1
                    horizontal_bridge_var = self.var_pool[(horizontal_bridge['idx'], 1)]
                    vertical_bridge_var = self.var_pool[(vertical_bridge['idx'], 1)]
                    self.cnf.append([-horizontal_bridge_var, -vertical_bridge_var])

        # 3. Ràng buộc số lượng cầu tại mỗi đảo (Island Capacity)
        # Tổng số cầu nối vào đảo phải bằng giá trị của đảo.
        for island in self.islands:
            connected_vars = []

            # Tìm tất cả cầu nối vào đảo này
            for b in self.bridges:
                if b['u'] == island or b['v'] == island:
                    # Lấy cả biến 1 cầu và biến 2 cầu
                    # Vì: 1 cầu đơn đóng góp 1 vào tổng. 1 cầu đôi đóng góp 2 vào tổng.
                    # Mẹo: Coi cầu đôi là "cầu thứ 2".
                    # Tổng = x_1 + x_2
                    # Nếu cầu đơn: x_1 = 1, x_2 = 0 => Tổng = 1.
                    # Nếu cầu đôi: x_1 = 1, x_2 = 1 => Tổng = 2.
                    connected_vars.append(self.var_pool[(b['idx'], 1)])
                    connected_vars.append(self.var_pool[(b['idx'], 2)])

            # Sử dụng CardEnc để tạo ràng buộc: Tổng các biến True == island['val']
            # CardEnc.equals(lits, bound) trả về danh sách các mệnh đề CNF
            clauses = CardEnc.equals(lits = connected_vars, bound = island['val'], top_id = self.cnf.nv)

            # Cập nhật top_id (số lượng biến lớn nhất đã dùng) và thêm vào CNF chính
            # Lưu ý: CardEnc có thể sinh thêm biến phụ (auxiliary variables).
            self.cnf.extend(clauses)

        return self.cnf
