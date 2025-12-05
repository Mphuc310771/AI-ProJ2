#!/usr/bin/env python3
"""
helper_debug.py
Simple debug runner: load input, show islands & edges
Usage: python helper_debug.py Inputs/input-01.txt
"""
import sys
from pysat_solver import parse_input, debug_show

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python helper_debug.py Inputs/input-01.txt")
        sys.exit(1)
    grid = parse_input(sys.argv[1])
    debug_show(grid)
