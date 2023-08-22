import socket
import pyautogui
import utils
import time
import os
import threading
from pynput import keyboard
from typing import List

utils.startup()  # 开机启动
STATUS = 0  # 运行状态


class Client(object):
    def __init__(self):
        self.client_ip = utils.get_shopfloor_ip()
        self.client_hostname = socket.gethostname()
        self.client_login_user = os.getlogin()

        self.redis_cli = utils.redis_connect()

        #  添加设备描述
        self.setting_client_desc()

        #  图像推送远程线程
        utils.start_thread(self.listening_screen)
        #  鼠标事件执行线程
        utils.start_thread(self.mouse_execute_thread)
        #  键盘事件执行线程
        utils.start_thread(self.listening_keyboard)

    def listening_screen(self):
        """
        图像推送至缓冲区
        :return:
        """
        key = "screen:" + self.client_ip
        try:
            while True:
                queue_length = self.redis_cli.llen(key)
                if queue_length < 2:
                    frame = utils.screenshot()
                    threading.Thread(target=self.redis_cli.lpush, args=(key, frame)).start()
        except ConnectionError as conn_e:
            print(conn_e)
            self.redis_cli = None
            while self.redis_cli is None:
                self.redis_cli = utils.redis_connect()
        except Exception as e:
            print(e)
            utils.start_thread(self.mouse_execute_thread)

    def mouse_execute_thread(self):
        try:
            while True:
                event = self.redis_cli.rpop(f"mouse:{self.client_ip}")
                if event is None:
                    continue
                else:
                    info = event.decode('utf-8').split(",")
                    event_code = int(info[0])
                    x = int(info[1])
                    y = int(info[2])
                pyautogui.moveTo(x, y)
                self.mouse_event_excute(event_code, x, y)

        except ConnectionError as conn_e:
            print(conn_e)
            self.redis_cli = None
            while self.redis_cli is None:
                self.redis_cli = utils.redis_connect()
        except Exception as e:
            print(e)
            utils.start_thread(self.mouse_execute_thread)

    def mouse_event_excute(self, event_code, x, y):
        try:
            if event_code == 0:
                pass
            elif event_code == 1:
                pyautogui.mouseDown(button='left')
            elif event_code == 2:
                pyautogui.mouseDown(button='right')
            elif event_code == 4:
                pyautogui.mouseUp(button='left')
            elif event_code == 5:
                pyautogui.mouseUp(button='right')
            return True
        except FileNotFoundError as e:
            print(e)
            return False

        except Exception as e:
            print(e)
            return False

    def setting_client_desc(self):
        """
        推送设备描述到redis
        :return:
        """
        desc_list: List[str] = [self.client_ip, self.client_hostname, self.client_login_user]
        model, station = utils.get_client_info(self.client_login_user)
        desc_list.append(model)
        desc_list.append(station)
        desc = ";".join(desc_list)
        print("client description:", desc)
        if self.redis_cli.get(f"desc:{self.client_ip}") is None:
            self.redis_cli.set(f"desc:{self.client_ip}", desc)

    def listening_keyboard(self):
        """
        键盘执行线程
        :return:
        """
        try:
            keyboard_ctler = keyboard.Controller()
            key = "keyboard:" + self.client_ip
            while True:
                keyboard_event = self.redis_cli.rpop(key)
                if keyboard_event is None:
                    continue
                else:
                    keyboard_event = keyboard_event.decode("utf-8")
                    key_action = int(keyboard_event[0])
                    if key_action == 0:  # press
                        if "Key" in keyboard_event:
                            key_name = keyboard_event.split(".")[-1]
                            keyboard_ctler.press(getattr(keyboard.Key, key_name))
                        else:
                            key_name = keyboard_event.split(',')[-1]
                            keyboard_ctler.press(key_name)

                    elif key_action == 1:
                        if "Key" in keyboard_event:
                            key_name = keyboard_event.split(".")[-1]
                            keyboard_ctler.release(getattr(keyboard.Key, key_name))
                        else:
                            key_name = keyboard_event.split(',')[-1]
                            keyboard_ctler.release(key_name)
        except ConnectionError as conn_e:
            print(conn_e)
            self.redis_cli = None
            while self.redis_cli is None:
                self.redis_cli = utils.redis_connect()
        except Exception as e:
            print(e)
            utils.start_thread(self.listening_keyboard)

def main():
    global STATUS
    try:
        client = Client()
        STATUS = 1
    except Exception as e:
        print(e)
        STATUS = -1
        return None


if __name__ == "__main__":
    while True:
        if STATUS != 1:
            main()
        else:
            time.sleep(1)
