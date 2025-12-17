from hashiwokakero import Puzzle, PuzzleState
from itertools import product
import time


class BruteForceSolver:
    
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.tg_chay = 0
        self.so_lan_thu = 0
    
    def solve(self):
        t1 = time.time()
        self.so_lan_thu = 0
        
        ds_cau = self.puzzle.get_possible_bridges()
        n = len(ds_cau)
        
        # canh bao neu qua nhieu to hop
        if n > 20:
            tong = 3 ** n
            print(">> Canh bao: %d cap dao -> %d to hop!" % (n, tong))
        
        # duyet het tat ca to hop (0, 1, 2) cho moi cap dao
        for to_hop in product([0, 1, 2], repeat=n):
            self.so_lan_thu += 1
            
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
            "algorithm": "Brute-force"
        }


def solve_bruteforce(puzzle):
    solver = BruteForceSolver(puzzle)
    kq = solver.solve()
    return kq, solver.tg_chay, solver.get_stats()
