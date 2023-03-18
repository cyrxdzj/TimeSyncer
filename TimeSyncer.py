import os
import shutil
import subprocess
import threading
import time
import traceback

import ntplib
import tkinter
import tkinter.messagebox
import sys

# 基本指示定义
is_log_to_file = sys.argv[0].endswith(".exe")
if "gui" in sys.argv:
    is_gui = True
elif "nogui" in sys.argv:
    is_gui = False
else:
    is_gui = r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup" not in sys.argv[0]
__version__ = "V1.0"

# LOG初始化
if is_log_to_file:
    sys.stdout = sys.stderr = open("C:/Windows/Temp/TimeSyncerLog.txt", "a")


def update_system_time():
    cnt = 0
    while True:
        try:
            cnt += 1
            if cnt > 60:
                break
            if is_gui:
                status_text['text'] = "向服务器请求时间，第%d/60次尝试。" % cnt
            print("Try %d/60 times." % cnt)
            c = ntplib.NTPClient()
            response = c.request('ntp.tencent.com')
            ts = response.tx_time
            now_date = time.strftime('%Y-%m-%d', time.localtime(ts))
            now_time = time.strftime('%X', time.localtime(ts))
            if is_gui:
                status_text['text'] = "获取到了服务器响应，日期为%s，时间为%s。" % (now_date, now_time)
            print("Sync time successfully:", now_date, now_time)
            if is_gui and not tkinter.messagebox.askyesno("",
                                                          "根据服务器响应，当前日期为%s，时间为%s。\n将结果写入系统中吗？" % (now_date, now_time)):
                status_text['text'] = "取消写入。"
                break
            elif is_gui:
                status_text['text'] = "执行写入。"
            print("Write to system:")
            command_obj = subprocess.Popen("date %s && time %s" % (now_date, now_time), shell=True,
                                           stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("STDOUT")
            stdout = command_obj.stdout.read().decode('gbk').strip('\r\n') if command_obj.stdout.readable() else ""
            print(stdout)
            print("STDERR")
            stderr = command_obj.stderr.read().decode('gbk').strip('\r\n') if command_obj.stderr.readable() else ""
            print(stderr)
            print("DONE")
            if is_gui and stderr:
                status_text['text'] = "出错。"
                tkinter.messagebox.showerror("", "在写入系统时间时出现了错误：\n" + stderr)
            if is_gui and not stderr:
                status_text['text'] = "更新系统时间完成。"
                print("Update system time successfully.")
            break
        except:
            if is_gui:
                status_text['text'] = "出错。"
            print(traceback.format_exc())
            time.sleep(1)


def set_startup():
    try:
        status_text['text'] = "正在设置自己为开机自启。"
        print("Set self as startup.")
        if sys.argv[0].endswith(".exe"):
            shutil.copyfile(sys.argv[0], os.path.join(os.path.expanduser('~'),
                                                      r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\TimeSyncer.exe"))
            status_text['text'] = "完成设置开机自启。"
            print("Set self as startup successfully.")
        else:
            status_text['text'] = "不可以设置非exe程序为开机自启。"
            print("Unable to set non-exe program as startup.")
    except:
        status_text['text'] = "出错。"
        tkinter.messagebox.showerror("", "在设置开机自启时出错。\n" + traceback.format_exc())
        print(traceback.format_exc())


if __name__ == "__main__":
    if is_gui:
        root = tkinter.Tk()
        update_button = tkinter.Button(root, text="更新系统时间。", command=threading.Thread(target=update_system_time).start)
        startup_button = tkinter.Button(root, text="设置为开机自启。", command=threading.Thread(target=set_startup).start)
        status_text = tkinter.Label(root, text="就绪。", anchor="nw")
        copyright_text = tkinter.Label(root, text="Version %s, by cyrxdzj." % __version__, anchor="nw")
        update_button.place(relx=0, rely=0, relwidth=0.5, relheight=0.5)
        startup_button.place(relx=0.5, rely=0, relwidth=0.5, relheight=0.5)
        status_text.place(relx=0, rely=0.5, relwidth=1, relheight=0.25)
        copyright_text.place(relx=0, rely=0.75, relwidth=1, relheight=0.25)
        root.title("TimeSyncer")
        root.geometry("400x100")
        root.mainloop()
    else:
        update_system_time()
