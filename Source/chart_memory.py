import json
import matplotlib.pyplot as plt
import os

def draw_memory_chart():
    # 1. Đọc dữ liệu từ file JSON
    if not os.path.exists("results.json"):
        print("Lỗi: Không tìm thấy file results.json. Hãy chạy compare.py trước!")
        return

    with open("results.json", "r", encoding="utf-8") as f:
        results = json.load(f)

    # 2. Chuẩn bị dữ liệu
    input_files = sorted(results.keys())
    algorithms = ['pysat', 'astar', 'backtracking', 'bruteforce']
    
    # Giữ nguyên bảng màu và marker để đồng bộ với biểu đồ thời gian
    styles = {
        'pysat': {'color': 'blue', 'marker': 'o'},
        'astar': {'color': 'green', 'marker': 's'},
        'backtracking': {'color': 'orange', 'marker': '^'},
        'bruteforce': {'color': 'red', 'marker': 'x'}
    }

    plt.figure(figsize=(12, 7))

    for algo in algorithms:
        mem_usages = []
        for file in input_files:
            val = results[file].get(algo, {}).get("mem", "N/A")
            
            try:
                # Chuyển đổi sang float nếu là số
                mem_usages.append(float(val))
            except (ValueError, TypeError):
                # Nếu là N/A (do Timeout), gán là None để matplotlib không vẽ điểm đó
                # Hoặc gán 0 tùy theo ý muốn của bạn. Ở đây dùng None để đường bị ngắt.
                mem_usages.append(None) 

        # Vẽ đường cho thuật toán này
        plt.plot(input_files, mem_usages, label=algo, 
                 color=styles[algo]['color'], 
                 marker=styles[algo]['marker'], 
                 linewidth=2, markersize=8)

    # 3. Định dạng biểu đồ
    plt.title("So sánh mức độ sử dụng bộ nhớ của 4 thuật toán", fontsize=16, fontweight='bold')
    plt.xlabel("Input Files", fontsize=12)
    plt.ylabel("Bộ nhớ (MB)", fontsize=12)
    
    plt.xticks(rotation=45)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend()
    
    # Tối ưu khoảng cách
    plt.tight_layout()

    # 4. Lưu và hiển thị
    plt.savefig("algorithm_memory_chart.png")
    print("Đã lưu biểu đồ bộ nhớ vào file: algorithm_memory_chart.png")
    plt.show()

if __name__ == "__main__":
    draw_memory_chart()