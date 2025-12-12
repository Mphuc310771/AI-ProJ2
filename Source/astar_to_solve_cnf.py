import heapq
import time
import tracemalloc
from collections import Counter

# Giả định bạn đã có các file này trong project
from cnf_generator import HashiCNF
from hashiwokakero import PuzzleState

def _clause_satisfied(clause, assignment):
    """Kiểm tra xem mệnh đề đã được thỏa mãn (True) chưa."""
    for lit in clause:
        v = abs(lit)
        if v in assignment:
            val = assignment[v]
            # Nếu lit dương và val True -> True
            # Nếu lit âm và val False -> True
            if (lit > 0 and val) or (lit < 0 and not val):
                return True
    return False

def _count_unsatisfied_clauses(clauses, assignment):
    """Hàm Heuristic: Đếm số mệnh đề chưa được thỏa mãn."""
    cnt = 0
    for cl in clauses:
        if not _clause_satisfied(cl, assignment):
            cnt += 1
    return cnt

def unit_propagate(clauses, assignment):
    """
    KỸ THUẬT TỐI ƯU: Unit Propagation.
    Tự động gán giá trị cho các biến nếu mệnh đề chỉ còn 1 lựa chọn duy nhất.
    Trả về: (assignment_mới, có_mâu_thuẫn_không)
    """
    new_assignment = assignment.copy()
    changed = True
    
    while changed:
        changed = False
        
        for clause in clauses:
            # 1. Kiểm tra mệnh đề đã True chưa
            if _clause_satisfied(clause, new_assignment):
                continue
            
            # 2. Tìm các literal chưa được gán giá trị
            unassigned = []
            for lit in clause:
                if abs(lit) not in new_assignment:
                    unassigned.append(lit)
            
            # 3. Nếu không còn literal nào chưa gán mà mệnh đề vẫn chưa True
            # -> Mâu thuẫn (Conflict) -> Nhánh này sai
            if not unassigned:
                return None, True
            
            # 4. Nếu chỉ còn ĐÚNG 1 literal chưa gán (Unit Clause)
            # -> Bắt buộc phải gán giá trị để mệnh đề True
            if len(unassigned) == 1:
                lit = unassigned[0]
                var = abs(lit)
                val_to_assign = (lit > 0) # True nếu lit dương, False nếu lit âm
                
                # Nếu biến này đã gán rồi mà khác giá trị bắt buộc -> Mâu thuẫn
                if var in new_assignment and new_assignment[var] != val_to_assign:
                    return None, True
                
                if var not in new_assignment:
                    new_assignment[var] = val_to_assign
                    changed = True
                    
    return new_assignment, False

def _assignment_to_puzzlestate(hc: HashiCNF, assignment, puzzle):
    """Chuyển đổi từ bảng chân trị True/False về trạng thái bàn cờ."""
    state = PuzzleState()
    
    # Duyệt qua map cầu nối trong đối tượng CNF
    # Lưu ý: Cần đảm bảo HashiCNF có thuộc tính 'bridges' lưu thông tin mapping
    for b in hc.bridges:
        idx = b['idx']
        # Lấy biến logic tương ứng với 1 cầu và 2 cầu
        var1 = hc.var_pool.get((idx, 1))
        var2 = hc.var_pool.get((idx, 2))
        
        count = 0
        # Ưu tiên kiểm tra 2 cầu trước
        if var2 is not None and assignment.get(var2, False):
            count = 2
        elif var1 is not None and assignment.get(var1, False):
            count = 1

        if count > 0:
            u = b['u']
            v = b['v']
            # Lấy đối tượng Island thực tế từ puzzle map
            isl_u = puzzle.island_map[(u['r'], u['c'])]
            isl_v = puzzle.island_map[(v['r'], v['c'])]
            state.add_bridge(isl_u, isl_v, count)

    return state

def solve_astar(puzzle, time_limit=300, max_nodes=2000000):
    """
    Hàm chính giải CNF bằng A* (Custom Implementation).
    """
    # 1. Sinh CNF từ bàn cờ
    hc = HashiCNF(puzzle.grid)
    hc.generate_cnf()
    clauses, num_vars = hc.get_clause_list()

    # 2. Bắt đầu đo đạc
    tracemalloc.start()
    t0 = time.perf_counter()

    # 3. Khởi tạo trạng thái đầu
    # Chạy Unit Propagation ngay từ đầu để điền các biến bắt buộc
    start_assignment, conflict = unit_propagate(clauses, {})
    if conflict:
        return None, time.perf_counter() - t0, {'status': 'unsatisfiable_initial'}

    g0 = len(start_assignment)
    h0 = _count_unsatisfied_clauses(clauses, start_assignment)
    
    # Priority Queue: (f, h, g, assignment_dict)
    # Lưu ý: assignment được lưu trực tiếp trong tuple
    open_heap = []
    heapq.heappush(open_heap, (g0 + h0, h0, g0, start_assignment))
    
    # Closed set lưu key là tuple các item đã sort để hash được
    closed = set()
    start_key = tuple(sorted(start_assignment.items()))
    closed.add(start_key)

    nodes_expanded = 0
    max_open_size = 1

    while open_heap:
        # Kiểm tra thời gian
        if (time.perf_counter() - t0) > time_limit:
            break

        # Lấy node tốt nhất
        f, h, g, current_assign = heapq.heappop(open_heap)
        max_open_size = max(max_open_size, len(open_heap))
        
        nodes_expanded += 1
        if nodes_expanded > max_nodes:
            break

        # --- KIỂM TRA ĐÍCH (GOAL) ---
        if h == 0:
            # Double check để chắc chắn
            if _count_unsatisfied_clauses(clauses, current_assign) == 0:
                current_mem, peak_mem = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                elapsed = time.perf_counter() - t0
                
                stats = {
                    'nodes_expanded': nodes_expanded,
                    'max_open_size': max_open_size,
                    'peak_memory_bytes': peak_mem,
                    'num_vars': num_vars,
                    'algorithm': 'A* on CNF'
                }
                
                result_state = _assignment_to_puzzlestate(hc, current_assign, puzzle)
                return result_state, elapsed, stats

        # --- CHIẾN LƯỢC CHỌN BIẾN (HEURISTIC) ---
        # MOMs: Chọn biến xuất hiện nhiều nhất trong các mệnh đề ngắn nhất chưa thỏa mãn
        min_len = float('inf')
        best_vars = Counter()
        
        has_unsatisfied = False
        for cl in clauses:
            if _clause_satisfied(cl, current_assign):
                continue
            
            has_unsatisfied = True
            # Lấy các literal chưa gán trong mệnh đề này
            unassigned = [abs(lit) for lit in cl if abs(lit) not in current_assign]
            
            if not unassigned: continue # Should be handled by unit prop, but safe check
            
            curr_len = len(unassigned)
            if curr_len < min_len:
                min_len = curr_len
                best_vars = Counter() # Reset nếu tìm thấy mệnh đề ngắn hơn
            
            if curr_len == min_len:
                for v in unassigned:
                    best_vars[v] += 1
        
        if not has_unsatisfied:
            # Trường hợp hiếm: h > 0 nhưng không tìm thấy mệnh đề unsatisfied (bug logic?)
            # Thường h=0 sẽ return ở trên rồi.
            continue

        if not best_vars:
            continue

        # Lấy biến tốt nhất để phân nhánh
        next_var = best_vars.most_common(1)[0][0]

        # --- SINH TRẠNG THÁI CON (BRANCHING) ---
        # Thử gán True và False
        for val in [True, False]:
            new_assign = current_assign.copy()
            new_assign[next_var] = val
            
            # Kích hoạt Unit Propagation ngay lập tức
            prop_assign, conflict = unit_propagate(clauses, new_assign)
            
            if conflict:
                continue # Nhánh này dẫn đến mâu thuẫn -> Cắt tỉa ngay
            
            # Kiểm tra Closed Set
            prop_key = tuple(sorted(prop_assign.items()))
            if prop_key in closed:
                continue
            
            closed.add(prop_key)
            
            # Tính toán chi phí
            new_g = len(prop_assign) # Chi phí g là số lượng biến đã gán
            new_h = _count_unsatisfied_clauses(clauses, prop_assign)
            
            heapq.heappush(open_heap, (new_g + new_h, new_h, new_g, prop_assign))

    # Kết thúc mà không tìm thấy
    tracemalloc.stop()
    return None, time.perf_counter() - t0, {
        'nodes_expanded': nodes_expanded, 
        'max_open_size': max_open_size
    }