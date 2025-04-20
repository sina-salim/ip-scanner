#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import socket
import subprocess
import threading
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext, font
    import ipaddress
except ImportError:
    print("لطفاً کتابخانه‌های مورد نیاز را نصب کنید:")
    print("pip install tk")
    sys.exit(1)

def get_local_ip():
    """گرفتن آدرس IP لوکال دستگاه کاربر"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return None

def ping_ip(ip):
    """پینگ کردن یک آدرس IP برای بررسی فعال بودن آن"""
    try:
        if sys.platform.startswith('win'):
            # دستور پینگ در ویندوز
            output = subprocess.run(['ping', '-n', '1', '-w', '500', ip], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE,
                                text=True,
                                timeout=1)
        else:
            # دستور پینگ در لینوکس/مک
            output = subprocess.run(['ping', '-c', '1', '-W', '1', ip], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE,
                                text=True,
                                timeout=1)
        
        return output.returncode == 0
    except (subprocess.SubprocessError, subprocess.TimeoutExpired):
        return False

# تعریف رنگ‌های تم تاریک
DARK_BG = "#1E1E2D"
DARKER_BG = "#151521"
ACCENT_COLOR = "#6366F1"
ACCENT_HOVER = "#4F46E5"
TEXT_COLOR = "#F1F1F3"
SECONDARY_TEXT = "#A1A1A5"
SUCCESS_COLOR = "#0EA5E9"
WARNING_COLOR = "#F59E0B"
DANGER_COLOR = "#EF4444"
BORDER_COLOR = "#2D2D3F"
PANEL_BG = "#2A2A3C"
CARD_BG = "#252538"

class DarkTheme:
    def __init__(self):
        # تنظیمات استایل برای تم تاریک
        self.style = ttk.Style()
        self.configure_style()
    
    def configure_style(self):
        # پیکربندی استایل تم تاریک
        self.style.theme_use('alt')  # استفاده از تم پایه alt
        
        # استایل فریم اصلی
        self.style.configure('TFrame', background=DARK_BG)
        
        # استایل لیبل‌ها
        self.style.configure('TLabel', background=DARK_BG, foreground=TEXT_COLOR, font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), foreground=TEXT_COLOR)
        self.style.configure('SubHeader.TLabel', font=('Segoe UI', 12), foreground=SECONDARY_TEXT)
        
        # استایل دکمه‌ها
        self.style.configure('TButton', 
                        background=ACCENT_COLOR, 
                        foreground=TEXT_COLOR, 
                        borderwidth=0,
                        focusthickness=3,
                        focuscolor=ACCENT_COLOR,
                        font=('Segoe UI', 10))
        self.style.map('TButton',
                   background=[('active', ACCENT_HOVER), ('disabled', DARKER_BG)],
                   foreground=[('disabled', SECONDARY_TEXT)])
        
        # استایل ورودی‌ها
        self.style.configure('TEntry', 
                        fieldbackground=DARKER_BG, 
                        foreground=TEXT_COLOR, 
                        insertcolor=TEXT_COLOR,
                        bordercolor=BORDER_COLOR,
                        lightcolor=ACCENT_COLOR,
                        darkcolor=ACCENT_COLOR)
        
        # استایل اسپین باکس
        self.style.configure('TSpinbox', 
                        fieldbackground=DARKER_BG, 
                        foreground=TEXT_COLOR, 
                        insertcolor=TEXT_COLOR,
                        bordercolor=BORDER_COLOR,
                        lightcolor=ACCENT_COLOR,
                        darkcolor=ACCENT_COLOR,
                        arrowcolor=TEXT_COLOR)
        
        # استایل درخت نمایش
        self.style.configure("Treeview", 
                        background=DARKER_BG, 
                        foreground=TEXT_COLOR, 
                        fieldbackground=DARKER_BG,
                        bordercolor=BORDER_COLOR)
        self.style.configure("Treeview.Heading", 
                        background=PANEL_BG, 
                        foreground=TEXT_COLOR, 
                        font=('Segoe UI', 10, 'bold'),
                        relief='flat')
        self.style.map('Treeview',
                   background=[('selected', ACCENT_COLOR)],
                   foreground=[('selected', TEXT_COLOR)])
        
        # استایل نوار پیشرفت
        self.style.configure("Horizontal.TProgressbar", 
                        troughcolor=DARKER_BG, 
                        background=SUCCESS_COLOR, 
                        bordercolor=BORDER_COLOR)
        
        # استایل برای فریم‌های عنوان‌دار
        self.style.configure('TLabelframe', 
                        background=DARK_BG, 
                        bordercolor=BORDER_COLOR)
        self.style.configure('TLabelframe.Label', 
                        background=DARK_BG, 
                        foreground=TEXT_COLOR,
                        font=('Segoe UI', 11, 'bold'))
        
        # استایل اسکرول‌بار
        self.style.configure('TScrollbar', 
                        background=DARK_BG, 
                        troughcolor=DARKER_BG, 
                        bordercolor=BORDER_COLOR,
                        arrowcolor=TEXT_COLOR)

class IPScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IP Scanner | Dark Theme")
        self.root.geometry("850x650")
        self.root.resizable(True, True)
        self.root.configure(bg=DARK_BG)  # تنظیم رنگ پس‌زمینه اصلی
        
        # برای ویندوز: تغییر رنگ نوار عنوان
        try:
            from ctypes import windll
            self.root.update()
            HWND = windll.user32.GetParent(self.root.winfo_id())
            DWMWA_CAPTION_COLOR = 35
            windll.dwmapi.DwmSetWindowAttribute(HWND, DWMWA_CAPTION_COLOR, 
                                              byref(c_int(int(DARK_BG.replace('#', '0x'), 16))), 
                                              sizeof(c_int))
        except:
            pass  # در صورت عدم پشتیبانی، نادیده بگیرید
        
        # اعمال تم تاریک
        self.theme = DarkTheme()
        
        # متغیرهای برنامه
        self.active_ips = []
        self.scan_thread = None
        self.is_scanning = False
        self.local_ip = get_local_ip() or "127.0.0.1"
        self.ip_base = '.'.join(self.local_ip.split('.')[:3])
        
        # ایجاد ساختار رابط کاربری
        self.setup_ui()
        
        # وضعیت اولیه
        self.log("برنامه اسکنر IP آماده است. لطفاً پارامترهای اسکن را تنظیم کنید و روی 'شروع اسکن' کلیک کنید.")
    
    def setup_ui(self):
        """ایجاد رابط کاربری برنامه با تم تاریک"""
        # فونت‌های مورد استفاده
        header_font = font.Font(family="Segoe UI", size=15, weight="bold")
        subheader_font = font.Font(family="Segoe UI", size=11)
        
        # فریم اصلی
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ایجاد هدر با عنوان برنامه
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # هدر جذاب
        header_bg = tk.Frame(header_frame, bg=CARD_BG, padx=15, pady=15)
        header_bg.pack(fill=tk.X, pady=(0, 15))
        
        header_content = tk.Frame(header_bg, bg=CARD_BG)
        header_content.pack(fill=tk.X)
        
        # لوگو یا آیکون (به صورت متنی)
        logo_frame = tk.Frame(header_content, bg=CARD_BG, padx=10, pady=5)
        logo_frame.pack(side=tk.RIGHT)
        
        network_icon = tk.Label(logo_frame, text="🌐", font=font.Font(size=24), bg=CARD_BG, fg=SUCCESS_COLOR)
        network_icon.pack(side=tk.RIGHT)
        
        title_frame = tk.Frame(header_content, bg=CARD_BG, padx=10)
        title_frame.pack(side=tk.RIGHT)
        
        title_label = tk.Label(title_frame, text="اسکنر شبکه‌های IP", font=header_font, 
                            bg=CARD_BG, fg=TEXT_COLOR)
        title_label.pack(anchor=tk.E)
        
        subtitle_label = tk.Label(title_frame, text="جستجو و مدیریت دستگاه‌های فعال در شبکه", 
                              font=subheader_font, bg=CARD_BG, fg=SECONDARY_TEXT)
        subtitle_label.pack(anchor=tk.E)
        
        # اطلاعات IP محلی
        local_ip_frame = tk.Frame(header_content, bg=CARD_BG)
        local_ip_frame.pack(side=tk.LEFT, padx=10)
        
        local_ip_label = tk.Label(local_ip_frame, text=f"IP محلی: {self.local_ip}", 
                              font=subheader_font, bg=CARD_BG, fg=TEXT_COLOR)
        local_ip_label.pack(anchor=tk.W)
        
        # ایجاد فریم دو ستونه
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # ستون سمت راست برای تنظیمات و کنترل‌ها
        right_column = ttk.Frame(content_frame)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0), expand=False)
        
        # ستون سمت چپ برای نتایج و لاگ
        left_column = ttk.Frame(content_frame)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # === بخش تنظیمات (ستون راست) ===
        settings_frame = ttk.LabelFrame(right_column, text="تنظیمات اسکن", padding=15)
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        # ایجاد یک کارت گرافیکی برای تنظیمات
        settings_card = tk.Frame(settings_frame, bg=CARD_BG, highlightbackground=BORDER_COLOR, 
                             highlightthickness=1, padx=15, pady=10)
        settings_card.pack(fill=tk.X, pady=5)
        
        # کانتینر برای محدود کردن عرض
        settings_container = ttk.Frame(settings_card)
        settings_container.pack(fill=tk.X)
        
        # آدرس شبکه
        network_frame = tk.Frame(settings_container, bg=CARD_BG)
        network_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(network_frame, text="آدرس شبکه:", bg=CARD_BG, fg=TEXT_COLOR, 
             font=('Segoe UI', 10)).pack(side=tk.RIGHT, padx=(0, 5))
        
        self.network_var = tk.StringVar(value=self.ip_base)
        network_entry = tk.Entry(network_frame, textvariable=self.network_var, width=16, justify='left',
                             bg=DARKER_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                             relief='flat', highlightbackground=BORDER_COLOR, highlightthickness=1)
        network_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # محدوده اسکن
        range_frame = tk.Frame(settings_container, bg=CARD_BG)
        range_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(range_frame, text="محدوده اسکن:", bg=CARD_BG, fg=TEXT_COLOR,
             font=('Segoe UI', 10)).pack(side=tk.RIGHT, padx=(0, 5))
        
        range_input_frame = tk.Frame(range_frame, bg=CARD_BG)
        range_input_frame.pack(side=tk.LEFT)
        
        self.start_range = tk.IntVar(value=1)
        tk.Entry(range_input_frame, textvariable=self.start_range, width=5,
             bg=DARKER_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
             relief='flat', highlightbackground=BORDER_COLOR, highlightthickness=1).pack(side=tk.RIGHT, padx=2)
        
        tk.Label(range_input_frame, text="تا", bg=CARD_BG, fg=TEXT_COLOR).pack(side=tk.RIGHT, padx=5)
        
        self.end_range = tk.IntVar(value=254)
        tk.Entry(range_input_frame, textvariable=self.end_range, width=5,
             bg=DARKER_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
             relief='flat', highlightbackground=BORDER_COLOR, highlightthickness=1).pack(side=tk.RIGHT, padx=2)
        
        # تعداد تردها
        thread_frame = tk.Frame(settings_container, bg=CARD_BG)
        thread_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(thread_frame, text="تعداد تِرِد‌ها:", bg=CARD_BG, fg=TEXT_COLOR,
             font=('Segoe UI', 10)).pack(side=tk.RIGHT, padx=(0, 5))
        
        self.threads_var = tk.IntVar(value=20)
        threads_spin = tk.Spinbox(thread_frame, from_=1, to=50, textvariable=self.threads_var, width=5,
                             bg=DARKER_BG, fg=TEXT_COLOR, buttonbackground=PANEL_BG,
                             relief='flat', highlightbackground=BORDER_COLOR, highlightthickness=1)
        threads_spin.pack(side=tk.LEFT, padx=5)
        
        # پنل آمار در ستون راست
        stats_frame = ttk.LabelFrame(right_column, text="آمار اسکن", padding=15)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        # ایجاد یک کارت گرافیکی برای آمار
        stats_card = tk.Frame(stats_frame, bg=CARD_BG, highlightbackground=BORDER_COLOR, 
                          highlightthickness=1, padx=15, pady=10)
        stats_card.pack(fill=tk.X, pady=5)
        
        # کانتینر برای محدود کردن عرض
        stats_container = tk.Frame(stats_card, bg=CARD_BG)
        stats_container.pack(fill=tk.X)
        
        # وضعیت فعلی
        status_frame = tk.Frame(stats_container, bg=CARD_BG)
        status_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(status_frame, text="وضعیت:", bg=CARD_BG, fg=TEXT_COLOR,
             font=('Segoe UI', 10)).pack(side=tk.RIGHT, padx=(0, 5))
        self.status_var = tk.StringVar(value="آماده برای اسکن")
        tk.Label(status_frame, textvariable=self.status_var, bg=CARD_BG, fg=TEXT_COLOR).pack(side=tk.LEFT)
        
        # تعداد IP های فعال
        active_frame = tk.Frame(stats_container, bg=CARD_BG)
        active_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(active_frame, text="IP‌های فعال:", bg=CARD_BG, fg=TEXT_COLOR,
             font=('Segoe UI', 10)).pack(side=tk.RIGHT, padx=(0, 5))
        self.active_count_var = tk.StringVar(value="0")
        tk.Label(active_frame, textvariable=self.active_count_var, bg=CARD_BG, fg=SUCCESS_COLOR,
             font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        
        # زمان اسکن
        time_frame = tk.Frame(stats_container, bg=CARD_BG)
        time_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(time_frame, text="زمان اسکن:", bg=CARD_BG, fg=TEXT_COLOR,
             font=('Segoe UI', 10)).pack(side=tk.RIGHT, padx=(0, 5))
        self.scan_time_var = tk.StringVar(value="00:00:00")
        tk.Label(time_frame, textvariable=self.scan_time_var, bg=CARD_BG, fg=TEXT_COLOR,
             font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        
        # دکمه‌های کنترل
        control_frame = ttk.Frame(right_column, padding=5)
        control_frame.pack(fill=tk.X, pady=5)
        
        # ایجاد دکمه‌های زیبا با آیکون
        # دکمه شروع اسکن
        scan_button_frame = tk.Frame(control_frame, bg=ACCENT_COLOR, padx=5, pady=5)
        scan_button_frame.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        
        self.scan_button = tk.Button(scan_button_frame, text="▶ شروع اسکن", 
                                 command=self.start_scan,
                                 font=('Segoe UI', 10, 'bold'),
                                 bg=ACCENT_COLOR, fg=TEXT_COLOR,
                                 activebackground=ACCENT_HOVER, 
                                 activeforeground=TEXT_COLOR,
                                 relief='flat', bd=0)
        self.scan_button.pack(fill=tk.BOTH, expand=True)
        
        # دکمه توقف اسکن
        stop_button_frame = tk.Frame(control_frame, bg=DANGER_COLOR, padx=5, pady=5)
        stop_button_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.stop_button = tk.Button(stop_button_frame, text="■ توقف اسکن", 
                                 command=self.stop_scan,
                                 font=('Segoe UI', 10, 'bold'),
                                 bg=DANGER_COLOR, fg=TEXT_COLOR,
                                 activebackground="#D32F2F", 
                                 activeforeground=TEXT_COLOR,
                                 relief='flat', bd=0,
                                 state=tk.DISABLED)
        self.stop_button.pack(fill=tk.BOTH, expand=True)
        
        # === بخش نتایج و لاگ (ستون چپ) ===
        
        # نوار پیشرفت
        progress_frame = ttk.Frame(left_column)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X)
        
        # جدول نتایج
        results_frame = ttk.LabelFrame(left_column, text="نتایج اسکن", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # ایجاد یک کارت گرافیکی برای جدول نتایج
        results_card = tk.Frame(results_frame, bg=CARD_BG, highlightbackground=BORDER_COLOR, 
                            highlightthickness=1, padx=5, pady=5)
        results_card.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # ساخت جدول
        results_tree_frame = tk.Frame(results_card, bg=CARD_BG)
        results_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ip", "hostname", "status")
        self.results_tree = ttk.Treeview(results_tree_frame, columns=columns, show="headings")
        
        # تعریف ستون‌ها
        self.results_tree.heading("ip", text="آدرس IP")
        self.results_tree.heading("hostname", text="نام میزبان")
        self.results_tree.heading("status", text="وضعیت")
        
        self.results_tree.column("ip", width=150)
        self.results_tree.column("hostname", width=250)
        self.results_tree.column("status", width=100)
        
        # تنظیم رنگ و استایل برای تگ‌های مختلف
        self.results_tree.tag_configure("active", background="#1E293B", foreground=SUCCESS_COLOR)
        self.results_tree.tag_configure("inactive", background=DARKER_BG, foreground=SECONDARY_TEXT)
        
        # اسکرول بار برای جدول
        tree_scroll = ttk.Scrollbar(results_tree_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=tree_scroll.set)
        
        # قرار دادن جدول و اسکرول بار
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # محل نمایش لاگ
        log_frame = ttk.LabelFrame(left_column, text="گزارش فعالیت", padding=10)
        log_frame.pack(fill=tk.X, pady=(0, 0))
        
        # ایجاد یک کارت گرافیکی برای گزارش‌ها
        log_card = tk.Frame(log_frame, bg=CARD_BG, highlightbackground=BORDER_COLOR, 
                        highlightthickness=1, padx=5, pady=5)
        log_card.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_card, wrap=tk.WORD, height=7)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.configure(
            background=DARKER_BG,
            foreground=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            relief=tk.FLAT,
            font=('Consolas', 10),
            padx=5,
            pady=5
        )
        
        # افزودن نوار وضعیت در پایین پنجره اصلی (خارج از main_frame)
        status_bar = tk.Frame(self.root, bg=DARK_BG, height=30)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        status_bar.pack_propagate(False)  # ثابت نگه داشتن ارتفاع
        
        # خط جداکننده بالای نوار وضعیت
        separator = tk.Frame(self.root, height=1, bg=BORDER_COLOR)
        separator.pack(side=tk.BOTTOM, fill=tk.X)
        
        # بخش طراح در سمت چپ نوار وضعیت
        designer_font = font.Font(family='Courier New', size=9, weight='bold')
        designer_label = tk.Label(
            status_bar, 
            text="Designed by Sina-Salim", 
            font=designer_font, 
            bg=DARK_BG, 
            fg=SUCCESS_COLOR,
            padx=10,
            pady=5
        )
        designer_label.pack(side=tk.LEFT)
        
        # نسخه برنامه در سمت راست نوار وضعیت
        version_label = tk.Label(
            status_bar, 
            text="نسخه ۱.۰", 
            font=('Segoe UI', 9), 
            bg=DARK_BG, 
            fg=TEXT_COLOR,
            padx=10,
            pady=5
        )
        version_label.pack(side=tk.RIGHT)

    def log(self, message):
        """افزودن پیام به محل نمایش لاگ"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def start_scan(self):
        """شروع عملیات اسکن"""
        if self.is_scanning:
            return
        
        # پاک‌سازی نتایج قبلی
        self.results_tree.delete(*self.results_tree.get_children())
        self.active_ips = []
        
        # بررسی اعتبار مقادیر
        try:
            network = self.network_var.get()
            start_range = self.start_range.get()
            end_range = self.end_range.get()
            threads = self.threads_var.get()
            
            if not (1 <= start_range <= 254 and 1 <= end_range <= 254 and start_range <= end_range):
                raise ValueError("محدوده IP باید بین 1 تا 254 باشد")
                
            if not (1 <= threads <= 50):
                raise ValueError("تعداد تِرِد‌ها باید بین 1 تا 50 باشد")
                
            # بررسی اعتبار آدرس شبکه
            try:
                if not network.count('.') == 3:
                    network = network.rstrip('.')
                    if network.count('.') < 2:
                        raise ValueError("فرمت آدرس شبکه نامعتبر است")
                    
                    # اگر کاربر فقط دو یا سه بخش اول را وارد کرده باشد
                    parts = network.split('.')
                    while len(parts) < 3:
                        parts.append('0')
                    network = '.'.join(parts)
                
                # تست اعتبار آدرس IP
                test_ip = f"{network}.1"
                ipaddress.ip_address(test_ip)
            except:
                raise ValueError("آدرس شبکه نامعتبر است")
                
        except ValueError as e:
            messagebox.showerror("خطای ورودی", str(e))
            return
            
        # تغییر وضعیت دکمه‌ها
        self.scan_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # تنظیم وضعیت اسکن
        self.is_scanning = True
        self.progress_var.set(0)
        self.status_var.set("در حال اسکن...")
        self.active_count_var.set("0")
        
        # شروع تایمر اسکن
        self.scan_start_time = datetime.now()
        self.update_scan_time()
        
        self.log(f"شروع اسکن شبکه {network}.{start_range} تا {network}.{end_range}")
        self.log(f"تعداد تِرِد‌ها: {threads}")
        
        # شروع اسکن در یک ترد جداگانه
        self.scan_thread = threading.Thread(
            target=self.scan_network, 
            args=(network, start_range, end_range, threads)
        )
        self.scan_thread.daemon = True
        self.scan_thread.start()
    
    def update_scan_time(self):
        """به‌روزرسانی زمان اسکن"""
        if self.is_scanning:
            elapsed = datetime.now() - self.scan_start_time
            # تبدیل به ساعت:دقیقه:ثانیه
            hours, remainder = divmod(elapsed.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            self.scan_time_var.set(time_str)
            
            # فراخوانی مجدد این تابع هر ثانیه
            self.root.after(1000, self.update_scan_time)
        else:
            # پایان اسکن، نمایش زمان نهایی
            elapsed = datetime.now() - self.scan_start_time
            hours, remainder = divmod(elapsed.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            self.scan_time_var.set(time_str)
    
    def stop_scan(self):
        """توقف عملیات اسکن"""
        if not self.is_scanning:
            return
            
        self.is_scanning = False
        self.status_var.set("اسکن متوقف شد")
        self.log("اسکن توسط کاربر متوقف شد")
        
        # تغییر وضعیت دکمه‌ها
        self.scan_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def scan_ip(self, ip, result_list):
        """اسکن یک آدرس IP"""
        if not self.is_scanning:
            return
            
        is_active = ping_ip(ip)
        status = "فعال" if is_active else "غیرفعال"
        
        hostname = "ناشناس"
        if is_active:
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except socket.herror:
                hostname = "ناشناس"
                
            result_list.append((ip, hostname))
            
            # نمایش در رابط کاربری (از طریق یک تابع امن برای ترد)
            self.root.after(0, lambda: self.add_result_to_ui(ip, hostname, status))
            # به‌روزرسانی شمارنده IP‌های فعال
            self.root.after(0, lambda: self.active_count_var.set(str(len(result_list))))
    
    def add_result_to_ui(self, ip, hostname, status):
        """افزودن نتیجه به رابط کاربری"""
        # تعیین تگ برای ردیف جدید
        tag = "active" if status == "فعال" else "inactive"
        
        # افزودن به جدول
        item_id = self.results_tree.insert("", tk.END, values=(ip, hostname, status), tags=(tag,))
        
        # اگر فعال است، آن را لاگ کن
        if status == "فعال":
            self.log(f"IP فعال یافت شد: {ip} ({hostname})")
    
    def update_progress(self, value):
        """به‌روزرسانی نوار پیشرفت"""
        self.progress_var.set(value)
    
    def scan_network(self, network, start, end, thread_count):
        """اسکن شبکه با استفاده از چند ترد"""
        try:
            total_ips = end - start + 1
            completed = 0
            
            # تقسیم کار بین تردها
            ip_chunks = (end - start + 1) // thread_count
            thread_ranges = []
            
            for i in range(thread_count):
                chunk_start = start + i * ip_chunks
                chunk_end = start + (i + 1) * ip_chunks - 1 if i < thread_count - 1 else end
                thread_ranges.append((chunk_start, chunk_end))
            
            # استفاده از ThreadPoolExecutor برای اجرای همزمان اسکن
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                futures = []
                
                for t_start, t_end in thread_ranges:
                    for i in range(t_start, t_end + 1):
                        if not self.is_scanning:
                            break
                            
                        ip = f"{network}.{i}"
                        futures.append(
                            executor.submit(self.scan_ip, ip, self.active_ips)
                        )
                        
                        # به‌روزرسانی پیشرفت
                        completed += 1
                        progress = (completed / total_ips) * 100
                        self.root.after(0, lambda p=progress: self.update_progress(p))
                        
                # منتظر اتمام همه تردها
                for future in futures:
                    future.result()
            
            # پایان اسکن
            if self.is_scanning:  # اگر با دکمه توقف متوقف نشده باشد
                self.root.after(0, self.finish_scan)
                
        except Exception as e:
            self.root.after(0, lambda: self.log(f"خطا در اسکن: {str(e)}"))
            self.root.after(0, self.finish_scan)
    
    def finish_scan(self):
        """اتمام عملیات اسکن"""
        self.is_scanning = False
        self.progress_var.set(100)
        
        if not self.active_ips:
            self.status_var.set("اسکن تمام شد - هیچ IP فعالی یافت نشد")
            self.log("اسکن به پایان رسید. هیچ IP فعالی در شبکه یافت نشد.")
        else:
            self.status_var.set(f"اسکن تمام شد - {len(self.active_ips)} IP فعال یافت شد")
            self.log(f"اسکن به پایان رسید. تعداد {len(self.active_ips)} IP فعال در شبکه یافت شد.")
        
        # تغییر وضعیت دکمه‌ها
        self.scan_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = IPScannerApp(root)
        root.mainloop()
    except Exception as e:
        print(f"خطای برنامه: {str(e)}")
        input("برای خروج، کلیدی را فشار دهید...")  # اضافه کردن توقف قبل از خروج
        sys.exit(1)
    finally:
        # این بخش در هر صورت اجرا می‌شود تا اطمینان حاصل شود کنسول بسته نمی‌شود
        # حتی اگر برنامه به طور معمول به پایان برسد
        if not sys.platform.startswith('win'):
            # در ویندوز، این تابع مورد نیاز نیست زیرا قبلاً input را فراخوانی کرده‌ایم
            pass
        else:
            # فقط اگر برنامه از طریق دابل کلیک روی فایل اجرا شده باشد (و نه از طریق ترمینال)
            if len(sys.argv) <= 1:
                print("\nبرنامه به پایان رسید.")
                print("برای بستن این پنجره، کلید Enter را فشار دهید...")
                input() 


