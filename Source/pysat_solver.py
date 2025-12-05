#!/usr/bin/env python3
"""
pysat_solver.py
Core Hashiwokakero solver using PySAT (CardEnc).
Provides: parse_input, solve_hashi_with_pysat, format_solution, helper debug.
"""

from itertools import combinations
from collections import deque, defaultdict

from pysat.formula import CNF, IDPool
from pysat.card import CardEnc
from pysat.solvers import Solver

# ---------- Parsing ----------
def parse_input(path):
    """Đọc file input (commas or spaces), trả về grid list[list[int]]"""
    with open(path, 'r', encoding='utf8') as f:
        lines = [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith('#')]
    grid = []
    for ln in lines:
        parts = [p.strip() for p in ln.replace(',', ' ').split()]
        if not parts:
            continue
        row = [int(x) for x in parts]
        grid.append(row)
    if not grid:
        raise ValueError("Input empty or invalid.")
    # pad rows to same width
    width = max(len(r) for r in grid)
    for r in grid:
        if len(r) < width:
            r.extend([0] * (width - len(r)))
    return grid

# ---------- Utilities ----------
def find_islands(grid):
    islands = {}
    for r,row in enumerate(grid):
        for c,val in enumerate(row):
            if val != 0:
                islands[(r,c)] = val
    return islands

def find_edges(grid):
    """Tìm các cạnh có thể nối (ngang/dọc) giữa đảo.
    edge = ((r1,c1),(r2,c2), orientation, path_cells) -- path_cells là tuple
    """
    R, C = len(grid), len(grid[0])
    islands = find_islands(grid)
    coords = sorted(islands.keys())
    edges = []
    for (r,c) in coords:
        # đi phải
        cc = c + 1
        while cc < C:
            if grid[r][cc] != 0:
                edges.append(((r,c),(r,cc),'H', tuple((r,x) for x in range(c+1, cc))))
                break
            cc += 1
        # đi xuống
        rr = r + 1
        while rr < R:
            if grid[rr][c] != 0:
                edges.append(((r,c),(rr,c),'V', tuple((x,c) for x in range(r+1, rr))))
                break
            rr += 1
    # chuẩn hoá: mỗi cặp 1 lần, path là tuple
    norm = {}
    for a,b,orient,path in edges:
        key = tuple(sorted([a,b]))
        if key not in norm:
            ori = 'H' if key[0][0] == key[1][0] else 'V'
            (r1,c1),(r2,c2) = key
            if ori == 'H':
                path_cells = tuple((r1,x) for x in range(min(c1,c2)+1, max(c1,c2)))
            else:
                path_cells = tuple((x,c1) for x in range(min(r1,r2)+1, max(r1,r2)))
            norm[key] = (key[0], key[1], ori, path_cells)
    return list(norm.values())

# ---------- CNF building ----------
def build_cnf(grid, vpool=None):
    """
    Trả về (cnf, edge_vars, edges, vpool).
    edge_vars: dict edge -> (v1, v2) (mỗi biến = 1 sợi cầu)
    """
    if vpool is None:
        vpool = IDPool()
    cnf = CNF()
    islands = find_islands(grid)
    edges = find_edges(grid)

    # biến cho mỗi cạnh: 2 biến (mỗi biến = 1 sợi cầu)
    edge_vars = {}
    for idx, edge in enumerate(edges):
        b1 = vpool.id(f"e{idx}_b1")
        b2 = vpool.id(f"e{idx}_b2")
        edge_vars[edge] = (b1, b2)

    # ràng buộc tại mỗi đảo: sum(vars incident) == required
    for island_coord, required in islands.items():
        lits = []
        incident_edges = 0
        for edge, (v1, v2) in edge_vars.items():
            a,b,_,_ = edge
            if island_coord == a or island_coord == b:
                lits.append(v1)
                lits.append(v2)
                incident_edges += 1
        if required > 0 and incident_edges == 0:
            # không có cạnh nào nối tới đảo -> UNSAT
            raise ValueError(f"Island at {island_coord} requires {required} but has no incident edges -> UNSAT")
        # max possible number of bridges incident to this island = 2 * incident_edges
        n = len(lits)  # equals 2 * incident_edges
        if required < 0:
            raise ValueError(f"Island at {island_coord} has invalid required number {required}")
        if required > n:
            # báo rõ ràng: required lớn hơn khả năng tối đa
            raise ValueError(f"Island at {island_coord} requires {required} but max possible is {n} (incident edges: {incident_edges}) -> UNSAT")
        if lits:
            # sum(lits) <= required
            at_most = CardEnc.atmost(lits=lits, bound=required, vpool=vpool)
            for cl in at_most.clauses:
                cnf.append(cl)
            # sum(lits) >= required  <=> sum(not lits) <= n - required
            neg_lits = [-x for x in lits]
            at_most2 = CardEnc.atmost(lits=neg_lits, bound=n - required, vpool=vpool)
            for cl in at_most2.clauses:
                cnf.append(cl)


    # Non-crossing constraints: nếu 2 đường cắt nhau, không cho cả hai có >0
    edge_list = list(edge_vars.keys())
    for i,j in combinations(range(len(edge_list)), 2):
        e1 = edge_list[i]; e2 = edge_list[j]
        a1,b1,orient1,path1 = e1
        a2,b2,orient2,path2 = e2
        if set(path1) & set(path2):
            v1_1, v1_2 = edge_vars[e1]
            v2_1, v2_2 = edge_vars[e2]
            cnf.append([-v1_1, -v2_1])
            cnf.append([-v1_1, -v2_2])
            cnf.append([-v1_2, -v2_1])
            cnf.append([-v1_2, -v2_2])

    return cnf, edge_vars, edges, vpool

# ---------- Decode model -> graph ----------
def decode_model(model, edge_vars, edges):
    assigned = set(l for l in model if l > 0)
    present_edges = {}
    for edge in edges:
        v1, v2 = edge_vars[edge]
        cnt = 0
        if v1 in assigned:
            cnt += 1
        if v2 in assigned:
            cnt += 1
        if cnt > 0:
            present_edges[edge] = cnt
    return present_edges

def is_connected(present_edges, islands):
    if not islands:
        return True
    adj = defaultdict(list)
    for (a,b,orient,path), cnt in present_edges.items():
        if cnt > 0:
            adj[a].append(b)
            adj[b].append(a)
    start = next(iter(islands.keys()))
    visited = set([start])
    q = deque([start])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in visited:
                visited.add(v)
                q.append(v)
    return len(visited) == len(islands)

# ---------- Output formatting ----------
def format_solution(grid, present_edges):
    R, C = len(grid), len(grid[0])
    out = [['0' for _ in range(C)] for __ in range(R)]
    for r in range(R):
        for c in range(C):
            if grid[r][c] != 0:
                out[r][c] = str(grid[r][c])
    for (a,b,orient,path), cnt in present_edges.items():
        if cnt == 0:
            continue
        if orient == 'H':
            ch = '-' if cnt == 1 else '='
            for (r,c) in path:
                out[r][c] = ch
        else:
            ch = '|' if cnt == 1 else '$'
            for (r,c) in path:
                out[r][c] = ch
    return out

def print_out_grid(out):
    for row in out:
        print("[ " + " , ".join(f'"{x}"' for x in row) + " ]")

# ---------- Solve with PySAT + lazy connectivity blocking ----------
def solve_hashi_with_pysat(grid, max_iter=1000):
    islands = find_islands(grid)
    cnf, edge_vars, edges, vpool = build_cnf(grid)
    with Solver(bootstrap_with=cnf.clauses) as solver:
        blocked = 0
        while True:
            sat = solver.solve()
            if not sat:
                return None, "UNSAT"
            model = solver.get_model()
            model_set = set(l for l in model if l > 0)
            present_edges = decode_model(model_set, edge_vars, edges)
            if is_connected(present_edges, islands):
                return present_edges, "SAT_connected"
            # block this exact assignment on the edge variables:
            block_clause = []
            all_edge_vars = []
            for edge in edges:
                v1, v2 = edge_vars[edge]
                all_edge_vars.append((v1, v1 in model_set))
                all_edge_vars.append((v2, v2 in model_set))
            for var, is_true in all_edge_vars:
                block_clause.append(-var if is_true else var)
            solver.add_clause(block_clause)
            blocked += 1
            if blocked >= max_iter:
                return None, "loop_limit"

# ---------- Debug helper ----------
def debug_show(grid):
    islands = find_islands(grid)
    edges = find_edges(grid)
    print("Grid:", len(grid), "x", len(grid[0]))
    for r in grid:
        print(' '.join(str(x) for x in r))
    print("\nIslands:")
    for k,v in sorted(islands.items()):
        print(" ", k, "->", v)
    print("\nEdges:")
    for e in edges:
        a,b,ori,path = e
        print(" ", a, "<->", b, ori, "path:", path)
    inc = {}
    for k in islands:
        inc[k] = 0
    for a,b,_,_ in edges:
        inc[a] += 1
        inc[b] += 1
    print("\nIncident counts:")
    for k in sorted(islands.keys()):
        print(" ", k, "->", inc.get(k,0), "(requires", islands[k], ")")
