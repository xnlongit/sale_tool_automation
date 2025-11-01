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
import subprocess
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, \
    UnexpectedAlertPresentException
from selenium.webdriver.common.alert import Alert
import queue
import sys
import shutil
import re

# Thử import webdriver-manager để tự động quản lý ChromeDriver
try:
    from webdriver_manager.chrome import ChromeDriverManager

    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

# URL cố định để mua tất cả sản phẩm (trang liệt kê sản phẩm)
PRODUCT_LIST_URL = "https://www.er-sports.com/shop/shopbrand.html?search=mezz&sort=price_desc&money1=&money2=&prize1=&company1=&content1=&originalcode1=&category=&subcategory="


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

    def close_popups(self, verbose=False):
        """
        Đóng các popup và overlay có thể che các element cần click

        Args:
            verbose (bool): Nếu True, in log chi tiết
        """
        if verbose:
            print("[close_popups] Bắt đầu đóng popups...")

        try:
            # Kiểm tra và đóng popup WorldShopping với ID: zigzag-modal
            popup_found = False
            try:
                # Thử tìm popup với ID zigzag-modal (popup chính)
                if verbose:
                    print("[close_popups] Đang tìm popup zigzag-modal...")
                popup = self.driver.find_element(By.ID, 'zigzag-modal')
                if popup.is_displayed():
                    if verbose:
                        print("[close_popups] ✓ Tìm thấy popup zigzag-modal đang hiển thị")
                    popup_found = True
                else:
                    if verbose:
                        print("[close_popups] Tìm thấy popup zigzag-modal nhưng không hiển thị")
            except NoSuchElementException:
                if verbose:
                    print("[close_popups] Không tìm thấy popup zigzag-modal")
            except Exception as e:
                if verbose:
                    print(f"[close_popups] Lỗi khi tìm popup zigzag-modal: {str(e)}")

            # Thử tìm nút close với nhiều selector khác nhau nếu tìm thấy popup
            if popup_found:
                if verbose:
                    print("[close_popups] Bắt đầu đóng popup...")

                try:
                    close_selectors = [
                        'button#zigzag-test__modal-close',  # Nút close chính
                        '#zigzag-modal button',
                        '#zigzag-modal button.close',
                        '#zigzag-modal [alt="Close"]',
                        '#zigzag-modal .close',
                        '#zigzag-modal img[alt="Close"]',
                        'button[type="button"] img[alt="Close"]',
                        '#zigzag-worldshopping-checkout button.close',
                        '#zigzag-worldshopping-checkout .close-btn',
                        '#zigzag-worldshopping-checkout .modal-close'
                    ]

                    for selector in close_selectors:
                        try:
                            close_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if close_btn.is_displayed():
                                if verbose:
                                    print(f"[close_popups] Tìm thấy nút close với selector: {selector}")
                                self.driver.execute_script("arguments[0].click();", close_btn)
                                time.sleep(0.3)
                                if verbose:
                                    print("[close_popups] ✓ Đã click vào nút close")
                                break
                        except:
                            continue

                    # Nếu không tìm thấy nút close, thử Escape key
                    try:
                        if verbose:
                            print("[close_popups] Thử nhấn phím ESC...")
                        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                        time.sleep(0.3)
                        if verbose:
                            print("[close_popups] ✓ Đã nhấn ESC")
                    except Exception as e:
                        if verbose:
                            print(f"[close_popups] Không thể nhấn ESC: {str(e)}")
                except Exception as e:
                    if verbose:
                        print(f"[close_popups] Lỗi khi tìm nút close: {str(e)}")
                    # Click ra ngoài bằng cách click vào body
                    try:
                        body = self.driver.find_element(By.TAG_NAME, 'body')
                        self.driver.execute_script("arguments[0].click();", body)
                        time.sleep(0.3)
                        if verbose:
                            print("[close_popups] ✓ Đã click ra ngoài popup")
                    except Exception as e2:
                        if verbose:
                            print(f"[close_popups] Không thể click ra ngoài: {str(e2)}")

                # Ẩn popup bằng CSS - thử nhiều cách
                try:
                    if verbose:
                        print("[close_popups] Thử ẩn popup bằng JavaScript...")
                    scripts = [
                        "document.getElementById('zigzag-modal').style.display='none';",
                        "var popup = document.getElementById('zigzag-modal'); if(popup) popup.style.display='none';",
                        "document.getElementById('zigzag-modal').remove();",
                        "document.getElementById('zigzag-worldshopping-checkout').style.display='none';",
                        "document.getElementById('zigzag-worldshopping-checkout').remove();"
                    ]
                    for script in scripts:
                        try:
                            self.driver.execute_script(script)
                            time.sleep(0.2)
                            if verbose:
                                print(f"[close_popups] ✓ Đã chạy script: {script}")
                        except:
                            continue
                except Exception as e:
                    if verbose:
                        print(f"[close_popups] Lỗi khi ẩn popup bằng JS: {str(e)}")

            # Kiểm tra popup WorldShopping với nhiều selector khác nhau (fallback)
            if not popup_found:
                try:
                    worldshopping_popups = [
                        (By.ID, 'zigzag-modal'),  # Popup chính
                        (By.ID, 'zigzag-worldshopping-checkout'),
                        (By.CLASS_NAME, 'worldshopping-popup'),
                        (By.CSS_SELECTOR, '[class*="worldshopping"]'),
                        (By.CSS_SELECTOR, '[id*="zigzag"]'),
                        (By.CSS_SELECTOR, '[class*="NoticeV2"]'),
                        (By.CSS_SELECTOR, '.modal[class*="world"]')
                    ]

                    for locator_type, locator_value in worldshopping_popups:
                        try:
                            popup = self.driver.find_element(locator_type, locator_value)
                            if popup.is_displayed():
                                # Thử đóng popup
                                try:
                                    # Tìm nút X trong popup
                                    close_btn = popup.find_element(By.CSS_SELECTOR,
                                                                   'button, .close, [aria-label*="close" i]')
                                    self.driver.execute_script("arguments[0].click();", close_btn)
                                    time.sleep(0.3)
                                except:
                                    # Ẩn popup
                                    self.driver.execute_script("arguments[0].style.display='none';", popup)
                                    time.sleep(0.3)
                                break
                        except:
                            continue
                except:
                    pass

            # Kiểm tra các popup/overlay khác có thể che element
            try:
                overlay_selectors = [
                    '.modal-backdrop',
                    '.overlay',
                    '.popup-overlay',
                    '[style*="position: fixed"]',
                    '[style*="z-index"]'
                ]

                for selector in overlay_selectors:
                    try:
                        overlays = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for overlay in overlays:
                            try:
                                overlay_id = overlay.get_attribute('id') or ''
                                if overlay.is_displayed() and 'zigzag' not in overlay_id:
                                    self.driver.execute_script("arguments[0].style.display='none';", overlay)
                                    time.sleep(0.2)
                            except:
                                pass
                    except:
                        pass
            except:
                pass

        except:
            pass

    @staticmethod
    def find_chrome_executable():
        """
        Tìm đường dẫn Chrome executable trên Windows

        Returns:
            str: Đường dẫn đến chrome.exe hoặc None nếu không tìm thấy
        """
        # Danh sách các đường dẫn có thể có
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None

    @staticmethod
    def find_chromedriver_executable():
        """
        Tìm đường dẫn ChromeDriver executable

        Returns:
            str: Đường dẫn đến chromedriver.exe hoặc None nếu không tìm thấy
        """
        # Nếu đang chạy trong môi trường PyInstaller
        if getattr(sys, 'frozen', False):
            # Lấy thư mục chứa executable
            base_path = os.path.dirname(sys.executable)
            chromedriver_path = os.path.join(base_path, 'chromedriver.exe')
            if os.path.exists(chromedriver_path):
                return chromedriver_path

        # Tìm trong PATH
        chromedriver = shutil.which('chromedriver.exe')
        if chromedriver:
            return chromedriver

        # Tìm trong các thư mục thông thường
        possible_paths = [
            r"C:\Program Files\ChromeDriver\chromedriver.exe",
            r"C:\chromedriver\chromedriver.exe",
            os.path.join(os.path.dirname(__file__), 'chromedriver.exe'),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None

    def setup_driver(self, verbose=True):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--lang=en-US")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_experimental_option("detach", True)  # Giữ Chrome mở

            # Nếu bạn tick Headless thì dùng headless mới
            if self.headless:
                chrome_options.add_argument("--headless=new")

            # Tìm đường dẫn Chrome
            chrome_executable = self.chrome_path if (
                    self.chrome_path and os.path.exists(self.chrome_path)) else self.find_chrome_executable()

            if chrome_executable:
                chrome_options.binary_location = chrome_executable
                if verbose:
                    print(f"Sử dụng Chrome tại: {chrome_executable}")
            elif verbose:
                print("Không tìm thấy Chrome, sẽ sử dụng Chrome mặc định trong PATH")

            # Tìm đường dẫn ChromeDriver
            # Ưu tiên: 1. ChromeDriver đã có sẵn, 2. webdriver-manager tự động tải, 3. Service() mặc định
            chromedriver_path = self.find_chromedriver_executable()
            service = None

            if chromedriver_path:
                if verbose:
                    print(f"Sử dụng ChromeDriver tại: {chromedriver_path}")
                service = Service(chromedriver_path)
            elif WEBDRIVER_MANAGER_AVAILABLE:
                try:
                    if verbose:
                        print("Không tìm thấy ChromeDriver, đang tải tự động bằng webdriver-manager...")
                    chromedriver_path = ChromeDriverManager().install()
                    if verbose:
                        print(f"✓ Đã tải và cài đặt ChromeDriver tại: {chromedriver_path}")
                    service = Service(chromedriver_path)
                except Exception as e:
                    if verbose:
                        print(f"Cảnh báo: Không thể tải ChromeDriver tự động: {str(e)}")
                    # Fallback: thử dùng Service() mặc định
                    if verbose:
                        print("Đang thử sử dụng ChromeDriver mặc định từ selenium...")
                    service = Service()
            else:
                if verbose:
                    print("⚠️  Không tìm thấy ChromeDriver!")
                    print("💡 Để tự động tải ChromeDriver, vui lòng cài đặt:")
                    print("   pip install webdriver-manager")
                    print("   Hoặc tải ChromeDriver thủ công từ: https://chromedriver.chromium.org/")
                    print("Đang thử sử dụng ChromeDriver mặc định từ selenium...")
                service = Service()

            # Khởi tạo WebDriver
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # Ẩn dấu hiệu automation
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            return True
        except Exception as e:
            error_msg = f"Lỗi khởi tạo browser: {str(e)}"
            if verbose:
                print(error_msg)
                print("Đang thử sử dụng Chrome và ChromeDriver mặc định...")

            try:
                # Thử với webdriver-manager nếu có
                if WEBDRIVER_MANAGER_AVAILABLE:
                    try:
                        if verbose:
                            print("Đang thử tải ChromeDriver bằng webdriver-manager...")
                        chromedriver_path = ChromeDriverManager().install()
                        if verbose:
                            print(f"Đã tải ChromeDriver tại: {chromedriver_path}")
                        service = Service(chromedriver_path)
                    except Exception as e_manager:
                        if verbose:
                            print(f"Cảnh báo: Không thể tải ChromeDriver: {str(e_manager)}")
                        service = Service()
                else:
                    service = Service()

                # Thử với cài đặt mặc định
                chrome_options = Options()
                chrome_options.add_argument("--lang=en-US")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")

                if self.headless:
                    chrome_options.add_argument("--headless=new")

                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.driver.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )
                if verbose:
                    print("Khởi tạo browser thành công với cài đặt mặc định")
                return True
            except Exception as e2:
                if verbose:
                    print(f"Lỗi khởi tạo browser với cài đặt mặc định: {str(e2)}")
                    if "chromedriver" in str(e2).lower():
                        print("\n⚠️  LỖI: Không tìm thấy ChromeDriver!")
                        print("💡 Giải pháp:")
                        print("   1. Cài đặt webdriver-manager: pip install webdriver-manager")
                        print("   2. Hoặc tải ChromeDriver thủ công từ: https://chromedriver.chromium.org/")
                        print("   3. Đặt ChromeDriver vào PATH hoặc cùng thư mục với script")
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
        print(f"[login] Bắt đầu đăng nhập với email: {email}")

        try:
            if not self.driver:
                print("[login] Driver chưa khởi tạo, đang thiết lập...")
                if not self.setup_driver():
                    print("[login] ✗ Không thể khởi tạo driver")
                    return False
                print("[login] ✓ Driver đã được khởi tạo")

            # Truy cập trang chủ
            print("[login] Đang truy cập trang chủ...")
            self.driver.get("https://www.er-sports.com/index.html")
            time.sleep(2)
            print("[login] ✓ Đã tải trang chủ")

            # Đóng popup WorldShopping nếu có (xuất hiện lần đầu vào website)
            print("[login] Đang đóng popup lần 1...")
            self.close_popups(verbose=True)
            time.sleep(1)

            # Gọi trực tiếp hàm JavaScript để mở form login
            print("[login] Đang gọi hàm ssl_login('login') để mở form...")
            try:
                self.driver.execute_script("ssl_login('login');")
                print("[login] ✓ Đã gọi ssl_login('login')")
            except Exception as e:
                print(f"[login] Không thể gọi ssl_login trực tiếp: {str(e)}")
                # Fallback: click link
                print("[login] Thử click link đăng nhập...")
                login_link = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, '#header ul li a[href="javascript:ssl_login(\'login\')"]'))
                )
                login_link.click()
                print("[login] ✓ Đã click vào link đăng nhập")

            # Đợi form login xuất hiện
            print("[login] Đang đợi form login xuất hiện...")

            # Thử nhiều cách để đợi form xuất hiện
            form_loaded = False
            try:
                # Đợi cho đến khi có input với name="id"
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="id"]'))
                )
                form_loaded = True
                print("[login] ✓ Form login đã xuất hiện")
            except TimeoutException:
                print("[login] ✗ Timeout đợi form xuất hiện")

            if not form_loaded:
                time.sleep(2)  # Thêm delay nếu form chưa xuất hiện

            # Đóng popup WorldShopping nếu có (thử nhiều lần vì popup có thể tự hiện lại)
            print("[login] Đang đóng popup nhiều lần...")
            for i in range(5):  # Tăng số lần thử
                print(f"[login] Đóng popup lần {i + 1}/5...")
                self.close_popups(verbose=True)
                time.sleep(0.5)

            # Điền thông tin đăng nhập - thử nhiều selector
            print("[login] Đang tìm ô nhập email...")

            # Thử nhiều selector khác nhau cho email input
            email_input = None
            email_selectors = [
                'table.loginform input[name="id"]',
                'input[name="id"]',
                'input[type="text"]',
                'input[type="email"]',
                'table.loginform input[type="text"]'
            ]

            for selector in email_selectors:
                try:
                    print(f"[login] Thử tìm email với selector: {selector}")
                    email_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"[login] ✓ Tìm thấy ô email với selector: {selector}")
                    break
                except TimeoutException:
                    continue

            if not email_input:
                print("[login] ✗ Không tìm thấy ô email với bất kỳ selector nào")
                print("[login] Đang chụp màn hình và lưu HTML để debug...")
                try:
                    self.driver.save_screenshot('debug_login_not_found.png')
                    print("[login] Đã lưu screenshot: debug_login_not_found.png")
                except Exception as e:
                    print(f"[login] Không thể chụp màn hình: {str(e)}")
                try:
                    with open('debug_login_page.html', 'w', encoding='utf-8') as f:
                        f.write(self.driver.page_source)
                    print("[login] Đã lưu HTML: debug_login_page.html")
                except Exception as e:
                    print(f"[login] Không thể lưu HTML: {str(e)}")
                raise Exception("Không tìm thấy ô nhập email")

            # Scroll đến element
            print("[login] Đang scroll đến ô email...")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", email_input)
            time.sleep(0.5)

            # Đóng popup lại một lần nữa sau khi scroll
            print("[login] Đóng popup sau khi scroll...")
            self.close_popups(verbose=True)
            time.sleep(0.5)

            # Thử điền bằng JavaScript để tránh bị che
            print("[login] Đang điền email bằng JavaScript...")
            try:
                self.driver.execute_script(
                    "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input'));",
                    email_input, email)
                print("[login] ✓ Đã điền email bằng JavaScript")
            except Exception as e:
                print(f"[login] Lỗi JS, thử clear thông thường: {str(e)}")
                email_input.clear()
                email_input.send_keys(email)
                print("[login] ✓ Đã điền email bằng cách thông thường")

            # Điền password
            print("[login] Đang điền password...")
            password_input = self.driver.find_element(By.CSS_SELECTOR, 'table.loginform input[name="passwd"]')

            # Scroll đến password field
            self.driver.execute_script("arguments[0].scrollIntoView(true);", password_input)
            time.sleep(0.5)

            # Thử điền bằng JavaScript
            try:
                self.driver.execute_script(
                    "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input'));",
                    password_input, password)
                print("[login] ✓ Đã điền password bằng JavaScript")
            except Exception as e:
                print(f"[login] Lỗi JS, thử cách thông thường: {str(e)}")
                password_input.clear()
                password_input.send_keys(password)
                print("[login] ✓ Đã điền password bằng cách thông thường")

            # Đóng popup lại một lần nữa trước khi submit (popup có thể xuất hiện lại)
            print("[login] Đóng popup lần cuối trước khi submit...")
            self.close_popups(verbose=True)
            time.sleep(0.5)

            # Click nút đăng nhập
            print("[login] Đang tìm nút đăng nhập...")
            login_button = self.driver.find_element(By.CSS_SELECTOR,
                                                    'div.btn input[onclick="javascript:login_check();"]')
            print("[login] ✓ Tìm thấy nút đăng nhập, đang click...")

            # Sử dụng JavaScript click để tránh popup che button
            try:
                self.driver.execute_script("arguments[0].click();", login_button)
                print("[login] ✓ Đã click nút đăng nhập bằng JavaScript")
            except Exception as e:
                print(f"[login] Không thể click bằng JS: {str(e)}, thử click thường...")
                login_button.click()
                print("[login] ✓ Đã click nút đăng nhập bằng click thường")

            time.sleep(3)
            print("[login] Đang kiểm tra kết quả đăng nhập...")

            # Kiểm tra đăng nhập thành công
            try:
                # Kiểm tra xem có xuất hiện link đăng xuất không
                logout_link = self.driver.find_element(By.CSS_SELECTOR, 'a[href*="logout"]')
                print("[login] ✓✓✓ Đăng nhập THÀNH CÔNG!")
                self.is_logged_in = True
                return True
            except NoSuchElementException:
                print("[login] ✗ Không tìm thấy link logout")
                # Kiểm tra xem có thông báo lỗi không
                try:
                    error_message = self.driver.find_element(By.CSS_SELECTOR, '.error, .alert, .warning')
                    print(f"[login] ✗ Lỗi đăng nhập: {error_message.text}")
                except NoSuchElementException:
                    print("[login] ✗ Không thể xác định trạng thái đăng nhập")
                print("[login] ✗✗✗ Đăng nhập THẤT BẠI!")
                return False

        except TimeoutException as e:
            print(f"[login] ✗✗✗ TIMEOUT khi đăng nhập: {str(e)}")
            return False
        except Exception as e:
            print(f"[login] ✗✗✗ LỖI đăng nhập: {str(e)}")
            import traceback
            print(f"[login] Traceback: {traceback.format_exc()}")
            return False

    def purchase_product(self, product_url, product_id):
        """
        Mua sản phẩm bằng cách quét từng page trong listing, tìm sản phẩm có chứa product_id trong tên

        Args:
            product_url (str): URL của trang listing (không dùng trực tiếp)
            product_id (str): ID của sản phẩm cần tìm (tìm trong tên sản phẩm)

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
            print(f"[purchase] Xóa giỏ hàng trước khi mua sản phẩm {product_id}")
            self.driver.get("https://www.er-sports.com/shop/basket.html")
            time.sleep(2)
            self.close_popups()
            time.sleep(0.5)

            try:
                clear_button = self.driver.find_element(By.CSS_SELECTOR,
                                                        '.btn-wrap-back a[href*="basket_clear"]')
                try:
                    self.driver.execute_script("arguments[0].click();", clear_button)
                    time.sleep(1)
                    try:
                        WebDriverWait(self.driver, 5).until(EC.alert_is_present())
                        alert = self.driver.switch_to.alert
                        alert.accept()
                        time.sleep(1)
                    except TimeoutException:
                        pass
                except:
                    clear_button.click()
                    time.sleep(1)
                    try:
                        WebDriverWait(self.driver, 5).until(EC.alert_is_present())
                        alert = self.driver.switch_to.alert
                        alert.accept()
                        time.sleep(1)
                    except TimeoutException:
                        pass
            except NoSuchElementException:
                pass  # Giỏ hàng đã trống

            # Bắt đầu quét từ page đầu tiên
            listing_url = PRODUCT_LIST_URL
            current_page = 1
            max_pages_to_scan = 5  # Giới hạn số page để tránh vòng lặp vô hạn
            total_scans = 0  # Đếm tổng số lần quét để tránh vòng lặp vô hạn khi refresh
            product_found = False
            product_detail_url = None

            while not product_found and current_page <= max_pages_to_scan and total_scans < max_pages_to_scan:
                total_scans += 1
                print(f"[purchase] Quét page {current_page} để tìm sản phẩm {product_id} (Lần quét: {total_scans}/{max_pages_to_scan})")

                # Truy cập trang listing
                if current_page == 1:
                    listing_url = PRODUCT_LIST_URL
                    self.driver.get(listing_url)
                else:
                    self.driver.get(listing_url)

                time.sleep(2)
                self.close_popups()
                time.sleep(0.5)

                # Tìm tất cả các sản phẩm trong trang
                try:
                    # Thử nhiều selector khác nhau để tìm link sản phẩm
                    product_items = self.driver.find_elements(By.CSS_SELECTOR,
                                                              'ul.category-list li .detail p.name a, .category-list li .detail p.name a, '
                                                              '.category-list li p.name a, ul.category-list p.name a, '
                                                              'a[href*="/shopdetail"], a[href*="shopdetail.html"]')

                    # Lọc các link có text (tên sản phẩm)
                    valid_product_items = []
                    for item in product_items:
                        try:
                            text = item.text.strip()
                            href = item.get_attribute('href') or ''
                            if text and href and ('shopdetail' in href):
                                valid_product_items.append(item)
                        except:
                            continue

                    product_items = valid_product_items
                    print(f"[purchase] Tìm thấy {len(product_items)} sản phẩm trong page {current_page}")

                    for product_link in product_items:
                        try:
                            product_name = product_link.text
                            href = product_link.get_attribute('href')

                            # Kiểm tra xem product_id có trong tên sản phẩm không
                            if product_id and product_id in product_name:
                                print(f"[purchase] ✓ Tìm thấy sản phẩm: {product_name}")
                                product_found = True

                                # Lấy URL đầy đủ
                                if href.startswith('/'):
                                    product_detail_url = f"https://www.er-sports.com{href}"
                                elif href.startswith('http'):
                                    product_detail_url = href
                                else:
                                    product_detail_url = f"https://www.er-sports.com/{href}"

                                break
                        except Exception as e:
                            print(f"[purchase] Lỗi khi xử lý sản phẩm: {str(e)}")
                            continue

                    # Nếu không tìm thấy trong page này, thử tìm link "次の48件"
                    if not product_found:
                        try:
                            # Tìm link "次の48件" trong li.next
                            next_link = self.driver.find_element(By.CSS_SELECTOR, 'li.next a')
                            next_text = next_link.text

                            # Kiểm tra xem có phải link "次の48件" không
                            if "次の" in next_text or "»" in next_text:
                                next_href = next_link.get_attribute('href')
                                if next_href:
                                    # Chuẩn hóa URL
                                    if next_href.startswith('/'):
                                        next_href = f"https://www.er-sports.com{next_href}"

                                    # Trích xuất số page từ URL
                                    page_match = re.search(r'page=(\d+)', next_href)
                                    if page_match:
                                        next_page_num = int(page_match.group(1))
                                        if next_page_num > current_page:
                                            current_page = next_page_num
                                            listing_url = next_href
                                            print(f"[purchase] Chuyển sang page {current_page}")
                                            continue
                            else:
                                # Không tìm thấy link next hợp lệ, thử tăng page number
                                current_page += 1
                                if current_page <= max_pages_to_scan:
                                    separator = "&" if "?" in listing_url else "?"
                                    if "page=" not in listing_url:
                                        listing_url = f"{listing_url}{separator}page={current_page}"
                                    else:
                                        listing_url = re.sub(r'page=\d+', f'page={current_page}', listing_url)
                                    continue
                        except NoSuchElementException:
                            print(f"[purchase] Không tìm thấy link chuyển trang tiếp theo")
                            # Nếu không tìm thấy link next và đã quét hết, F5 và quét lại từ đầu
                            print(f"[purchase] Quét hết page, refresh và quét lại từ đầu")
                            self.driver.refresh()
                            time.sleep(2)
                            self.close_popups()
                            current_page = 1
                            listing_url = PRODUCT_LIST_URL
                            continue

                except Exception as e:
                    print(f"[purchase] Lỗi khi quét sản phẩm: {str(e)}")
                    # Nếu có lỗi, refresh và thử lại từ đầu
                    self.driver.refresh()
                    time.sleep(2)
                    self.close_popups()
                    current_page = 1
                    listing_url = PRODUCT_LIST_URL
                    continue

            # Nếu không tìm thấy sản phẩm sau khi quét hết
            if not product_found:
                result['error'] = f"Không tìm thấy sản phẩm có ID {product_id} sau khi quét {max_pages_to_scan} pages"
                return result

            # Đã tìm thấy sản phẩm, vào trang chi tiết
            print(f"[purchase] Vào trang chi tiết sản phẩm: {product_detail_url}")
            self.driver.get(product_detail_url)
            time.sleep(2)
            self.close_popups()
            time.sleep(0.5)

            # Tìm và click nút "カートへ入れる" (thêm vào giỏ hàng)
            print(f"[purchase] Tìm nút thêm vào giỏ hàng...")
            try:
                add_to_cart_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                '.item-basket-btn a.btn-basket, a[href*="JavaScript:send"][class*="btn-basket"]'))
                )

                print(f"[purchase] Tìm thấy nút thêm vào giỏ hàng, đang click...")
                try:
                    self.driver.execute_script("arguments[0].click();", add_to_cart_button)
                    print(f"[purchase] ✓ Đã click nút thêm vào giỏ hàng bằng JavaScript")
                except:
                    add_to_cart_button.click()
                    print(f"[purchase] ✓ Đã click nút thêm vào giỏ hàng bằng click thường")

                # Đợi một chút để JavaScript xử lý
                time.sleep(2)

                # Đợi cho đến khi URL thay đổi hoặc có dấu hiệu chuyển trang
                try:
                    WebDriverWait(self.driver, 10).until(
                        lambda d: "basket.html" in d.current_url or d.current_url != product_detail_url
                    )
                    print(f"[purchase] ✓ URL đã thay đổi, đang chuyển sang giỏ hàng...")
                except TimeoutException:
                    print(f"[purchase] Cảnh báo: URL chưa thay đổi sau khi click, nhưng vẫn tiếp tục...")
                    # Thử navigate trực tiếp nếu cần
                    if "basket.html" not in self.driver.current_url:
                        print(f"[purchase] Tự động chuyển sang trang giỏ hàng...")
                        self.driver.get("https://www.er-sports.com/shop/basket.html")
            except TimeoutException:
                result['error'] = "Không tìm thấy nút thêm vào giỏ hàng"
                return result

            # Đợi chuyển sang trang giỏ hàng
            print(f"[purchase] Đợi chuyển sang trang giỏ hàng...")
            WebDriverWait(self.driver, 15).until(
                lambda d: "basket.html" in d.current_url
            )
            # Đợi trang load hoàn toàn
            time.sleep(3)
            self.close_popups()
            time.sleep(1)

            # Đợi cho đến khi trang basket load xong (kiểm tra xem có table.basket không)
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'table.basket, .basket-wrap'))
                )
            except TimeoutException:
                print(f"[purchase] Cảnh báo: Không tìm thấy bảng giỏ hàng sau khi đợi")

            # Kiểm tra trong giỏ hàng có sản phẩm hay không
            print(f"[purchase] Kiểm tra giỏ hàng...")

            # Kiểm tra xem có thông báo "giỏ hàng trống" không
            page_source = self.driver.page_source
            is_empty = "買い物かごに商品がありません" in page_source or "カートに商品がありません" in page_source

            if is_empty:
                result['error'] = "Giỏ hàng trống, sản phẩm không được thêm vào"
                print(f"[purchase] ✗ Giỏ hàng trống")
                return result

            print(f"[purchase] ✓ Giỏ hàng có sản phẩm (không trống)")

            # Thử đếm số sản phẩm (nhưng không bắt buộc phải chính xác)
            try:
                # Tìm các hàng sản phẩm trong table.basket (loại trừ header và message trống)
                cart_rows = self.driver.find_elements(By.CSS_SELECTOR,
                                                      'table.basket tbody tr')

                # Lọc các hàng có sản phẩm (không phải header, không phải message trống)
                actual_items = []
                for row in cart_rows:
                    try:
                        row_text = row.text.strip()
                        # Loại trừ header và message trống
                        if (row_text and
                                "商品情報" not in row_text and
                                "数量" not in row_text and
                                "買い物かごに商品がありません" not in row_text and
                                "カートに商品がありません" not in row_text):
                            # Kiểm tra xem có input amount hoặc link sản phẩm không
                            has_amount_input = row.find_elements(By.CSS_SELECTOR,
                                                                 'input[type="text"][name*="amount"], input[type="number"][name*="amount"]')
                            has_product_link = row.find_elements(By.CSS_SELECTOR, 'a[href*="shopdetail"]')
                            if has_amount_input or has_product_link:
                                actual_items.append(row)
                    except:
                        pass

                item_count = len(actual_items)
                print(f"[purchase] Số sản phẩm trong giỏ hàng (ước tính): {item_count}")

                # Nếu đếm được ít nhất 1 sản phẩm, tiếp tục
                # Nếu đếm được 0 nhưng đã kiểm tra không trống ở trên (is_empty = False),
                # vẫn tiếp tục (có thể selector không đúng, nhưng có sản phẩm trong giỏ hàng)
                if item_count == 0:
                    print(f"[purchase] Cảnh báo: Không đếm được sản phẩm, nhưng giỏ hàng không trống, vẫn tiếp tục...")
            except Exception as e:
                print(f"[purchase] Cảnh báo: Không thể đếm sản phẩm: {str(e)}, nhưng vẫn tiếp tục...")

            # Tìm và click nút "購入手続きへ進む"
            print(f"[purchase] Tìm nút checkout...")
            try:
                checkout_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                '.btn-wrap-order a[href*="sslorder"], a.btn[href*="sslorder"], .btn-wrap-order a.btn'))
                )
            except TimeoutException:
                # Thử tìm bằng text
                try:
                    checkout_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH,
                                                    '//a[contains(text(), "購入手続きへ進む")]'))
                    )
                except TimeoutException:
                    result['error'] = "Không tìm thấy nút checkout"
                    return result

                # Kiểm tra xem nút có bị disable không (nếu disable, có thể là giỏ hàng trống)
                button_href = checkout_button.get_attribute('href')
                if button_href and 'alert' in button_href.lower():
                    result['error'] = "Nút checkout bị disable, giỏ hàng có thể trống"
                    return result

                print(f"[purchase] Tìm thấy nút checkout, đang click...")
                try:
                    self.driver.execute_script("arguments[0].click();", checkout_button)
                    time.sleep(3)
                except:
                    checkout_button.click()
                    time.sleep(3)

                print(f"[purchase] ✓ Đã click nút checkout")

            except TimeoutException as e:
                result['error'] = f"Không tìm thấy nút checkout: {str(e)}"
                return result
            except Exception as e:
                result['error'] = f"Lỗi khi xử lý nút checkout: {str(e)}"
                return result

            # Đợi chuyển sang trang checkout (có thể là step02 hoặc trang khác)
            print(f"[purchase] Đợi chuyển sang trang checkout...")
            WebDriverWait(self.driver, 15).until(
                lambda d: "checkout" in d.current_url or "order" in d.current_url
            )
            time.sleep(3)
            self.close_popups()
            time.sleep(0.5)

            # Tìm và click nút xác nhận đơn hàng "注文を確定する"
            print(f"[purchase] Tìm nút xác nhận đơn hàng...")
            try:
                confirm_button = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                'input[name="checkout"][type="button"], input.checkout-confirm[type="button"], '
                                                'input[value*="注文を確定"], input[value*="確定"]'))
                )

                print(f"[purchase] Tìm thấy nút xác nhận, đang click...")
                try:
                    self.driver.execute_script("arguments[0].click();", confirm_button)
                    time.sleep(3)
                except:
                    confirm_button.click()
                    time.sleep(3)

                print(f"[purchase] ✓ Đã click nút xác nhận đơn hàng")
            except TimeoutException:
                result['error'] = "Không tìm thấy nút xác nhận đơn hàng"
                return result

            # Đợi một chút để trang load
            time.sleep(3)

            # Kiểm tra thông báo thành công "ご注文ありがとうございました"
            print(f"[purchase] Kiểm tra kết quả đặt hàng...")
            page_source = self.driver.page_source

            if "ご注文ありがとうございました" in page_source:
                print(f"[purchase] ✓✓✓ Đặt hàng THÀNH CÔNG!")
                result['success'] = True
            else:
                result['error'] = "Không tìm thấy thông báo đặt hàng thành công"
                print(f"[purchase] ✗ Đặt hàng thất bại")

        except Exception as e:
            result['error'] = f"Lỗi không xác định: {str(e)}"
            print(f"[purchase] ✗ Lỗi: {str(e)}")
            import traceback
            print(f"[purchase] Traceback: {traceback.format_exc()}")

        return result

    def logout(self):
        """
        Đăng xuất khỏi tài khoản
        """
        try:
            if not self.driver or not self.is_logged_in:
                return True

            # Truy cập trang đăng xuất
            self.driver.get("https://www.er-sports.com/shop/logout.html")
            time.sleep(2)

            self.is_logged_in = False
            return True

        except Exception as e:
            print(f"Lỗi khi đăng xuất: {str(e)}")
            return False

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


class OpenVPNManager:
    """
    Class quản lý kết nối OpenVPN
    Sử dụng để thay đổi IP address bằng cách kết nối/disconnect VPN
    """

    def __init__(self, openvpn_path=None):
        """
        Khởi tạo OpenVPN Manager

        Args:
            openvpn_path (str): Đường dẫn đến OpenVPN executable
        """
        self.openvpn_path = openvpn_path or "C:\\Program Files\\OpenVPN\\bin\\openvpn.exe"
        self.current_connection = None
        self.config_files = []
        self.current_config_index = 0

    def load_config_files(self, config_files):
        """
        Nạp danh sách file config OpenVPN

        Args:
            config_files (list): List các đường dẫn đến file .ovpn
        """
        self.config_files = [f for f in config_files if os.path.exists(f)]

    def connect(self, config_file):
        """
        Kết nối VPN sử dụng config file

        Args:
            config_file (str): Đường dẫn đến file .ovpn

        Returns:
            bool: True nếu kết nối thành công
        """
        try:
            if not os.path.exists(config_file):
                print(f"File config không tồn tại: {config_file}")
                return False

            # Đóng kết nối cũ nếu có
            self.disconnect()

            # Kết nối OpenVPN với config file
            self.current_connection = subprocess.Popen(
                [self.openvpn_path, '--config', config_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Đợi kết nối thành công (tối đa 30 giây)
            time.sleep(5)

            # Kiểm tra xem process còn chạy không
            if self.current_connection and self.current_connection.poll() is None:
                return True
            else:
                return False

        except Exception as e:
            print(f"Lỗi khi kết nối VPN: {str(e)}")
            return False

    def disconnect(self):
        """
        Ngắt kết nối VPN hiện tại
        """
        try:
            if self.current_connection:
                self.current_connection.terminate()
                self.current_connection.wait(timeout=10)
                self.current_connection = None

            # Đảm bảo đóng tất cả OpenVPN processes
            subprocess.run(['taskkill', '/F', '/IM', 'openvpn.exe'],
                           capture_output=True)

            time.sleep(3)

        except Exception as e:
            print(f"Lỗi khi ngắt kết nối VPN: {str(e)}")

    def connect_random_japan(self):
        """
        Kết nối VPN random với một IP Nhật Bản

        Returns:
            str: Đường dẫn config file được sử dụng, None nếu thất bại
        """
        if not self.config_files:
            print("Không có config file nào được load")
            return None

        # Random một config file
        selected_config = random.choice(self.config_files)

        if self.connect(selected_config):
            return selected_config
        else:
            return None

    def connect_next_japan(self):
        """
        Kết nối VPN với IP Nhật Bản tiếp theo trong danh sách

        Returns:
            str: Đường dẫn config file được sử dụng, None nếu thất bại
        """
        if not self.config_files:
            print("Không có config file nào được load")
            return None

        # Lấy config file tiếp theo
        config_file = self.config_files[self.current_config_index % len(self.config_files)]
        self.current_config_index += 1

        if self.connect(config_file):
            return config_file
        else:
            return None


class ERSportsAutomationGUI:
    """
    Class chính cho giao diện đồ họa của ER Sports Automation Tool
    Sử dụng tkinter để tạo GUI với các tính năng:
    - Nhập danh sách tài khoản (60 accounts)
    - Nhập danh sách sản phẩm (60 products)
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
        self.vpn_manager = None
        self.openvpn_config_files = []

        # Biến đếm
        self.scan_count = 0
        self.success_count = 0
        self.failure_count = 0

        # Trạng thái mua hàng theo ngày
        self.purchased_today = set()
        self.purchased_date = datetime.now().strftime('%Y-%m-%d')

        # Queue để giao tiếp giữa threads
        self.log_queue = queue.Queue()

        # Thiết lập logging
        self.setup_logging()

        # Tạo giao diện
        self.create_widgets()

        # Load cấu hình đã lưu
        self.load_settings()

        # Bắt đầu kiểm tra log queue
        self.check_log_queue()

        # Lưu khi đóng app
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

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
        account_frame = ttk.LabelFrame(main_frame, text="Danh sách tài khoản (Tối đa 60)")
        account_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview cho tài khoản (chỉ còn Email, Password)
        columns = ('Email', 'Password')
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

        # Buttons cho tài khoản
        account_buttons_frame = ttk.Frame(account_input_frame)
        account_buttons_frame.grid(row=1, column=0, columnspan=4, pady=5)

        ttk.Button(account_buttons_frame, text="Thêm tài khoản", command=self.add_account).pack(side=tk.LEFT, padx=2)
        ttk.Button(account_buttons_frame, text="Xóa tài khoản", command=self.remove_account).pack(side=tk.LEFT, padx=2)
        ttk.Button(account_buttons_frame, text="Xóa tất cả", command=self.clear_accounts).pack(side=tk.LEFT, padx=2)
        ttk.Button(account_buttons_frame, text="Import JSON", command=self.import_accounts).pack(side=tk.LEFT, padx=2)
        ttk.Button(account_buttons_frame, text="Export JSON", command=self.export_accounts).pack(side=tk.LEFT, padx=2)

        # Frame cho sản phẩm
        product_frame = ttk.LabelFrame(main_frame, text="Danh sách sản phẩm (Tối đa 60)")
        product_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview cho sản phẩm (chỉ còn ID)
        product_columns = ('ID',)
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

        # Các trường nhập liệu cho sản phẩm (chỉ Product ID)
        ttk.Label(product_input_frame, text="Product ID:").grid(row=0, column=0, sticky=tk.W, padx=2)
        self.product_id_var = tk.StringVar()
        ttk.Entry(product_input_frame, textvariable=self.product_id_var, width=15).grid(row=0, column=1, padx=2)

        # Buttons cho sản phẩm
        product_buttons_frame = ttk.Frame(product_input_frame)
        product_buttons_frame.grid(row=1, column=0, columnspan=2, pady=5)

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

        ttk.Label(stats_grid, text="Số lần quét:", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky=tk.W,
                                                                                    padx=5)
        self.scan_count_label = ttk.Label(stats_grid, text="0", font=('Arial', 12), foreground='blue')
        self.scan_count_label.grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(stats_grid, text="Mua thành công:", font=('Arial', 12, 'bold')).grid(row=0, column=2, sticky=tk.W,
                                                                                       padx=5)
        self.success_count_label = ttk.Label(stats_grid, text="0", font=('Arial', 12), foreground='green')
        self.success_count_label.grid(row=0, column=3, sticky=tk.W, padx=5)

        ttk.Label(stats_grid, text="Mua thất bại:", font=('Arial', 12, 'bold')).grid(row=1, column=0, sticky=tk.W,
                                                                                     padx=5)
        self.failure_count_label = ttk.Label(stats_grid, text="0", font=('Arial', 12), foreground='red')
        self.failure_count_label.grid(row=1, column=1, sticky=tk.W, padx=5)

        ttk.Label(stats_grid, text="Tỷ lệ thành công:", font=('Arial', 12, 'bold')).grid(row=1, column=2, sticky=tk.W,
                                                                                         padx=5)
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

        self.stop_button = ttk.Button(buttons_frame, text="Dừng Automation", command=self.stop_automation,
                                      state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(buttons_frame, text="Reset Thống kê", command=self.reset_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Reset tài khoản đã mua hôm nay", command=self.reset_daily_purchases).pack(
            side=tk.LEFT, padx=5)
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
        ttk.Checkbutton(browser_settings, text="Chạy browser ở chế độ ẩn (Headless)", variable=self.headless_var).pack(
            anchor=tk.W)

        # Đường dẫn Chrome
        ttk.Label(browser_settings, text="Đường dẫn Chrome:").pack(anchor=tk.W)
        chrome_path_frame = ttk.Frame(browser_settings)
        chrome_path_frame.pack(fill=tk.X, pady=2)

        self.chrome_path_var = tk.StringVar(value="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
        ttk.Entry(chrome_path_frame, textvariable=self.chrome_path_var, width=60).pack(side=tk.LEFT, fill=tk.X,
                                                                                       expand=True)
        ttk.Button(chrome_path_frame, text="Chọn", command=self.browse_chrome_path).pack(side=tk.RIGHT, padx=5)

        # Frame cài đặt timing
        timing_frame = ttk.LabelFrame(settings_frame, text="Cài đặt Thời gian")
        timing_frame.pack(fill=tk.X, padx=5, pady=5)

        timing_settings = ttk.Frame(timing_frame)
        timing_settings.pack(fill=tk.X, padx=10, pady=10)

        # Delay giữa các tài khoản
        ttk.Label(timing_settings, text="Delay giữa các tài khoản (giây):").pack(anchor=tk.W)
        self.account_delay_var = tk.IntVar(value=5)
        ttk.Scale(timing_settings, from_=1, to=30, variable=self.account_delay_var, orient=tk.HORIZONTAL).pack(
            fill=tk.X)

        # Delay giữa các sản phẩm
        ttk.Label(timing_settings, text="Delay giữa các sản phẩm (giây):").pack(anchor=tk.W)
        self.product_delay_var = tk.IntVar(value=3)
        ttk.Scale(timing_settings, from_=1, to=20, variable=self.product_delay_var, orient=tk.HORIZONTAL).pack(
            fill=tk.X)

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
        ttk.Checkbutton(other_settings, text="Thử lại mua hàng thất bại", variable=self.retry_failed_var).pack(
            anchor=tk.W)

        # Max retries
        ttk.Label(other_settings, text="Số lần thử lại tối đa:").pack(anchor=tk.W)
        self.max_retries_var = tk.IntVar(value=3)
        ttk.Scale(other_settings, from_=1, to=10, variable=self.max_retries_var, orient=tk.HORIZONTAL).pack(fill=tk.X)

        # Frame cài đặt OpenVPN
        vpn_frame = ttk.LabelFrame(settings_frame, text="Cài đặt OpenVPN (Japan IP)")
        vpn_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        vpn_settings = ttk.Frame(vpn_frame)
        vpn_settings.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Enable OpenVPN
        self.enable_openvpn_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(vpn_settings, text="Sử dụng OpenVPN để fake IP Nhật Bản",
                        variable=self.enable_openvpn_var).pack(anchor=tk.W)

        # Đường dẫn OpenVPN
        ttk.Label(vpn_settings, text="Đường dẫn OpenVPN:").pack(anchor=tk.W, pady=(5, 2))
        openvpn_path_frame = ttk.Frame(vpn_settings)
        openvpn_path_frame.pack(fill=tk.X)

        self.openvpn_path_var = tk.StringVar(value="C:\\Program Files\\OpenVPN\\bin\\openvpn.exe")
        ttk.Entry(openvpn_path_frame, textvariable=self.openvpn_path_var, width=60).pack(side=tk.LEFT, fill=tk.X,
                                                                                         expand=True)
        ttk.Button(openvpn_path_frame, text="Chọn", command=self.browse_openvpn_path).pack(side=tk.RIGHT, padx=5)

        # Danh sách config files
        ttk.Label(vpn_settings, text="Danh sách file config OpenVPN (.ovpn):").pack(anchor=tk.W, pady=(10, 2))

        # Listbox cho config files
        config_list_frame = ttk.Frame(vpn_settings)
        config_list_frame.pack(fill=tk.BOTH, expand=True)

        config_scrollbar = ttk.Scrollbar(config_list_frame, orient=tk.VERTICAL)
        self.config_listbox = tk.Listbox(config_list_frame, height=6, yscrollcommand=config_scrollbar.set)
        self.config_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        config_scrollbar.config(command=self.config_listbox.yview)
        config_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons cho config files
        config_buttons_frame = ttk.Frame(vpn_settings)
        config_buttons_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(config_buttons_frame, text="Thêm file config", command=self.add_openvpn_config).pack(side=tk.LEFT,
                                                                                                        padx=2)
        ttk.Button(config_buttons_frame, text="Xóa file config", command=self.remove_openvpn_config).pack(side=tk.LEFT,
                                                                                                          padx=2)
        ttk.Button(config_buttons_frame, text="Xóa tất cả", command=self.clear_openvpn_configs).pack(side=tk.LEFT,
                                                                                                     padx=2)

        # OpenVPN mode
        ttk.Label(vpn_settings, text="Chế độ kết nối:").pack(anchor=tk.W, pady=(5, 2))
        self.openvpn_mode_var = tk.StringVar(value="sequential")
        ttk.Radiobutton(vpn_settings, text="Tuần tự (Sequential)", variable=self.openvpn_mode_var,
                        value="sequential").pack(anchor=tk.W)
        ttk.Radiobutton(vpn_settings, text="Ngẫu nhiên (Random)", variable=self.openvpn_mode_var,
                        value="random").pack(anchor=tk.W)

        # Nút lưu cấu hình thủ công
        ttk.Separator(settings_frame, orient='horizontal').pack(fill=tk.X, padx=5, pady=10)
        manual_save_frame = ttk.Frame(settings_frame)
        manual_save_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(manual_save_frame, text="💾 Lưu cấu hình thủ công",
                   command=lambda: (
                       self.save_settings(), self.log_message("Đã lưu cấu hình thủ công", "SUCCESS"))).pack(
            side=tk.LEFT,
            padx=5)

        ttk.Button(manual_save_frame, text="🔄 Load lại cấu hình",
                   command=lambda: (self.load_settings(), self.log_message("Đã load lại cấu hình", "INFO"))).pack(
            side=tk.LEFT, padx=5)

    def add_account(self):
        """
        Thêm tài khoản mới vào danh sách
        """
        if len(self.account_tree.get_children()) >= 60:
            messagebox.showwarning("Cảnh báo", "Chỉ được thêm tối đa 60 tài khoản!")
            return

        email = self.email_var.get().strip()
        password = self.password_var.get().strip()

        if not email or not password:
            messagebox.showerror("Lỗi", "Email và Password không được để trống!")
            return

        # Kiểm tra email đã tồn tại chưa
        for item in self.account_tree.get_children():
            if self.account_tree.item(item)['values'][0] == email:
                messagebox.showerror("Lỗi", "Email này đã tồn tại!")
                return

        # Thêm vào treeview
        self.account_tree.insert('', tk.END, values=(email, password))

        # Xóa các trường nhập liệu
        self.email_var.set("")
        self.password_var.set("")

        self.log_message(f"Đã thêm tài khoản: {email}", "INFO")

        # Auto-save nếu bật
        if self.auto_save_var.get():
            self.save_settings()

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

        # Auto-save nếu bật
        if self.auto_save_var.get():
            self.save_settings()

    def clear_accounts(self):
        """
        Xóa tất cả tài khoản
        """
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa tất cả tài khoản?"):
            self.account_tree.delete(*self.account_tree.get_children())
            self.log_message("Đã xóa tất cả tài khoản", "INFO")

            # Auto-save nếu bật
            if self.auto_save_var.get():
                self.save_settings()

    def add_product(self):
        """
        Thêm sản phẩm mới vào danh sách
        """
        if len(self.product_tree.get_children()) >= 60:
            messagebox.showwarning("Cảnh báo", "Chỉ được thêm tối đa 60 sản phẩm!")
            return

        product_id = self.product_id_var.get().strip()

        if not product_id:
            messagebox.showerror("Lỗi", "Product ID không được để trống!")
            return

        # Kiểm tra product ID đã tồn tại chưa
        for item in self.product_tree.get_children():
            if self.product_tree.item(item)['values'][0] == product_id:
                messagebox.showerror("Lỗi", "Product ID này đã tồn tại!")
                return

        # Thêm vào treeview
        self.product_tree.insert('', tk.END, values=(product_id,))

        # Xóa các trường nhập liệu
        self.product_id_var.set("")

        self.log_message(f"Đã thêm sản phẩm: {product_id}", "INFO")

        # Auto-save nếu bật
        if self.auto_save_var.get():
            self.save_settings()

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

        # Auto-save nếu bật
        if self.auto_save_var.get():
            self.save_settings()

    def clear_products(self):
        """
        Xóa tất cả sản phẩm
        """
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa tất cả sản phẩm?"):
            self.product_tree.delete(*self.product_tree.get_children())
            self.log_message("Đã xóa tất cả sản phẩm", "INFO")

            # Auto-save nếu bật
            if self.auto_save_var.get():
                self.save_settings()

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
                for account in accounts[:60]:  # Giới hạn 60 tài khoản
                    if isinstance(account, dict) and 'email' in account and 'password' in account:
                        self.account_tree.insert('', tk.END, values=(
                            account.get('email', ''),
                            account.get('password', '')
                        ))

                self.log_message(f"Đã import {len(accounts)} tài khoản từ {filename}", "SUCCESS")

                # Auto-save sau khi import
                if self.auto_save_var.get():
                    self.save_settings()

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
                'password': values[1]
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
                for product in products[:60]:  # Giới hạn 60 sản phẩm
                    if isinstance(product, dict) and 'productId' in product:
                        self.product_tree.insert('', tk.END, values=(
                            product.get('productId', '')
                        ))

                self.log_message(f"Đã import {len(products)} sản phẩm từ {filename}", "SUCCESS")

                # Auto-save sau khi import
                if self.auto_save_var.get():
                    self.save_settings()

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
                'productId': values[0]
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
                'password': values[1]
            })

        products = []
        for item in self.product_tree.get_children():
            values = self.product_tree.item(item)['values']
            products.append({
                'productId': values[0]
            })

        if not accounts:
            messagebox.showerror("Lỗi", "Vui lòng thêm ít nhất một tài khoản!")
            return

        if not products:
            messagebox.showerror("Lỗi", "Vui lòng thêm ít nhất một sản phẩm!")
            return

        # Kiểm tra cấu hình OpenVPN nếu bật
        if self.enable_openvpn_var.get():
            if not self.openvpn_config_files:
                messagebox.showerror("Lỗi", "Vui lòng thêm ít nhất một file config OpenVPN!")
                return

            if not os.path.exists(self.openvpn_path_var.get()):
                messagebox.showerror("Lỗi", "Đường dẫn OpenVPN không hợp lệ!")
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

        if self.vpn_manager:
            try:
                self.vpn_manager.disconnect()
                self.log_message("Đã ngắt kết nối VPN", "INFO")
            except Exception as e:
                self.log_message(f"Lỗi khi ngắt VPN: {str(e)}", "ERROR")

        # Cập nhật trạng thái UI
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        self.log_message("Đã dừng automation", "WARNING")

    def run_automation(self, accounts, products):
        """
        Chạy automation trong thread riêng với logic mới:
        - Kết nối OpenVPN (nếu bật)
        - Mỗi sản phẩm chỉ mua 1 lần
        - Nếu mua thành công: đổi IP và tài khoản
        - Nếu mua thất bại: giữ nguyên IP và tài khoản

        Args:
            accounts (list): Danh sách tài khoản
            products (list): Danh sách sản phẩm
        """
        try:
            # Khởi tạo OpenVPN manager nếu bật
            if self.enable_openvpn_var.get() and self.openvpn_config_files:
                self.vpn_manager = OpenVPNManager(self.openvpn_path_var.get())
                self.vpn_manager.load_config_files(self.openvpn_config_files)
                self.log_message("Đã khởi tạo OpenVPN Manager", "INFO")

            # Khởi tạo biến trạng thái
            current_account_index = 0
            current_account = None
            is_logged_in = False

            # Kết nối VPN đầu tiên (nếu bật)
            if self.vpn_manager and self.vpn_manager.config_files:
                if self.openvpn_mode_var.get() == "random":
                    self.vpn_manager.connect_random_japan()
                else:
                    self.vpn_manager.connect_next_japan()
                self.log_message("Đã kết nối VPN với IP Nhật Bản đầu tiên", "INFO")
                time.sleep(5)

            # Vòng lặp chính: chạy liên tục đến khi dừng hoặc hết tài khoản hợp lệ
            while self.is_running:
                # Đảm bảo ngày hiện tại; nếu qua ngày mới, tự làm sạch đánh dấu
                today_str = datetime.now().strftime('%Y-%m-%d')
                if self.purchased_date != today_str:
                    self.purchased_today.clear()
                    self.purchased_date = today_str
                    self.save_settings()

                # Tìm tài khoản kế tiếp chưa mua hôm nay
                found_account = False
                start_idx = current_account_index
                while current_account_index < len(accounts):
                    candidate = accounts[current_account_index]
                    if candidate['email'] not in self.purchased_today:
                        current_account = candidate
                        found_account = True
                        break
                    current_account_index += 1

                if not found_account:
                    self.log_message("Đã sử dụng hết tài khoản hợp lệ (đã mua hôm nay sẽ bị bỏ qua).", "WARNING")
                    break

                # Nếu chưa đăng nhập, đăng nhập vào tài khoản hiện tại
                if not is_logged_in or self.browser is None:
                    self.log_message(f"Đăng nhập với tài khoản: {current_account['email']}", "INFO")

                    # Khởi tạo browser
                    self.browser = BrowserAutomation(
                        headless=self.headless_var.get(),
                        chrome_path=self.chrome_path_var.get() if self.chrome_path_var.get() else None
                    )

                    if self.browser.login(current_account['email'], current_account['password']):
                        self.log_message(f"Đăng nhập thành công: {current_account['email']}", "SUCCESS")
                        is_logged_in = True
                    else:
                        self.log_message(f"Đăng nhập thất bại: {current_account['email']}", "ERROR")
                        # Đóng browser nếu có
                        if self.browser:
                            self.browser.close()
                            self.browser = None
                        is_logged_in = False
                        # Chuyển qua tài khoản tiếp theo
                        current_account_index += 1

                        # Đổi VPN nếu còn tài khoản
                        if self.vpn_manager and self.vpn_manager.config_files and current_account_index < len(accounts):
                            self.log_message("Đang đổi sang IP Nhật Bản mới...", "INFO")
                            self.vpn_manager.disconnect()
                            time.sleep(3)
                            if self.openvpn_mode_var.get() == "random":
                                self.vpn_manager.connect_random_japan()
                            else:
                                self.vpn_manager.connect_next_japan()
                            self.log_message("Đã kết nối VPN mới", "INFO")
                            time.sleep(5)
                        continue

                # Đã đăng nhập -> quét liên tục danh sách sản phẩm cho đến khi mua thành công hoặc bị dừng
                purchase_success = False
                while self.is_running and is_logged_in and not purchase_success:
                    for product_idx, product in enumerate(products):
                        if not self.is_running or not is_logged_in:
                            break

                        # Thử mua sản phẩm
                        self.scan_count += 1
                        self.update_stats()

                        product_name = product.get('productId')
                        self.log_message(
                            f"Đang thử mua sản phẩm ({product_idx + 1}/{len(products)}): {product_name}",
                            "INFO"
                        )

                        result = self.browser.purchase_product(PRODUCT_LIST_URL, product['productId'])

                        if result['success']:
                            purchase_success = True
                            self.success_count += 1
                            self.log_message(f"Mua thành công: {product_name}", "SUCCESS")
                            self.update_stats()

                            # Đánh dấu tài khoản đã mua hôm nay và lưu
                            self.purchased_today.add(current_account['email'])
                            self.purchased_date = today_str
                            self.save_settings()

                            # Đăng xuất và đóng browser trước khi đổi IP
                            try:
                                self.browser.logout()
                            except Exception:
                                pass
                            if self.browser:
                                self.browser.close()
                                self.browser = None
                            is_logged_in = False

                            # Chuyển tài khoản tiếp theo
                            current_account = None
                            current_account_index += 1

                            # Đổi VPN sang IP Nhật Bản khác (nếu bật) cho tài khoản kế tiếp
                            if self.vpn_manager and self.vpn_manager.config_files and current_account_index < len(
                                    accounts):
                                self.log_message("Đang đổi sang IP Nhật Bản mới...", "INFO")
                                self.vpn_manager.disconnect()
                                time.sleep(3)
                                if self.openvpn_mode_var.get() == "random":
                                    self.vpn_manager.connect_random_japan()
                                else:
                                    self.vpn_manager.connect_next_japan()
                                self.log_message("Đã kết nối VPN mới", "INFO")
                                time.sleep(5)

                            # Delay giữa các tài khoản
                            if self.account_delay_var.get() > 0:
                                time.sleep(self.account_delay_var.get())

                            break
                        else:
                            self.failure_count += 1
                            error_msg = result['error'] or "Lỗi không xác định"
                            self.log_message(f"Mua thất bại: {product_name} - {error_msg}", "ERROR")
                            self.update_stats()

                            # Giữ nguyên IP và tài khoản, tiếp tục sản phẩm tiếp theo
                            self.log_message(
                                "Mua thất bại -> Giữ nguyên IP và tài khoản, tiếp tục quét tiếp",
                                "INFO"
                            )
                            # Delay giữa các sản phẩm
                            if self.product_delay_var.get() > 0:
                                time.sleep(self.product_delay_var.get())

                    # Kết thúc một vòng quét toàn bộ danh sách -> lặp lại nếu chưa thành công
                    # Thêm một nhịp nghỉ ngắn để giảm tải
                    if not purchase_success and self.is_running and is_logged_in:
                        time.sleep(1)

            # Đóng browser và VPN nếu còn
            if self.browser:
                self.browser.close()
                self.browser = None

            if self.vpn_manager:
                self.vpn_manager.disconnect()
                self.log_message("Đã ngắt kết nối VPN", "INFO")

            self.log_message("Hoàn thành automation!", "SUCCESS")

        except Exception as e:
            self.log_message(f"Lỗi trong automation: {str(e)}", "ERROR")

        finally:
            # Đảm bảo đóng tất cả kết nối
            if self.browser:
                try:
                    self.browser.close()
                except:
                    pass

            if self.vpn_manager:
                try:
                    self.vpn_manager.disconnect()
                except:
                    pass

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

    def reset_daily_purchases(self):
        """
        Xóa đánh dấu các tài khoản đã mua thành công trong hôm nay
        """
        self.purchased_today.clear()
        self.purchased_date = datetime.now().strftime('%Y-%m-%d')
        self.save_settings()
        self.log_message("Đã reset danh sách tài khoản đã mua hôm nay", "INFO")

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
                'email': values[0]
            })

        # Thêm thông tin sản phẩm
        for item in self.product_tree.get_children():
            values = self.product_tree.item(item)['values']
            report['products'].append({
                'productId': values[0]
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

    def browse_openvpn_path(self):
        """
        Chọn đường dẫn OpenVPN
        """
        filename = filedialog.askopenfilename(
            title="Chọn OpenVPN executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )

        if filename:
            self.openvpn_path_var.set(filename)

    def add_openvpn_config(self):
        """
        Thêm file config OpenVPN
        """
        filename = filedialog.askopenfilename(
            title="Chọn file config OpenVPN",
            filetypes=[("OVPN files", "*.ovpn"), ("All files", "*.*")]
        )

        if filename and filename not in self.openvpn_config_files:
            self.openvpn_config_files.append(filename)
            self.config_listbox.insert(tk.END, os.path.basename(filename))
            self.log_message(f"Đã thêm config: {os.path.basename(filename)}", "INFO")

            # Auto-save nếu bật
            if self.auto_save_var.get():
                self.save_settings()

    def remove_openvpn_config(self):
        """
        Xóa file config OpenVPN được chọn
        """
        selection = self.config_listbox.curselection()
        if selection:
            index = selection[0]
            removed_file = self.openvpn_config_files.pop(index)
            self.config_listbox.delete(index)
            self.log_message(f"Đã xóa config: {os.path.basename(removed_file)}", "INFO")

            # Auto-save nếu bật
            if self.auto_save_var.get():
                self.save_settings()

    def clear_openvpn_configs(self):
        """
        Xóa tất cả file config OpenVPN
        """
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa tất cả config?"):
            self.openvpn_config_files.clear()
            self.config_listbox.delete(0, tk.END)
            self.log_message("Đã xóa tất cả config OpenVPN", "INFO")

            # Auto-save nếu bật
            if self.auto_save_var.get():
                self.save_settings()

    def save_settings(self):
        """
        Lưu tất cả cấu hình vào file
        """
        try:
            settings = {
                'accounts': [],
                'products': [],
                'chrome_path': self.chrome_path_var.get(),
                'headless': self.headless_var.get(),
                'account_delay': self.account_delay_var.get(),
                'product_delay': self.product_delay_var.get(),
                'auto_save': self.auto_save_var.get(),
                'retry_failed': self.retry_failed_var.get(),
                'max_retries': self.max_retries_var.get(),
                'enable_openvpn': self.enable_openvpn_var.get(),
                'openvpn_path': self.openvpn_path_var.get(),
                'openvpn_configs': self.openvpn_config_files,
                'openvpn_mode': self.openvpn_mode_var.get(),
                'purchased_today': list(self.purchased_today),
                'purchased_date': self.purchased_date,
            }

            # Lưu tài khoản (email, password)
            for item in self.account_tree.get_children():
                values = self.account_tree.item(item)['values']
                settings['accounts'].append({
                    'email': values[0],
                    'password': values[1]
                })

            # Lưu sản phẩm (chỉ productId)
            for item in self.product_tree.get_children():
                values = self.product_tree.item(item)['values']
                settings['products'].append({
                    'productId': values[0]
                })

            # Tìm config_dir - hỗ trợ cả khi chạy từ source và từ .exe
            if getattr(sys, 'frozen', False):
                # Chạy từ .exe
                base_path = os.path.dirname(sys.executable)
            else:
                # Chạy từ source
                base_path = os.path.dirname(__file__)

            config_dir = os.path.join(base_path, 'config')
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)

            settings_file = os.path.join(config_dir, 'settings.json')
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Lỗi khi lưu cấu hình: {str(e)}")

    def load_settings(self):
        """
        Load cấu hình từ file
        """
        try:
            # Tìm config_dir - hỗ trợ cả khi chạy từ source và từ .exe
            if getattr(sys, 'frozen', False):
                # Chạy từ .exe
                base_path = os.path.dirname(sys.executable)
            else:
                # Chạy từ source
                base_path = os.path.dirname(__file__)

            config_dir = os.path.join(base_path, 'config')
            settings_file = os.path.join(config_dir, 'settings.json')

            if not os.path.exists(settings_file):
                return

            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # Load tài khoản
            if 'accounts' in settings:
                for account in settings['accounts']:
                    if len(self.account_tree.get_children()) < 60:
                        self.account_tree.insert('', tk.END, values=(
                            account.get('email', ''),
                            account.get('password', '')
                        ))

            # Load sản phẩm
            if 'products' in settings:
                for product in settings['products']:
                    if len(self.product_tree.get_children()) < 60:
                        self.product_tree.insert('', tk.END, values=(
                            product.get('productId', '')
                        ))

            # Load cài đặt
            if 'chrome_path' in settings:
                self.chrome_path_var.set(settings.get('chrome_path', ''))

            if 'headless' in settings:
                self.headless_var.set(settings.get('headless', False))

            if 'account_delay' in settings:
                self.account_delay_var.set(settings.get('account_delay', 5))

            if 'product_delay' in settings:
                self.product_delay_var.set(settings.get('product_delay', 3))

            if 'auto_save' in settings:
                self.auto_save_var.set(settings.get('auto_save', True))

            if 'retry_failed' in settings:
                self.retry_failed_var.set(settings.get('retry_failed', True))

            if 'max_retries' in settings:
                self.max_retries_var.set(settings.get('max_retries', 3))

            # Load OpenVPN settings
            if 'enable_openvpn' in settings:
                self.enable_openvpn_var.set(settings.get('enable_openvpn', False))

            if 'openvpn_path' in settings:
                self.openvpn_path_var.set(settings.get('openvpn_path', ''))

            if 'openvpn_mode' in settings:
                self.openvpn_mode_var.set(settings.get('openvpn_mode', 'sequential'))

            if 'openvpn_configs' in settings:
                self.openvpn_config_files = [c for c in settings['openvpn_configs'] if os.path.exists(c)]
                for config in self.openvpn_config_files:
                    self.config_listbox.insert(tk.END, os.path.basename(config))

            # Load đánh dấu tài khoản đã mua hôm nay
            today_str = datetime.now().strftime('%Y-%m-%d')
            saved_date = settings.get('purchased_date', today_str)
            if saved_date == today_str:
                self.purchased_today = set(settings.get('purchased_today', []))
            else:
                self.purchased_today = set()
            self.purchased_date = today_str

            self.log_message("Đã load cấu hình đã lưu", "INFO")

        except Exception as e:
            print(f"Lỗi khi load cấu hình: {str(e)}")

    def on_closing(self):
        """
        Xử lý khi đóng app
        """
        if self.is_running:
            if messagebox.askokcancel("Thoát", "Automation đang chạy. Bạn có chắc muốn thoát?"):
                self.stop_automation()
                # Đợi một chút để cleanup
                time.sleep(1)
                # Lưu settings
                self.save_settings()
                self.root.destroy()
        else:
            # Lưu settings trước khi thoát
            self.save_settings()
            self.root.destroy()

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