import subprocess
import os
import time

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

    print(f"{'File':<15} | {'Algo':<12} | {'Time (s)':<10} | {'Status'}")
    print("-" * 55)

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
            try:
                # Chạy lệnh và giới hạn thời gian (timeout) 60 giây cho mỗi test
                # Tránh việc Brute-force chạy vô tận trên file lớn
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                end_time = time.time()
                duration = end_time - start_time

                if process.returncode == 0:
                    results[file_name][algo] = f"{duration:.4f}"
                    status = "OK"
                else:
                    results[file_name][algo] = "Error"
                    status = "Fail"
            except subprocess.TimeoutExpired:
                results[file_name][algo] = "Timeout"
                status = "Timeout (>60s)"
            except Exception as e:
                results[file_name][algo] = "Crash"
                status = "Crash"

            print(f"{file_name:<15} | {algo:<12} | {results[file_name][algo]:<10} | {status}")

    # In bảng tổng kết cuối cùng
    print("\n" + "="*80)
    print("BẢNG TỔNG HỢP THỜI GIAN CHẠY (GIÂY)")
    print("="*80)
    header = f"{'Input File':<15}"
    for algo in algorithms:
        header += f" | {algo:<12}"
    print(header)
    print("-" * 80)

    for file_name, data in results.items():
        row = f"{file_name:<15}"
        for algo in algorithms:
            val = data.get(algo, "N/A")
            row += f" | {val:<12}"
        print(row)

if __name__ == "__main__":
    run_comparison()