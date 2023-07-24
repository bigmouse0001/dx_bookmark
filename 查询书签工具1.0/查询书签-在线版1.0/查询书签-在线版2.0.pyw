import tkinter as tk
import requests
import json
import pyperclip
from tkinter import filedialog
import configparser
import os
from tkinter import ttk

# 创建一个 Tkinter 应用程序窗口
root = tk.Tk()
root.title('查询书签')

# 设置窗口大小和位置
window_width = 400
window_height = 550
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = int((screen_width - window_width) / 2)
y = int((screen_height - window_height) / 2)
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# 设置窗口背景色
root.configure(bg='#f5f5f5')

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

# 定义一个函数，用于执行api查询并将结果输出到文本框和剪贴板中
def execute_query(event=None):
    ssid_value = ''.join(filter(str.isdigit, ssid_entry.get())) if event is None else root.focus_get().get()
    # 从配置文件中获取数据库路径
    config_value = config_combobox.get()
    api_url = config.get(config_value, 'api_url')
    api_url = f"{api_url}/{ssid_value}"
    try:
        # 执行api查询
        response = requests.get(api_url)

        # 获取查询结果
        if response.status_code == 200:
            data = response.json()

            # 将查询结果写入文本框和剪贴板中
            output_text.delete(1.0, tk.END)
            clipboard_text = ''
            for mark in data:
                output_text.insert(tk.END, f"{mark['c']}  {mark['p']}\n")
                clipboard_text += f"{mark['c']}  {mark['p']}\n"
            pyperclip.copy(clipboard_text)
        else:
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, f"服务器返回错误：{response.status_code}")
    except requests.exceptions.RequestException as error:
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, f"请求发生错误：{error}")

# 定义一个函数，用于从剪贴板中获取内容并将其粘贴到ssid输入框中，并自动查询和复制查询结果
def paste_clipboard(event=None):
    clipboard_text = pyperclip.paste()
    ssid_entry.delete(0, tk.END)
    ssid_entry.insert(0, ''.join(filter(str.isdigit, clipboard_text)))
    execute_query()
    pyperclip.copy(output_text.get(1.0, tk.END))

# 在窗口中添加一个标签和一个下拉框，用于选择数据库路径
config_label = tk.Label(root, text='接口配置：', bg='#f5f5f5', font=('微软雅黑', 14))
config_label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)

config_combobox = tk.ttk.Combobox(root, values=config.sections(), font=('微软雅黑', 14), width=13, state='readonly')
config_combobox.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
config_combobox.current(0)

# 在窗口中添加一个标签和一个输入框，用于输入数字ssid
def is_valid_input(input_str):
    return input_str.isdigit()

ssid_validate = root.register(is_valid_input)
ssid_label = tk.Label(root, text='ssid：', bg='#f5f5f5', font=('微软雅黑', 14))
ssid_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)

ssid_entry = tk.Entry(root, font=('微软雅黑', 14), width=14, validate="key", validatecommand=(ssid_validate, '%S'), highlightbackground='#c8c8c8', highlightthickness=1)
ssid_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
ssid_entry.bind("<Return>", execute_query)
ssid_entry.bind("<Double-Button-1>", paste_clipboard) # 绑定双击事件

# 在窗口中添加一个查询按钮
query_button = tk.Button(root, text='查询', font=('微软雅黑', 11), bg='#4caf50', fg='white', command=execute_query)
query_button.grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
query_button.bind("<Return>", execute_query)

# 在窗口中添加一个文本框，用于显示查询结果，并允许复制到剪贴板中
output_text = tk.Text(root, font=('微软雅黑', 10), bg='white', width=45, height=20, highlightbackground='#c8c8c8', highlightthickness=1)
output_text.grid(row=3, column=0, columnspan=3, sticky=tk.W+tk.E, padx=10, pady=5)
output_text.bind("<Double-Button-1>", lambda event: pyperclip.copy(output_text.get(1.0, tk.END)))

# 在窗口中添加一个文本框，用于显示额外的文本
extra_text = tk.Label(root, text='对持真境应无取\n愿得身闲便做僧', font=('楷体', 14, 'bold'), bg='#f5f5f5')
extra_text.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

# 将焦点设置到ssid输入框中
ssid_entry.focus()

# 绑定结果文本框的双击事件
output_text.bind("<Double-Button-1>", paste_clipboard)

# 运行 Tkinter 应用程序
root.mainloop()
