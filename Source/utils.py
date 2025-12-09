# cac ham tien ich

from hashiwokakero import Puzzle, PuzzleState
import os
import time
import tracemalloc


def format_output(grid):
    # chuyen grid thanh string
    kq = []
    for row in grid:
        kq.append(str(row))
    return '\n'.join(kq)


def save_output(grid, duong_dan):
    # luu grid ra file
    f = open(duong_dan, 'w', encoding='utf-8')
    f.write(format_output(grid))
    f.close()


def print_puzzle(puzzle):
    # in puzzle ra man hinh
    print("Puzzle: %dx%d, %d dao" % (puzzle.rows, puzzle.cols, len(puzzle.islands)))
    for row in puzzle.grid:
        dong = ""
        for x in row:
            if x > 0:
                dong = dong + str(x) + " "
            else:
                dong = dong + ". "
        print(dong)
    print()


def print_solution(puzzle, state):
    # in loi giai
    output = puzzle.state_to_output(state)
    print("Loi giai:")
    for row in output:
        print(' '.join(row))
    print()


def print_output(grid):
    # in output format
    for row in grid:
        print(row)


def measure_memory(ham, *args, **kwargs):
    # do bo nho
    tracemalloc.start()
    kq = ham(*args, **kwargs)
    cur, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return kq, peak / 1024 / 1024


def compare_algorithms(puzzle, danh_sach_algo, timeout=60.0):
    # so sanh cac thuat toan
    ket_qua = {}
    
    for ten in danh_sach_algo:
        ham = danh_sach_algo[ten]
        print("Dang chay %s..." % ten)
        
        try:
            tracemalloc.start()
            t1 = time.time()
            
            sol, t, stats = ham(puzzle)
            
            cur, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            ket_qua[ten] = {
                "success": sol != None,
                "time": t,
                "memory_mb": peak / 1024 / 1024,
                "stats": stats
            }
            
            if sol != None:
                ket_qua[ten]["valid"] = puzzle.is_solution(sol)
        
        except Exception as e:
            tracemalloc.stop()
            ket_qua[ten] = {
                "success": False,
                "error": str(e)
            }
        
        # in status
        if ket_qua[ten].get('success'):
            print("  %s: OK" % ten)
        else:
            print("  %s: FAIL" % ten)
        
        if ket_qua[ten].get('time'):
            print("  Thoi gian: %.4fs" % ket_qua[ten]['time'])
        print()
    
    return ket_qua


def make_table(all_results):
    # tao bang markdown de in
    if len(all_results) == 0:
        return ""
    
    # lay ten cac algo
    first = list(all_results.keys())[0]
    algo_names = list(all_results[first].keys())
    
    lines = []
    
    # header
    header = "| File |"
    for a in algo_names:
        header = header + " " + a + " |"
    lines.append(header)
    
    # sep
    sep = "|"
    for i in range(len(algo_names) + 1):
        sep = sep + "---|"
    lines.append(sep)
    
    # rows
    for fname in all_results:
        res = all_results[fname]
        row = "| " + fname + " |"
        for a in algo_names:
            if a in res and res[a].get('time') != None:
                row = row + " %.4fs |" % res[a]['time']
            else:
                row = row + " N/A |"
        lines.append(row)
    
    return '\n'.join(lines)


def check_input_file(duong_dan):
    # kiem tra file input co hop le ko
    try:
        f = open(duong_dan, 'r')
        cac_dong = f.readlines()
        f.close()
        
        if len(cac_dong) == 0:
            return False
        
        so_cot = None
        for dong in cac_dong:
            dong = dong.strip()
            if dong == "":
                continue
            
            parts = dong.split(',')
            for p in parts:
                val = int(p.strip())
                if val < 0 or val > 8:
                    return False
            
            if so_cot == None:
                so_cot = len(parts)
            else:
                if len(parts) != so_cot:
                    return False
        
        return True
    except:
        return False


def get_input_files(folder):
    # lay danh sach cac file input
    kq = []
    for ten in os.listdir(folder):
        if ten.startswith('input-') and ten.endswith('.txt'):
            kq.append(os.path.join(folder, ten))
    kq.sort()
    return kq
