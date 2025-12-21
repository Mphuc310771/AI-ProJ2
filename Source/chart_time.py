import json
import matplotlib.pyplot as plt
import os

def draw_chart():
    # 1. Đọc dữ liệu từ file JSON
    if not os.path.exists("results.json"):
        print("Lỗi: Không tìm thấy file results.json. Hãy chạy compare.py trước!")
        return

    with open("results.json", "r", encoding="utf-8") as f:
        results = json.load(f)

    # 2. Chuẩn bị dữ liệu để vẽ
    # Sắp xếp tên file input theo đúng thứ tự từ 01 đến 10
    input_files = sorted(results.keys())
    algorithms = ['pysat', 'astar', 'backtracking', 'bruteforce']
    
    # Tạo bảng màu và ký hiệu cho các đường
    styles = {
        'pysat': {'color': 'blue', 'marker': 'o'},
        'astar': {'color': 'green', 'marker': 's'},
        'backtracking': {'color': 'orange', 'marker': '^'},
        'bruteforce': {'color': 'red', 'marker': 'x'}
    }

    plt.figure(figsize=(12, 7))

    for algo in algorithms:
        times = []
        for file in input_files:
            val = results[file].get(algo, {}).get("time", "N/A")
            
            # Xử lý các trường hợp không phải là số (Timeout, Error, N/A)
            try:
                times.append(float(val))
            except (ValueError, TypeError):
                # Nếu Timeout (>60s), ta có thể vẽ ở mức 60 để thấy sự khác biệt
                # hoặc gán None để đường biểu đồ bị ngắt quãng. Ở đây gán 60:
                times.append(60.0) 

        # Vẽ đường cho thuật toán này
        plt.plot(input_files, times, label=algo, 
                 color=styles[algo]['color'], 
                 marker=styles[algo]['marker'], 
                 linewidth=2, markersize=8)

    # 3. Định dạng biểu đồ
    plt.title("So sánh thời gian chạy của 4 thuật toán", fontsize=16, fontweight='bold')
    plt.xlabel("Input Files", fontsize=12)
    plt.ylabel("Thời gian (Giây)", fontsize=12)
    
    # Vẽ đường kẻ ngang mờ tại mức 60s để đánh dấu ngưỡng Timeout
    plt.axhline(y=60, color='gray', linestyle='--', alpha=0.5, label="Timeout (60s)")
    
    plt.xticks(rotation=45)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend()
    
    # Tối ưu khoảng cách
    plt.tight_layout()

    # 4. Lưu và hiển thị
    plt.savefig("algorithm_comparison_chart.png")
    print("Đã lưu biểu đồ vào file: algorithm_comparison_chart.png")
    plt.show()

if __name__ == "__main__":
    draw_chart()