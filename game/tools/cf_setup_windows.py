#!/usr/bin/env python3
"""Set Cloudflare credentials in Windows user environment without logging them."""

import argparse
import os
import re
import sys


def main():
    if os.name != "nt":
        print("この設定画面はWindows専用です。環境変数を設定してください。", file=sys.stderr)
        return 1

    import tkinter as tk
    import winreg
    from tkinter import messagebox, ttk

    parser = argparse.ArgumentParser(description="Cloudflareの認証情報をWindowsのユーザー環境変数に設定")
    parser.add_argument("--account-id", default="")
    args = parser.parse_args()

    root = tk.Tk()
    root.title("Claude Code用 Cloudflare画像生成の設定")
    root.geometry("620x310")
    root.resizable(False, False)
    frame = ttk.Frame(root, padding=20)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="CloudflareのAccount IDとWorkers AI用API Tokenを入力してください。\n"
              "Windowsのユーザー環境変数に保存します。チャットやリポジトリには保存しません。",
              wraplength=570).pack(anchor="w", pady=(0, 14))
    ttk.Label(frame, text="Account ID").pack(anchor="w")
    account = ttk.Entry(frame)
    account.pack(fill="x", pady=(3, 10))
    account.insert(0, args.account_id)
    ttk.Label(frame, text="API Token（入力は非表示）").pack(anchor="w")
    token = ttk.Entry(frame, show="*")
    token.pack(fill="x", pady=(3, 10))

    def save():
        account_value, token_value = account.get().strip(), token.get().strip()
        if not re.fullmatch(r"[0-9a-fA-F]{32}", account_value):
            messagebox.showerror("設定できません", "Account IDは32桁の英数字を確認してください。", parent=root)
            return
        if not token_value or any(char.isspace() for char in token_value):
            messagebox.showerror("設定できません", "API Tokenを空白なしで入力してください。", parent=root)
            return
        try:
            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "CLOUDFLARE_ACCOUNT_ID", 0, winreg.REG_SZ, account_value)
                winreg.SetValueEx(key, "CLOUDFLARE_API_TOKEN", 0, winreg.REG_SZ, token_value)
        except OSError:
            messagebox.showerror("設定できません", "Windowsのユーザー環境変数に保存できませんでした。", parent=root)
            return
        token.delete(0, tk.END)
        messagebox.showinfo("設定を保存しました", "認証情報を保存しました。\n"
                            "cf_image.pyは、起動中のClaude Codeからもこの設定を読み取れます。\n"
                            "APIで実際に使えるかは、まだ未確認です。", parent=root)
        root.destroy()

    ttk.Button(frame, text="Windowsのユーザー環境変数に保存", command=save).pack(anchor="e", pady=(8, 0))
    token.focus_set()
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
