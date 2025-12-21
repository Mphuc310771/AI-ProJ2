import subprocess
import os
import time
try:
    import psutil
    _PSUTIL_AVAILABLE = True
except Exception:
    psutil = None
    _PSUTIL_AVAILABLE = False

def run_comparison():
    # Cấu hình đường dẫn
    input_folder = "Inputs"
    output_folder = "Outputs"
    algorithms = ['pysat', 'astar', 'backtracking', 'bruteforce']
    
    # Tạo thư mục output nếu chưa có
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Khởi tạo bảng kết quả
    # { 'input-01.txt': { 'pysat': time, 'astar': time, ... }, ... }
    results = {}

    print(f"{'File':<15} | {'Algo':<12} | {'Time (s)':<10} | {'Mem (MB)':<10} | {'Status'}")
    print("-" * 80)

    for i in range(1, 11):
        file_name = f"input-{i:02d}.txt"
        input_path = os.path.join(input_folder, file_name)
        results[file_name] = {}

        if not os.path.exists(input_path):
            print(f"Lỗi: Không tìm thấy {input_path}")
            continue

        for algo in algorithms:
            # Đối với Brute-force, nếu input quá lớn có thể bỏ qua để tránh treo máy
            # Bạn có thể điều chỉnh logic này tùy theo sức mạnh máy tính
            out_file = os.path.join(output_folder, f"output-{algo}-{i:02d}.txt")
            
            cmd = [
                "python", "main.py",
                "--input", input_path,
                "--algorithm", algo,
                "--output", out_file,
                "--quiet" # Sử dụng chế độ im lặng để dễ parse kết quả
            ]

            start_time = time.time()
            peak_mem = 0
            status = ""
            try:
                # Khởi chạy tiến trình con để dễ theo dõi bộ nhớ
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                pid = proc.pid

                psproc = None
                if _PSUTIL_AVAILABLE:
                    try:
                        psproc = psutil.Process(pid)
                    except Exception:
                        psproc = None

                timeout = 60.0
                deadline = start_time + timeout
                # Poll loop để lấy memory peak
                while True:
                    if psproc is not None:
                        try:
                            mem = psproc.memory_info().rss
                            if mem > peak_mem:
                                peak_mem = mem
                        except psutil.NoSuchProcess:
                            break
                        except Exception:
                            pass

                    ret = proc.poll()
                    if ret is not None:
                        break
                    if time.time() > deadline:
                        proc.kill()
                        raise subprocess.TimeoutExpired(cmd, timeout)
                    time.sleep(0.01)

                # Đảm bảo đọc hết output
                try:
                    out, err = proc.communicate(timeout=1)
                except Exception:
                    out, err = (None, None)

                end_time = time.time()
                duration = end_time - start_time

                # Chuyển đổi peak_mem sang MB, nếu không có psutil thì ghi N/A
                if peak_mem and peak_mem > 0:
                    mem_mb = peak_mem / 1024.0 / 1024.0
                    mem_display = f"{mem_mb:.2f}"
                else:
                    mem_display = "N/A" if not _PSUTIL_AVAILABLE else "0.00"

                if proc.returncode == 0:
                    results[file_name][algo] = {"time": f"{duration:.4f}", "mem": mem_display}
                    status = "OK"
                else:
                    results[file_name][algo] = {"time": "Error", "mem": mem_display}
                    status = "Fail"
            except subprocess.TimeoutExpired:
                results[file_name][algo] = {"time": "Timeout", "mem": "N/A"}
                status = "Timeout (>60s)"
            except Exception:
                results[file_name][algo] = {"time": "Crash", "mem": "N/A"}
                status = "Crash"

            time_display = results[file_name][algo]["time"]
            mem_display = results[file_name][algo]["mem"]
            print(f"{file_name:<15} | {algo:<12} | {time_display:<10} | {mem_display:<10} | {status}")

    # In bảng tổng kết cuối cùng
    print("\n" + "="*80)
    if _PSUTIL_AVAILABLE:
        print("BẢNG TỔNG HỢP THỜI GIAN VÀ BỘ NHỚ (GIÂY / MB)")
    else:
        print("BẢNG TỔNG HỢP THỜI GIAN (GIÂY) — psutil không có, bộ nhớ hiển thị N/A")
    print("="*80)
    header = f"{'Input File':<15}"
    for algo in algorithms:
        header += f" | {algo:<12}"
        header += " " * 0
    print(header)
    print("-" * 80)

    for file_name, data in results.items():
        row = f"{file_name:<15}"
        for algo in algorithms:
            val = data.get(algo, {"time": "N/A", "mem": "N/A"})
            if isinstance(val, dict):
                cell = f"{val.get('time','N/A')}/{val.get('mem','N/A')}"
            else:
                # Cũ: chỉ có chuỗi thời gian
                cell = f"{val}/N/A"
            row += f" | {cell:<12}"
        print(row)

    import json
    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
    print("\n[Thông báo] Đã lưu kết quả vào file results.json")

if __name__ == "__main__":
    run_comparison()