from datetime import datetime
import pytz



def noww():
    tashkent_tz = pytz.timezone('Asia/Tashkent')
    return f"{datetime.now(tashkent_tz).strftime("%d-%m-%Y %H:%M")}"