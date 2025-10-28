# Changelog

Tất cả các thay đổi quan trọng của dự án này sẽ được ghi lại trong file này.

Format dựa trên [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
và dự án này tuân theo [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-10-28

### Added
- Giao diện đồ họa hoàn chỉnh với tkinter
- Quản lý tối đa 10 tài khoản và 20 sản phẩm
- Thống kê chi tiết: số lần quét, mua thành công/thất bại
- Log viewer với chú thích chi tiết và màu sắc
- Xử lý lỗi thông minh, phát hiện hết hàng
- Import/Export JSON cho tài khoản và sản phẩm
- Cấu hình linh hoạt: timing, browser settings
- Báo cáo chi tiết và xuất kết quả
- Multi-threading cho automation
- Graceful shutdown và progress tracking
- Package Python hoàn chỉnh với setup.py
- Documentation đầy đủ và hướng dẫn cài đặt

### Technical Details
- Sử dụng Selenium WebDriver cho browser automation
- Tkinter cho giao diện đồ họa
- Queue-based logging system
- Anti-detection mechanisms
- Comprehensive error handling
- Modular architecture với separation of concerns

### Security
- Không lưu trữ mật khẩu trong plain text
- Validation đầu vào đầy đủ
- Safe file handling
- Error logging không chứa thông tin nhạy cảm

## [Unreleased]

### Planned Features
- Database integration cho lưu trữ dữ liệu
- API endpoints cho remote control
- Plugin system cho extensibility
- Advanced scheduling và cron jobs
- Multi-language support
- Cloud deployment options
- Advanced analytics và reporting
- Integration với các platform khác
