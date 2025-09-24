import sqlite3
import json
import socket
import threading
from typing import Tuple


def create_database():
    """创建数据库和表格"""
    #连接到SQLite数据库（如果不存在会自动创建）
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    # 创建用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nickname TEXT NOT NULL,
        qq_number TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        friend_list TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("数据库和表创建成功！")


def insert_user(nickname: str, qq_number: str, password: str, friend_list) -> Tuple[bool, str]:
    """插入用户数据到数据库, 返回 (是否成功, 错误消息)"""
    try:
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        friend_list_json = json.dumps(friend_list)
        cursor.execute('''
        INSERT INTO users (nickname, qq_number, password, friend_list)
        VALUES (?, ?, ?, ?)
        ''', (nickname, qq_number, password, friend_list_json))
        conn.commit()
        print(f"用户 {qq_number} 插入成功")
        return True, ""
    except sqlite3.IntegrityError:
        msg = "QQ号已存在"
        print("错误：" + msg)
        return False, msg
    except Exception as e:
        msg = f"发生错误：{e}"
        print(msg)
        return False, msg
    finally:
        try:
            conn.close()
        except Exception:
            pass


def display_all_users():
    """显示所有用户数据"""
    try:
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()

        print("\n所有用户数据：")
        print("-" * 80)
        for user in users:
            # 解析好友列表JSON
            friend_list = json.loads(user[4]) if user[4] else []
            print(
                f"ID: {user[0]}, 昵称: {user[1]}, QQ号: {user[2]}, 密码: {user[3]}, 好友列表: {friend_list}, 创建时间: {user[5]}")

    except Exception as e:
        print(f"读取数据时发生错误：{e}")
    finally:
        conn.close()


# ===================== Socket Server 部分 ===================== #

HOST = '127.0.0.1'
PORT = 5000


def handle_client(conn: socket.socket, addr):
    print(f"客户端连接: {addr}")
    try:
        f = conn.makefile('r', encoding='utf-8')
        line = f.readline()
        if not line:
            return
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            resp = {"type": "error", "message": "JSON解析失败"}
            conn.sendall((json.dumps(resp) + "\n").encode('utf-8'))
            return

        msg_type = data.get("type")
        if msg_type == "register":
            payload = data.get("data", {})
            nickname = payload.get("nickname", "")
            qq_number = payload.get("qq_number", "")
            password = payload.get("password", "")
            if not all([nickname, qq_number, password]):
                resp = {"type": "register_response", "status": "error", "message": "缺少必要字段"}
            else:
                ok, err = insert_user(nickname, qq_number, password, [])
                if ok:
                    resp = {"type": "register_response", "status": "ok"}
                else:
                    resp = {"type": "register_response", "status": "error", "message": err}
            conn.sendall((json.dumps(resp) + "\n").encode('utf-8'))
        elif msg_type == "get_friends":
            qq_number = data.get("qq_number", "")
            try:
                conn_db = sqlite3.connect('user_data.db')
                c = conn_db.cursor()
                c.execute('SELECT friend_list FROM users WHERE qq_number=?', (qq_number,))
                row = c.fetchone()
                if row:
                    friend_list = json.loads(row[0]) if row[0] else []
                    resp = {"type": "get_friends_response", "status": "ok", "friends": friend_list}
                else:
                    resp = {"type": "get_friends_response", "status": "error", "message": "用户不存在"}
            except Exception as e:
                resp = {"type": "get_friends_response", "status": "error", "message": str(e)}
            finally:
                try:
                    conn_db.close()
                except Exception:
                    pass
            conn.sendall((json.dumps(resp) + "\n").encode('utf-8'))
        elif msg_type == "add_friend":
            owner = data.get("owner")
            target = data.get("target")
            if not owner or not target or owner == target:
                resp = {"type": "add_friend_response", "status": "error", "message": "参数错误"}
                conn.sendall((json.dumps(resp) + "\n").encode('utf-8'))
            else:
                try:
                    conn_db = sqlite3.connect('user_data.db')
                    c = conn_db.cursor()
                    # 确认双方存在
                    c.execute('SELECT id, friend_list FROM users WHERE qq_number=?', (owner,))
                    owner_row = c.fetchone()
                    c.execute('SELECT id FROM users WHERE qq_number=?', (target,))
                    target_row = c.fetchone()
                    if not owner_row or not target_row:
                        resp = {"type": "add_friend_response", "status": "error", "message": "用户不存在"}
                    else:
                        friend_list = json.loads(owner_row[1]) if owner_row[1] else []
                        if target not in friend_list:
                            friend_list.append(target)
                            c.execute('UPDATE users SET friend_list=? WHERE qq_number=?', (json.dumps(friend_list), owner))
                            conn_db.commit()
                        resp = {"type": "add_friend_response", "status": "ok", "friends": friend_list}
                except Exception as e:
                    resp = {"type": "add_friend_response", "status": "error", "message": str(e)}
                finally:
                    try:
                        conn_db.close()
                    except Exception:
                        pass
                conn.sendall((json.dumps(resp) + "\n").encode('utf-8'))
        else:
            resp = {"type": "error", "message": "未知消息类型"}
            conn.sendall((json.dumps(resp) + "\n").encode('utf-8'))
    except Exception as e:
        print(f"处理客户端 {addr} 出错: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass
        print(f"客户端断开: {addr}")


def run_server():
    create_database()
    print(f"启动服务器 {HOST}:{PORT} ...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print("服务器已启动，等待客户端连接...")
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()


# 主程序
if __name__ == "__main__":
    # 启动多线程socket服务器
    run_server()