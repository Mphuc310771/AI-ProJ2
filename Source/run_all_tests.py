#!/usr/bin/env python3
"""
Run main.py on all Inputs/*.txt and store outputs in Outputs/
Usage: cd Source && python run_all_tests.py
"""
import os, subprocess, sys, time

inputs_dir = "Inputs"
outputs_dir = "Outputs"
os.makedirs(outputs_dir, exist_ok=True)

files = sorted([f for f in os.listdir(inputs_dir) if f.lower().endswith('.txt')])
for fn in files:
    inp = os.path.join(inputs_dir, fn)
    outf = os.path.join(outputs_dir, f"output-{fn.replace('input-','')}")
    start = time.perf_counter()
    p = subprocess.run([sys.executable, "main.py", inp], capture_output=True, text=True)
    elapsed = time.perf_counter() - start
    with open(outf, 'w', encoding='utf8') as f:
        f.write(p.stdout)
        f.write("\n# STDERR\n")
        f.write(p.stderr)
        f.write(f"\n# TIME {elapsed:.3f}s\n")
    print(f"Ran {fn} -> {outf} ({elapsed:.2f}s)")
