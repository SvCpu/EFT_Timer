# https://github.com/adamburgess/tarkov-time
# SvCpu 2025/1/3
# For SvBot Project

import time
from datetime import datetime

TARKOV_RATIO = 7
night_ranges = [(23*60, 24*60), (0, 4*60)]  # 定義夜晚時間範圍（從23:00到次日04:00，轉換為分鐘）

def get_tarkov_time(left:bool=True, current_time:int=None):
    """獲取塔科夫時間

    參數:
        left (bool, optional): 指定是否為左邊時間, 預設值: True.
        current_time (int, optional): 指定要轉換的時間, 預設值: None.

    返回:
        str: 代表塔科夫時間的格式化字串
    """
    if current_time is None:
        current_time = int(time.time()) * 1000
    one_day = 24 * 3600 * 1000
    russia = 3 * 3600 * 1000
    offset = russia + (0 if left else 12 * 3600 * 1000)
    tarkov_time = (offset + current_time * TARKOV_RATIO) % one_day
    return format_hms(tarkov_time)

def format_hms(time):
    total = int(time / 1000)
    hours = total // 3600
    mins = (total // 60) % 60
    secs = total % 60
    return f"{hours:02}:{mins:02}:{secs:02}"

def real_time_to_tarkov_time(year:int, month:int, day:int, hour:int=0, minute:int=0, left:bool=True):
    """將指定的現實時間轉換為塔克夫時間

    參數:
        year (int): 年
        month (int): 月
        day (int): 天
        hour (int): 小時
        minute (int): 分鐘
        left (bool, optional): 指定是否為左邊時間, 預設值: True.

    Raises:
        ValueError: 給出的時間不在指定範圍內

    返回:
        str: 代表塔科夫時間的格式化字串
    """
    if not (1 <= month <= 12 and 1 <= day <= 31):
        raise ValueError("Invalid date values: month must be in 1-12, day must be in 1-31")
    now = datetime.now()
    target_date = datetime(year or now.year, month or now.month, day or now.day, hour, minute)
    target_time = int((target_date - datetime(1970, 1, 1)).total_seconds() * 1000)
    return get_tarkov_time(left,target_time)

def in_night_range(minutes:int):
    for start, end in night_ranges:
        if start <= minutes < end:
            return True
    return False

def is_night_time(tarkov_time_str:str):
    """判斷時間是否為夜晚

    參數:
        tarkov_time_str (str): 塔科夫時間的格式化字符串(HH:MM:SS)

    返回:
        bool: 是否為夜晚
    """
    # 將塔克夫時間分解為小時、分鐘和秒
    try:
        hours, minutes, seconds = map(int, tarkov_time_str.split(':'))
    except ValueError:
        return None
    
    # 將時間轉換為總分鐘數
    total_minutes = int(hours * 60 + minutes + (seconds / 60))
    return in_night_range(total_minutes)

def time_until_night_ends(tarkov_time_str:str, fstr:bool=True)->str|tuple:
    """獲取距離夜晚結束還有多少時間

    參數:
        tarkov_time_str (str): 塔科夫時間的格式化字符串(HH:MM:SS)
        fstr (bool): 是否返回格式化後的時間

    返回:
        str|tuple
    """
    # if not is_night_time(tarkov_time_str):
        # return None
    hours, minutes, seconds = map(int, tarkov_time_str.split(':'))
    current_minutes = hours * 60 + minutes + (seconds / 60)
    add_minutes = 0
    if 23*60<=current_minutes<=24*60:
        add_minutes = 60
        current_minutes = 0
    
    time_left_minutes = 4*60 - current_minutes

    time_left_minutes +=add_minutes
    true_time = time_left_minutes / TARKOV_RATIO #轉換為現實時間
    hours_left = int(true_time // 60)
    minutes_left = int(true_time % 60)
    if fstr:
        return f"{hours_left:02d}:{minutes_left:02d}"
    else:
        return hours_left, minutes_left

def time_until_night_starts(tarkov_time_str:str, fstr:bool=True):
    """獲取距離夜晚開始還有多少時間

    參數:
        tarkov_time_str (str): 塔科夫時間的格式化字符串(HH:MM:SS)
        fstr (bool): 是否返回格式化後的時間

    返回:
        str|tuple
    """
    # if is_night_time(tarkov_time_str):
    #     return None
    hours, minutes, seconds = map(int, tarkov_time_str.split(':'))
    current_minutes = hours * 60 + minutes + (seconds / 60)
    if 4*60<=current_minutes<=23*60:
        time_left_minutes = 23*60 - current_minutes
    else:
        return None
    true_time = time_left_minutes / TARKOV_RATIO #轉換為現實時間
    hours_left = int(true_time // 60)
    minutes_left = int(true_time % 60)
    if fstr:
        return f"{hours_left:02d}:{minutes_left:02d}"
    else:
        return hours_left,minutes_left
    
def get_time_until_night(tarkov_time_str:str):
    if is_night_time(tarkov_time_str):
        return True, time_until_night_ends(tarkov_time_str)
    else:
        return False, time_until_night_starts(tarkov_time_str)

if __name__ == "__main__":
    print("Left Time:", get_tarkov_time(True))
    print("Right Time:", get_tarkov_time(False))
    print(is_night_time("22:53:00"))
    print(is_night_time("05:00:00"))
    print(is_night_time("18:19:29"))
