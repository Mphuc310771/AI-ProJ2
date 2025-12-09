================================================================================
                    HASHIWOKAKERO PUZZLE SOLVER
                    Do an mon Co So Tri Tue Nhan Tao
================================================================================

1. YEU CAU HE THONG
-------------------
- Python 3.7 tro len (khuyen nghi Python 3.9+)
- pip (de cai thu vien)


2. CAI DAT
----------
Buoc 1: Mo terminal/cmd, di chuyen vao thu muc Source
    cd duong/dan/toi/Source

Buoc 2: Cai thu vien can thiet
    pip install -r requirements.txt

Neu bi loi permission thi dung:
    pip install --user -r requirements.txt

Neu van bi loi thi thu:
    python -m pip install python-sat


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

e) Xem huong dan:
    python main.py --help


4. CAU TRUC THU MUC
-------------------
Source/
  |- main.py               # file chinh, chay chuong trinh tu day
  |- hashiwokakero.py      # dinh nghia puzzle, dao, cau
  |- cnf_generator.py      # sinh menh de CNF cho SAT solver
  |- sat_solver.py         # giai bang PySAT
  |- astar_solver.py       # giai bang thuat toan A*
  |- brute_force_solver.py # giai bang vet can
  |- backtracking_solver.py # giai bang quay lui
  |- utils.py              # cac ham tien ich
  |- requirements.txt      # thu vien can cai
  |- Inputs/               # cac file input mau
  |- Outputs/              # ket qua sau khi giai


5. DINH DANG FILE INPUT
-----------------------
File input la file text, moi dong la 1 hang cua puzzle.
Cac so cach nhau boi dau phay (,).

Y nghia cac so:
- 0: o trong (khong co dao)
- 1-8: dao, so la so cau can noi

Vi du file input:
    0,2,0,5,0,0,2
    0,0,0,0,0,0,0
    4,0,2,0,2,0,4
    0,0,0,0,0,0,0
    0,1,0,5,0,2,0
    0,0,0,0,0,0,0
    4,0,0,0,0,0,3


6. DINH DANG FILE OUTPUT
------------------------
Output la luoi puzzle da giai, voi cac ky hieu:
- So (1-8): dao
- 0: o trong
- -: 1 cau ngang
- =: 2 cau ngang
- |: 1 cau doc
- $: 2 cau doc


7. CAC THUAT TOAN
-----------------
a) pysat: dung thu vien PySAT, chuyen bai toan sang CNF roi giai.
   Nhanh nhat, khuyen dung cho puzzle lon.

b) astar: thuat toan A* voi heuristic tinh so cau con thieu.
   Kha nhanh, dam bao tim loi giai neu co.

c) backtracking: quay lui co cat tia.
   Trung binh, phu hop puzzle vua.

d) bruteforce: vet can tat ca to hop.
   Cham nhat, chi dung cho puzzle nho (duoi 15 cau).


8. MOT SO LOI THUONG GAP
------------------------
Loi: ModuleNotFoundError: No module named 'pysat'
Cach sua: Chay lai "pip install python-sat"

Loi: FileNotFoundError
Cach sua: Kiem tra duong dan file input co dung khong

Loi: Khong tim duoc loi giai
Nguyen nhan: Puzzle khong co loi giai hop le


================================================================================
