import sys
import os
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkextrafont import Font
from datetime import datetime
from eft_time import get_tarkov_time, is_night_time, get_time_until_night
from sound_player import play_alert
import argparse

class TimeDisplay(ttk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        # 加載自定義字體
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'MindEscape.ttf')
        try:
            # 檢查字體是否已經加載
            loaded_fonts = [f for f in font.families(root=self)]
            if 'MindEscape' not in loaded_fonts:
                self.custom_font = Font(file=font_path, family='MindEscape')
            else:
                self.custom_font = Font(family='MindEscape')

        except Exception as e:
            print(f"無法加載MindEscape字體: {e}，使用默認字體Helvetica")
            self.custom_font = font.Font(family='Helvetica')
        self.create_widgets()
        self.bind('<Configure>', self.on_resize)
        self.min_width = 200  # 最小寬度
        self.max_width = 800  # 最大寬度
        self.min_font_size = 12  # 最小字體大小
        self.max_font_size = 64  # 最大字體大小

    def create_widgets(self):
        # 時間顯示標籤
        self.time_label = ttk.Label(
            self,
            font=(self.custom_font.actual()['family'], 16),
            anchor='center'
        )
        self.time_label.pack(expand=True, fill='both', pady=5)

        # 倒計時標籤
        self.countdown_label = ttk.Label(
            self,
            font=(self.custom_font.actual()['family'], 12),
            anchor='center'
        )
        self.countdown_label.pack(expand=True, fill='both', pady=5)

    def calculate_font_size(self, widget_width):
        # 根據窗口寬度計算字體大小
        ratio = (widget_width - self.min_width) / (self.max_width - self.min_width)
        ratio = max(0, min(1, ratio))  # 確保比例在0-1之間
        font_size = self.min_font_size + (self.max_font_size - self.min_font_size) * ratio
        return int(font_size)

    def on_resize(self, event):
        # 獲取當前Frame的寬度
        width = self.winfo_width()
        
        # 計算新的字體大小
        time_font_size = self.calculate_font_size(width)
        countdown_font_size = max(int(time_font_size * 0.75), self.min_font_size)
        
        # 更新標籤字體
        self.time_label.configure(font=(self.custom_font.name, time_font_size))
        self.countdown_label.configure(font=(self.custom_font.name, countdown_font_size))

    def update_display(self, is_left=True):
        # 獲取時間
        time_str = get_tarkov_time(is_left)
        # 更新夜晚狀態
        is_night = is_night_time(time_str)
        
        self.time_label.config(text=f'{"🌙" if is_night else "🌞"} {time_str}')

        # 更新倒計時
        status, countdown = get_time_until_night(time_str)
        self.countdown_label.config(
            text=f'距離{"白天" if status else "夜晚"}還有: {countdown}')
        
        return time_str, is_night

class MainWindow(tk.Tk):
    def __init__(self, maximize=False, update_interval=1):
        super().__init__()

        self.title('EFT Timer')
        self.minsize(400, 240)  # 設置最小窗口大小
        self.configure(bg='#1a1a1a')
        
        if maximize:
            self.state('zoomed')  # 最大化窗口
        
        # 初始化提示音狀態
        self.day_alert = False
        self.night_alert = False
        self.update_interval = max(1, min(update_interval, 60))  # 限制更新間隔在1-60秒之間
        self.alert_interval = 1.5  # 提示音觸發間隔（秒）
        self.last_alert_time = 0  # 上次提示音觸發時間

        # 設置深色主題
        style = ttk.Style()
        style.configure('TFrame', background='#1a1a1a')
        style.configure('TLabel', background='#1a1a1a', foreground='white')
        style.configure('TButton', background='#2a2a2a', foreground='black')
        style.configure('Active.TButton', background='#3d3d3d', foreground='black')
        style.configure('TStatusbar.TFrame', background='#2a2a2a')
        style.configure('TStatusbar.TLabel', background='#2a2a2a', foreground='white')

        # 創建主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        # 左側時間顯示
        self.left_display = TimeDisplay(main_frame)
        self.left_display.pack(side='left', expand=True, fill='both', padx=5)

        # 右側時間顯示
        self.right_display = TimeDisplay(main_frame)
        self.right_display.pack(side='right', expand=True, fill='both', padx=5)

        # 創建狀態欄
        self.status_frame = ttk.Frame(self, style='TStatusbar.TFrame')
        self.status_frame.pack(side='bottom', fill='x', pady=(5, 0))

        # 創建按鈕
        self.day_button = ttk.Button(
            self.status_frame,
            text='日',
            command=self.toggle_day_alert,
            style='TButton',
            width=3
        )
        self.day_button.pack(side='left', padx=5, pady=5)

        self.night_button = ttk.Button(
            self.status_frame,
            text='夜',
            command=self.toggle_night_alert,
            style='TButton',
            width=3,
        )
        self.night_button.pack(side='left', padx=5, pady=5)

        self.stop_button = ttk.Button(
            self.status_frame,
            text='⏹',
            command=self.stop_alert,
            style='TButton',
            width=3
        )
        self.stop_button.pack(side='right', padx=5, pady=5)

        # 狀態標籤
        self.status_label = ttk.Label(
            self.status_frame,
            text='點擊左方的按鈕選擇提示',
            style='TStatusbar.TLabel'
        )
        self.status_label.pack(side='left', padx=5, pady=5)

        # 開始更新時間
        self.update_time()

    def toggle_day_alert(self):
        if self.night_alert:
            self.night_alert = False
            self.night_button.configure(style='TButton')
        self.day_alert = not self.day_alert
        self.day_button.configure(
            style='Active.TButton' if self.day_alert else 'TButton'
        )
        self.update_status_text()

    def toggle_night_alert(self):
        if self.day_alert:
            self.day_alert = False
            self.day_button.configure(style='TButton')
        self.night_alert = not self.night_alert
        self.night_button.configure(
            style='Active.TButton' if self.night_alert else 'TButton'
        )
        self.update_status_text()

    def stop_alert(self):
        if self.day_alert:
            self.day_alert = False
            self.day_button.configure(style='TButton')
        if self.night_alert:
            self.night_alert = False
            self.night_button.configure(style='TButton')
        self.update_status_text()

    def update_status_text(self):
        status = []
        if self.day_alert:
            status.append('白天')
        if self.night_alert:
            status.append('夜晚')
        
        if status:
            self.status_label.config(text=f'已啟用提示音: {" 和 ".join(status)}')
        else:
            self.status_label.config(text='等待提示音觸發...')

    def update_time(self):
        left_time, left_is_night = self.left_display.update_display(True)
        right_time, right_is_night = self.right_display.update_display(False)

        # 檢查是否需要播放提示音
        current_time = datetime.now().timestamp()
        if current_time - self.last_alert_time >= self.alert_interval:
            if (self.day_alert and (not left_is_night or not right_is_night)):
                play_alert()
                self.last_alert_time = current_time
            elif (self.night_alert and (left_is_night or right_is_night)):
                play_alert()
                self.last_alert_time = current_time

        self.after(self.update_interval * 1000, self.update_time)

def get_time_info():
    """獲取當前時間信息的JSON格式字符串"""
    import json
    left_time = get_tarkov_time(True)
    right_time = get_tarkov_time(False)
    left_is_night = is_night_time(left_time)
    right_is_night = is_night_time(right_time)
    left_status, left_countdown = get_time_until_night(left_time)
    right_status, right_countdown = get_time_until_night(right_time)
    
    json_str = json.dumps({
        'left': {
            'time': left_time,
            'is_night': left_is_night,
            'next_phase': '白天' if left_status else '夜晚',
            'countdown': left_countdown
        },
        'right': {
            'time': right_time,
            'is_night': right_is_night,
            'next_phase': '白天' if right_status else '夜晚',
            'countdown': right_countdown
        }
    }, ensure_ascii=False)
    return json_str

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='EFT Timer')
    alert_group = parser.add_mutually_exclusive_group()
    alert_group.add_argument('--wait_sun', '-l', action='store_true', help='啟動時開啟白天提示')
    alert_group.add_argument('--wait_night', '-n', action='store_true', help='啟動時開啟夜晚提示')
    parser.add_argument('--maximize', '-m', action='store_true', help='以最大化方式啟動窗口')
    parser.add_argument('--update_time', '-u', type=int, default=1, help='設置更新時間間隔（秒），範圍1-60')
    parser.add_argument('--api', '-a', action='store_true', help='以API模式運行，返回JSON格式的時間信息')
    args = parser.parse_args()

    if args.api:
        if not getattr(sys, 'frozen', False):
            print(get_time_info())
    else:
        app = MainWindow(maximize=args.maximize, update_interval=args.update_time)
        if args.wait_sun:
            app.toggle_day_alert()
        elif args.wait_night:
            app.toggle_night_alert()
        app.mainloop()