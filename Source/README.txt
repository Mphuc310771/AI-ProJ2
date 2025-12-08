# Hashiwokakero (Bridges) Puzzle Solver

## Mô tả
Chương trình giải câu đố Hashiwokakero sử dụng nhiều thuật toán:
- CNF + PySAT
- A* Search
- Brute-force
- Backtracking

## Cài đặt

```bash
pip install -r requirements.txt
```

## Cách sử dụng

```bash
# Chạy với một file input cụ thể
python main.py --input Inputs/input-01.txt

# Chạy với thuật toán cụ thể
python main.py --input Inputs/input-01.txt --algorithm pysat
python main.py --input Inputs/input-01.txt --algorithm astar
python main.py --input Inputs/input-01.txt --algorithm bruteforce
python main.py --input Inputs/input-01.txt --algorithm backtracking

# Chạy tất cả test cases và so sánh thuật toán
python main.py --benchmark

# Hiển thị trợ giúp
python main.py --help
```

## Cấu trúc thư mục

```
Source/
├── main.py                 # Entry point
├── hashiwokakero.py        # Core puzzle representation
├── cnf_generator.py        # CNF clause generation
├── sat_solver.py           # PySAT integration
├── astar_solver.py         # A* algorithm
├── brute_force_solver.py   # Brute-force algorithm
├── backtracking_solver.py  # Backtracking algorithm
├── utils.py                # Utility functions
├── Inputs/                 # Test cases
└── Outputs/                # Generated solutions
```

## Định dạng Input
File input là ma trận CSV với:
- 0: ô trống
- 1-8: đảo với số cầu cần kết nối

Ví dụ:
```
0,2,0,5,0,0,2
0,0,0,0,0,0,0
4,0,2,0,2,0,4
0,0,0,0,0,0,0
0,1,0,5,0,2,0
0,0,0,0,0,0,0
4,0,0,0,0,0,3
```

## Định dạng Output
- Số: đảo
- `-`: một cầu ngang
- `=`: hai cầu ngang
- `|`: một cầu dọc
- `$`: hai cầu dọc
- `0`: ô trống
