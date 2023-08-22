import os
import datetime
from PIL import ImageGrab, Image
import io
from config import settings
import threading
import redis


def startup() -> None:
    """
    开机自启
    :return:  None
    """
    print("setting startup...")
    user_names = os.listdir(r"C:\Users")
    for user_name in user_names:
        os.popen(f'''copy /Y "C:\\control\\远程协助.lnk" "C:\\Users\\{user_name}\\Desktop\\远程协助.lnk"''')
        os.popen(f'''copy /Y "C:\\control\\远程协助.lnk" "C:\\Users\\{user_name}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\远程协助.lnk"''')


def get_shopfloor_ip() -> str:
    """
    获取本机的shopfloorIP
    :return:  ip: str  返回本机的shopfloor IP
    """
    res = os.popen("ipconfig").read()
    ip = res[res.find('172'):]
    ip = ip[:ip.find('\n')]
    return ip


def get_client_info(user):
    for i in range(365):
        today = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y%m%d")
        for root, dirs, files in os.walk(f"C:\\Users\\{user}\\Testprogram"):
            for _dir in dirs:
                if today in _dir:
                    arr = root.split("\\")
                    model = arr[-2]
                    station = arr[-1]
                    return model, station

    return "",""


def make_dir(path) -> None:
    """
    创建文件夹
    :param path:  要创建的路径
    :return:  None
    """
    os.makedirs(path)


def screenshot():
    """
    用PIL进行截图
    :return: PIL.Image.Image
    """

    img = ImageGrab.grab()
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


def redis_connect():
    redis_cli = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PSW)

    return redis_cli


def start_thread(func, *args):
    listener = threading.Thread(target=func, args=args)
    listener.setDaemon(True)
    listener.start()


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    print(get_shopfloor_ip())