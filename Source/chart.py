import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# 1. Chuẩn bị dữ liệu từ bảng kết quả của bạn
data = {
    'Input File': ['input-01', 'input-02', 'input-03', 'input-04', 'input-05', 
                    'input-06', 'input-07', 'input-08', 'input-09', 'input-10'],
    'PySAT': [2.1407, 1.8747, 2.1578, 2.0146, 2.0546, 2.0022, 2.4420, 2.1014, 1.9350, 2.1064],
    'A*': [2.1700, 1.8266, 2.3348, 2.6636, np.nan, np.nan, 2.6573, np.nan, 2.0446, np.nan],
    # Quy đổi Timeout thành 10 giây để minh họa trực quan
    'Backtracking': [7.3936, 10.0, 6.8947, 10.0, 2.1505, 2.3539, 5.3300, 1.9161, 10.0, 10.0],
    'Brute-force': [6.5666, 10.0, 7.8280, 10.0, 2.6146, 2.7676, 3.3559, 2.1699, 10.0, 10.0]
}

df = pd.DataFrame(data)

# 2. Cấu hình vẽ biểu đồ
plt.figure(figsize=(12, 7))

# Vẽ đường cho từng thuật toán
plt.plot(df['Input File'], df['PySAT'], marker='o', markersize=8, linewidth=2, label='PySAT', color='#1f77b4')
plt.plot(df['Input File'], df['A*'], marker='s', markersize=8, linewidth=2, label='A* (Error = đứt đoạn)', color='#ff7f0e')
plt.plot(df['Input File'], df['Backtracking'], marker='^', markersize=8, linewidth=2, label='Backtracking', color='#2ca02c')
plt.plot(df['Input File'], df['Brute-force'], marker='x', markersize=8, linewidth=2, label='Brute-force', color='#d62728')

# 3. Thêm đường kẻ ngang đánh dấu ngưỡng Timeout
plt.axhline(y=10, color='red', linestyle='--', alpha=0.6)
plt.text(0, 10.2, 'Ngưỡng Timeout (Giả lập 10s)', color='red', fontweight='bold')

# 4. Trang trí biểu đồ
plt.title('So sánh thời gian thực thi của các thuật toán Hashiwokakero', fontsize=15, pad=20)
plt.xlabel('Tệp đầu vào (Input Files)', fontsize=12)
plt.ylabel('Thời gian chạy (Giây)', fontsize=12)
plt.xticks(rotation=45)
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

# Tối ưu không gian hiển thị
plt.tight_layout()

# 5. Hiển thị hoặc Lưu file
plt.show()
# Nếu muốn lưu ảnh vào báo cáo, hãy bỏ dấu # ở dòng dưới:
# plt.savefig('bieu_do_so_sanh_thuat_toan.png', dpi=300)