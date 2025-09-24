#!/usr/bin/python
# encoding=utf8
 
import tkinter as tk
import time

class ChatWindow:
    def __init__(self, root, chat_user='对方'):
        self.root = root
        self.chat_user = chat_user
        self.win = tk.Toplevel(root)
        self.win.title(f'与 {chat_user} 聊天')
        w, h = 800, 660
        sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        x, y = 200, int((sh - h) / 2)
        self.win.geometry(f"{w}x{h}+{x}+{y}")
        self.win.resizable(0, 0)

        self.t1_Msg = tk.Text(self.win, width=113, height=32)
        self.t1_Msg.tag_config('green', foreground='#008C00')
        self.t1_Msg.place(x=2, y=35)
        self.t1_Msg.config(state=tk.DISABLED)

        self.t2_sendMsg = tk.Text(self.win, width=112, height=10)
        self.t2_sendMsg.place(x=2, y=485)

        tk.Button(self.win, text='远程协助').place(x=700, y=2)
        tk.Button(self.win, text='表情').place(x=2, y=457)
        tk.Button(self.win, text='文件传送').place(x=62, y=457)
        tk.Button(self.win, text='截图').place(x=150, y=457)
        tk.Button(self.win, text='查找').place(x=210, y=457)
        tk.Button(self.win, text='语音').place(x=660, y=457)
        tk.Button(self.win, text='视频').place(x=720, y=457)
        tk.Button(self.win, text='发送（Send）', command=self.send_message).place(x=665, y=628)

    def send_message(self):
        self.t1_Msg.configure(state=tk.NORMAL)
        header = "我:" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n'
        self.t1_Msg.insert('end', header, 'green')
        body = self.t2_sendMsg.get('0.0', 'end')
        self.t1_Msg.insert('end', body)
        self.t2_sendMsg.delete('0.0', 'end')
        self.t1_Msg.config(state=tk.DISABLED)
        print(header + body)

__all__ = ['ChatWindow']