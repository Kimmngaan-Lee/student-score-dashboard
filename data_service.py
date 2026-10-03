from pathlib import Path
import pandas as pd

# Đường dẫn trỏ tới tệp scores.csv trong thư mục data/
DATA_PATH = Path(__file__).resolve().parent / "data" / "scores.csv"
SCORE_COLUMNS = ["attendance", "assignment", "midterm", "final"]


def load_scores() -> pd.DataFrame:
    # 1. Kiểm tra sự tồn tại của tệp dữ liệu
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Data file not found at: {DATA_PATH}")

    # 2. Đọc dữ liệu từ file CSV vào DataFrame
    df = pd.read_csv(DATA_PATH)

    # 3. Kiểm tra các cột bắt buộc phải có trong file CSV
    required = {"student_id", "full_name", "class_name", *SCORE_COLUMNS}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    # 4. Ép kiểu dữ liệu của các cột điểm sang dạng số (với errors='coerce', dữ liệu không phải số sẽ thành NaN)
    df[SCORE_COLUMNS] = df[SCORE_COLUMNS].apply(pd.to_numeric, errors="coerce")

    return df

def clean_scores(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Tạo bản sao để tránh làm thay đổi dữ liệu gốc
    data = df.copy()

    # 2. Xóa khoảng trắng thừa ở hai đầu chuỗi ký tự
    data["student_id"] = data["student_id"].astype(str).str.strip()
    data["full_name"] = data["full_name"].astype(str).str.strip()
    data["class_name"] = data["class_name"].astype(str).str.strip()

    # 3. Loại bỏ các dòng trùng lặp Mã số sinh viên (giữ lại bản ghi cuối cùng)
    data = data.drop_duplicates(subset="student_id", keep="last")

    # 4. Xóa các dòng bị thiếu điểm (chứa giá trị NaN/Null)
    data = data.dropna(subset=SCORE_COLUMNS)

    # 5. Kiểm tra điểm hợp lệ (phải nằm trong khoảng từ 0 đến 10)
    valid = (
        data[SCORE_COLUMNS].apply(lambda column: column.between(0, 10)).all(axis=1)
    )

    # 6. Lọc chỉ lấy các dòng hợp lệ và đánh lại chỉ số dòng (index)
    return data.loc[valid].reset_index(drop=True)


def enrich_scores(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()

    # 1. Tính điểm tổng kết (trọng số: 10% Chuyên cần, 20% Bài tập, 30% Giữa kỳ, 40% Cuối kỳ)
    data["total_score"] = (
        0.10 * data["attendance"]
        + 0.10 * data["assignment"]
        + 0.30 * data["midterm"]
        + 0.50 * data["final"]
    ).round(2)

    # 2. Phân loại học lực dựa trên thang điểm
    bins = [-0.01, 3.5, 5.0, 6.5, 8.0, 9.0, 10.01]
    labels = ["Kem", "Yeu", "Trungbinh", "Kha", "Gioi", "XuatSac"]
    data["classification"] = pd.cut(
        data["total_score"], bins=bins, labels=labels, right=False
    )

    # 3. Xác định trạng thái Đạt / Không đạt (từ 4.0 trở lên là Đạt)
    data["status"] = (
        data["total_score"].ge(4.0).map({True: "Dat", False: "Khongdat"})
    )

    return data


def filter_scores(df: pd.DataFrame, class_name: str | None):
    # Nếu không truyền class_name (None hoặc chuỗi rỗng), trả về toàn bộ dữ liệu
    if not class_name:
        return df.copy()

    # Nếu có class_name, chỉ lọc ra các dòng thuộc lớp đó
    return df.loc[df["class_name"] == class_name].copy()


def summarize(df: pd.DataFrame) -> dict:
    # 1. Kiểm tra nếu DataFrame rỗng (không có dữ liệu/sinh viên nào)
    if df.empty:
        return {
            "student_count": 0,
            "mean_score": 0,
            "highest_score": 0,
            "pass_rate": 0,
        }

    # 2. Tính toán các chỉ số thống kê
    return {
        "student_count": int(len(df)),
        "mean_score": round(float(df["total_score"].mean()), 2),
        "highest_score": round(float(df["total_score"].max()), 2),
        "pass_rate": round(float(df["total_score"].ge(4).mean() * 100), 2),
    }