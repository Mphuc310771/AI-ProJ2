from hashiwokakero import Puzzle, PuzzleState
from itertools import product
import time


class BruteForceSolver:
    
    def __init__(self, puzzle, timeout_seconds=None):
        self.puzzle = puzzle
        self.tg_chay = 0
        self.so_lan_thu = 0
        self._start_time = None
        self._timeout_seconds = timeout_seconds
        self.timed_out = False
    
    def solve(self):
        t1 = time.time()
        self.so_lan_thu = 0
        self._start_time = t1
        self.timed_out = False
        
        ds_cau = self.puzzle.get_possible_bridges()
        n = len(ds_cau)
        
        # canh bao neu qua nhieu to hop
        if n > 20:
            tong = 3 ** n
            print(">> Canh bao: %d cap dao -> %d to hop!" % (n, tong))
        
        # duyet het tat ca to hop (0, 1, 2) cho moi cap dao
        for to_hop in product([0, 1, 2], repeat=n):
            self.so_lan_thu += 1

            # Kiểm tra timeout mỗi vòng lặp
            if self._timeout_seconds is not None and self._start_time is not None:
                if time.time() - self._start_time > self._timeout_seconds:
                    self.tg_chay = time.time() - t1
                    self.timed_out = True
                    return None
            
            # tao state tu to hop
            state = PuzzleState()
            for i in range(n):
                so_cau = to_hop[i]
                if so_cau > 0:
                    d1, d2 = ds_cau[i]
                    state.bridges[(d1, d2)] = so_cau
            
            # kiem tra xem co phai loi giai khong
            if self.puzzle.is_solution(state):
                self.tg_chay = time.time() - t1
                return state
            
            # in tien do moi 100k lan thu
            if self.so_lan_thu % 100000 == 0:
                dt = time.time() - t1
                print("   Da thu %d to hop (%.1f giay)..." % (self.so_lan_thu, dt))
        
        self.tg_chay = time.time() - t1
        return None
    
    def get_stats(self):
        n = len(self.puzzle.get_possible_bridges())
        return {
            "time": self.tg_chay,
            "da_thu": self.so_lan_thu,
            "tong": 3 ** n,
            "so_cap": n,
            "algorithm": "Brute-force",
            "timed_out": getattr(self, 'timed_out', False),
            "timeout_seconds": self._timeout_seconds
        }


def solve_bruteforce(puzzle, timeout_seconds=60):
    solver = BruteForceSolver(puzzle, timeout_seconds=timeout_seconds)
    kq = solver.solve()
    return kq, solver.tg_chay, solver.get_stats()
