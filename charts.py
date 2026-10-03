from io import BytesIO
import matplotlib

# Chuyển backend của Matplotlib sang "Agg" (không hiển thị cửa sổ GUI)
# Thích hợp chạy trên Server / Web App / Script không có giao diện đồ họa
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns


def distribution_png(df):
    # 1. Khởi tạo khung vẽ (figure) và trục (axes) với kích thước 8x4.5 inches
    fig, ax = plt.subplots(figsize=(8, 4.5))

    # 2. Vẽ biểu đồ phân bố (Histogram) kết hợp đường ước lượng mật độ (KDE)
    sns.histplot(
        data=df,
        x="total_score",  # Cột dữ liệu điểm tổng kết cần vẽ
        bins=10,  # Chia khoảng điểm thành 10 cột
        kde=True,  # Hiển thị đường cong mật độ (Kernel Density Estimate)
        color="#eb2543", 
        ax=ax,
    )

    # 3. Đặt tiêu đề và nhãn cho các trục của biểu đồ
    ax.set(
        title="Phân phối điểm tổng kết",
        xlabel="Điểm tổng kết",
        ylabel="Số sinh viên",
    )

    # 4. Tối ưu khoảng cách lề xung quanh biểu đồ không bị che chữ
    fig.tight_layout()

    # 5. Lưu biểu đồ vào bộ nhớ đệm RAM dưới dạng BytesIO
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=140)  # Độ phân giải 140 DPI
    plt.close(fig)  # Giải phóng bộ nhớ RAM sau khi vẽ xong

    # 6. Đưa con trỏ đọc bộ nhớ về vị trí đầu tiên (index 0)
    buffer.seek(0)

    # 7. Trả về luồng dữ liệu hình ảnh (BytesIO buffer)
    return buffer

import plotly.express as px


def classification_chart_html(df) :
    # 1. Thống kê số lượng sinh viên theo từng mức xếp loại
    counts = (
        df["classification"].astype(str)
        .value_counts()
        .rename_axis("classification")
        .reset_index(name="count")
    )

    # 2. Tạo biểu đồ cột (Bar Chart) bằng Plotly Express
    fig = px.bar(
        counts,
        x="classification",  # Trục hoành: Các mức xếp loại (Giỏi, Khá, TB,...)
        y="count",  # Trục tung: Số lượng sinh viên
        color="classification",  # Tô màu riêng biệt cho từng cột xếp loại
        title="So sinh vien theo xep loai",  # Tiêu đề biểu đồ
    )

    # 3. Tùy chỉnh giao diện biểu đồ
    fig.update_layout( showlegend=False,   height=420  # Chiều cao biểu đồ (420px)
    )

    # 4. Chuyển đổi biểu đồ thành đoạn mã HTML
    return fig.to_html( 
        full_html=False,  include_plotlyjs="cdn"
    )