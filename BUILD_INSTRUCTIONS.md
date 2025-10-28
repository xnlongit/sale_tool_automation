# Hướng dẫn Build Desktop App cho Windows

## Yêu cầu khi build thành Desktop App

Khi build thành file `.exe` trên Windows, bạn cần chuẩn bị:

### 1. Cài đặt Chrome và ChromeDriver

#### Option 1: Sử dụng ChromeDriver có sẵn (Khuyên dùng)

1. Đảm bảo Google Chrome đã được cài đặt trên máy
   - Tải tại: https://www.google.com/chrome/
   
2. Download ChromeDriver phù hợp với version Chrome của bạn
   - Kiểm tra version Chrome: Mở Chrome > Help > About Google Chrome
   - Tải ChromeDriver tại: https://chromedriver.chromium.org/downloads

3. Thêm ChromeDriver vào PATH hoặc đặt vào cùng thư mục với file .exe

#### Option 2: Sử dụng webdriver-manager (Tự động download)

Cài đặt thêm package:
```bash
pip install webdriver-manager
```

### 2. Build với PyInstaller

1. Cài đặt PyInstaller:
```bash
pip install pyinstaller
```

2. Tạo file spec để build:
```bash
pyinstaller --name="ER Sports Automation" --windowed --onefile --icon=icon.ico src/main.py
```

Hoặc nếu muốn bao gồm ChromeDriver:
```bash
pyinstaller --name="ER Sports Automation" --windowed --onefile --add-data "chromedriver.exe;." --icon=icon.ico src/main.py
```

### 3. Vấn đề thường gặp

#### Lỗi: Không tìm thấy ChromeDriver

**Giải pháp:**
1. Copy file `chromedriver.exe` vào cùng thư mục với file `.exe`
2. Hoặc thêm ChromeDriver vào PATH môi trường

#### Lỗi: Chrome không mở được

**Giải pháp:**
1. Đảm bảo Google Chrome đã được cài đặt đúng
2. Kiểm tra đường dẫn Chrome trong tab "Cài đặt" của ứng dụng
3. Thử chạy ứng dụng với quyền Administrator

#### Lỗi: Antivirus block file .exe

**Giải pháp:**
1. Thêm exception vào Antivirus
2. Hoặc build với `--onefile --noconsole` để ít bị false positive hơn

### 4. Cấu trúc thư mục khi build

Khi build với `--onefile`, cấu trúc sẽ như sau:
```
dist/
  └── ER Sports Automation.exe
  
build/
  └── (các file tạm thời)
  
(hoặc nếu có chromedriver.exe)
dist/
  ├── ER Sports Automation.exe
  └── chromedriver.exe
```

### 5. Build command hoàn chỉnh

Để build với đầy đủ dependencies và ít lỗi nhất:

```bash
pyinstaller --name="ER Sports Automation" ^
    --windowed ^
    --onefile ^
    --noconsole ^
    --add-data "config;config" ^
    --hidden-import=selenium ^
    --hidden-import=tkinter ^
    --icon=icon.ico ^
    src/main.py
```

### 6. Kiểm tra sau khi build

1. Chạy file `.exe` để test
2. Kiểm tra tab "Cài đặt" trong ứng dụng
3. Đảm bảo Chrome path đúng
4. Test thử đăng nhập một account

### 7. Tips

- **Nếu vẫn lỗi:** Chạy file `.exe` với quyền Administrator
- **Tăng tốc độ:** Sử dụng `--onefile` thay vì `--onedir`
- **Dễ debug:** Bỏ `--noconsole` để xem log
- **Giảm kích thước:** Dùng `--onefile --zip`

### 8. Troubleshooting

#### Chrome không mở được trong .exe

Thử thêm vào code (đã được thêm trong phiên bản mới):
```python
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
```

#### Không tìm thấy ChromeDriver

Copy file `chromedriver.exe` vào cùng thư mục với file `.exe`.

#### Antivirus báo virus

PyInstaller thường bị false positive. Thêm exception hoặc submit file lên các antivirus để kiểm tra.

