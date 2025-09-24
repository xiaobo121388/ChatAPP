import socket, json
import tkinter as tk
from tkinter import ttk, messagebox

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000


class RegisterScreen:
    def __init__(self, parent, on_success=None):
        self.parent = parent
        self.on_success = on_success
        self.win = tk.Toplevel(parent)
        self.win.title("QQ注册")
        self.win.geometry("400x600")
        style = ttk.Style(self.win)
        style.configure('TLabel', font=('Microsoft YaHei', 10))
        style.configure('TButton', font=('Microsoft YaHei', 10))
        ttk.Label(self.win, text="QQ注册", font=('Microsoft YaHei', 16, 'bold')).pack(pady=10)
        form_frame = ttk.Frame(self.win)
        form_frame.pack(padx=20, pady=10, fill=tk.X)
        ttk.Label(form_frame, text="昵称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.nickname_entry = ttk.Entry(form_frame)
        self.nickname_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        ttk.Label(form_frame, text="QQ号:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.qq_entry = ttk.Entry(form_frame)
        self.qq_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)
        ttk.Label(form_frame, text="密码:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(form_frame, show="*")
        self.password_entry.grid(row=2, column=1, sticky=tk.EW, pady=5)
        ttk.Label(form_frame, text="确认密码:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.confirm_password_entry = ttk.Entry(form_frame, show="*")
        self.confirm_password_entry.grid(row=3, column=1, sticky=tk.EW, pady=5)
        ttk.Label(form_frame, text="手机号:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.phone_entry = ttk.Entry(form_frame)
        self.phone_entry.grid(row=4, column=1, sticky=tk.EW, pady=5)
        ttk.Label(form_frame, text="性别:").grid(row=5, column=0, sticky=tk.W, pady=5)
        gender_frame = ttk.Frame(form_frame)
        gender_frame.grid(row=5, column=1, sticky=tk.W)
        self.gender_var = tk.StringVar(value="男")
        ttk.Radiobutton(gender_frame, text="男", variable=self.gender_var, value="男").pack(side=tk.LEFT)
        ttk.Radiobutton(gender_frame, text="女", variable=self.gender_var, value="女").pack(side=tk.LEFT)
        ttk.Label(form_frame, text="生日:").grid(row=6, column=0, sticky=tk.W, pady=5)
        birth_frame = ttk.Frame(form_frame)
        birth_frame.grid(row=6, column=1, sticky=tk.W)
        self.year_combobox = ttk.Combobox(birth_frame, width=5, values=[str(y) for y in range(1900, 2024)])
        self.year_combobox.set("2000")
        self.year_combobox.pack(side=tk.LEFT)
        ttk.Label(birth_frame, text="年").pack(side=tk.LEFT)
        self.month_combobox = ttk.Combobox(birth_frame, width=3, values=[f"{m:02d}" for m in range(1, 13)])
        self.month_combobox.set("01")
        self.month_combobox.pack(side=tk.LEFT)
        ttk.Label(birth_frame, text="月").pack(side=tk.LEFT)
        self.day_combobox = ttk.Combobox(birth_frame, width=3, values=[f"{d:02d}" for d in range(1, 32)])
        self.day_combobox.set("01")
        self.day_combobox.pack(side=tk.LEFT)
        ttk.Label(birth_frame, text="日").pack(side=tk.LEFT)
        ttk.Button(self.win, text="立即注册", command=self.submit).pack(pady=20)
        self.agreement_var = tk.IntVar()
        ttk.Checkbutton(self.win, text="我已阅读并同意相关服务条款和隐私政策", variable=self.agreement_var).pack()
        form_frame.columnconfigure(1, weight=1)

    def submit(self):
        nickname = self.nickname_entry.get().strip()
        qq_number = self.qq_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        phone = self.phone_entry.get().strip()
        if not all([nickname, qq_number, password, confirm_password, phone]):
            messagebox.showerror("错误", "请填写所有必填字段")
            return
        if password != confirm_password:
            messagebox.showerror("错误", "两次输入的密码不一致")
            return
        payload = {
            "type": "register",
            "data": {"nickname": nickname, "qq_number": qq_number, "password": password}
        }
        try:
            with socket.create_connection((SERVER_HOST, SERVER_PORT), timeout=5) as s:
                s.sendall((json.dumps(payload) + "\n").encode('utf-8'))
                f = s.makefile('r', encoding='utf-8')
                line = f.readline().strip()
                if not line:
                    messagebox.showerror("错误", "服务器无响应")
                    return
                try:
                    resp = json.loads(line)
                except json.JSONDecodeError:
                    messagebox.showerror("错误", "服务器返回格式错误")
                    return
                if resp.get('type') == 'register_response' and resp.get('status') == 'ok':
                    messagebox.showinfo("成功", "注册成功！")
                    if callable(self.on_success):
                        self.on_success(qq_number, password, nickname)
                    self.win.destroy()
                else:
                    messagebox.showerror("失败", resp.get('message', '注册失败'))
        except (ConnectionRefusedError, socket.timeout):
            messagebox.showerror("错误", "无法连接服务器，请确认服务器已启动")
        except Exception as e:
            messagebox.showerror("错误", f"发生异常: {e}")


def open_register(parent, on_success=None):
    return RegisterScreen(parent, on_success=on_success)


__all__ = ["RegisterScreen", "open_register"]