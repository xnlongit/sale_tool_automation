# ER Sports Automation Tool - Python GUI

Công cụ tự động đăng nhập và mua hàng từ website er-sports.com với giao diện đồ họa Python.

## 🚀 Tính năng chính

- ✅ **Giao diện đồ họa thân thiện** - Sử dụng tkinter
- ✅ **Quản lý tài khoản** - Hỗ trợ tối đa 10 tài khoản
- ✅ **Quản lý sản phẩm** - Hỗ trợ tối đa 20 sản phẩm
- ✅ **Thống kê chi tiết** - Đếm số lần quét, mua thành công/thất bại
- ✅ **Log viewer** - Xem log chi tiết với chú thích
- ✅ **Xử lý lỗi thông minh** - Phát hiện hết hàng và các lỗi khác
- ✅ **Import/Export** - Hỗ trợ JSON cho tài khoản và sản phẩm
- ✅ **Cấu hình linh hoạt** - Tùy chỉnh timing, browser settings
- ✅ **Báo cáo chi tiết** - Xuất báo cáo kết quả
- ✅ **OpenVPN Integration** - Tự động fake IP Nhật Bản
- ✅ **Smart Automation Logic** - Mỗi sản phẩm chỉ mua 1 lần, tự động đổi IP khi thành công

## 📋 Yêu cầu hệ thống

- **Python**: 3.7 trở lên
- **Chrome Browser**: Cài đặt Google Chrome
- **Operating System**: Windows, macOS, Linux
- **OpenVPN**: (Tùy chọn) Để sử dụng tính năng fake IP Nhật Bản

## 🛠️ Cài đặt

### Cách 1: Tự động cài đặt
```bash
python install.py
```

### Cách 2: Cài đặt thủ công
```bash
# Cài đặt Python dependencies
pip install -r requirements.txt

# Hoặc cài đặt từng package
pip install selenium>=4.15.0
pip install webdriver-manager>=4.0.0
```

## 🎯 Sử dụng

### 1. Khởi chạy chương trình
```bash
python er_sports_automation.py
```

### 2. Cấu hình tài khoản
- Mở tab **"Tài khoản & Sản phẩm"**
- Nhập thông tin tài khoản:
  - Email
  - Password
  - Tên (tùy chọn)
  - Ghi chú (tùy chọn)
- Nhấn **"Thêm tài khoản"**
- Tối đa 10 tài khoản

### 3. Cấu hình sản phẩm
- Trong cùng tab, nhập thông tin sản phẩm:
  - Product ID
  - Tên sản phẩm
  - URL sản phẩm
  - Danh mục
  - Ghi chú
- Nhấn **"Thêm sản phẩm"**
- Tối đa 20 sản phẩm

### 4. Cấu hình OpenVPN (Tùy chọn)
- Mở tab **"Cài đặt"**
- Kéo xuống phần **"Cài đặt OpenVPN"**
- Bật **"Sử dụng OpenVPN để fake IP Nhật Bản"**
- Chọn đường dẫn OpenVPN executable
- Thêm các file config (.ovpn) của VPN Nhật Bản
- Chọn chế độ:
  - **Tuần tự**: Đổi IP theo thứ tự
  - **Ngẫu nhiên**: Random IP mỗi lần

### 5. Cài đặt
- Mở tab **"Cài đặt"**
- Cấu hình:
  - **Headless mode**: Chạy browser ẩn/hiện
  - **Chrome path**: Đường dẫn Chrome executable
  - **Timing**: Delay giữa các tài khoản/sản phẩm
  - **Retry settings**: Số lần thử lại

### 6. Chạy automation
- Mở tab **"Điều khiển & Thống kê"**
- Nhấn **"Bắt đầu Automation"**
- Theo dõi tiến trình trong **"Trạng thái"**
- Xem log chi tiết trong tab **"Log Chi tiết"**

## 📊 Giao diện chính

### Tab 1: Tài khoản & Sản phẩm
- **Quản lý tài khoản**: Thêm/xóa/sửa tối đa 10 tài khoản
- **Quản lý sản phẩm**: Thêm/xóa/sửa tối đa 20 sản phẩm
- **Import/Export**: Hỗ trợ JSON format

### Tab 2: Điều khiển & Thống kê
- **Thống kê real-time**:
  - Số lần quét
  - Mua thành công
  - Mua thất bại
  - Tỷ lệ thành công
- **Điều khiển**: Start/Stop automation
- **Trạng thái**: Hiển thị log real-time

### Tab 3: Log Chi tiết
- **Log viewer**: Xem log chi tiết với màu sắc
- **Toolbar**: Làm mới/xóa/lưu log
- **Mức độ log**: INFO, WARNING, ERROR, SUCCESS

### Tab 4: Cài đặt
- **Browser settings**: Headless, Chrome path
- **Timing settings**: Delay giữa các thao tác
- **Other settings**: Auto-save, retry options
- **OpenVPN settings**: Enable VPN, config files, connection mode

## 🤖 Logic Automation

Tool hoạt động theo logic thông minh:

### Khi OpenVPN được bật:
1. **Kết nối VPN** với IP Nhật Bản đầu tiên
2. **Đăng nhập** tài khoản đầu tiên
3. **Thử mua từng sản phẩm** (mỗi sản phẩm chỉ mua 1 lần):
   - **Nếu mua thành công**:
     - Đăng xuất tài khoản
     - Ngắt kết nối VPN
     - Kết nối VPN với IP Nhật Bản khác
     - Đăng nhập tài khoản tiếp theo
     - Tiếp tục với sản phẩm tiếp theo
   - **Nếu mua thất bại**:
     - Giữ nguyên IP hiện tại
     - Giữ nguyên tài khoản hiện tại
     - Tiếp tục thử sản phẩm tiếp theo

### Khi OpenVPN tắt:
- Hoạt động tương tự nhưng không thay đổi IP
- Mua thành công sẽ chuyển sang tài khoản tiếp theo

## 🔧 Cấu hình nâng cao

### File JSON mẫu

#### accounts.json
```json
[
  {
    "email": "user1@example.com",
    "password": "password123",
    "name": "Tài khoản 1",
    "notes": "Tài khoản chính"
  },
  {
    "email": "user2@example.com",
    "password": "password456",
    "name": "Tài khoản 2",
    "notes": "Tài khoản phụ"
  }
]
```

#### products.json
```json
[
  {
    "productId": "12345",
    "name": "Sản phẩm A",
    "url": "https://www.er-sports.com/shop/product/12345.html",
    "category": "Thể thao",
    "notes": "Sản phẩm hot"
  },
  {
    "productId": "67890",
    "name": "Sản phẩm B",
    "url": "https://www.er-sports.com/shop/product/67890.html",
    "category": "Phụ kiện",
    "notes": "Hàng mới"
  }
]
```

## 📈 Thống kê và báo cáo

### Các chỉ số được theo dõi:
- **Số lần quét**: Tổng số lần thử mua hàng
- **Mua thành công**: Số lần mua hàng thành công
- **Mua thất bại**: Số lần mua hàng thất bại
- **Tỷ lệ thành công**: Phần trăm thành công

### Xuất báo cáo:
- Nhấn **"Xuất Báo cáo"** trong tab điều khiển
- File JSON chứa thống kê chi tiết
- Bao gồm thông tin tài khoản và sản phẩm

## 🚨 Xử lý lỗi

### Các lỗi được phát hiện:
- **Hết hàng**: Phát hiện sản phẩm không còn hàng
- **Đăng nhập thất bại**: Sai email/password
- **Timeout**: Quá thời gian chờ
- **Network error**: Lỗi kết nối
- **Element not found**: Không tìm thấy element

### Log chi tiết:
- Mỗi lỗi được ghi log với timestamp
- Phân loại theo mức độ: INFO, WARNING, ERROR
- Màu sắc phân biệt trong log viewer

## 🔒 Bảo mật

⚠️ **Lưu ý quan trọng:**
- Không chia sẻ file chứa thông tin đăng nhập
- Sử dụng mật khẩu mạnh
- Chạy trong môi trường an toàn
- Kiểm tra kết quả trước khi thực hiện giao dịch

## 🐛 Troubleshooting

### Lỗi thường gặp:

#### 1. ChromeDriver không tìm thấy
```bash
# Cài đặt ChromeDriver tự động
pip install webdriver-manager
```

#### 2. Chrome không mở
- Kiểm tra đường dẫn Chrome trong cài đặt
- Cài đặt Google Chrome
- Chạy với quyền administrator

#### 3. Import/Export lỗi
- Kiểm tra format JSON
- Đảm bảo file không bị corrupt
- Kiểm tra encoding UTF-8

#### 4. Automation chạy chậm
- Tăng delay trong cài đặt
- Chạy headless mode
- Kiểm tra tốc độ internet

#### 5. OpenVPN không kết nối
- Kiểm tra đường dẫn OpenVPN executable
- Đảm bảo file config (.ovpn) hợp lệ
- Chạy với quyền administrator
- Kiểm tra OpenVPN đã được cài đặt

#### 6. VPN bị ngắt kết nối
- Kiểm tra kết nối internet
- Đảm bảo file config không có lỗi
- Tăng delay giữa các thao tác

## 📁 Cấu trúc file

```
project/
├── er_sports_automation.py    # File chính
├── install.py                # Script cài đặt
├── requirements.txt          # Python dependencies
├── README.md                # Hướng dẫn này
├── logs/                    # Thư mục log
│   └── automation_*.log    # File log
├── sample_accounts.json     # File tài khoản mẫu
├── sample_products.json     # File sản phẩm mẫu
└── reports/                 # Thư mục báo cáo
    └── report_*.json       # File báo cáo
```

## 🤝 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra log trong tab "Log Chi tiết"
2. Xem file log trong thư mục logs/
3. Kiểm tra cấu hình trong tab "Cài đặt"
4. Đảm bảo Chrome và ChromeDriver được cài đặt đúng

## 📄 License

MIT License - Sử dụng tự do cho mục đích cá nhân và thương mại.

## 🔄 Cập nhật

- **v1.1.0**: 
  - Thêm tích hợp OpenVPN
  - Logic automation thông minh: Mỗi sản phẩm chỉ mua 1 lần
  - Tự động đổi IP khi mua thành công
  - Giữ nguyên IP khi mua thất bại
- **v1.0.0**: Phiên bản đầu tiên với GUI hoàn chỉnh
  - Hỗ trợ đầy đủ các tính năng automation
  - Giao diện thân thiện và dễ sử dụng
  - Xử lý lỗi toàn diện
