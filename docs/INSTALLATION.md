# ER Sports Automation Tool - Installation Guide

Hướng dẫn cài đặt chi tiết cho ER Sports Automation Tool trên các hệ điều hành khác nhau.

## Yêu cầu hệ thống

### Minimum Requirements
- **Python**: 3.7 trở lên
- **RAM**: 4GB (khuyến nghị 8GB)
- **Disk Space**: 1GB trống
- **Internet**: Kết nối internet ổn định

### Browser Requirements
- **Google Chrome**: Phiên bản 90 trở lên
- **ChromeDriver**: Sẽ được tự động cài đặt

## Cài đặt trên Windows

### Cách 1: Sử dụng script tự động
```cmd
# Tải về và giải nén package
# Chạy script cài đặt
python install.py
```

### Cách 2: Cài đặt thủ công
```cmd
# 1. Cài đặt Python dependencies
pip install -r requirements.txt

# 2. Cài đặt ChromeDriver tự động
pip install webdriver-manager

# 3. Chạy ứng dụng
python src/main.py
```

### Cách 3: Cài đặt như package
```cmd
# Cài đặt package
pip install -e .

# Chạy ứng dụng
er-sports-automation
```

## Cài đặt trên macOS

### Sử dụng Homebrew (khuyến nghị)
```bash
# Cài đặt Python
brew install python@3.9

# Cài đặt Chrome
brew install --cask google-chrome

# Cài đặt dependencies
pip3 install -r requirements.txt

# Chạy ứng dụng
python3 src/main.py
```

### Cài đặt thủ công
```bash
# 1. Tải Python từ python.org
# 2. Tải Chrome từ google.com/chrome
# 3. Cài đặt dependencies
pip3 install selenium webdriver-manager

# 4. Chạy ứng dụng
python3 src/main.py
```

## Cài đặt trên Linux (Ubuntu/Debian)

### Cài đặt dependencies hệ thống
```bash
# Cập nhật package list
sudo apt update

# Cài đặt Python và pip
sudo apt install python3 python3-pip python3-venv

# Cài đặt Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable
```

### Cài đặt Python package
```bash
# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy ứng dụng
python src/main.py
```

## Cài đặt trên Linux (CentOS/RHEL/Fedora)

### Fedora
```bash
# Cài đặt Python và Chrome
sudo dnf install python3 python3-pip
sudo dnf install google-chrome-stable

# Cài đặt dependencies
pip3 install -r requirements.txt
```

### CentOS/RHEL
```bash
# Cài đặt Python
sudo yum install python3 python3-pip

# Cài đặt Chrome
sudo yum install google-chrome-stable

# Cài đặt dependencies
pip3 install -r requirements.txt
```

## Cài đặt từ source code

### Clone repository
```bash
git clone https://github.com/your-username/er-sports-automation.git
cd er-sports-automation
```

### Cài đặt development dependencies
```bash
# Cài đặt package ở development mode
pip install -e .

# Cài đặt development dependencies
pip install -e .[dev]
```

## Verification

### Kiểm tra cài đặt
```bash
# Kiểm tra Python version
python --version

# Kiểm tra Selenium
python -c "import selenium; print(selenium.__version__)"

# Kiểm tra ChromeDriver
python -c "from webdriver_manager.chrome import ChromeDriverManager; print(ChromeDriverManager().install())"
```

### Test chạy ứng dụng
```bash
# Chạy ứng dụng
python src/main.py

# Hoặc sử dụng entry point
er-sports-automation
```

## Troubleshooting

### Lỗi thường gặp

#### 1. Python không tìm thấy
```bash
# Windows: Thêm Python vào PATH
# macOS/Linux: Sử dụng python3 thay vì python
python3 --version
```

#### 2. ChromeDriver không tìm thấy
```bash
# Cài đặt ChromeDriver tự động
pip install webdriver-manager
```

#### 3. Permission denied
```bash
# Linux/macOS: Sử dụng sudo hoặc virtual environment
sudo pip install -r requirements.txt
# Hoặc
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. Chrome không mở
- Kiểm tra Chrome đã được cài đặt
- Cập nhật Chrome lên phiên bản mới nhất
- Kiểm tra đường dẫn Chrome trong cài đặt

### Log files
Kiểm tra log files trong thư mục `logs/` để debug:
```bash
# Xem log mới nhất
ls -la logs/
tail -f logs/automation_*.log
```

## Uninstall

### Gỡ cài đặt package
```bash
pip uninstall er-sports-automation
```

### Xóa files cấu hình
```bash
# Xóa thư mục cấu hình
rm -rf ~/.er_sports_automation/
rm -rf logs/
rm -rf data/
```

## Support

Nếu gặp vấn đề trong quá trình cài đặt:
1. Kiểm tra log files
2. Xem TROUBLESHOOTING.md
3. Tạo issue trên GitHub
4. Liên hệ support
