#!/usr/bin/python
# encoding=utf8

import tkinter as tk
from tkinter import ttk
import json, socket
from tkinter import simpledialog, messagebox

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000

class FriendListWindow:
    def __init__(self, root, on_open_chat=None):
        self.root = root
        self.on_open_chat = on_open_chat
        self.user_name = self._load_user_name()
        self.win = tk.Toplevel(root)
        self.win.title(f"[{self.user_name}] - 好友列表")
        w, h = 320, 800
        sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        x, y = 200, int((sh - h) / 2)
        self.win.geometry(f"{w}x{h}+{x}+{y}")
        self.win.resizable(0, 0)
        self._build_widgets()

    def _load_user_name(self):
        try:
            with open('usr.json', 'r') as fp:
                data = json.load(fp)
                return data.get('usrname', '未知用户')
        except Exception:
            return '未知用户'

    def _build_widgets(self):
        top_frame = tk.Frame(self.win)
        top_frame.place(x=10, y=2)
        tk.Button(top_frame, text='好友').pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text='群聊').pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text='添加好友', command=self._add_friend_dialog).pack(side=tk.LEFT, padx=5)

        self.fri_list = ttk.Treeview(self.win, height=39, show='tree')
        self.fri_list.place(x=10, y=30)
        self._load_friends()

        tk.Label(self.win, text='查找好友:').place(x=10, y=771)
        tk.Entry(self.win, width=12).place(x=80, y=770)
        tk.Button(self.win, text='搜索').place(x=190, y=770)
        tk.Button(self.win, text='设置').place(x=256, y=770)

        self.fri_list.bind('<Double-1>', self._on_double)

    def _socket_request(self, obj):
        try:
            with socket.create_connection((SERVER_HOST, SERVER_PORT), timeout=5) as s:
                s.sendall((json.dumps(obj) + "\n").encode('utf-8'))
                f = s.makefile('r', encoding='utf-8')
                line = f.readline().strip()
                if not line:
                    return None
                return json.loads(line)
        except Exception as e:
            messagebox.showerror('错误', f'网络异常: {e}')
            return None

    def _load_friends(self):
        # 清空
        for item in self.fri_list.get_children():
            self.fri_list.delete(item)
        # 当前用户(usr.json 存的是带引号的值, 去除外层引号)
        owner_raw = self.user_name.strip()
        owner = owner_raw.strip("'")
        resp = self._socket_request({"type": "get_friends", "qq_number": owner})
        if not resp or resp.get('status') != 'ok':
            group = self.fri_list.insert('', 'end', text='好友')
            return
        friends = resp.get('friends', [])
        group = self.fri_list.insert('', 'end', text='好友')
        for f in friends:
            self.fri_list.insert(group, 'end', text=f)

    def _add_friend_dialog(self):
        target = simpledialog.askstring('添加好友', '输入好友QQ号:', parent=self.win)
        if not target:
            return
        owner = self.user_name.strip("'")
        resp = self._socket_request({"type": "add_friend", "owner": owner, "target": target})
        if not resp:
            return
        if resp.get('status') == 'ok':
            messagebox.showinfo('成功', '添加成功')
            self._load_friends()
        else:
            messagebox.showerror('失败', resp.get('message', '添加失败'))

    def _on_double(self, _event):
        sel = self.fri_list.selection()
        if not sel:
            return
        item_text = self.fri_list.item(sel[0], 'text')
        self._persist_chat_target(item_text)
        if callable(self.on_open_chat):
            self.on_open_chat(item_text)

    def _persist_chat_target(self, chat_name):
        try:
            with open('usr.json', 'r') as fp:
                base = json.load(fp)
        except Exception:
            base = {}
        base['chatname'] = f"'{chat_name}'"
        with open('usr.json', 'w') as wf:
            json.dump(base, wf)

__all__ = ['FriendListWindow']