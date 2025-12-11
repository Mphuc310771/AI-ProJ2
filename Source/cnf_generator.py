from pysat.formula import CNF
from pysat.card import CardEnc
from pysat.solvers import Glucose3
import collections
import itertools

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

    # --- PHẦN MỚI: KIỂM TRA LIÊN THÔNG (BFS) ---
    def _get_connected_component(self, current_bridges, start_node_idx=0):
        """
        Dùng BFS để tìm nhóm đảo liên thông bắt đầu từ đảo start_node_idx.
        Trả về tập hợp các ID đảo đã ghé thăm.
        """
        # Xây dựng danh sách kề (Adjacency List) từ các cầu hiện tại
        adj = collections.defaultdict(list)
        for b in current_bridges:
            # Lưu ý: current_bridges đã parse ra dạng (r,c), cần map về ID đảo
            # Để nhanh, ta tìm đảo dựa vào tọa độ
            u_id = next(isl['id'] for isl in self.islands if (isl['r'], isl['c']) == b['u'])
            v_id = next(isl['id'] for isl in self.islands if (isl['r'], isl['c']) == b['v'])
            adj[u_id].append(v_id)
            adj[v_id].append(u_id)

        # BFS
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
        Giải lặp (Iterative Solving) để xử lý tính liên thông.
        """
        # Khởi tạo Solver với các luật cơ bản
        with Glucose3(bootstrap_with=self.cnf) as solver:
            while True:
                # 1. Tìm lời giải thử
                if not solver.solve():
                    return None  # Vô nghiệm

                model = solver.get_model()
                solution_bridges = self._parse_model(model)

                # 2. Kiểm tra tính liên thông
                # Lấy tập hợp các đảo đã kết nối được từ đảo số 0
                visited_islands = self._get_connected_component(solution_bridges, start_node_idx=0)

                # Nếu số lượng đảo ghé thăm == Tổng số đảo => Đã liên thông hoàn toàn -> XONG
                if len(visited_islands) == len(self.islands):
                    return solution_bridges

                # 3. Nếu KHÔNG liên thông => Thêm luật chặn (Blocking Clause)
                # Logic: Nhóm visited_islands đang bị cô lập.
                # Cần thêm luật: "Phải có ít nhất 1 cây cầu nối từ nhóm này ra bên ngoài".

                # Tìm "Vết cắt" (Cut): Các cầu tiềm năng nối từ nhóm visited ra nhóm chưa visited
                cut_bridges_vars = []
                for b in self.bridges:
                    u_id = b['u']['id']
                    v_id = b['v']['id']

                    # Nếu cầu nối giữa 1 đảo đã thăm và 1 đảo chưa thăm
                    if (u_id in visited_islands and v_id not in visited_islands) or \
                            (u_id not in visited_islands and v_id in visited_islands):
                        # Lấy biến logic "Có ít nhất 1 cầu" của cạnh này
                        var_id = self.var_pool[(b['idx'], 1)]
                        cut_bridges_vars.append(var_id)

                if not cut_bridges_vars:
                    # Nếu không còn cầu nào nối ra ngoài mà vẫn chưa liên thông -> Vô nghiệm thực sự
                    return None

                # Thêm mệnh đề OR: (cầu_1 HOẶC cầu_2 HOẶC ... cầu_n phải tồn tại)
                solver.add_clause(cut_bridges_vars)
                # print(f"Phát hiện đảo cô lập. Thêm ràng buộc liên thông với {len(cut_bridges_vars)} lựa chọn cầu nối.")

    def _parse_model(self, model):
        """
        Chuyển đổi kết quả từ SAT model về dạng dễ đọc
        """
        result_bridges = []
        model_set = set(model)  # Để tra cứu nhanh

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

    # --- HÀM MỚI THÊM VÀO ĐỂ FORMAT OUTPUT ---
    def format_output(self, solution_bridges):
        """
        Tạo ma trận string kết quả dựa trên lời giải.
        Ký hiệu:
        - Ngang: "-" (1 cầu), "=" (2 cầu)
        - Dọc: "|" (1 cầu), "$" (2 cầu) (Lưu ý: Đề bài dùng "$" thay vì "||")
        - Đảo: "Số"
        - Trống: "0"
        """
        # 1. Khởi tạo grid output toàn "0"
        output_grid = [["0" for _ in range(self.cols)] for _ in range(self.rows)]

        # 2. Điền các đảo vào grid
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] > 0:
                    output_grid[r][c] = str(self.grid[r][c])

        # 3. Điền các cầu vào grid
        for bridge in solution_bridges:
            r1, c1 = bridge['u']
            r2, c2 = bridge['v']
            count = bridge['count']
            b_type = bridge['type']

            # Xác định ký tự cầu
            symbol = ""
            if b_type == 'horizontal':
                symbol = "-" if count == 1 else "="
                # Điền vào các ô NẰM GIỮA 2 đảo (không đè lên đảo)
                # range từ (cột nhỏ + 1) đến (cột lớn)
                start_c, end_c = min(c1, c2), max(c1, c2)
                for c in range(start_c + 1, end_c):
                    output_grid[r1][c] = symbol

            else:  # vertical
                symbol = "|" if count == 1 else "$"  # Dùng $ cho cầu đôi dọc theo đề bài
                # range từ (hàng nhỏ + 1) đến (hàng lớn)
                start_r, end_r = min(r1, r2), max(r1, r2)
                for r in range(start_r + 1, end_r):
                    output_grid[r][c1] = symbol

        return output_grid

# --- Ví dụ sử dụng ---
if __name__ == "__main__":
    # Ví dụ input đơn giản (như source 88-94)
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

    print(f"Đã sinh {len(cnf.clauses)} mệnh đề CNF.")
    print(f"Tổng số biến: {cnf.nv}")

    solution = solver.solve()
    if solution:
        # Gọi hàm format output
        formatted_grid = solver.format_output(solution)

        # In ra từng dòng giống hệt hình ảnh đề bài
        for row in formatted_grid:
            print(row)

            # Nếu muốn print đẹp hơn không có dấu nháy và ngoặc thì dùng lệnh dưới:
            # print(" ".join(f"{x:^3}" for x in row))
    else:
        print("Không tìm thấy lời giải.")
