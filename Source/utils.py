from hashiwokakero import Puzzle, PuzzleState
import os
import time
import tracemalloc


def format_output(grid):
    ds = []
    for row in grid:
        ds.append(str(row))
    return '\n'.join(ds)


def save_output(grid, duong_dan):
    with open(duong_dan, 'w', encoding='utf-8') as f:
        f.write(format_output(grid))


def print_puzzle(puzzle):
    print("Puzzle: %dx%d, %d dao" % (puzzle.rows, puzzle.cols, len(puzzle.islands)))
    for row in puzzle.grid:
        dong = ""
        for val in row:
            if val > 0:
                dong += str(val) + " "
            else:
                dong += ". "
        print(dong)
    print()


def print_solution(puzzle, state):
    out = puzzle.state_to_output(state)
    print("Loi giai:")
    for row in out:
        print(' '.join(row))
    print()


def print_output(grid):
    for row in grid:
        print(row)


def do_bo_nho(ham, *args, **kwargs):
    """Do bo nho su dung cua ham"""
    tracemalloc.start()
    kq = ham(*args, **kwargs)
    hien_tai, dinh = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return kq, dinh / 1024 / 1024  # tra ve MB


def compare_algorithms(puzzle, ds_algo, timeout=60.0):
    """So sanh cac thuat toan tren cung 1 puzzle"""
    ket_qua = {}
    
    for ten_algo in ds_algo:
        ham = ds_algo[ten_algo]
        print("Dang chay %s..." % ten_algo)
        
        try:
            tracemalloc.start()
            t1 = time.time()
            
            loi_giai, tg, thong_ke = ham(puzzle)
            
            hien_tai, dinh = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            ket_qua[ten_algo] = {
                "success": loi_giai is not None,
                "time": tg,
                "memory_mb": dinh / 1024 / 1024,
                "stats": thong_ke
            }
            
            if loi_giai is not None:
                ket_qua[ten_algo]["valid"] = puzzle.is_solution(loi_giai)
        
        except Exception as loi:
            tracemalloc.stop()
            ket_qua[ten_algo] = {
                "success": False,
                "error": str(loi)
            }
        
        # in ket qua
        if ket_qua[ten_algo].get('success'):
            print("  %s: OK" % ten_algo)
        else:
            print("  %s: FAIL" % ten_algo)
        
        if ket_qua[ten_algo].get('time'):
            print("  Thoi gian: %.4fs" % ket_qua[ten_algo]['time'])
        print()
    
    return ket_qua


def make_table(tat_ca_kq):
    """Tao bang so sanh dang markdown"""
    if len(tat_ca_kq) == 0:
        return ""
    
    # lay ten cac algo tu file dau tien
    file_dau = list(tat_ca_kq.keys())[0]
    ds_algo = list(tat_ca_kq[file_dau].keys())
    
    ds_dong = []
    
    # header
    header = "| File |"
    for a in ds_algo:
        header += " " + a + " |"
    ds_dong.append(header)
    
    # separator
    sep = "|"
    for _ in range(len(ds_algo) + 1):
        sep += "---|"
    ds_dong.append(sep)
    
    # data rows
    for fname in tat_ca_kq:
        res = tat_ca_kq[fname]
        row = "| " + fname + " |"
        
        for a in ds_algo:
            if a in res and res[a].get('time') is not None:
                row += " %.4fs |" % res[a]['time']
            else:
                row += " N/A |"
        
        ds_dong.append(row)
    
    return '\n'.join(ds_dong)


def check_input_file(duong_dan):
    """Kiem tra file input co hop le khong"""
    try:
        with open(duong_dan, 'r') as f:
            ds_dong = f.readlines()
        
        if len(ds_dong) == 0:
            return False
        
        so_cot = None
        for dong in ds_dong:
            dong = dong.strip()
            if not dong:
                continue
            
            parts = dong.split(',')
            for p in parts:
                val = int(p.strip())
                if val < 0 or val > 8:
                    return False
            
            if so_cot is None:
                so_cot = len(parts)
            elif len(parts) != so_cot:
                return False
        
        return True
    except:
        return False


def get_input_files(folder):
    """Lay danh sach cac file input trong folder"""
    ds = []
    for ten in os.listdir(folder):
        if ten.startswith('input-') and ten.endswith('.txt'):
            ds.append(os.path.join(folder, ten))
    ds.sort()
    return ds
