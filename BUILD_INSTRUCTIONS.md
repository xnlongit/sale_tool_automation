# Hướng dẫn Build Desktop App cho Windows và Linux

## Yêu cầu khi build thành Desktop App

### Windows - Build file `.exe`

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

---

## Linux - Build và chạy ứng dụng

### 1. Cài đặt dependencies cần thiết

Trước khi build hoặc chạy trên Linux, bạn cần cài đặt các dependencies:

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y python3-tk python3-dev
sudo apt-get install -y xfonts-base xfonts-75dpi
sudo apt-get install -y libx11-dev libxext-dev libxrender-dev
sudo apt-get install -y build-essential
```

#### CentOS/RHEL:
```bash
sudo yum install -y python3-tkinter python3-devel
sudo yum install -y xorg-x11-fonts-base xorg-x11-fonts-75dpi
sudo yum install -y libX11-devel libXext-devel libXrender-devel
sudo yum groupinstall -y "Development Tools"
```

### 2. Cài đặt Python dependencies

```bash
pip install -r requirements.txt
pip install pyinstaller  # Nếu muốn build
```

### 3. Chạy ứng dụng trực tiếp

```bash
# Chạy từ source code
python src/main.py

# Hoặc với quyền thực thi
chmod +x src/main.py
./src/main.py
```

### 4. Xử lý lỗi X11 Rendering

Nếu gặp lỗi **"BadLength (poly request too large or internal Xlib length error)"**, thử các giải pháp sau:

#### Giải pháp 1: Cài đặt đầy đủ dependencies
```bash
sudo apt-get install -y python3-tk python3-dev xfonts-base xfonts-75dpi
```

#### Giải pháp 2: Set environment variables
```bash
export TK_SILENCE_DEPRECATION=1
export XLIB_SKIP_ARGB_VISUALS=1
export DISPLAY=:0.0
python src/main.py
```

#### Giải pháp 3: Nếu chạy qua SSH
```bash
# Kết nối với X11 forwarding
ssh -X user@hostname

# Hoặc trusted X11 forwarding (nếu -X không hoạt động)
ssh -Y user@hostname

# Sau đó chạy ứng dụng
python src/main.py
```

#### Giải pháp 4: Sử dụng xvfb (cho headless servers)
```bash
# Cài đặt xvfb
sudo apt-get install -y xvfb

# Chạy với xvfb
xvfb-run -a python src/main.py

# Hoặc với display số cụ thể
xvfb-run --server-args="-screen 0 1024x768x24" python src/main.py
```

#### Giải pháp 5: Kiểm tra DISPLAY
```bash
# Kiểm tra DISPLAY hiện tại
echo $DISPLAY

# Nếu không có, set DISPLAY
export DISPLAY=:0.0

# Hoặc nếu đang dùng X server khác
export DISPLAY=:10.0
```

### 5. Build với PyInstaller trên Linux

```bash
# Build với PyInstaller
pyinstaller --name="ER-Sports-Automation" \
    --onefile \
    --windowed \
    --hidden-import=selenium \
    --hidden-import=tkinter \
    --add-data "config:config" \
    src/main.py

# File executable sẽ ở: dist/ER-Sports-Automation
```

**Lưu ý khi build trên Linux:**
- Nên build trên cùng hệ điều hành nơi sẽ chạy ứng dụng
- Đảm bảo đã cài đặt tất cả dependencies trước khi build
- File executable cần quyền thực thi: `chmod +x dist/ER-Sports-Automation`

### 6. Troubleshooting trên Linux

#### Lỗi: "No display name and no $DISPLAY environment variable"
**Giải pháp:**
```bash
export DISPLAY=:0.0
# hoặc
xvfb-run -a python src/main.py
```

#### Lỗi: "BadLength (poly request too large or internal Xlib length error)"
**Giải pháp:**
1. Cài đặt fonts: `sudo apt-get install xfonts-base xfonts-75dpi`
2. Set environment variables:
   ```bash
   export XLIB_SKIP_ARGB_VISUALS=1
   export TK_SILENCE_DEPRECATION=1
   ```
3. Hoặc dùng xvfb: `xvfb-run -a python src/main.py`

#### Lỗi: "cannot connect to X server"
**Giải pháp:**
- Kiểm tra DISPLAY: `echo $DISPLAY`
- Set DISPLAY: `export DISPLAY=:0.0`
- Hoặc dùng xvfb: `xvfb-run -a python src/main.py`

#### Lỗi: "ModuleNotFoundError: No module named '_tkinter'"
**Giải pháp:**
```bash
sudo apt-get install python3-tk
# hoặc
sudo yum install python3-tkinter
```

### 7. Chạy ứng dụng trên Linux Server (không có màn hình)

Nếu bạn cần chạy trên server không có màn hình:

```bash
# Cài đặt xvfb
sudo apt-get install xvfb

# Chạy với xvfb
xvfb-run -a python src/main.py

# Hoặc tạo service để chạy tự động
```

**Tạo systemd service:**
```bash
# /etc/systemd/system/er-sports-automation.service
[Unit]
Description=ER Sports Automation
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/er_sports_automation
Environment="DISPLAY=:99"
ExecStart=/usr/bin/xvfb-run -a python /path/to/er_sports_automation/src/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Sau đó:
```bash
sudo systemctl daemon-reload
sudo systemctl enable er-sports-automation
sudo systemctl start er-sports-automation
```

### 8. So sánh Windows vs Linux

| Tính năng | Windows | Linux |
|-----------|---------|-------|
| Build executable | `.exe` với PyInstaller | Binary với PyInstaller |
| X11/Display | Không cần | Cần X11 hoặc xvfb |
| Dependencies | Chỉ Python packages | Python packages + system libraries |
| Chrome/ChromeDriver | Tương tự | Cần cài đặt riêng |
| Troubleshooting | Antivirus issues | X11 rendering issues |

### 9. Tips cho Linux

- **Development:** Chạy trực tiếp từ source với `python src/main.py`
- **Production:** Build với PyInstaller hoặc chạy với xvfb
- **Remote:** Dùng `ssh -X` hoặc `xvfb-run` cho servers
- **Debug:** Bỏ `--windowed` để xem console output khi build

