# -*- coding: utf-8 -*-

import Tkinter
from Tkinter import *
import tkMessageBox
import ttk
import datetime
import os
from crawl.crawl_sales import CrawlSales

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


def MainCallBack():
    if not NameEn.get() or not PwdEn.get():
        tkMessageBox.showinfo(title='错误', message="用户名密码不能为空")
        return

    try:
        f_start = datetime.datetime(year=int(start_year.get()), day=int(start_day.get()), month=int(start_month.get()))
        f_end = datetime.datetime(year=int(year.get()), day=int(day.get()), month=int(month.get()))
    except:
        tkMessageBox.showinfo(title='错误', message="日期格式错误")
    content = "%s;%s;%s;%s" % (NameEn.get(), PwdEn.get(), f_start.strftime("%Y-%m-%d"), f_end.strftime("%Y-%m-%d"))
    file = open(os.path.dirname(__file__) + "/info.dat", "w+")
    file.write(content)
    file.flush()
    file.close()

    data = {'account_name': NameEn.get(), "account_pwd": PwdEn.get(), "start_str": f_start.strftime("%Y-%m-%d"),
            "end_str": f_end.strftime("%Y-%m-%d")}
    root.withdraw()  # 隐藏
    try:
        crawl = CrawlSales(data)
        crawl.crawl_sales(lambda: root.deiconify())
    except Exception, ex:
        print(ex.message)
        root.deiconify()  # 显示
        # root.destroy()


name, pwd, start_str, end_str = ";;;".split(';')
if os.path.exists(os.path.dirname(__file__) + "/info.dat"):
    file = open(os.path.dirname(__file__) + "/info.dat", "r+")
    content = file.read()
    if content and len(content.split(';')) == 4:
        name, pwd, start_str, end_str = content.split(';')

root = Tkinter.Tk()

if not end_str:
    now = datetime.datetime.now()
else:
    now = datetime.datetime.strptime(end_str, "%Y-%m-%d")
if not start_str:
    start = datetime.datetime.now() - datetime.timedelta(days=7)
else:
    start = datetime.datetime.strptime(start_str, "%Y-%m-%d")

curWidth = 640  # get current width
curHeight = 480  # get current height
scnWidth, scnHeight = root.maxsize()  # get screen width and height

# 屏幕居中
tmpcnf = '%dx%d+%d+%d' % (curWidth, curHeight,
                          (scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
root.geometry(tmpcnf)
root.iconbitmap('c:\\yunying_exe.ico')
root.resizable(width=False, height=False)
root.title('卖家后台订单抓取客户端')

Nameframe = Tkinter.Frame(root)
Nameframe.pack(anchor=Tkinter.N)
NameLb = Tkinter.Label(Nameframe, text="用户名:")
NameLb.pack(padx=10, pady=12, side=Tkinter.LEFT)
var_name = Tkinter.StringVar()
var_name.set(name)
NameEn = Tkinter.Entry(Nameframe, bd=2, width=12, textvariable=var_name)
NameEn.pack(ipadx=20, pady=5, side=Tkinter.LEFT)

Pwdframe = Tkinter.Frame(root)
Pwdframe.pack(anchor=Tkinter.N)
PwdLb = Tkinter.Label(Pwdframe, text="密   码:")
PwdLb.pack(padx=10, pady=12, side=Tkinter.LEFT)
var_pwd = Tkinter.StringVar()
var_pwd.set(pwd)
PwdEn = Tkinter.Entry(Pwdframe, bd=2, width=12, textvariable=var_pwd)
PwdEn.pack(ipadx=20, pady=5, side=Tkinter.LEFT)

dateframe = Tkinter.Frame(root)
dateframe.pack(anchor=Tkinter.N)

Tkinter.Label(dateframe, text="年").grid(column=1, row=0)
Tkinter.Label(dateframe, text="月").grid(column=2, row=0)
Tkinter.Label(dateframe, text="日:").grid(column=3, row=0)

Tkinter.Label(dateframe, text="起   始:").grid(column=0, row=1)
start_year = Tkinter.StringVar()
yearChosen = ttk.Combobox(dateframe, width=5, textvariable=start_year, justify='center')
yearChosen['values'] = range(2001, 2020)
yearChosen.grid(column=1, row=1)
yearChosen.set(start.year)

start_month = Tkinter.StringVar()
monthChosen = ttk.Combobox(dateframe, width=5, textvariable=start_month, justify='center')
monthChosen['values'] = range(1, 13)
monthChosen.grid(column=2, row=1)
monthChosen.set(start.month)

start_day = Tkinter.StringVar()
dayChosen = ttk.Combobox(dateframe, width=5, textvariable=start_day, justify='center')
dayChosen['values'] = range(1, 31)
dayChosen.grid(column=3, row=1)
dayChosen.set(start.day)

Tkinter.Label(dateframe, text="结   束:").grid(column=0, row=2)
year = Tkinter.StringVar()
yearChosen = ttk.Combobox(dateframe, width=5, textvariable=year, justify='center')
yearChosen['values'] = range(2001, 2020)
yearChosen.grid(column=1, row=2)
yearChosen.set(now.year)

month = Tkinter.StringVar()
monthChosen = ttk.Combobox(dateframe, width=5, textvariable=month, justify='center')
monthChosen['values'] = range(1, 13)
monthChosen.grid(column=2, row=2)
monthChosen.set(now.month)

day = Tkinter.StringVar()
dayChosen = ttk.Combobox(dateframe, width=5, textvariable=day, justify='center')
dayChosen['values'] = range(1, 31)
dayChosen.grid(column=3, row=2)
dayChosen.set(now.day)

btnframe = Tkinter.Frame(root)
btnframe.pack(anchor=Tkinter.N)
w = Tkinter.Button(btnframe, text="登   录", width=20, command=MainCallBack)
w.pack(padx=16, pady=10, side=Tkinter.LEFT)

q = Tkinter.Button(btnframe, text="退   出", width=20, command=btnframe.quit)
q.pack(padx=16, pady=10, side=Tkinter.LEFT)

root.mainloop()
# root.destroy()
