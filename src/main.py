#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ER Sports Automation Tool - Python GUI Version
Công cụ tự động đăng nhập và mua hàng từ er-sports.com với giao diện đồ họa

Tác giả: AI Assistant
Phiên bản: 1.0.0
Ngày tạo: 2024
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import time
import json
import os
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import queue


class BrowserAutomation:
    """
    Class quản lý automation browser cho er-sports.com
    Sử dụng Selenium WebDriver để điều khiển Chrome browser
    """
    
    def __init__(self, headless=False, chrome_path=None):
        """
        Khởi tạo browser automation
        
        Args:
            headless (bool): Chạy browser ở chế độ ẩn (True) hoặc hiện (False)
            chrome_path (str): Đường dẫn đến Chrome executable
        """
        self.driver = None
        self.headless = headless
        self.chrome_path = chrome_path
        self.is_logged_in = False
        
    def setup_driver(self):
        """
        Thiết lập Chrome WebDriver với các tùy chọn cần thiết
        """
        try:
            chrome_options = Options()
            
            # Cấu hình Chrome options
            chrome_options.add_argument("--lang=en-US")
            chrome_options.add_argument("--disable-encryption")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Chế độ headless
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Đường dẫn Chrome nếu được cung cấp
            if self.chrome_path and os.path.exists(self.chrome_path):
                chrome_options.binary_location = self.chrome_path
            
            # Khởi tạo driver
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Thực thi script để ẩn automation
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return True
            
        except Exception as e:
            print(f"Lỗi khởi tạo browser: {str(e)}")
            return False
    
    def login(self, email, password):
        """
        Đăng nhập vào tài khoản er-sports.com
        
        Args:
            email (str): Email đăng nhập
            password (str): Mật khẩu
            
        Returns:
            bool: True nếu đăng nhập thành công, False nếu thất bại
        """
        try:
            if not self.driver:
                if not self.setup_driver():
                    return False
            
            # Truy cập trang chủ
            self.driver.get("https://www.er-sports.com/index.html")
            time.sleep(2)
            
            # Tìm và click vào link đăng nhập
            login_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#header ul li a[href="javascript:ssl_login(\'login\')"]'))
            )
            login_link.click()
            time.sleep(1)
            
            # Điền thông tin đăng nhập
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'table.loginform input[name="id"]'))
            )
            email_input.clear()
            email_input.send_keys(email)
            
            password_input = self.driver.find_element(By.CSS_SELECTOR, 'table.loginform input[name="passwd"]')
            password_input.clear()
            password_input.send_keys(password)
            
            # Click nút đăng nhập
            login_button = self.driver.find_element(By.CSS_SELECTOR, 'div.btn input[onclick="javascript:login_check();"]')
            login_button.click()
            time.sleep(3)
            
            # Kiểm tra đăng nhập thành công
            try:
                # Kiểm tra xem có xuất hiện link đăng xuất không
                logout_link = self.driver.find_element(By.CSS_SELECTOR, 'a[href*="logout"]')
                self.is_logged_in = True
                return True
            except NoSuchElementException:
                # Kiểm tra xem có thông báo lỗi không
                try:
                    error_message = self.driver.find_element(By.CSS_SELECTOR, '.error, .alert, .warning')
                    print(f"Lỗi đăng nhập: {error_message.text}")
                except NoSuchElementException:
                    print("Không thể xác định trạng thái đăng nhập")
                return False
                
        except TimeoutException:
            print("Timeout khi đăng nhập")
            return False
        except Exception as e:
            print(f"Lỗi đăng nhập: {str(e)}")
            return False
    
    def purchase_product(self, product_url, product_id):
        """
        Mua sản phẩm từ URL và product ID
        
        Args:
            product_url (str): URL của sản phẩm
            product_id (str): ID của sản phẩm
            
        Returns:
            dict: Kết quả mua hàng với thông tin chi tiết
        """
        result = {
            'success': False,
            'error': None,
            'product_id': product_id,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            if not self.is_logged_in:
                result['error'] = "Chưa đăng nhập"
                return result
            
            # Xóa giỏ hàng trước
            self.driver.get("https://www.er-sports.com/shop/basket.html")
            time.sleep(2)
            
            try:
                clear_button = self.driver.find_element(By.CSS_SELECTOR, '.btn-wrap-back a[href="JavaScript:basket_clear()"]')
                clear_button.click()
                time.sleep(2)
            except NoSuchElementException:
                pass  # Giỏ hàng có thể đã trống
            
            # Truy cập trang sản phẩm
            self.driver.get(product_url)
            time.sleep(2)
            
            # Kiểm tra sản phẩm có tồn tại không
            try:
                product_title = self.driver.find_element(By.CSS_SELECTOR, 'h1, .product-title, .product-name')
                print(f"Đang mua sản phẩm: {product_title.text}")
            except NoSuchElementException:
                result['error'] = "Không tìm thấy sản phẩm"
                return result
            
            # Kiểm tra tình trạng hàng
            try:
                # Kiểm tra các thông báo hết hàng
                out_of_stock_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    '.out-of-stock, .sold-out, .unavailable, .no-stock, [class*="out"], [class*="sold"]')
                
                for element in out_of_stock_elements:
                    if element.is_displayed() and any(keyword in element.text.lower() 
                        for keyword in ['hết hàng', 'sold out', 'out of stock', 'unavailable']):
                        result['error'] = "Sản phẩm đã hết hàng"
                        return result
                        
            except Exception:
                pass
            
            # Chọn sản phẩm
            try:
                product_selector = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f'input[name="product_id"][value="{product_id}"]'))
                )
                product_selector.click()
                time.sleep(1)
            except TimeoutException:
                result['error'] = "Không tìm thấy selector sản phẩm"
                return result
            
            # Thêm vào giỏ hàng
            try:
                add_to_cart_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="javascript:basket_add(\'detail\')"]'))
                )
                add_to_cart_button.click()
                time.sleep(2)
            except TimeoutException:
                result['error'] = "Không thể thêm vào giỏ hàng"
                return result
            
            # Chuyển đến trang đặt hàng
            self.driver.get("https://www.er-sports.com/shop/order.html")
            time.sleep(2)
            
            # Submit đơn hàng
            try:
                submit_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[onclick="javascript:order_submit()"]'))
                )
                submit_button.click()
                time.sleep(2)
                
                # Submit lần thứ 2 nếu cần
                try:
                    submit_button2 = self.driver.find_element(By.CSS_SELECTOR, 'input[onclick="javascript:order_submit()"]')
                    submit_button2.click()
                    time.sleep(2)
                except NoSuchElementException:
                    pass
                
                result['success'] = True
                
            except TimeoutException:
                result['error'] = "Không thể submit đơn hàng"
                return result
            
        except Exception as e:
            result['error'] = f"Lỗi không xác định: {str(e)}"
        
        return result
    
    def close(self):
        """
        Đóng browser
        """
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Lỗi khi đóng browser: {str(e)}")
            finally:
                self.driver = None
                self.is_logged_in = False


class ERSportsAutomationGUI:
    """
    Class chính cho giao diện đồ họa của ER Sports Automation Tool
    Sử dụng tkinter để tạo GUI với các tính năng:
    - Nhập danh sách tài khoản (10 accounts)
    - Nhập danh sách sản phẩm (20 products)
    - Hiển thị số liệu thống kê
    - Xem log chi tiết
    """
    
    def __init__(self):
        """
        Khởi tạo giao diện chính
        """
        self.root = tk.Tk()
        self.root.title("ER Sports Automation Tool - Python GUI")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Biến trạng thái
        self.is_running = False
        self.automation_thread = None
        self.browser = None
        
        # Biến đếm
        self.scan_count = 0
        self.success_count = 0
        self.failure_count = 0
        
        # Queue để giao tiếp giữa threads
        self.log_queue = queue.Queue()
        
        # Thiết lập logging
        self.setup_logging()
        
        # Tạo giao diện
        self.create_widgets()
        
        # Bắt đầu kiểm tra log queue
        self.check_log_queue()
    
    def setup_logging(self):
        """
        Thiết lập hệ thống logging
        """
        # Tạo thư mục logs nếu chưa có
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Cấu hình logging
        log_filename = f"logs/automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def create_widgets(self):
        """
        Tạo các widget cho giao diện
        """
        # Tạo notebook để chia thành các tab
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Cấu hình tài khoản và sản phẩm
        self.create_account_product_tab()
        
        # Tab 2: Thống kê và điều khiển
        self.create_control_tab()
        
        # Tab 3: Log viewer
        self.create_log_tab()
        
        # Tab 4: Cài đặt
        self.create_settings_tab()
    
    def create_account_product_tab(self):
        """
        Tạo tab nhập tài khoản và sản phẩm
        """
        # Frame chính cho tab
        main_frame = ttk.Frame(self.notebook)
        self.notebook.add(main_frame, text="Tài khoản & Sản phẩm")
        
        # Frame cho tài khoản
        account_frame = ttk.LabelFrame(main_frame, text="Danh sách tài khoản (Tối đa 10)")
        account_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview cho tài khoản
        columns = ('Email', 'Password', 'Tên', 'Ghi chú')
        self.account_tree = ttk.Treeview(account_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.account_tree.heading(col, text=col)
            self.account_tree.column(col, width=150)
        
        # Scrollbar cho account tree
        account_scrollbar = ttk.Scrollbar(account_frame, orient=tk.VERTICAL, command=self.account_tree.yview)
        self.account_tree.configure(yscrollcommand=account_scrollbar.set)
        
        self.account_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        account_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame nhập tài khoản
        account_input_frame = ttk.Frame(account_frame)
        account_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Các trường nhập liệu cho tài khoản
        ttk.Label(account_input_frame, text="Email:").grid(row=0, column=0, sticky=tk.W, padx=2)
        self.email_var = tk.StringVar()
        ttk.Entry(account_input_frame, textvariable=self.email_var, width=30).grid(row=0, column=1, padx=2)
        
        ttk.Label(account_input_frame, text="Password:").grid(row=0, column=2, sticky=tk.W, padx=2)
        self.password_var = tk.StringVar()
        ttk.Entry(account_input_frame, textvariable=self.password_var, show="*", width=20).grid(row=0, column=3, padx=2)
        
        ttk.Label(account_input_frame, text="Tên:").grid(row=1, column=0, sticky=tk.W, padx=2)
        self.name_var = tk.StringVar()
        ttk.Entry(account_input_frame, textvariable=self.name_var, width=30).grid(row=1, column=1, padx=2)
        
        ttk.Label(account_input_frame, text="Ghi chú:").grid(row=1, column=2, sticky=tk.W, padx=2)
        self.notes_var = tk.StringVar()
        ttk.Entry(account_input_frame, textvariable=self.notes_var, width=20).grid(row=1, column=3, padx=2)
        
        # Buttons cho tài khoản
        account_buttons_frame = ttk.Frame(account_input_frame)
        account_buttons_frame.grid(row=2, column=0, columnspan=4, pady=5)
        
        ttk.Button(account_buttons_frame, text="Thêm tài khoản", command=self.add_account).pack(side=tk.LEFT, padx=2)
        ttk.Button(account_buttons_frame, text="Xóa tài khoản", command=self.remove_account).pack(side=tk.LEFT, padx=2)
        ttk.Button(account_buttons_frame, text="Xóa tất cả", command=self.clear_accounts).pack(side=tk.LEFT, padx=2)
        ttk.Button(account_buttons_frame, text="Import JSON", command=self.import_accounts).pack(side=tk.LEFT, padx=2)
        ttk.Button(account_buttons_frame, text="Export JSON", command=self.export_accounts).pack(side=tk.LEFT, padx=2)
        
        # Frame cho sản phẩm
        product_frame = ttk.LabelFrame(main_frame, text="Danh sách sản phẩm (Tối đa 20)")
        product_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview cho sản phẩm
        product_columns = ('ID', 'Tên', 'URL', 'Danh mục', 'Ghi chú')
        self.product_tree = ttk.Treeview(product_frame, columns=product_columns, show='headings', height=6)
        
        for col in product_columns:
            self.product_tree.heading(col, text=col)
            self.product_tree.column(col, width=120)
        
        # Scrollbar cho product tree
        product_scrollbar = ttk.Scrollbar(product_frame, orient=tk.VERTICAL, command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=product_scrollbar.set)
        
        self.product_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        product_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame nhập sản phẩm
        product_input_frame = ttk.Frame(product_frame)
        product_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Các trường nhập liệu cho sản phẩm
        ttk.Label(product_input_frame, text="Product ID:").grid(row=0, column=0, sticky=tk.W, padx=2)
        self.product_id_var = tk.StringVar()
        ttk.Entry(product_input_frame, textvariable=self.product_id_var, width=15).grid(row=0, column=1, padx=2)
        
        ttk.Label(product_input_frame, text="Tên:").grid(row=0, column=2, sticky=tk.W, padx=2)
        self.product_name_var = tk.StringVar()
        ttk.Entry(product_input_frame, textvariable=self.product_name_var, width=25).grid(row=0, column=3, padx=2)
        
        ttk.Label(product_input_frame, text="URL:").grid(row=1, column=0, sticky=tk.W, padx=2)
        self.product_url_var = tk.StringVar()
        ttk.Entry(product_input_frame, textvariable=self.product_url_var, width=40).grid(row=1, column=1, columnspan=2, padx=2)
        
        ttk.Label(product_input_frame, text="Danh mục:").grid(row=1, column=3, sticky=tk.W, padx=2)
        self.product_category_var = tk.StringVar()
        ttk.Entry(product_input_frame, textvariable=self.product_category_var, width=15).grid(row=1, column=4, padx=2)
        
        ttk.Label(product_input_frame, text="Ghi chú:").grid(row=2, column=0, sticky=tk.W, padx=2)
        self.product_notes_var = tk.StringVar()
        ttk.Entry(product_input_frame, textvariable=self.product_notes_var, width=40).grid(row=2, column=1, columnspan=3, padx=2)
        
        # Buttons cho sản phẩm
        product_buttons_frame = ttk.Frame(product_input_frame)
        product_buttons_frame.grid(row=3, column=0, columnspan=5, pady=5)
        
        ttk.Button(product_buttons_frame, text="Thêm sản phẩm", command=self.add_product).pack(side=tk.LEFT, padx=2)
        ttk.Button(product_buttons_frame, text="Xóa sản phẩm", command=self.remove_product).pack(side=tk.LEFT, padx=2)
        ttk.Button(product_buttons_frame, text="Xóa tất cả", command=self.clear_products).pack(side=tk.LEFT, padx=2)
        ttk.Button(product_buttons_frame, text="Import JSON", command=self.import_products).pack(side=tk.LEFT, padx=2)
        ttk.Button(product_buttons_frame, text="Export JSON", command=self.export_products).pack(side=tk.LEFT, padx=2)
    
    def create_control_tab(self):
        """
        Tạo tab điều khiển và thống kê
        """
        control_frame = ttk.Frame(self.notebook)
        self.notebook.add(control_frame, text="Điều khiển & Thống kê")
        
        # Frame thống kê
        stats_frame = ttk.LabelFrame(control_frame, text="Thống kê")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Các label hiển thị số liệu
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(stats_grid, text="Số lần quét:", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.scan_count_label = ttk.Label(stats_grid, text="0", font=('Arial', 12), foreground='blue')
        self.scan_count_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(stats_grid, text="Mua thành công:", font=('Arial', 12, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=5)
        self.success_count_label = ttk.Label(stats_grid, text="0", font=('Arial', 12), foreground='green')
        self.success_count_label.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(stats_grid, text="Mua thất bại:", font=('Arial', 12, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=5)
        self.failure_count_label = ttk.Label(stats_grid, text="0", font=('Arial', 12), foreground='red')
        self.failure_count_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(stats_grid, text="Tỷ lệ thành công:", font=('Arial', 12, 'bold')).grid(row=1, column=2, sticky=tk.W, padx=5)
        self.success_rate_label = ttk.Label(stats_grid, text="0%", font=('Arial', 12), foreground='purple')
        self.success_rate_label.grid(row=1, column=3, sticky=tk.W, padx=5)
        
        # Frame điều khiển
        control_buttons_frame = ttk.LabelFrame(control_frame, text="Điều khiển")
        control_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        buttons_frame = ttk.Frame(control_buttons_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Buttons điều khiển
        self.start_button = ttk.Button(buttons_frame, text="Bắt đầu Automation", command=self.start_automation)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(buttons_frame, text="Dừng Automation", command=self.stop_automation, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="Reset Thống kê", command=self.reset_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Xuất Báo cáo", command=self.export_report).pack(side=tk.LEFT, padx=5)
        
        # Frame trạng thái
        status_frame = ttk.LabelFrame(control_frame, text="Trạng thái")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=15, state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_log_tab(self):
        """
        Tạo tab xem log
        """
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="Log Chi tiết")
        
        # Frame toolbar cho log
        log_toolbar = ttk.Frame(log_frame)
        log_toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(log_toolbar, text="Làm mới Log", command=self.refresh_log).pack(side=tk.LEFT, padx=2)
        ttk.Button(log_toolbar, text="Xóa Log", command=self.clear_log).pack(side=tk.LEFT, padx=2)
        ttk.Button(log_toolbar, text="Lưu Log", command=self.save_log).pack(side=tk.LEFT, padx=2)
        
        # Text widget cho log
        self.log_text = scrolledtext.ScrolledText(log_frame, height=25, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Cấu hình màu sắc cho log
        self.log_text.tag_configure("INFO", foreground="black")
        self.log_text.tag_configure("WARNING", foreground="orange")
        self.log_text.tag_configure("ERROR", foreground="red")
        self.log_text.tag_configure("SUCCESS", foreground="green")
    
    def create_settings_tab(self):
        """
        Tạo tab cài đặt
        """
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Cài đặt")
        
        # Frame cài đặt browser
        browser_frame = ttk.LabelFrame(settings_frame, text="Cài đặt Browser")
        browser_frame.pack(fill=tk.X, padx=5, pady=5)
        
        browser_settings = ttk.Frame(browser_frame)
        browser_settings.pack(fill=tk.X, padx=10, pady=10)
        
        # Checkbox headless
        self.headless_var = tk.BooleanVar()
        ttk.Checkbutton(browser_settings, text="Chạy browser ở chế độ ẩn (Headless)", variable=self.headless_var).pack(anchor=tk.W)
        
        # Đường dẫn Chrome
        ttk.Label(browser_settings, text="Đường dẫn Chrome:").pack(anchor=tk.W)
        chrome_path_frame = ttk.Frame(browser_settings)
        chrome_path_frame.pack(fill=tk.X, pady=2)
        
        self.chrome_path_var = tk.StringVar(value="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
        ttk.Entry(chrome_path_frame, textvariable=self.chrome_path_var, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(chrome_path_frame, text="Chọn", command=self.browse_chrome_path).pack(side=tk.RIGHT, padx=5)
        
        # Frame cài đặt timing
        timing_frame = ttk.LabelFrame(settings_frame, text="Cài đặt Thời gian")
        timing_frame.pack(fill=tk.X, padx=5, pady=5)
        
        timing_settings = ttk.Frame(timing_frame)
        timing_settings.pack(fill=tk.X, padx=10, pady=10)
        
        # Delay giữa các tài khoản
        ttk.Label(timing_settings, text="Delay giữa các tài khoản (giây):").pack(anchor=tk.W)
        self.account_delay_var = tk.IntVar(value=5)
        ttk.Scale(timing_settings, from_=1, to=30, variable=self.account_delay_var, orient=tk.HORIZONTAL).pack(fill=tk.X)
        
        # Delay giữa các sản phẩm
        ttk.Label(timing_settings, text="Delay giữa các sản phẩm (giây):").pack(anchor=tk.W)
        self.product_delay_var = tk.IntVar(value=3)
        ttk.Scale(timing_settings, from_=1, to=20, variable=self.product_delay_var, orient=tk.HORIZONTAL).pack(fill=tk.X)
        
        # Frame cài đặt khác
        other_frame = ttk.LabelFrame(settings_frame, text="Cài đặt khác")
        other_frame.pack(fill=tk.X, padx=5, pady=5)
        
        other_settings = ttk.Frame(other_frame)
        other_settings.pack(fill=tk.X, padx=10, pady=10)
        
        # Auto-save results
        self.auto_save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(other_settings, text="Tự động lưu kết quả", variable=self.auto_save_var).pack(anchor=tk.W)
        
        # Retry failed purchases
        self.retry_failed_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(other_settings, text="Thử lại mua hàng thất bại", variable=self.retry_failed_var).pack(anchor=tk.W)
        
        # Max retries
        ttk.Label(other_settings, text="Số lần thử lại tối đa:").pack(anchor=tk.W)
        self.max_retries_var = tk.IntVar(value=3)
        ttk.Scale(other_settings, from_=1, to=10, variable=self.max_retries_var, orient=tk.HORIZONTAL).pack(fill=tk.X)
    
    def add_account(self):
        """
        Thêm tài khoản mới vào danh sách
        """
        if len(self.account_tree.get_children()) >= 10:
            messagebox.showwarning("Cảnh báo", "Chỉ được thêm tối đa 10 tài khoản!")
            return
        
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        name = self.name_var.get().strip()
        notes = self.notes_var.get().strip()
        
        if not email or not password:
            messagebox.showerror("Lỗi", "Email và Password không được để trống!")
            return
        
        # Kiểm tra email đã tồn tại chưa
        for item in self.account_tree.get_children():
            if self.account_tree.item(item)['values'][0] == email:
                messagebox.showerror("Lỗi", "Email này đã tồn tại!")
                return
        
        # Thêm vào treeview
        self.account_tree.insert('', tk.END, values=(email, password, name, notes))
        
        # Xóa các trường nhập liệu
        self.email_var.set("")
        self.password_var.set("")
        self.name_var.set("")
        self.notes_var.set("")
        
        self.log_message(f"Đã thêm tài khoản: {email}", "INFO")
    
    def remove_account(self):
        """
        Xóa tài khoản được chọn
        """
        selected = self.account_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài khoản cần xóa!")
            return
        
        item = selected[0]
        email = self.account_tree.item(item)['values'][0]
        self.account_tree.delete(item)
        self.log_message(f"Đã xóa tài khoản: {email}", "INFO")
    
    def clear_accounts(self):
        """
        Xóa tất cả tài khoản
        """
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa tất cả tài khoản?"):
            self.account_tree.delete(*self.account_tree.get_children())
            self.log_message("Đã xóa tất cả tài khoản", "INFO")
    
    def add_product(self):
        """
        Thêm sản phẩm mới vào danh sách
        """
        if len(self.product_tree.get_children()) >= 20:
            messagebox.showwarning("Cảnh báo", "Chỉ được thêm tối đa 20 sản phẩm!")
            return
        
        product_id = self.product_id_var.get().strip()
        name = self.product_name_var.get().strip()
        url = self.product_url_var.get().strip()
        category = self.product_category_var.get().strip()
        notes = self.product_notes_var.get().strip()
        
        if not product_id or not url:
            messagebox.showerror("Lỗi", "Product ID và URL không được để trống!")
            return
        
        # Kiểm tra product ID đã tồn tại chưa
        for item in self.product_tree.get_children():
            if self.product_tree.item(item)['values'][0] == product_id:
                messagebox.showerror("Lỗi", "Product ID này đã tồn tại!")
                return
        
        # Thêm vào treeview
        self.product_tree.insert('', tk.END, values=(product_id, name, url, category, notes))
        
        # Xóa các trường nhập liệu
        self.product_id_var.set("")
        self.product_name_var.set("")
        self.product_url_var.set("")
        self.product_category_var.set("")
        self.product_notes_var.set("")
        
        self.log_message(f"Đã thêm sản phẩm: {name or product_id}", "INFO")
    
    def remove_product(self):
        """
        Xóa sản phẩm được chọn
        """
        selected = self.product_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sản phẩm cần xóa!")
            return
        
        item = selected[0]
        product_id = self.product_tree.item(item)['values'][0]
        self.product_tree.delete(item)
        self.log_message(f"Đã xóa sản phẩm: {product_id}", "INFO")
    
    def clear_products(self):
        """
        Xóa tất cả sản phẩm
        """
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa tất cả sản phẩm?"):
            self.product_tree.delete(*self.product_tree.get_children())
            self.log_message("Đã xóa tất cả sản phẩm", "INFO")
    
    def import_accounts(self):
        """
        Import danh sách tài khoản từ file JSON
        """
        filename = filedialog.askopenfilename(
            title="Chọn file JSON chứa tài khoản",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    accounts = json.load(f)
                
                if not isinstance(accounts, list):
                    raise ValueError("File JSON phải chứa một array")
                
                # Xóa tài khoản hiện tại
                self.clear_accounts()
                
                # Thêm tài khoản mới
                for account in accounts[:10]:  # Giới hạn 10 tài khoản
                    if isinstance(account, dict) and 'email' in account and 'password' in account:
                        self.account_tree.insert('', tk.END, values=(
                            account.get('email', ''),
                            account.get('password', ''),
                            account.get('name', ''),
                            account.get('notes', '')
                        ))
                
                self.log_message(f"Đã import {len(accounts)} tài khoản từ {filename}", "SUCCESS")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể import file: {str(e)}")
    
    def export_accounts(self):
        """
        Export danh sách tài khoản ra file JSON
        """
        accounts = []
        for item in self.account_tree.get_children():
            values = self.account_tree.item(item)['values']
            accounts.append({
                'email': values[0],
                'password': values[1],
                'name': values[2],
                'notes': values[3]
            })
        
        if not accounts:
            messagebox.showwarning("Cảnh báo", "Không có tài khoản nào để export!")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Lưu danh sách tài khoản",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(accounts, f, ensure_ascii=False, indent=2)
                
                self.log_message(f"Đã export {len(accounts)} tài khoản ra {filename}", "SUCCESS")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể export file: {str(e)}")
    
    def import_products(self):
        """
        Import danh sách sản phẩm từ file JSON
        """
        filename = filedialog.askopenfilename(
            title="Chọn file JSON chứa sản phẩm",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    products = json.load(f)
                
                if not isinstance(products, list):
                    raise ValueError("File JSON phải chứa một array")
                
                # Xóa sản phẩm hiện tại
                self.clear_products()
                
                # Thêm sản phẩm mới
                for product in products[:20]:  # Giới hạn 20 sản phẩm
                    if isinstance(product, dict) and 'productId' in product and 'url' in product:
                        self.product_tree.insert('', tk.END, values=(
                            product.get('productId', ''),
                            product.get('name', ''),
                            product.get('url', ''),
                            product.get('category', ''),
                            product.get('notes', '')
                        ))
                
                self.log_message(f"Đã import {len(products)} sản phẩm từ {filename}", "SUCCESS")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể import file: {str(e)}")
    
    def export_products(self):
        """
        Export danh sách sản phẩm ra file JSON
        """
        products = []
        for item in self.product_tree.get_children():
            values = self.product_tree.item(item)['values']
            products.append({
                'productId': values[0],
                'name': values[1],
                'url': values[2],
                'category': values[3],
                'notes': values[4]
            })
        
        if not products:
            messagebox.showwarning("Cảnh báo", "Không có sản phẩm nào để export!")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Lưu danh sách sản phẩm",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(products, f, ensure_ascii=False, indent=2)
                
                self.log_message(f"Đã export {len(products)} sản phẩm ra {filename}", "SUCCESS")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể export file: {str(e)}")
    
    def start_automation(self):
        """
        Bắt đầu quá trình automation
        """
        # Kiểm tra dữ liệu đầu vào
        accounts = []
        for item in self.account_tree.get_children():
            values = self.account_tree.item(item)['values']
            accounts.append({
                'email': values[0],
                'password': values[1],
                'name': values[2],
                'notes': values[3]
            })
        
        products = []
        for item in self.product_tree.get_children():
            values = self.product_tree.item(item)['values']
            products.append({
                'productId': values[0],
                'name': values[1],
                'url': values[2],
                'category': values[3],
                'notes': values[4]
            })
        
        if not accounts:
            messagebox.showerror("Lỗi", "Vui lòng thêm ít nhất một tài khoản!")
            return
        
        if not products:
            messagebox.showerror("Lỗi", "Vui lòng thêm ít nhất một sản phẩm!")
            return
        
        # Cập nhật trạng thái UI
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Bắt đầu thread automation
        self.automation_thread = threading.Thread(target=self.run_automation, args=(accounts, products))
        self.automation_thread.daemon = True
        self.automation_thread.start()
        
        self.log_message("Bắt đầu automation...", "INFO")
    
    def stop_automation(self):
        """
        Dừng quá trình automation
        """
        self.is_running = False
        
        if self.browser:
            try:
                self.browser.close()
            except Exception as e:
                self.log_message(f"Lỗi khi đóng browser: {str(e)}", "ERROR")
        
        # Cập nhật trạng thái UI
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        self.log_message("Đã dừng automation", "WARNING")
    
    def run_automation(self, accounts, products):
        """
        Chạy automation trong thread riêng
        
        Args:
            accounts (list): Danh sách tài khoản
            products (list): Danh sách sản phẩm
        """
        try:
            for account in accounts:
                if not self.is_running:
                    break
                
                self.log_message(f"Đang xử lý tài khoản: {account['email']}", "INFO")
                
                # Khởi tạo browser cho tài khoản này
                self.browser = BrowserAutomation(
                    headless=self.headless_var.get(),
                    chrome_path=self.chrome_path_var.get() if self.chrome_path_var.get() else None
                )
                
                # Đăng nhập
                if self.browser.login(account['email'], account['password']):
                    self.log_message(f"Đăng nhập thành công: {account['email']}", "SUCCESS")
                    
                    # Mua từng sản phẩm
                    for product in products:
                        if not self.is_running:
                            break
                        
                        self.scan_count += 1
                        self.update_stats()
                        
                        self.log_message(f"Đang mua sản phẩm: {product['name'] or product['productId']}", "INFO")
                        
                        result = self.browser.purchase_product(product['url'], product['productId'])
                        
                        if result['success']:
                            self.success_count += 1
                            self.log_message(f"Mua thành công: {product['name'] or product['productId']}", "SUCCESS")
                        else:
                            self.failure_count += 1
                            error_msg = result['error'] or "Lỗi không xác định"
                            self.log_message(f"Mua thất bại: {product['name'] or product['productId']} - {error_msg}", "ERROR")
                        
                        self.update_stats()
                        
                        # Delay giữa các sản phẩm
                        if self.product_delay_var.get() > 0:
                            time.sleep(self.product_delay_var.get())
                
                else:
                    self.log_message(f"Đăng nhập thất bại: {account['email']}", "ERROR")
                
                # Đóng browser
                if self.browser:
                    self.browser.close()
                    self.browser = None
                
                # Delay giữa các tài khoản
                if self.account_delay_var.get() > 0:
                    time.sleep(self.account_delay_var.get())
            
            self.log_message("Hoàn thành automation!", "SUCCESS")
            
        except Exception as e:
            self.log_message(f"Lỗi trong automation: {str(e)}", "ERROR")
        
        finally:
            # Cập nhật trạng thái UI
            self.root.after(0, self.automation_finished)
    
    def automation_finished(self):
        """
        Callback khi automation hoàn thành
        """
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def update_stats(self):
        """
        Cập nhật hiển thị thống kê
        """
        self.scan_count_label.config(text=str(self.scan_count))
        self.success_count_label.config(text=str(self.success_count))
        self.failure_count_label.config(text=str(self.failure_count))
        
        # Tính tỷ lệ thành công
        if self.scan_count > 0:
            success_rate = (self.success_count / self.scan_count) * 100
            self.success_rate_label.config(text=f"{success_rate:.1f}%")
        else:
            self.success_rate_label.config(text="0%")
    
    def reset_stats(self):
        """
        Reset thống kê về 0
        """
        self.scan_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.update_stats()
        self.log_message("Đã reset thống kê", "INFO")
    
    def export_report(self):
        """
        Xuất báo cáo chi tiết
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'statistics': {
                'total_scans': self.scan_count,
                'successful_purchases': self.success_count,
                'failed_purchases': self.failure_count,
                'success_rate': (self.success_count / self.scan_count * 100) if self.scan_count > 0 else 0
            },
            'accounts': [],
            'products': []
        }
        
        # Thêm thông tin tài khoản
        for item in self.account_tree.get_children():
            values = self.account_tree.item(item)['values']
            report['accounts'].append({
                'email': values[0],
                'name': values[2],
                'notes': values[3]
            })
        
        # Thêm thông tin sản phẩm
        for item in self.product_tree.get_children():
            values = self.product_tree.item(item)['values']
            report['products'].append({
                'productId': values[0],
                'name': values[1],
                'url': values[2],
                'category': values[3],
                'notes': values[4]
            })
        
        filename = filedialog.asksaveasfilename(
            title="Lưu báo cáo",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
                
                self.log_message(f"Đã xuất báo cáo ra {filename}", "SUCCESS")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xuất báo cáo: {str(e)}")
    
    def log_message(self, message, level="INFO"):
        """
        Ghi log message
        
        Args:
            message (str): Nội dung log
            level (str): Mức độ log (INFO, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        # Thêm vào queue để xử lý trong main thread
        self.log_queue.put((log_entry, level))
        
        # Ghi vào file log
        self.logger.info(f"[{level}] {message}")
    
    def check_log_queue(self):
        """
        Kiểm tra và xử lý log queue
        """
        try:
            while True:
                log_entry, level = self.log_queue.get_nowait()
                
                # Thêm vào log text widget
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, log_entry + "\n")
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
                
                # Thêm vào status text
                self.status_text.config(state=tk.NORMAL)
                self.status_text.insert(tk.END, log_entry + "\n")
                self.status_text.see(tk.END)
                self.status_text.config(state=tk.DISABLED)
                
        except queue.Empty:
            pass
        
        # Lên lịch kiểm tra lại sau 100ms
        self.root.after(100, self.check_log_queue)
    
    def refresh_log(self):
        """
        Làm mới log viewer
        """
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log_message("Đã làm mới log viewer", "INFO")
    
    def clear_log(self):
        """
        Xóa log viewer
        """
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa log?"):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state=tk.DISABLED)
            self.log_message("Đã xóa log", "INFO")
    
    def save_log(self):
        """
        Lưu log ra file
        """
        filename = filedialog.asksaveasfilename(
            title="Lưu log",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                
                self.log_message(f"Đã lưu log ra {filename}", "SUCCESS")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu log: {str(e)}")
    
    def browse_chrome_path(self):
        """
        Chọn đường dẫn Chrome
        """
        filename = filedialog.askopenfilename(
            title="Chọn Chrome executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        
        if filename:
            self.chrome_path_var.set(filename)
    
    def run(self):
        """
        Chạy ứng dụng
        """
        self.log_message("Khởi động ER Sports Automation Tool", "INFO")
        self.root.mainloop()


def main():
    """
    Hàm main để khởi chạy ứng dụng
    """
    try:
        app = ERSportsAutomationGUI()
        app.run()
    except Exception as e:
        print(f"Lỗi khởi động ứng dụng: {str(e)}")
        messagebox.showerror("Lỗi", f"Không thể khởi động ứng dụng: {str(e)}")


if __name__ == "__main__":
    main()
