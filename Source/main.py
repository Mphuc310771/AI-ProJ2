"""
Hashiwokakero Puzzle Solver
@author: [Điền tên của bạn vào đây]
@date: 12/2024

Chương trình giải câu đố Hashiwokakero bằng nhiều thuật toán:
- PySAT (CNF)
- A*
- Backtracking
- Brute-force
"""

import argparse
import os
import sys
import time

from hashiwokakero import Puzzle, PuzzleState
from sat_solver import solve_with_pysat
from astar_solver import solve_with_astar
from brute_force_solver import solve_with_bruteforce
from backtracking_solver import solve_with_backtracking
from utils import (
    in_puzzle, in_loi_giai, in_output_format,
    save_output, so_sanh_thuat_toan, tao_bang_so_sanh,
    lay_cac_file_input, format_output
)


def lay_solver(algorithm):
    """Lấy hàm giải theo tên thuật toán"""
    solvers = {
        'pysat': solve_with_pysat,
        'astar': solve_with_astar,
        'bruteforce': solve_with_bruteforce,
        'backtracking': solve_with_backtracking
    }
    return solvers.get(algorithm.lower())


def giai_mot_puzzle(input_file, algorithm='pysat', output_file=None, verbose=True):
    """Giải một puzzle"""
    
    if verbose:
        print(f"Đang đọc: {input_file}")
    
    puzzle = Puzzle.from_file(input_file)
    
    if verbose:
        in_puzzle(puzzle)
    
    solver = lay_solver(algorithm)
    if solver is None:
        print(f"Thuật toán không hợp lệ: {algorithm}")
        print("Các thuật toán hỗ trợ: pysat, astar, bruteforce, backtracking")
        return None
    
    if verbose:
        print(f"Đang giải bằng {algorithm}...")
    
    solution, t, stats = solver(puzzle)
    
    if solution is None:
        print("Không tìm được lời giải!")
        return None
    
    if verbose:
        print(f"Đã tìm được lời giải trong {t:.4f}s")
        print()
        in_loi_giai(puzzle, solution)
        print()
        print("Output format:")
    
    output = puzzle.state_to_output(solution)
    in_output_format(output)
    
    if output_file:
        save_output(output, output_file)
        if verbose:
            print(f"\nĐã lưu: {output_file}")
    
    if verbose:
        print("\nThống kê:")
        for k, v in stats.items():
            print(f"  {k}: {v}")
    
    return solution


def chay_benchmark(input_dir='Inputs', output_dir='Outputs'):
    """Chạy benchmark trên tất cả file input"""
    
    print("=" * 60)
    print("HASHIWOKAKERO SOLVER BENCHMARK")
    print("=" * 60)
    print()
    
    input_files = lay_cac_file_input(input_dir)
    
    if not input_files:
        print(f"Không tìm thấy file input trong {input_dir}")
        return
    
    print(f"Tìm thấy {len(input_files)} file")
    print()
    
    # các thuật toán cần test
    algorithms = {
        'PySAT': solve_with_pysat,
        'A*': solve_with_astar,
        'Backtracking': solve_with_backtracking,
    }
    
    all_results = {}
    
    for input_file in input_files:
        fname = os.path.basename(input_file)
        print("-" * 60)
        print(f"Testing: {fname}")
        print("-" * 60)
        
        try:
            puzzle = Puzzle.from_file(input_file)
            print(f"Kích thước: {puzzle.rows}x{puzzle.cols}, {len(puzzle.islands)} đảo")
            print()
            
            test_algs = algorithms.copy()
            # chỉ dùng brute-force cho puzzle nhỏ
            if len(puzzle.get_possible_bridges()) <= 12:
                test_algs['Brute-force'] = solve_with_bruteforce
            
            results = so_sanh_thuat_toan(puzzle, test_algs)
            all_results[fname] = results
            
            # lưu output
            for alg_name, result in results.items():
                if result.get('thanh_cong'):
                    solver = test_algs[alg_name]
                    sol, _, _ = solver(puzzle)
                    if sol:
                        out = puzzle.state_to_output(sol)
                        out_path = os.path.join(output_dir, fname.replace('input-', 'output-'))
                        save_output(out, out_path)
                    break
        
        except Exception as e:
            print(f"Lỗi: {e}")
            all_results[fname] = {"error": str(e)}
        
        print()
    
    # in tổng kết
    print("=" * 60)
    print("TỔNG KẾT")
    print("=" * 60)
    print()
    
    valid = {k: v for k, v in all_results.items() if 'error' not in v}
    if valid:
        print(tao_bang_so_sanh(valid))
    
    print()
    print("Benchmark hoàn tất!")


def main():
    parser = argparse.ArgumentParser(
        description='Hashiwokakero Puzzle Solver',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  python main.py --input Inputs/input-01.txt
  python main.py --input Inputs/input-01.txt --algorithm astar
  python main.py --input Inputs/input-01.txt --output result.txt
  python main.py --benchmark

Thuật toán hỗ trợ:
  pysat       - Dùng thư viện PySAT (nhanh nhất)
  astar       - Thuật toán A*
  backtracking - Quay lui với cắt tỉa
  bruteforce   - Vét cạn (chậm)
        """
    )
    
    parser.add_argument('--input', '-i', type=str, 
                        help='File input')
    parser.add_argument('--algorithm', '-a', type=str, default='pysat',
                        choices=['pysat', 'astar', 'bruteforce', 'backtracking'],
                        help='Thuật toán (mặc định: pysat)')
    parser.add_argument('--output', '-o', type=str,
                        help='File output')
    parser.add_argument('--benchmark', '-b', action='store_true',
                        help='Chạy benchmark')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Chế độ im lặng')
    
    args = parser.parse_args()
    
    if args.benchmark:
        chay_benchmark()
    elif args.input:
        giai_mot_puzzle(args.input, args.algorithm, args.output, 
                        verbose=not args.quiet)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
