"""
Các hàm tiện ích
"""
from hashiwokakero import Puzzle, PuzzleState
import os
import time
import tracemalloc


def format_output(output):
    lines = []
    for row in output:
        lines.append(str(row))
    return '\n'.join(lines)


def save_output(output, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(format_output(output))


def in_puzzle(puzzle):
    print(f"Puzzle: {puzzle.rows}x{puzzle.cols}, {len(puzzle.islands)} đảo")
    for row in puzzle.grid:
        print(' '.join(str(x) if x > 0 else '.' for x in row))
    print()


def in_loi_giai(puzzle, state):
    output = puzzle.state_to_output(state)
    print("Lời giải:")
    for row in output:
        print(' '.join(row))
    print()


def in_output_format(output):
    for row in output:
        print(row)


def do_memory(func, *args, **kwargs):
    """Đo bộ nhớ sử dụng"""
    tracemalloc.start()
    result = func(*args, **kwargs)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, peak / 1024 / 1024


def so_sanh_thuat_toan(puzzle, algorithms, timeout=60.0):
    """So sánh các thuật toán"""
    results = {}
    
    for name, solve_func in algorithms.items():
        print(f"Đang chạy {name}...")
        
        try:
            tracemalloc.start()
            start = time.time()
            
            solution, t, stats = solve_func(puzzle)
            
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            results[name] = {
                "thanh_cong": solution is not None,
                "thoi_gian": t,
                "bo_nho_mb": peak / 1024 / 1024,
                "stats": stats
            }
            
            if solution:
                results[name]["hop_le"] = puzzle.is_solution(solution)
            
        except Exception as e:
            tracemalloc.stop()
            results[name] = {
                "thanh_cong": False,
                "loi": str(e)
            }
        
        status = 'OK' if results[name].get('thanh_cong') else 'FAIL'
        print(f"  {name}: {status}")
        if results[name].get('thoi_gian'):
            print(f"  Thời gian: {results[name]['thoi_gian']:.4f}s")
        print()
    
    return results


def tao_bang_so_sanh(all_results):
    """Tạo bảng so sánh từ kết quả benchmark"""
    lines = []
    
    if not all_results:
        return ""
    
    algorithms = list(list(all_results.values())[0].keys())
    header = "| Input | " + " | ".join(f"{alg}" for alg in algorithms) + " |"
    sep = "|" + "|".join(["---"] * (len(algorithms) + 1)) + "|"
    
    lines.append(header)
    lines.append(sep)
    
    for input_file, results in all_results.items():
        row = f"| {input_file} |"
        for alg in algorithms:
            if alg in results and results[alg].get('thoi_gian'):
                row += f" {results[alg]['thoi_gian']:.4f}s |"
            else:
                row += " N/A |"
        lines.append(row)
    
    return '\n'.join(lines)


def kiem_tra_input(filepath):
    """Kiểm tra file input hợp lệ"""
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        if not lines:
            return False
        
        col_count = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            values = line.split(',')
            for v in values:
                num = int(v.strip())
                if num < 0 or num > 8:
                    return False
            
            if col_count is None:
                col_count = len(values)
            elif len(values) != col_count:
                return False
        
        return True
    except:
        return False


def lay_cac_file_input(input_dir):
    """Lấy danh sách file input"""
    files = []
    for f in os.listdir(input_dir):
        if f.startswith('input-') and f.endswith('.txt'):
            files.append(os.path.join(input_dir, f))
    return sorted(files)
