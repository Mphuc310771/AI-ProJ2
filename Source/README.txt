================================================================================
                         HASHIWOKAKERO SOLVER
================================================================================

<<<<<<< HEAD
INSTALLATION
------------
    cd Source
=======
1. YEU CAU HE THONG
-------------------
- Python 3.7 tro len (khuyen nghi Python 3.9+)
- pip (de cai thu vien)


2. CAI DAT
----------
Buoc 0: Tao va kich hoat moi truong ao (KHUYEN NGHI)
Su dung moi truong ao giup tranh xung dot thu vien va de dang chay tren nhieu may khac nhau.
Tren Windows:
    python -m venv venv
    venv\Scripts\activate

Tren Linux / macOS:
    python3 -m venv venv
    source venv/bin/activate

Buoc 1: Mo terminal/cmd, di chuyen vao thu muc Source
    cd duong/dan/toi/Source

Buoc 2: Cai thu vien can thiet
>>>>>>> fa6d456544fb179f4c19766ec59ae17f47d8aa2f
    pip install -r requirements.txt


USAGE
-----
    Solve a puzzle:
        python main.py --input Inputs/input-01.txt

    Choose algorithm:
        python main.py --input Inputs/input-01.txt --algorithm pysat
        python main.py --input Inputs/input-01.txt --algorithm astar
        python main.py --input Inputs/input-01.txt --algorithm backtracking
        python main.py --input Inputs/input-01.txt --algorithm bruteforce

    Run benchmark:
        python main.py --benchmark

    Compare algorithms:
        python compare.py


<<<<<<< HEAD
ALGORITHMS
----------
    pysat        - SAT solver using PySAT (fastest)
    astar        - A* search on CNF
    backtracking - Backtracking with pruning
    bruteforce   - Brute-force search
=======
3. CACH CHAY CHUONG TRINH
-------------------------

a) Giai 1 file input cu the:
    python main.py --input Inputs/input-01.txt

b) Chon thuat toan (mac dinh la pysat):
    python main.py --input Inputs/input-01.txt --algorithm pysat
    python main.py --input Inputs/input-01.txt --algorithm astar
    python main.py --input Inputs/input-01.txt --algorithm bruteforce
    python main.py --input Inputs/input-01.txt --algorithm backtracking

c) Luu ket qua ra file:
    python main.py --input Inputs/input-01.txt --output Outputs/output-01.txt

d) Chay benchmark (test tat ca file input):
    python main.py --benchmark

e) Chay so sanh pysat, A*, backtracking, bruteforce
    python compare.py

f) Ve bieu do so sanh pysat, A*, backtracking, bruteforce
    python chart.py

g) Xem huong dan:
    python main.py --help
>>>>>>> fa6d456544fb179f4c19766ec59ae17f47d8aa2f


FILE STRUCTURE
--------------
    main.py                  Entry point
    cnf_generator.py         CNF formula generator
    sat_solver.py            PySAT solver
    astar_to_solve_cnf.py    A* solver
    backtracking_solver.py   Backtracking solver
    brute_force_solver.py    Brute-force solver
    compare.py               Algorithm comparison
    Inputs/                  Input files
    Outputs/                 Output files


INPUT FORMAT
------------
    CSV with comma-separated values:
    - 0   = empty cell
    - 1-8 = island (number = required bridges)

    Example:
        0,2,0,5,0,0,2
        0,0,0,0,0,0,0
        4,0,2,0,2,0,4


OUTPUT FORMAT
-------------
    -  single horizontal bridge
    =  double horizontal bridge
    |  single vertical bridge
    $  double vertical bridge

================================================================================
