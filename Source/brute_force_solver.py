# brute force - vet can tat ca to hop
# chi nen dung cho puzzle nho

from hashiwokakero import Puzzle, PuzzleState
from itertools import product
import time


class BruteForceSolver:
    # vet can 3^n trang thai
    
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.time_spent = 0
        self.da_thu = 0
    
    def solve(self):
        t1 = time.time()
        self.da_thu = 0
        
        cac_cau = self.puzzle.get_possible_bridges()
        n = len(cac_cau)
        
        # canh bao neu puzzle qua lon
        if n > 20:
            tong = 3 ** n
            print("CANH BAO: %d cap dao -> %d to hop, rat lau!" % (n, tong))
        
        # thu het
        for to_hop in product([0, 1, 2], repeat=n):
            self.da_thu = self.da_thu + 1
            
            # tao state
            state = PuzzleState()
            for i in range(n):
                cnt = to_hop[i]
                if cnt > 0:
                    d1, d2 = cac_cau[i]
                    state.bridges[(d1, d2)] = cnt
            
            # check loi giai
            if self.puzzle.is_solution(state):
                self.time_spent = time.time() - t1
                return state
            
            # in tien do 
            if self.da_thu % 100000 == 0:
                dt = time.time() - t1
                print("Da thu %d to hop (%.1f giay)..." % (self.da_thu, dt))
        
        self.time_spent = time.time() - t1
        return None  # khong tim thay
    
    def get_stats(self):
        n = len(self.puzzle.get_possible_bridges())
        return {
            "time": self.time_spent,
            "da_thu": self.da_thu,
            "tong": 3 ** n,
            "so_cap": n,
            "algorithm": "Brute-force"
        }


def solve_bruteforce(puzzle):
    s = BruteForceSolver(puzzle)
    kq = s.solve()
    return kq, s.time_spent, s.get_stats()
