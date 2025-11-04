# Hướng dẫn Test API với Postman và Newman

## Tổng quan

Dự án này bao gồm bộ test suite hoàn chỉnh cho Library Management System API với 5 endpoints chính và 36 test assertions tự động.

## Các Endpoint được Test

### 1. Đăng nhập (POST /api/auth/login)
- Xác thực người dùng
- Lấy JWT token
- 7 test cases

### 2. Lấy danh sách sách (GET /api/books)
- Hiển thị tất cả sách với phân trang
- Tìm kiếm và lọc sách
- 7 test cases

### 3. Tạo sách mới (POST /api/books)
- Thêm sách vào thư viện
- Kiểm tra dữ liệu đầu vào
- 7 test cases

### 4. Mượn sách (POST /api/borrows)
- Tạo bản ghi mượn sách
- Cập nhật trạng thái sách
- 7 test cases

### 5. Trả sách (POST /api/borrows/{id}/return)
- Đánh dấu sách đã trả
- Cập nhật ngày trả
- 8 test cases

## Cài đặt

### 1. Cài đặt Newman (CLI của Postman)

```bash
npm install -g newman
```

### 2. Cài đặt Newman HTML Reporter (Tùy chọn)

```bash
npm install -g newman-reporter-html
```

## Chạy Test

### Cách 1: Sử dụng Script Tự Động (Khuyến nghị)

```bash
# 1. Khởi động Flask app
cd LibraryManageSystem
python app_swagger.py

# 2. Mở terminal mới và chạy test
cd LibraryManageSystem
./run-newman-tests.sh
```

Script sẽ tự động:
- ✅ Kiểm tra Newman đã cài đặt chưa
- ✅ Kiểm tra Flask app đang chạy
- ✅ Chạy tất cả tests
- ✅ Tạo báo cáo HTML và JSON

### Cách 2: Chạy Newman Trực Tiếp

```bash
# Chạy test cơ bản
newman run LibraryManagement.postman_collection.json

# Chạy với báo cáo HTML
newman run LibraryManagement.postman_collection.json \
    --reporters cli,html \
    --reporter-html-export newman-report.html

# Chạy với cả báo cáo JSON và HTML
newman run LibraryManagement.postman_collection.json \
    --reporters cli,html,json \
    --reporter-html-export newman-report.html \
    --reporter-json-export newman-results.json
```

### Cách 3: Sử dụng Postman Desktop

1. Mở Postman Desktop
2. Nhấn nút **Import**
3. Chọn file `LibraryManagement.postman_collection.json`
4. Chọn collection trong sidebar
5. Nhấn nút **Run** để mở Collection Runner
6. Nhấn **Run Library Management System API**

## Cấu trúc Test

### Biến Collection

Collection sử dụng các biến sau:
- `base_url`: URL gốc của API (mặc định: http://127.0.0.1:5000)
- `access_token`: JWT token từ đăng nhập (tự động lưu)
- `book_id`: ID của sách (tự động lưu)
- `created_book_id`: ID của sách mới tạo (tự động lưu)
- `borrow_record_id`: ID của bản ghi mượn sách (tự động lưu)

### Luồng Test

Tests chạy theo thứ tự:

```
1. Đăng nhập → Lấy access token
2. Lấy danh sách sách → Kiểm tra phân trang
3. Tạo sách → Lưu book ID
4. Mượn sách → Sử dụng book ID, lưu borrow ID
5. Trả sách → Sử dụng borrow ID
```

## Kết quả Test

### Kết quả Console

```
✓ Status code is 200
✓ Response has JSON body
✓ Success field is true
...

┌─────────────────────────┬───────────────────┬──────────────────┐
│                         │          executed │           failed │
├─────────────────────────┼───────────────────┼──────────────────┤
│              iterations │                 1 │                0 │
├─────────────────────────┼───────────────────┼──────────────────┤
│                requests │                 5 │                0 │
├─────────────────────────┼───────────────────┼──────────────────┤
│            test-scripts │                 5 │                0 │
├─────────────────────────┼───────────────────┼──────────────────┤
│              assertions │                36 │                0 │
└─────────────────────────┴───────────────────┴──────────────────┘
```

### Báo cáo HTML

Mở file `newman-report.html` trong trình duyệt để xem:
- Tổng quan kết quả test
- Thống kê pass/fail
- Chi tiết request/response
- Thời gian thực thi

### Báo cáo JSON

File `newman-results.json` chứa:
- Kết quả test có thể đọc bằng máy
- Chi tiết về từng test
- Có thể tích hợp vào CI/CD
- Có thể xử lý bằng các công cụ khác

## Xử lý Lỗi

### Newman không tìm thấy

```bash
npm install -g newman
```

### Flask app không chạy

```bash
cd LibraryManageSystem
python app_swagger.py
```

### Port đã được sử dụng

```bash
# Dừng process trên port 5000
lsof -ti:5000 | xargs kill -9

# Hoặc thay đổi port trong file .env
PORT=5001
```

### Test thất bại

1. Kiểm tra log của Flask app
2. Đảm bảo database đã được khởi tạo
3. Đảm bảo user test đã tồn tại:
   ```bash
   curl -X POST http://127.0.0.1:5000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "test123", "full_name": "Test User"}'
   ```

## Tích hợp CI/CD

### Ví dụ GitHub Actions

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      
      - name: Cài đặt dependencies
        run: |
          pip install -r requirements.txt
          npm install -g newman
      
      - name: Khởi động Flask app
        run: |
          cd LibraryManageSystem
          python app_swagger.py &
          sleep 5
      
      - name: Chạy API tests
        run: |
          cd LibraryManageSystem
          newman run LibraryManagement.postman_collection.json
```

## Thống kê Test

**Tổng số Endpoints:** 5  
**Tổng số Test Assertions:** 36

- Đăng nhập: 7 tests
- Lấy danh sách sách: 7 tests
- Tạo sách mới: 7 tests
- Mượn sách: 7 tests
- Trả sách: 8 tests

## Tài liệu Bổ sung

- [TESTING.md](./TESTING.md) - Tài liệu chi tiết bằng tiếng Anh
- [API_DOCUMENTATION.md](../API_DOCUMENTATION.md) - Tài liệu API
- [Newman Documentation](https://learning.postman.com/docs/running-collections/using-newman-cli/command-line-integration-with-newman/)
- [Postman Test Scripts](https://learning.postman.com/docs/writing-scripts/test-scripts/)
