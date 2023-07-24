import http.server
import socketserver
import sqlite3
import mysql.connector
import sys
import argparse
import configparser

sys.dont_write_bytecode = True

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

conn = None
query = None

if 'sqlite' in config:
    try:
        conn = sqlite3.connect(config['sqlite']['database'])
        query = config.get('sqlite', 'query', fallback='SELECT marklist FROM `读秀书签` WHERE ssid = ?')
        print("连接 SQLite 数据库成功，运行程序")
    except sqlite3.Error:
        print("连接 SQLite 数据库失败，尝试连接 MySQL 数据库...")
elif 'mysql' in config:
    conn = mysql.connector.connect(
        user=config['mysql']['user'],
        password=config['mysql']['password'],
        host=config['mysql']['host'],
        database=config['mysql']['database'],
        port=config['mysql']['port']
    )
    query = config.get('mysql', 'query', fallback='SELECT marklist FROM `读秀书签` WHERE ssid = %s')
else:
    print("config文件未正确配置")

if conn is None:
    # 尝试连接 MySQL 数据库
    if 'mysql' in config:
        try:
            conn = mysql.connector.connect(
                user=config['mysql']['user'],
                password=config['mysql']['password'],
                host=config['mysql']['host'],
                database=config['mysql']['database'],
                port=config['mysql']['port']
            )
            query = config.get('mysql', 'query', fallback='SELECT marklist FROM `读秀书签` WHERE ssid = %s')
        except mysql.connector.Error as e:
            print("连接 MySQL 数据库失败：{}".format(e))
    else:
        print("No database configuration found in config.ini")

if 'server' in config:
    port = int(config['server']['port'])
else:
    port = 7000

class BookmarkHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/'):
            path_parts = self.path.split('/')
            if len(path_parts) == 3 and path_parts[1] == 'bookmark':
                try:
                    ssid = int(path_parts[2])
                    cursor = conn.cursor()
                    cursor.execute(query, (ssid,))
                    result = cursor.fetchone()
                    cursor.close()
                    if result:
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/html; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(bytes(result[0], 'utf-8'))
                    else:
                        self.send_error(404)
                except ValueError:
                    self.send_error(404)
            else:
                self.send_error(404)
        else:
            self.send_error(404)

if __name__ == '__main__':
    with socketserver.TCPServer(("", port), BookmarkHandler) as httpd:
        print(f"Serving at port {port}")
        httpd.serve_forever()
