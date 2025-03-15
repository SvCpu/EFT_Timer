import winsound

def play_alert():
    """播放提醒音效
    """
    winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS | winsound.SND_ASYNC)