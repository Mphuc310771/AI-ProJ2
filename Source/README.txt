================================================================================
                         HASHIWOKAKERO SOLVER
================================================================================

INSTALLATION
------------
    cd Source
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


ALGORITHMS
----------
    pysat        - SAT solver using PySAT (fastest)
    astar        - A* search on CNF
    backtracking - Backtracking with pruning
    bruteforce   - Brute-force search


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
