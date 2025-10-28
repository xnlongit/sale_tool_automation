#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ER Sports Automation Tool - Python GUI Version
Hướng dẫn cài đặt và sử dụng

Tác giả: AI Assistant
Phiên bản: 1.0.0
"""

import subprocess
import sys
import os

def install_requirements():
    """
    Cài đặt các thư viện cần thiết
    """
    print("🚀 ER Sports Automation Tool - Cài đặt")
    print("=" * 50)
    
    # Kiểm tra Python version
    if sys.version_info < (3, 7):
        print("❌ Cần Python 3.7 trở lên!")
        print(f"   Phiên bản hiện tại: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version}")
    
    # Cài đặt requirements
    requirements = [
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.0"
    ]
    
    print("\n📦 Cài đặt thư viện Python...")
    for requirement in requirements:
        try:
            print(f"   Cài đặt {requirement}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", requirement])
            print(f"   ✅ Đã cài đặt {requirement}")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Lỗi cài đặt {requirement}: {e}")
            return False
    
    print("\n🌐 Cài đặt ChromeDriver...")
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        driver_path = ChromeDriverManager().install()
        print(f"   ✅ ChromeDriver đã được cài đặt tại: {driver_path}")
    except Exception as e:
        print(f"   ⚠️  Cảnh báo: Không thể tự động cài đặt ChromeDriver: {e}")
        print("   Bạn có thể cần cài đặt ChromeDriver thủ công")
    
    print("\n🎉 Cài đặt hoàn tất!")
    print("\n📋 Hướng dẫn sử dụng:")
    print("1. Chạy chương trình: python er_sports_automation.py")
    print("2. Thêm tài khoản trong tab 'Tài khoản & Sản phẩm'")
    print("3. Thêm sản phẩm cần mua")
    print("4. Cấu hình trong tab 'Cài đặt'")
    print("5. Nhấn 'Bắt đầu Automation' trong tab 'Điều khiển & Thống kê'")
    
    return True

def check_chrome():
    """
    Kiểm tra Chrome browser
    """
    print("\n🔍 Kiểm tra Chrome browser...")
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable"
    ]
    
    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"   ✅ Chrome tìm thấy tại: {path}")
            chrome_found = True
            break
    
    if not chrome_found:
        print("   ⚠️  Chrome không tìm thấy trong các đường dẫn thông thường")
        print("   Vui lòng cài đặt Google Chrome hoặc cập nhật đường dẫn trong cài đặt")
    
    return chrome_found

def create_sample_files():
    """
    Tạo các file mẫu
    """
    print("\n📝 Tạo file mẫu...")
    
    # Tạo thư mục logs
    if not os.path.exists('logs'):
        os.makedirs('logs')
        print("   ✅ Đã tạo thư mục logs")
    
    # Tạo file accounts mẫu
    sample_accounts = [
        {
            "email": "your-email@example.com",
            "password": "your-password",
            "name": "Tài khoản mẫu",
            "notes": "Thay đổi thông tin này"
        }
    ]
    
    try:
        import json
        with open('sample_accounts.json', 'w', encoding='utf-8') as f:
            json.dump(sample_accounts, f, ensure_ascii=False, indent=2)
        print("   ✅ Đã tạo sample_accounts.json")
    except Exception as e:
        print(f"   ⚠️  Không thể tạo file mẫu: {e}")
    
    # Tạo file products mẫu
    sample_products = [
        {
            "productId": "12345",
            "name": "Sản phẩm mẫu",
            "url": "https://www.er-sports.com/shop/product/12345.html",
            "category": "Thể thao",
            "notes": "Thay đổi thông tin này"
        }
    ]
    
    try:
        with open('sample_products.json', 'w', encoding='utf-8') as f:
            json.dump(sample_products, f, ensure_ascii=False, indent=2)
        print("   ✅ Đã tạo sample_products.json")
    except Exception as e:
        print(f"   ⚠️  Không thể tạo file mẫu: {e}")

def main():
    """
    Hàm main cho script cài đặt
    """
    print("ER Sports Automation Tool - Python GUI")
    print("Công cụ tự động đăng nhập và mua hàng từ er-sports.com")
    print()
    
    # Cài đặt requirements
    if not install_requirements():
        print("\n❌ Cài đặt thất bại!")
        return False
    
    # Kiểm tra Chrome
    check_chrome()
    
    # Tạo file mẫu
    create_sample_files()
    
    print("\n🎯 Bước tiếp theo:")
    print("1. Chỉnh sửa sample_accounts.json với thông tin tài khoản thực")
    print("2. Chỉnh sửa sample_products.json với sản phẩm cần mua")
    print("3. Chạy chương trình: python er_sports_automation.py")
    print("4. Import các file JSON vào chương trình")
    
    return True

if __name__ == "__main__":
    main()
