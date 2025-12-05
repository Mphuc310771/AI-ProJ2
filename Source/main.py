#!/usr/bin/env python3
"""
main.py
Entrypoint wrapper for pysat_solver.py
Usage: python main.py Inputs/input-01.txt
"""
import sys
from pysat_solver import parse_input, solve_hashi_with_pysat, format_solution, print_out_grid

def main(path):
    grid = parse_input(path)
    present_edges, status = solve_hashi_with_pysat(grid)
    if present_edges is None:
        print("No solution:", status)
        return
    out = format_solution(grid, present_edges)
    print_out_grid(out)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py Inputs/input-01.txt")
        sys.exit(1)
    main(sys.argv[1])
