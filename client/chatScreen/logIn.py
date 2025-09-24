import tkinter as tk
import tkinter.messagebox
import json
import os
from PIL import Image, ImageTk
from sx_friend_list import FriendListWindow
from sx_chat_win import ChatWindow
from registerScreen import open_register

class ChatApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("聊天登录窗口")
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        w, h = 690, 500
        x, y = int((sw - w) / 2), int((sh - h) / 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.resizable(0, 0)
        self.current_user = None
        self.friend_window = None
        self.chat_windows = {}  # chat_user -> ChatWindow
        self.users_file = 'users.json'
        self.users = self._load_users()
        self._build_login_ui()

    def _build_login_ui(self):
        img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'image', 'login_benner.png'))
        if os.path.exists(img_path):
            img = Image.open(img_path).resize((690, 300), Image.LANCZOS)
            self.login_benner = ImageTk.PhotoImage(img)
            tk.Label(self.root, image=self.login_benner).place(x=0, y=0)
        tk.Label(self.root, text='用户名：').place(x=200, y=320)
        tk.Label(self.root, text='密  码：').place(x=200, y=360)
        self.var_usr_name = tk.StringVar()
        self.var_usr_pwd = tk.StringVar()
        tk.Entry(self.root, textvariable=self.var_usr_name).place(x=260, y=320)
        tk.Entry(self.root, textvariable=self.var_usr_pwd, show='*').place(x=260, y=360)
        tk.Button(self.root, text='登录(Login)', command=self._on_login).place(x=160, y=400)
        tk.Button(self.root, text='注册(Register)', command=self._open_register).place(x=280, y=400)
        tk.Button(self.root, text='退出(Exit)', command=self.root.quit).place(x=430, y=400)
        tk.Label(self.root, text='聊天登录界面 for Python Tkinter', fg='red').pack(side=tk.BOTTOM, expand='yes', anchor='se')

    def _on_login(self):
        name = self.var_usr_name.get().strip()
        pwd = self.var_usr_pwd.get().strip()
        if not name or not pwd:
            tk.messagebox.showerror(message='用户名密码不能为空')
            return
        # 校验用户表
        if name in self.users and self.users[name]['password'] == pwd:
            self.current_user = name
            self._persist_user()
            self.root.withdraw()  # 保留根窗口
            self._open_friend_list()
        else:
            tk.messagebox.showerror(message='用户名密码错误！')

    def _open_register(self):
        def on_success(qq_number, password, nickname):
            # 注册成功后填充登录框（使用 qq_number 作为用户名）
            self.var_usr_name.set(qq_number)
            self.var_usr_pwd.set('')
            # 可扩展：将注册的用户缓存在本地 users.json
            self.users[qq_number] = {'password': password, 'nickname': nickname, 'qq': qq_number}
            self._save_users()
        open_register(self.root, on_success=on_success)

    def _load_users(self):
        if not os.path.exists(self.users_file):
            return {}
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_users(self):
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)

    def _persist_user(self):
        data = {'usrname': f"'{self.current_user}'", 'age': '19'}
        with open('usr.json', 'w') as fp:
            json.dump(data, fp)

    def _open_friend_list(self):
        if self.friend_window and tk.Toplevel.winfo_exists(self.friend_window.win):
            self.friend_window.win.deiconify()
            self.friend_window.win.lift()
            return
        self.friend_window = FriendListWindow(self.root, on_open_chat=self._open_chat_window)

    def _open_chat_window(self, chat_user):
        if chat_user in self.chat_windows:
            win = self.chat_windows[chat_user].win
            if tk.Toplevel.winfo_exists(win):
                win.deiconify()
                win.lift()
                return
        cw = ChatWindow(self.root, chat_user=chat_user)
        self.chat_windows[chat_user] = cw
        cw.win.protocol('WM_DELETE_WINDOW', lambda u=chat_user: self._close_chat(u))

    def _close_chat(self, chat_user):
        cw = self.chat_windows.get(chat_user)
        if cw and tk.Toplevel.winfo_exists(cw.win):
            cw.win.destroy()
        self.chat_windows.pop(chat_user, None)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    ChatApp().run()