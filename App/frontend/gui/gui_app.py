import sys
import os
import json
import numpy as np
import pyqtgraph as pg
import zmq
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                             QHeaderView, QComboBox, QSplitter, QPushButton, QCheckBox, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QUrl, pyqtSlot, QObject, QThread, pyqtSignal, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection

import config_manager

class PlotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCOPE")
        self.resize(1300, 800)
        self.setStyleSheet("background-color: #121212; color: #ddd;")

        self.is_paused = False
        self.selected_plot_idx = 0
        self.markers_enabled = False
        self._updating_table = False

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        # KHU VỰC ĐỒ THỊ
        self.mid_panel = QWidget()
        mid_layout = QVBoxLayout(self.mid_panel)

        tbar = QHBoxLayout()
        self.btn_pause = QPushButton("⏸ PAUSE TO MEASURE")
        self.btn_pause.setStyleSheet("background: #d97706; font-weight: bold; padding: 8px 15px; border-radius: 4px;")
        self.btn_pause.clicked.connect(self.toggle_pause)
        tbar.addWidget(self.btn_pause)

        self.cb_layout = QComboBox()
        self.cb_layout.addItems(["1 Plot", "2 Plots (Rows)", "4 Plots (Grid)"])
        self.cb_layout.setStyleSheet("background: #333; padding: 5px;")
        self.cb_layout.currentIndexChanged.connect(self.update_grid_layout)
        tbar.addWidget(QLabel(" Layout:"))
        tbar.addWidget(self.cb_layout)
        tbar.addStretch()
        mid_layout.addLayout(tbar)

        self.gw = pg.GraphicsLayoutWidget()
        self.gw.setBackground('#121212')
        mid_layout.addWidget(self.gw)
        self.splitter.addWidget(self.mid_panel)

        self.gw.scene().sigMouseClicked.connect(self.handle_scene_click)

        # SIDEBAR PHẢI
        self.right_sidebar = QWidget()
        side_layout = QVBoxLayout(self.right_sidebar)
        side_layout.setContentsMargins(5, 0, 5, 5)

        side_layout.addWidget(QLabel("VARIABLES & STYLE"))
        self.tbl_vars = QTableWidget(0, 5)
        self.tbl_vars.setHorizontalHeaderLabels(["Var", "Target", "Color", "Width", "Style"])
        self.tbl_vars.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tbl_vars.setColumnWidth(0, 80);
        self.tbl_vars.setColumnWidth(1, 80)
        self.tbl_vars.setColumnWidth(2, 80);
        self.tbl_vars.setColumnWidth(3, 50)
        self.tbl_vars.horizontalHeader().setStretchLastSection(True)
        self.tbl_vars.setStyleSheet(
            "QTableWidget { background: #1e1e1e; gridline-color: #333; font-size: 11px; } QComboBox { font-size: 10px; padding: 1px; background: #2d2d2d; border: 1px solid #555; }")
        side_layout.addWidget(self.tbl_vars, stretch=2)

        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("MARKER MEASUREMENTS"))
        self.chk_markers = QCheckBox("Markers")
        self.chk_markers.setStyleSheet("color: #00ff00; font-weight: bold;")
        self.chk_markers.stateChanged.connect(self.toggle_markers)
        header_layout.addWidget(self.chk_markers)
        side_layout.addLayout(header_layout)

        self.tbl_marker = QTableWidget(6, 2)
        self.tbl_marker.setHorizontalHeaderLabels(["Property", "Value"])
        self.tbl_marker.verticalHeader().setVisible(False)
        self.tbl_marker.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tbl_marker.setColumnWidth(0, 120)
        self.tbl_marker.horizontalHeader().setStretchLastSection(True)
        self.tbl_marker.setStyleSheet("background: #1e1e1e; color: #ff9f43; font-size: 11px;")
        self.tbl_marker.itemChanged.connect(self.on_marker_manual_input)
        self.setup_marker_table()
        side_layout.addWidget(self.tbl_marker, stretch=1)

        self.splitter.addWidget(self.right_sidebar)
        self.splitter.setSizes([850, 550])

        self.plots = []
        self.cursors_m1 = []
        self.cursors_m2 = []
        self.curves = {}
        self.color_list = ["Green", "Red", "Cyan", "Yellow", "Purple", "Orange", "White"]

        for i in range(4):
            p = pg.PlotItem(title=f"Scope {i + 1}")
            p.getAxis('left').setPen(pg.mkPen('#555555', width=1))
            p.getAxis('bottom').setPen(pg.mkPen('#555555', width=1))
            p.showGrid(x=True, y=True, alpha=0.2)
            p.addLegend(offset=(10, 10))

            m1 = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('#ffeb3b', width=2))
            m2 = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('#00e5ff', width=2))
            m1.sigDragged.connect(self.update_marker_results)
            m2.sigDragged.connect(self.update_marker_results)
            m1.hide();
            m2.hide()

            p.addItem(m1);
            p.addItem(m2)
            self.plots.append(p)
            self.cursors_m1.append(m1)
            self.cursors_m2.append(m2)

        self.update_grid_layout(0)
        self.highlight_selected_plot()

    def setup_marker_table(self):
        props = ["Time M1 (s)", "Time M2 (s)", "Delta T (s)", "Freq (Hz)", "Value M1", "Value M2"]
        self._updating_table = True
        for i, p in enumerate(props):
            self.tbl_marker.setItem(i, 0, QTableWidgetItem(p))
            item_val = QTableWidgetItem("--")
            if i not in [0, 1]: item_val.setFlags(item_val.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tbl_marker.setItem(i, 1, item_val)
        self._updating_table = False

    def on_marker_manual_input(self, item):
        if self._updating_table or item.column() != 1: return
        row = item.row()
        if row not in [0, 1]: return
        try:
            val = float(item.text())
            if row == 0:
                for m in self.cursors_m1: m.setValue(val)
            elif row == 1:
                for m in self.cursors_m2: m.setValue(val)
            self.update_marker_results()
        except ValueError:
            pass

    def handle_scene_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.scenePos()
            for i, p in enumerate(self.plots):
                if p.vb.sceneBoundingRect().contains(pos):
                    self.on_plot_clicked(i)
                    break

    def on_plot_clicked(self, idx):
        self.selected_plot_idx = idx
        self.highlight_selected_plot()
        self.update_marker_visibility()
        self.update_marker_results()

    def highlight_selected_plot(self):
        for i, p in enumerate(self.plots):
            is_sel = (i == self.selected_plot_idx)
            p.showAxis('top', show=False)
            p.showAxis('right', show=False)
            if is_sel:
                p.setLabel('top', f"Scope {i + 1} ", color='#00ff00', bold=True)
                p.vb.setBorder(pg.mkPen('#00ff00', width=2))
            else:
                p.setLabel('top', f"Scope {i + 1}", color='#888', bold=False)
                p.vb.setBorder(pg.mkPen('#444444', width=1))

    def toggle_markers(self, state):
        self.markers_enabled = (state == Qt.CheckState.Checked.value)
        self.update_marker_visibility()
        if not self.markers_enabled:
            self.setup_marker_table()
        else:
            self.update_marker_results()

    def update_marker_visibility(self):
        for i in range(4):
            is_sel = (i == self.selected_plot_idx)
            show = is_sel and self.markers_enabled
            self.cursors_m1[i].setVisible(show)
            self.cursors_m2[i].setVisible(show)
            self.cursors_m1[i].setMovable(show and self.is_paused)
            self.cursors_m2[i].setMovable(show and self.is_paused)

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.btn_pause.setText("▶ RESUME PLOT" if self.is_paused else "⏸ PAUSE TO MEASURE")
        self.btn_pause.setStyleSheet(
            f"background: {'#28a745' if self.is_paused else '#d97706'}; font-weight: bold; padding: 8px 15px; border-radius: 4px;")
        self.update_marker_visibility()

    def get_y_values_at_x(self, x_val):
        """ TÌM GIÁ TRỊ Y CỦA CÁC ĐƯỜNG CONG TẠI VỊ TRÍ MARKER (X) """
        res = []
        for var_name, info in self.curves.items():
            if info['p_idx'] == self.selected_plot_idx:
                x_data, y_data = info['curve'].getData()
                if x_data is not None and len(x_data) > 0:
                    # Tìm index có giá trị X gần với Marker nhất
                    idx = (np.abs(x_data - x_val)).argmin()
                    res.append(f"{var_name}: {y_data[idx]:.4g}")
        return " | ".join(res) if res else "--"

    def update_marker_results(self):
        if not self.markers_enabled: return
        self._updating_table = True

        idx = self.selected_plot_idx
        t1 = self.cursors_m1[idx].value()
        t2 = self.cursors_m2[idx].value()
        dt = abs(t2 - t1)
        freq = 1 / dt if dt > 0 else 0

        # Đọc giá trị Y từ Data Array thực tế
        val_m1 = self.get_y_values_at_x(t1)
        val_m2 = self.get_y_values_at_x(t2)

        self.tbl_marker.item(0, 1).setText(f"{t1:.8g}")
        self.tbl_marker.item(1, 1).setText(f"{t2:.8g}")
        self.tbl_marker.item(2, 1).setText(f"{dt:.8g}")
        self.tbl_marker.item(3, 1).setText(f"{freq:.2f}")
        self.tbl_marker.item(4, 1).setText(val_m1)
        self.tbl_marker.item(5, 1).setText(val_m2)

        self._updating_table = False

    def update_grid_layout(self, index):
        self.gw.clear()
        if index == 0:
            self.gw.addItem(self.plots[0], row=0, col=0)
        elif index == 1:
            self.gw.addItem(self.plots[0], row=0, col=0);
            self.gw.addItem(self.plots[1], row=1, col=0)
        else:
            self.gw.addItem(self.plots[0], row=0, col=0);
            self.gw.addItem(self.plots[1], row=0, col=1)
            self.gw.addItem(self.plots[2], row=1, col=0);
            self.gw.addItem(self.plots[3], row=1, col=1)
        self.highlight_selected_plot()

    def update_available_vars(self, var_name, is_checked):
        if is_checked:
            rows = self.tbl_vars.rowCount()
            self.tbl_vars.insertRow(rows)
            self.tbl_vars.setItem(rows, 0, QTableWidgetItem(var_name))

            cb_target = QComboBox()
            cb_target.addItems(["None", "Scope 1", "Scope 2", "Scope 3", "Scope 4"])
            cb_target.currentTextChanged.connect(lambda text, v=var_name: self.assign_var_to_plot(v, text))
            self.tbl_vars.setCellWidget(rows, 1, cb_target)

            cb_color = QComboBox()
            cb_color.addItems(self.color_list)
            cb_color.setCurrentText(self.color_list[rows % len(self.color_list)])
            cb_color.currentTextChanged.connect(lambda _, v=var_name: self.update_curve_style(v))
            self.tbl_vars.setCellWidget(rows, 2, cb_color)

            cb_width = QComboBox()
            cb_width.addItems(["1", "2", "3", "4", "5"])
            cb_width.setCurrentText("2")
            cb_width.currentTextChanged.connect(lambda _, v=var_name: self.update_curve_style(v))
            self.tbl_vars.setCellWidget(rows, 3, cb_width)

            cb_style = QComboBox()
            cb_style.addItems(["Solid", "Dash", "Dot", "DashDot"])
            cb_style.currentTextChanged.connect(lambda _, v=var_name: self.update_curve_style(v))
            self.tbl_vars.setCellWidget(rows, 4, cb_style)
        else:
            for i in range(self.tbl_vars.rowCount()):
                if self.tbl_vars.item(i, 0).text() == var_name:
                    self.tbl_vars.removeRow(i)
                    break
            self.assign_var_to_plot(var_name, "None")

    def update_curve_style(self, var_name):
        if var_name not in self.curves: return
        row = -1
        for i in range(self.tbl_vars.rowCount()):
            if self.tbl_vars.item(i, 0).text() == var_name:
                row = i;
                break
        if row == -1: return

        c_map = {"Green": "#00ff00", "Red": "#ff4757", "Cyan": "#00e5ff", "Yellow": "#ffeb3b", "Purple": "#9b59b6",
                 "Orange": "#ff9f43", "White": "#ffffff"}
        s_map = {"Solid": Qt.PenStyle.SolidLine, "Dash": Qt.PenStyle.DashLine, "Dot": Qt.PenStyle.DotLine,
                 "DashDot": Qt.PenStyle.DashDotLine}

        c_name = self.tbl_vars.cellWidget(row, 2).currentText()
        w_val = int(self.tbl_vars.cellWidget(row, 3).currentText())
        s_name = self.tbl_vars.cellWidget(row, 4).currentText()

        pen = pg.mkPen(color=c_map.get(c_name, '#fff'), width=w_val, style=s_map.get(s_name, Qt.PenStyle.SolidLine))
        self.curves[var_name]['curve'].setPen(pen)

    def assign_var_to_plot(self, var_name, target_text):
        if var_name in self.curves:
            old_p_idx = self.curves[var_name]['p_idx']
            old_plot = self.plots[old_p_idx]
            old_curve = self.curves[var_name]['curve']
            old_plot.legend.removeItem(old_curve)
            old_plot.removeItem(old_curve)
            del self.curves[var_name]

        if target_text != "None":
            p_idx = int(target_text.split(" ")[1]) - 1
            target_plot = self.plots[p_idx]
            curve = target_plot.plot(name=var_name)
            self.curves[var_name] = {'curve': curve, 'p_idx': p_idx}
            self.update_curve_style(var_name)

    # API BACKEND: Đẩy dữ liệu vào đồ thị
    def set_real_data(self, x_array, data_dict):
        if self.is_paused: return

        for var_name, info in self.curves.items():
            if var_name in data_dict:
                y_array = data_dict[var_name]
                min_len = min(len(x_array), len(y_array))

                if min_len > 1:
                    x_plot = x_array[-min_len:]
                    y_plot = y_array[-min_len:]

                    info['curve'].setData(x=x_plot, y=y_plot)
                    p_idx = info['p_idx']
                    target_plot = self.plots[p_idx]
                    if len(x_plot) > 0:
                        current_x_max = x_plot[-1]
                        target_plot.setXRange(current_x_max - 5, current_x_max, padding=0)


class WebBridge(QObject):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

    def parse_elf_file_real(self, file_path):
        from elftools.elf.elffile import ELFFile
        from elftools.elf.sections import SymbolTableSection

        symbols_dict = {}
        try:
            with open(file_path, 'rb') as f:
                elffile = ELFFile(f)

                # Bước 1: Quét nhanh bảng mã Symbol tĩnh để lấy Địa chỉ và Kích thước byte
                for section in elffile.iter_sections():
                    if isinstance(section, SymbolTableSection):
                        for symbol in section.iter_symbols():
                            if symbol['st_info']['type'] == 'STT_OBJECT' and symbol['st_size'] > 0:
                                var_name = symbol.name
                                byte_size = symbol['st_size']

                                # Dự phòng kiểu dữ liệu dựa trên kích thước byte nếu file không chứa mã debug
                                auto_type = "float32" if byte_size == 4 else ("int16" if byte_size == 2 else "uint8")
                                symbols_dict[var_name] = {"addr": hex(symbol['st_value']), "type": auto_type}

                # Bước 2: THO MÒ DWARF CẤU TRÚC (Giống y hệt STM32 CubeProgrammer)
                if elffile.has_dwarf_info():
                    print("[ELF Explorer] Đang bóc tách phân vùng DWARF để tìm Type chuẩn...")
                    dwarfinfo = elffile.get_dwarf_info()

                    for CU in dwarfinfo.iter_CUs():  # Duyệt qua các file .c thành phần
                        # Xây dựng bảng tra cứu nhanh các Node thông tin (DIE)
                        die_by_offset = {die.offset: die for die in CU.iter_DIEs()}

                        for die in die_by_offset.values():
                            # Nếu Node này khai báo một biến toàn cục
                            if die.tag == 'DW_TAG_variable' and 'DW_AT_name' in die.attributes:
                                var_name = die.attributes['DW_AT_name'].value.decode('utf-8', errors='ignore')

                                # Nếu biến này nằm trong danh sách cần giám sát
                                if var_name in symbols_dict and 'DW_AT_type' in die.attributes:
                                    type_offset = die.attributes['DW_AT_type'].value + CU.cu_offset

                                    # Gọi hàm giải mã đệ quy để xuyên qua các lớp typedef (ví dụ: uint8_t -> unsigned char)
                                    base_type_die = self.resolve_dwarf_type(die_by_offset, type_offset)

                                    if base_type_die and 'DW_AT_name' in base_type_die.attributes:
                                        raw_type_name = base_type_die.attributes['DW_AT_name'].value.decode('utf-8',
                                                                                                            errors='ignore').lower()

                                        # Ánh xạ từ kiểu dữ liệu C thuần sang kiểu dữ liệu của hệ thống DAQ
                                        if "float" in raw_type_name:
                                            mapped_type = "float32"
                                        elif "unsigned char" in raw_type_name or "uint8" in raw_type_name:
                                            mapped_type = "uint8"
                                        elif "char" in raw_type_name or "int8" in raw_type_name:
                                            mapped_type = "int8"
                                        elif "unsigned short" in raw_type_name or "uint16" in raw_type_name:
                                            mapped_type = "uint16"
                                        elif "short" in raw_type_name or "int16" in raw_type_name:
                                            mapped_type = "int16"
                                        elif "unsigned int" in raw_type_name or "uint32" in raw_type_name or "unsigned long" in raw_type_name:
                                            mapped_type = "uint32"
                                        else:
                                            mapped_type = "int32"

                                        # Ghi đè kiểu dữ liệu xịn từ DWARF vào bản đồ biến
                                        symbols_dict[var_name]["type"] = mapped_type
        except Exception as e:
            print(f"Lỗi phân tích file ELF/DWARF: {e}")
        return symbols_dict

    # THÊM HÀM PHỤ TRỢ ĐỆ QUY NÀY NGAY PHÍA DƯỚI HÀM TRÊN
    def resolve_dwarf_type(self, die_by_offset, type_offset):
        current_die = die_by_offset.get(type_offset)
        while current_die:
            if current_die.tag == 'DW_TAG_base_type':
                return current_die
            elif current_die.tag in ('DW_TAG_typedef', 'DW_TAG_const_type', 'DW_TAG_volatile_type'):
                if 'DW_AT_type' in current_die.attributes:
                    next_offset = current_die.attributes['DW_AT_type'].value + current_die.cu.cu_offset
                    current_die = die_by_offset.get(next_offset)
                else:
                    break
            else:
                break
        return None

    @pyqtSlot()
    def js_request_sync(self):
        json_str = json.dumps(self.main_app.mapping_data)
        self.main_app.web.page().runJavaScript(f"syncConfig({json_str});")

    @pyqtSlot()
    def js_load_elf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_app,
            "Chọn file Firmware ELF",
            "",
            "ELF Files (*.elf *.out);;All Files (*)"
        )

        if file_path:
            # Gọi hàm đọc ELF thật
            elf_symbols = self.parse_elf_file_real(file_path)

            if not elf_symbols:
                QMessageBox.warning(self.main_app, "Lỗi", "Không tìm thấy biến toàn cục nào trong file ELF này.")
                return

            self.main_app.mapping_data = config_manager.sync_addresses_with_elf(self.main_app.mapping_data, elf_symbols)
            elf_json = json.dumps(elf_symbols)
            self.main_app.web.page().runJavaScript(f"syncElf({elf_json});")
            self.js_request_sync()
            QMessageBox.information(self.main_app, "Thành công",
                                    f"Đã nạp file ELF:\n{os.path.basename(file_path)}\nTìm thấy {len(elf_symbols)} biến.")

    @pyqtSlot(str, str, str, str)
    def js_save_mapping(self, block, var_name, var_addr, var_type):
        self.main_app.mapping_data = config_manager.add_var_to_block(self.main_app.mapping_data, block, var_name,
                                                                     var_addr, var_type)
        try:
            self.main_app.cmd_socket.send_string("RELOAD")
            print("[Python GUI] ---> HOT-RELOAD UPDATE MAPING RAM!")
        except Exception as e:
            print(f"[Python GUI] KHONG THE GUI LENH RELOAD JSON: {e}")

    @pyqtSlot(str, str)
    def js_remove_mapping(self, block, var_name):
        self.main_app.mapping_data = config_manager.remove_var_from_block(self.main_app.mapping_data, block, var_name)

    @pyqtSlot(str, bool)
    def js_toggle_var_to_plot(self, var_name, is_checked):
        self.main_app.plot_win.update_available_vars(var_name, is_checked)

    @pyqtSlot()
    def js_open_plot_window(self):
        self.main_app.plot_win.show()
        self.main_app.plot_win.raise_()

    @pyqtSlot(bool)
    def js_toggle_pause(self, is_paused):
        if self.main_app.app_state != 'review':
            self.main_app.app_state = 'paused' if is_paused else 'realtime'

    @pyqtSlot()
    def js_save_csv(self):
        QMessageBox.information(self.main_app, "Lưu Data", "Dữ liệu đồ thị đã được xuất ra file CSV thành công!")

    @pyqtSlot()
    def js_load_csv(self):
        file_name, _ = QFileDialog.getOpenFileName(self.main_app, "Mở file CSV Data", "",
                                                   "CSV Files (*.csv);;All Files (*)")
        if file_name:
            self.main_app.app_state = 'review'
            self.main_app.web.page().runJavaScript("setAppMode('review');")

    @pyqtSlot(str, str, str)
    def js_write_data(self, addr_hex, val_str, data_type):
        try:
            # Gửi nguyên văn mọi thứ xuống C++ để C++ tự ép kiểu phần cứng
            payload = json.dumps({"addr": addr_hex, "val_str": val_str, "type": data_type})
            self.main_app.cmd_socket.send_string("WRITE", zmq.SNDMORE)
            self.main_app.cmd_socket.send_string(payload)
        except Exception as e:
            print(f"Lỗi gửi lệnh ghi: {e}")


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STM32 SCOPE")
        self.resize(1400, 850)

        self.plot_win = PlotWindow()
        self.app_state = 'offline'
        self.mapping_data = config_manager.load_mapping()

        self.web = QWebEngineView()
        self.channel = QWebChannel()
        self.bridge = WebBridge(self)
        self.channel.registerObject("py_bridge", self.bridge)
        self.web.page().setWebChannel(self.channel)

        path = os.path.abspath("foc_diagram.html")
        self.web.setUrl(QUrl.fromLocalFile(path))
        self.setCentralWidget(self.web)

        # BỘ NHỚ ĐỆM ĐỒ THỊ
        self.max_points = 500
        self.x_history = []
        self.y_history = {}

        # 1. KẾT NỐI ZMQ
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://127.0.0.1:5556")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "DATA")

        # 2. BỘ ĐỊNH THỜI VẼ ĐỒ THỊ 30 FPS
        self.timer = QTimer()
        self.timer.timeout.connect(self.poll_and_update_gui)
        self.timer.start(30)

        self.cmd_context = zmq.Context()
        self.cmd_socket = self.cmd_context.socket(zmq.PUB)
        self.cmd_socket.bind("tcp://127.0.0.1:5557")

    def poll_and_update_gui(self):
        has_new_data = False
        latest_payload = None
        data_dict = None

        # 1. HÚT DỮ LIỆU
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
                break  # Đã hút hết dữ liệu
            except Exception as e:
                print(f"\n[DEBUG LỖI MẠNG ZMQ]: {e}")
                break

        # 2. XỬ LÝ VÀ IN LOG DEBUG NẾU CÓ DỮ LIỆU
        if has_new_data and latest_payload:
            # --- KHU VỰC IN LOG RA TERMINAL ---
            # print(f"\n[DEBUG] Đã nhận Data: {latest_payload['data']}")

            danh_sach_duong_ve = list(self.plot_win.curves.keys())
            # print(f"[DEBUG] Đồ thị đang được cài để vẽ các biến này: {danh_sach_duong_ve}")

            if len(danh_sach_duong_ve) == 0:
                print(
                    " >>> [CẢNH BÁO]: BẠN CHƯA GÁN 'TARGET'. HÃY NHÌN SANG BẢNG BÊN PHẢI GIAO DIỆN, CHỌN TARGET LÀ 'SCOPE 1' <<<")

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

        # READ DATA
        if data_dict:
            json_str = json.dumps(data_dict)
            self.web.page().runJavaScript(f"updateReadDataFromPython('{json_str}')")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainApp()
    window.show()
    sys.exit(app.exec())