# main program
# giai puzzle hashiwokakero

import argparse
import os
import sys
import time

from hashiwokakero import Puzzle, PuzzleState
from sat_solver import solve_sat
from astar_solver import solve_astar  
from brute_force_solver import solve_bruteforce
from backtracking_solver import solve_backtracking
from utils import print_puzzle, print_solution, print_output, save_output, compare_algorithms, make_table, get_input_files


# anh xa ten thuat toan vao ham giai
CAC_SOLVER = {
    'pysat': solve_sat,
    'astar': solve_astar,
    'bruteforce': solve_bruteforce,
    'backtracking': solve_backtracking
}


def get_solver(ten):
    return CAC_SOLVER.get(ten.lower())


def giai_puzzle(file_input, algo='pysat', file_output=None, in_ra=True):
    # doc va giai 1 puzzle
    
    if in_ra:
        print("Dang doc:", file_input)
    
    puzzle = Puzzle.from_file(file_input)
    
    if in_ra:
        print_puzzle(puzzle)
    
    # lay ham giai
    solver_fn = get_solver(algo)
    if solver_fn == None:
        print("Khong biet thuat toan:", algo)
        print("Chon: pysat, astar, bruteforce, backtracking")
        return None
    
    if in_ra:
        print("Dang giai bang", algo, "...")
    
    # giai
    loi_giai, thoi_gian, stats = solver_fn(puzzle)
    
    if loi_giai == None:
        print("Khong tim duoc loi giai!")
        return None
    
    if in_ra:
        print("Tim duoc trong %.4f giay" % thoi_gian)
        print()
        print_solution(puzzle, loi_giai)
        print()
        print("Output:")
    
    output = puzzle.state_to_output(loi_giai)
    print_output(output)
    
    # luu file
    if file_output != None:
        save_output(output, file_output)
        if in_ra:
            print()
            print("Da luu:", file_output)
    
    if in_ra:
        print()
        print("Thong ke:")
        for k in stats:
            print("  %s: %s" % (k, stats[k]))
    
    return loi_giai


def chay_benchmark(folder_in='Inputs', folder_out='Outputs'):
    # test tat ca file input
    
    print("=" * 50)
    print("HASHIWOKAKERO BENCHMARK")
    print("=" * 50)
    print()
    
    cac_file = get_input_files(folder_in)
    
    if len(cac_file) == 0:
        print("Khong tim thay file input trong", folder_in)
        return
    
    print("Tim thay %d file" % len(cac_file))
    print()
    
    # cac thuat toan
    algos = {
        'PySAT': solve_sat,
        'A*': solve_astar,
        'Backtracking': solve_backtracking,
    }
    
    tat_ca_ket_qua = {}
    
    for fpath in cac_file:
        fname = os.path.basename(fpath)
        print("-" * 50)
        print("Testing:", fname)
        print("-" * 50)
        
        try:
            puzzle = Puzzle.from_file(fpath)
            so_dao = len(puzzle.islands)
            print("Kich thuoc: %dx%d, %d dao" % (puzzle.rows, puzzle.cols, so_dao))
            print()
            
            # chi dung bruteforce cho puzzle nho
            test_algos = algos.copy()
            so_cau = len(puzzle.get_possible_bridges())
            if so_cau <= 12:
                test_algos['Brute-force'] = solve_bruteforce
            
            kq = compare_algorithms(puzzle, test_algos)
            tat_ca_ket_qua[fname] = kq
            
            # luu output
            for alg in kq:
                if kq[alg].get('success'):
                    fn = test_algos[alg]
                    sol, _, _ = fn(puzzle)
                    if sol != None:
                        out = puzzle.state_to_output(sol)
                        out_name = fname.replace('input-', 'output-')
                        out_path = os.path.join(folder_out, out_name)
                        save_output(out, out_path)
                    break
        
        except Exception as loi:
            print("Loi:", loi)
            tat_ca_ket_qua[fname] = {"error": str(loi)}
        
        print()
    
    # tong ket
    print("=" * 50)
    print("TONG KET")
    print("=" * 50)
    print()
    
    ok = {}
    for k in tat_ca_ket_qua:
        if 'error' not in tat_ca_ket_qua[k]:
            ok[k] = tat_ca_ket_qua[k]
    
    if len(ok) > 0:
        print(make_table(ok))
    
    print()
    print("Xong!")


def main():
    # parse tham so dong lenh
    parser = argparse.ArgumentParser(description='Hashiwokakero Puzzle Solver')
    
    parser.add_argument('--input', '-i', type=str, help='file input')
    parser.add_argument('--algorithm', '-a', type=str, default='pysat',
                        choices=['pysat', 'astar', 'bruteforce', 'backtracking'],
                        help='thuat toan (mac dinh: pysat)')
    parser.add_argument('--output', '-o', type=str, help='file output')
    parser.add_argument('--benchmark', '-b', action='store_true', help='chay benchmark')
    parser.add_argument('--quiet', '-q', action='store_true', help='im lang')
    
    args = parser.parse_args()
    
    if args.benchmark:
        chay_benchmark()
    elif args.input:
        in_ra = not args.quiet
        giai_puzzle(args.input, args.algorithm, args.output, in_ra)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
