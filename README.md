# Percussion Search

Ứng dụng tìm kiếm và phân loại âm thanh nhạc cụ gõ dựa trên đặc trưng âm thanh. Giao diện web được xây dựng bằng Flask.

## Yêu cầu

- Python 3.10–3.12
- Bộ dữ liệu âm thanh định dạng WAV
- Windows PowerShell (các lệnh bên dưới dành cho Windows)

> Database và dữ liệu âm thanh không được lưu trong repository. Người dùng cần chuẩn bị dữ liệu và tự tạo `perc.db` theo hướng dẫn bên dưới.

## 1. Tải source code

```powershell
git clone <URL_REPOSITORY>
cd <TEN_THU_MUC_DU_AN>
```

Thay `<URL_REPOSITORY>` bằng URL của repository và `<TEN_THU_MUC_DU_AN>` bằng tên thư mục vừa clone.

## 2. Tạo môi trường Python

```powershell
py -m venv .venv
```

## 3. Cài đặt thư viện

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 4. Chuẩn bị dữ liệu

Đặt dữ liệu vào thư mục `raw_data/`. Mỗi loại nhạc cụ nằm trong một thư mục riêng:

```text
raw_data/
├── snare/
│   ├── sample_01.wav
│   └── sample_02.wav
├── kick/
│   ├── sample_01.wav
│   └── sample_02.wav
└── cymbal/
    ├── sample_01.wav
    └── sample_02.wav
```

Tên thư mục con được dùng làm nhãn của loại nhạc cụ.

## 5. Chia dữ liệu

Chia dữ liệu thành tập xây dựng database và tập truy vấn:

```powershell
.\.venv\Scripts\python.exe split_data.py --ratio 0.05
```

Lệnh trên tạo ra:

- `data/`: dữ liệu dùng để xây dựng database.
- `query/seen/`: dữ liệu truy vấn thuộc các lớp đã có trong database.

Để dành riêng một số lớp làm dữ liệu nhạc cụ chưa biết, truyền đúng tên thư mục của chúng vào `--unseen`:

```powershell
.\.venv\Scripts\python.exe split_data.py --unseen cowbell tambourine --ratio 0.05
```

Các lớp này sẽ được đưa vào `query/unseen/` và không được đưa vào database.

Nếu đã được cung cấp sẵn thư mục `data/`, có thể bỏ qua bước này.

## 6. Tạo database

```powershell
.\.venv\Scripts\python.exe build_db.py
```

Chương trình sẽ trích xuất đặc trưng âm thanh từ `data/` và tạo file `perc.db` tại thư mục gốc của dự án. Thời gian xử lý phụ thuộc vào số lượng file WAV và cấu hình máy.

Cấu trúc cần có trước khi chạy ứng dụng:

```text
<TEN_THU_MUC_DU_AN>/
├── data/
├── query/
├── perc.db
├── app.py
└── requirements.txt
```

## 7. Chạy ứng dụng

```powershell
.\.venv\Scripts\python.exe app.py
```

Mở trình duyệt và truy cập:

```text
http://127.0.0.1:5000
```

Ở những lần chạy tiếp theo, nếu `perc.db` và dữ liệu không thay đổi, chỉ cần chạy lại `app.py`.

## Lỗi thường gặp

### Không tìm thấy `perc.db`

Đảm bảo đã chạy `build_db.py` và file `perc.db` nằm cùng cấp với `app.py`.

### Không có file trong `data/`

Kiểm tra cấu trúc `raw_data/`, sau đó chạy lại `split_data.py`. Mỗi lớp cần có ít nhất một file WAV hợp lệ.

### Không phát được âm thanh kết quả

Không di chuyển hoặc đổi tên thư mục `data/` sau khi tạo database. Database lưu đường dẫn tương đối tới các file âm thanh trong thư mục này.

### Chạy lại bước chia dữ liệu

`split_data.py` sẽ dừng nếu `data/` đã chứa dữ liệu. Hãy sao lưu dữ liệu cần thiết, sau đó làm trống `data/` và `query/` trước khi chia lại.

## Dữ liệu không được đưa lên Git

Các nội dung cục bộ sau đã được cấu hình bỏ qua trong `.gitignore`:

- `raw_data/`
- `data/`
- `query/`
- `perc.db` và các file SQLite liên quan
- `uploads/`
- Môi trường `.venv/` và cache Python
- Các báo cáo, biểu đồ và kết quả được sinh tự động

Không commit dữ liệu cá nhân, file âm thanh riêng tư, khóa API, mật khẩu hoặc file cấu hình chứa thông tin đăng nhập.
