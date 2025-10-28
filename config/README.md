# ER Sports Automation Tool - Configuration Files

Thư mục này chứa các file cấu hình mẫu cho ER Sports Automation Tool.

## Files trong thư mục này:

### accounts_sample.json
File mẫu chứa danh sách tài khoản với format chuẩn:
```json
[
  {
    "email": "your-email@example.com",
    "password": "your-password",
    "name": "Account Name",
    "notes": "Optional notes"
  }
]
```

### products_sample.json
File mẫu chứa danh sách sản phẩm với format chuẩn:
```json
[
  {
    "productId": "12345",
    "name": "Product Name",
    "url": "https://www.er-sports.com/shop/product/12345.html",
    "category": "Category",
    "notes": "Optional notes"
  }
]
```

### config_sample.json
File cấu hình mẫu cho automation:
```json
{
  "browser": {
    "headless": false,
    "chrome_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
  },
  "timing": {
    "delay_between_accounts": 10,
    "delay_between_products": 5
  },
  "automation": {
    "max_retries": 3,
    "auto_save_results": true
  }
}
```

## Cách sử dụng:

1. Copy các file mẫu và đổi tên (bỏ "_sample")
2. Chỉnh sửa nội dung theo nhu cầu
3. Import vào chương trình hoặc sử dụng trực tiếp

## Lưu ý:

- Không commit các file chứa thông tin thực vào git
- Sử dụng .gitignore để loại trừ các file cấu hình cá nhân
- Backup các file cấu hình quan trọng
