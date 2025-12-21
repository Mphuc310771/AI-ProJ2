import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


# RAW TABLE: dán bảng kết quả ở đây (mỗi dòng một record)
raw_table = '''
File            | Algo         | Time (s)   | Mem (MB)   | Status
--------------------------------------------------------------------------------
input-01.txt    | pysat        | 0.1378     | 22.30      | OK
input-01.txt    | astar        | 0.1460     | 22.42      | OK
input-01.txt    | backtracking | 4.6556     | 22.27      | OK
input-01.txt    | bruteforce   | 3.7611     | 22.20      | OK
input-02.txt    | pysat        | 0.1324     | 23.12      | OK
input-02.txt    | astar        | 0.1816     | 22.48      | OK
input-02.txt    | backtracking | Timeout    | N/A        | Timeout (>60s)
input-02.txt    | bruteforce   | Timeout    | N/A        | Timeout (>60s)
input-03.txt    | pysat        | 0.1331     | 22.36      | OK
input-03.txt    | astar        | 0.1531     | 22.44      | OK
input-03.txt    | backtracking | 3.4071     | 22.21      | OK
input-03.txt    | bruteforce   | 4.1443     | 22.22      | OK
input-04.txt    | pysat        | 0.1375     | 22.71      | OK
input-04.txt    | astar        | 0.6297     | 24.89      | OK
input-04.txt    | backtracking | Timeout    | N/A        | Timeout (>60s)
input-04.txt    | bruteforce   | Timeout    | N/A        | Timeout (>60s)
input-05.txt    | pysat        | 0.1950     | 26.38      | OK
input-05.txt    | astar        | Timeout    | N/A        | Timeout (>60s)
input-05.txt    | backtracking | Timeout    | N/A        | Timeout (>60s)
input-05.txt    | bruteforce   | Timeout    | N/A        | Timeout (>60s)
input-06.txt    | pysat        | 0.1465     | 22.30      | OK
input-06.txt    | astar        | 0.1771     | 22.66      | OK
input-06.txt    | backtracking | Timeout    | N/A        | Timeout (>60s)
input-06.txt    | bruteforce   | Timeout    | N/A        | Timeout (>60s)
input-07.txt    | pysat        | 0.1323     | 22.66      | OK
input-07.txt    | astar        | 1.7412     | 28.33      | OK
input-07.txt    | backtracking | Timeout    | N/A        | Timeout (>60s)
input-07.txt    | bruteforce   | Timeout    | N/A        | Timeout (>60s)
input-08.txt    | pysat        | 0.1631     | 23.51      | OK
input-08.txt    | astar        | 7.3092     | 46.05      | OK
input-08.txt    | backtracking | Timeout    | N/A        | Timeout (>60s)
input-08.txt    | bruteforce   | Timeout    | N/A        | Timeout (>60s)
input-09.txt    | pysat        | 0.1439     | 23.60      | OK
input-09.txt    | astar        | 40.1612    | 200.59     | OK
input-09.txt    | backtracking | Timeout    | N/A        | Timeout (>60s)
input-09.txt    | bruteforce   | Timeout    | N/A        | Timeout (>60s)
input-10.txt    | pysat        | 0.1611     | 24.72      | OK
input-10.txt    | astar        | Timeout    | N/A        | Timeout (>60s)
input-10.txt    | backtracking | Timeout    | N/A        | Timeout (>60s)
input-10.txt    | bruteforce   | Timeout    | N/A        | Timeout (>60s)
'''


def parse_table(raw: str):
    rows = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('File') or line.startswith('-') or line.startswith('---'):
            continue
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 5:
            continue
        file, algo, time_s, mem_mb, status = parts[0], parts[1], parts[2], parts[3], parts[4]
        # Parse time
        time_val = None
        t = time_s.strip()
        if t == '' or 'timeout' in t.lower() or 'timeout' in status.lower():
            time_val = np.nan
        else:
            try:
                time_val = float(t)
            except Exception:
                time_val = np.nan

        # Parse memory
        mem_val = None
        m = mem_mb.strip()
        if m == '' or m.upper() == 'N/A':
            mem_val = np.nan
        else:
            try:
                mem_val = float(m)
            except Exception:
                mem_val = np.nan

        rows.append({'File': file, 'Algo': algo, 'Time': time_val, 'Mem': mem_val, 'Status': status})

    return pd.DataFrame(rows)


def natural_sort_files(files):
    def keyfn(name):
        import re
        m = re.search(r"(\d+)", name)
        return int(m.group(1)) if m else name
    return sorted(files, key=keyfn)


def plot_results(df_raw: pd.DataFrame, save_path='comparison_plot.png'):
    files = natural_sort_files(df_raw['File'].unique())
    algos = sorted(df_raw['Algo'].unique())

    df_time = df_raw.pivot(index='File', columns='Algo', values='Time').reindex(files)
    df_mem = df_raw.pivot(index='File', columns='Algo', values='Mem').reindex(files)

    colors = {'pysat': '#1f77b4', 'astar': '#ff7f0e', 'backtracking': '#2ca02c', 'bruteforce': '#d62728'}
    markers = {'pysat': 'o', 'astar': 's', 'backtracking': '^', 'bruteforce': 'x'}

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharex=True)

    # TIME PLOT
    ax_t = axes[0]
    for algo in algos:
        y = df_time[algo].values if algo in df_time else np.array([np.nan]*len(files))
        ax_t.plot(files, y, marker=markers.get(algo, 'o'), linewidth=2, label=algo, color=colors.get(algo))

    # Mark timeouts: where Time is NaN but Status contains 'Timeout'
    timeout_threshold = 60.0
    max_time = np.nanmax(df_time.values)
    if np.isfinite(max_time):
        tmark_y = max(max_time * 1.05, timeout_threshold * 0.6)
    else:
        tmark_y = timeout_threshold

    for f in files:
        row = df_raw[df_raw['File'] == f]
        for algo in algos:
            rec = row[row['Algo'] == algo]
            if not rec.empty:
                status = rec['Status'].values[0]
                if 'timeout' in status.lower():
                    ax_t.scatter(f, tmark_y, marker='X', color=colors.get(algo), s=80, zorder=5)

    ax_t.axhline(y=timeout_threshold, color='red', linestyle='--', alpha=0.6)
    ax_t.text(0, timeout_threshold * 1.01, 'Timeout (60s)', color='red', fontweight='bold')
    ax_t.set_title('Thời gian chạy (giây)')
    ax_t.set_xlabel('Input files')
    ax_t.set_ylabel('Time (s)')
    ax_t.set_xticklabels(files, rotation=45)
    ax_t.grid(True, linestyle=':', alpha=0.6)
    ax_t.legend(loc='upper left', bbox_to_anchor=(1, 1))

    # MEMORY PLOT
    ax_m = axes[1]
    for algo in algos:
        y = df_mem[algo].values if algo in df_mem else np.array([np.nan]*len(files))
        ax_m.plot(files, y, marker=markers.get(algo, 'o'), linewidth=2, label=algo, color=colors.get(algo))

    ax_m.set_title('Bộ nhớ đỉnh (MB)')
    ax_m.set_xlabel('Input files')
    ax_m.set_ylabel('Memory (MB)')
    ax_m.set_xticklabels(files, rotation=45)
    ax_m.grid(True, linestyle=':', alpha=0.6)
    ax_m.legend(loc='upper left', bbox_to_anchor=(1, 1))

    plt.tight_layout()
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    print(f"Saved plot to {save_path}")
    plt.show()


if __name__ == '__main__':
    df = parse_table(raw_table)
    plot_results(df)