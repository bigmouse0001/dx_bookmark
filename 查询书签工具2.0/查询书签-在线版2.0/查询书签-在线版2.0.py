import os
import sys
import json
import pyperclip
import sqlite3
import configparser
import re
from PySide6 import QtWidgets, QtGui, QtCore
import psutil
import subprocess
import requests


class QueryBookmarks(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和图标
        self.setWindowTitle('查询书签')
        self.setWindowIcon(QtGui.QIcon('bookmark.png'))

        # 设置窗口大小和位置
        self.resize(300, 300)
        screen = QtWidgets.QApplication.primaryScreen()
        screen_size = screen.availableGeometry()
        self.move((screen_size.width() - self.width()) / 2, (screen_size.height() - self.height()) / 2)

        # 设置窗口背景色
        self.setStyleSheet('background-color: #f5f5f5;')

        # 读取配置文件
        self.config = configparser.ConfigParser()
        self.config.read('config.ini', encoding='utf-8')

        # 初始化界面控件
        self.initUI()

    def initUI(self):
        # 创建布局
        layout = QtWidgets.QGridLayout()

        # 在窗口中添加一个标签和一个下拉框，用于选择数据库路径
        config_label = QtWidgets.QLabel('数据库配置：', self)
        config_label.setFont(QtGui.QFont('微软雅黑', 10))
        layout.addWidget(config_label, 0, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.config_combobox = QtWidgets.QComboBox(self)
        self.config_combobox.setFont(QtGui.QFont('微软雅黑', 12))
        self.config_combobox.addItems(self.config.sections())
        self.config_combobox.setCurrentIndex(0)
        layout.addWidget(self.config_combobox, 0, 1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        # 在窗口中添加一个标签和一个输入框，用于输入数字ssid
        ssid_label = QtWidgets.QLabel('SSID：', self)
        ssid_label.setFont(QtGui.QFont('微软雅黑', 12))
        layout.addWidget(ssid_label, 1, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.ssid_entry = QtWidgets.QLineEdit(self)
        self.ssid_entry.setFont(QtGui.QFont('微软雅黑', 12))
        self.ssid_entry.setValidator(QtGui.QIntValidator())
        self.ssid_entry.setFixedWidth(120)
        self.ssid_entry.setStyleSheet('background-color: white; border: 1px solid #c8c8c8;')
        layout.addWidget(self.ssid_entry, 1, 1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        # 在窗口中添加一个文本框，用于显示查询结果和复制查询结果
        self.output_text = QtWidgets.QTextEdit(self)
        self.output_text.setFont(QtGui.QFont('微软雅黑', 9))
        self.output_text.setFixedWidth(300)
        self.output_text.setFixedHeight(300)
        self.output_text.setStyleSheet('background-color: white; border: 1px solid #c8c8c8;')
        layout.addWidget(self.output_text, 2, 0, 1, 2, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        # 在窗口中添加一个按钮，用于执行查询
        self.query_button = QtWidgets.QPushButton('查询', self)
        self.query_button.setFont(QtGui.QFont('微软雅黑', 11))
        self.query_button.setStyleSheet('background-color: #4caf50; color: black;')
        self.query_button.setFixedWidth(80)
        self.query_button.setFixedHeight(35)
        layout.addWidget(self.query_button, 3, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        # 在窗口中添加一个 Label，显示一行字
        quote_label = QtWidgets.QLabel('对持真境应无取\n愿得身闲便做僧', self)
        quote_label.setFont(QtGui.QFont('楷体', 13))
        quote_label.setStyleSheet('background-color: transparent;padding-left: 30px;')
        layout.addWidget(quote_label, 3, 0, 1, 0, QtCore.Qt.AlignCenter)

        # 设置布局
        self.setLayout(layout)

        # 绑定事件响应函数
        self.query_button.clicked.connect(self.execute_query)
        self.ssid_entry.returnPressed.connect(self.execute_query)
        self.output_text.setReadOnly(True)
        self.output_text.setCursorWidth(0)
        self.setAcceptDrops(True)

        # 绑定双击事件
        self.output_text.mouseDoubleClickEvent = self.on_output_text_double_clicked

    def execute_query(self):
        ssid_value = self.ssid_entry.text()
        # 从配置文件中获取API地址
        config_value = self.config_combobox.currentText()
        api_url = self.config.get(config_value, 'api_url')

        # 发送API请求，并获取JSON数据
        try:
            response = requests.get(f"{api_url}/{ssid_value}")
            if response.status_code == 200:
                data = response.json()
            else:
                self.output_text.setText(f"查询出错：{response.status_code}")
                return
        except Exception as e:
            self.output_text.setText(f"查询出错：{e}")
            return

        # 将查询结果显示在文本框中
        if len(data) == 0:
            self.output_text.clear()
            self.output_text.insertPlainText('未找到相关记录')
        else:
            output_text = ''
            for mark in data:
                output_text += f"{mark['c']}\t{mark['p']}\n"
            self.output_text.clear()
            self.output_text.insertPlainText(output_text)
            pyperclip.copy(output_text)

    def copy_to_clipboard(self):
        selected_text = self.output_text.textCursor().selectedText()
        if selected_text:
            pyperclip.copy(selected_text)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            # 获取拖拽文件中的 ssid
            file_path = urls[0].toLocalFile()
            file_name = os.path.basename(file_path)
            ssid_value = ''
            if file_name.endswith('.pdf'):
                ssid_value = re.findall(r'\d{8}', file_name)
                if ssid_value:
                    ssid_value = ssid_value[0]

            # 将 ssid 粘贴至 ssid 输入框并执行查询
            self.ssid_entry.setText(ssid_value)
            self.execute_query()

            # 检查是否有 PdgCntEditor.exe 进程在运行，如果没有则启动它
            if 'PdgCntEditor.exe' not in (p.name() for p in psutil.process_iter()):
                pdg_editor_path = os.path.join(os.path.dirname(__file__), 'PdgCntEditor.exe')
                subprocess.Popen(pdg_editor_path)
                
    def on_output_text_double_clicked(self, event):
    # 获取剪贴板内容，并将其粘贴到 ssid_entry 控件中
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard_text = clipboard.text()
        if clipboard_text.isdigit():
            self.ssid_entry.setText(clipboard_text)
            self.execute_query()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    qb = QueryBookmarks()
    qb.show()
    sys.exit(app.exec_())
