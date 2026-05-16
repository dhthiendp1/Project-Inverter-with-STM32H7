import os
import json
import numpy as np
import zmq
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import QUrl, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

import config_manager
from views.plot_window import PlotWindow
from controllers.web_bridge import WebBridge


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STM32 SCOPE - DAQ HỆ THỐNG ĐIỀU KHIỂN ĐỘNG CƠ")
        self.resize(1400, 850)

        self.plot_win = PlotWindow()
        self.app_state = 'offline'
        self.mapping_data = config_manager.load_mapping()

        self.web = QWebEngineView()
        self.channel = QWebChannel()
        self.bridge = WebBridge(self)
        self.channel.registerObject("py_bridge", self.bridge)
        self.web.page().setWebChannel(self.channel)

        # Trỏ đường dẫn html lùi lại 1 thư mục (vì code này đang ở trong views/)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        html_path = os.path.join(parent_dir, "foc_diagram.html")
        self.web.setUrl(QUrl.fromLocalFile(html_path))

        self.setCentralWidget(self.web)

        self.max_points = 500
        self.x_history = []
        self.y_history = {}

        # MẠNG ZERO MQ
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://127.0.0.1:5556")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "DATA")

        self.cmd_context = zmq.Context()
        self.cmd_socket = self.cmd_context.socket(zmq.PUB)
        self.cmd_socket.bind("tcp://127.0.0.1:5557")

        self.timer = QTimer()
        self.timer.timeout.connect(self.poll_and_update_gui)
        self.timer.start(30)

    def poll_and_update_gui(self):
        has_new_data = False
        latest_payload = None
        data_dict = None

        while True:
            try:
                topic = self.socket.recv_string(flags=zmq.NOBLOCK)
                payload = self.socket.recv_json(flags=zmq.NOBLOCK)
                latest_payload = payload
                has_new_data = True

                t = float(payload['timestamp'])
                data_dict = payload['data']

                self.x_history.append(t)
                if len(self.x_history) > self.max_points:
                    self.x_history.pop(0)

                for var_name, val in data_dict.items():
                    if var_name not in self.y_history:
                        self.y_history[var_name] = []
                    self.y_history[var_name].append(float(val))
                    if len(self.y_history[var_name]) > self.max_points:
                        self.y_history[var_name].pop(0)

            except zmq.Again:
                break
            except Exception as e:
                print(f"\n[DEBUG LỖI MẠNG ZMQ]: {e}")
                break

        if has_new_data and latest_payload:
            if self.app_state == 'offline':
                self.app_state = 'realtime'
                self.web.page().runJavaScript("if(typeof setAppMode === 'function') setAppMode('realtime');")

            js_data = json.dumps(latest_payload['data'])
            self.web.page().runJavaScript(
                f"if(typeof updateRealtimeData === 'function') updateRealtimeData({js_data});")

            if not self.plot_win.is_paused:
                plot_dict = {}
                for var_name in latest_payload['data'].keys():
                    if var_name in self.y_history:
                        plot_dict[var_name] = np.array(self.y_history[var_name], dtype=float)

                if self.x_history:
                    self.plot_win.set_real_data(np.array(self.x_history, dtype=float), plot_dict)

        if data_dict:
            json_str = json.dumps(data_dict)
            self.web.page().runJavaScript(f"updateReadDataFromPython('{json_str}')")