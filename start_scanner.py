#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import time

def main():
    """
    اجرای برنامه اسکنر IP با نگه داشتن پنجره کنسول در پایان
    """
    print("در حال اجرای برنامه اسکنر شبکه IP با تم تاریک...")
    print("=" * 50)
    
    try:
        # بررسی وجود فایل اصلی
        if not os.path.exists("ip_scanner_gui.py"):
            print("خطا: فایل ip_scanner_gui.py یافت نشد!")
            input("برای خروج، کلیدی را فشار دهید...")
            return
        
        # نمایش اطلاعات پایتون
        print(f"نسخه پایتون: {sys.version}")
        print(f"سیستم عامل: {sys.platform}")
        print("=" * 50)
        print("در حال اجرای برنامه... (در صورت بروز خطا، پیغام آن در اینجا نمایش داده می‌شود)")
        print("برای خروج از برنامه، پنجره گرافیکی را ببندید.")
        print("=" * 50)
        
        # اجرای برنامه اصلی
        result = subprocess.run([sys.executable, "ip_scanner_gui.py"], 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            text=True,
                            encoding='utf-8')
        
        # نمایش نتیجه اجرا
        if result.returncode != 0:
            print("\nبرنامه با خطا مواجه شد:")
            print(result.stderr)
        else:
            print("\nبرنامه با موفقیت به پایان رسید.")
            
        if result.stdout:
            print("\nخروجی برنامه:")
            print(result.stdout)
    
    except Exception as e:
        print(f"\nخطای غیرمنتظره: {str(e)}")
    
    finally:
        print("\n" + "=" * 50)
        print("برنامه به پایان رسید. برای بستن این پنجره، کلیدی را فشار دهید...")
        input()

if __name__ == "__main__":
    main() 