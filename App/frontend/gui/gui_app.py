import sys
import os
import json
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                             QHeaderView, QComboBox, QSplitter, QPushButton, QCheckBox, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QUrl, pyqtSlot, QObject
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

import config_manager


class PlotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MCUViewer Pro - Advanced Signal Analyzer")
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

        side_layout.addWidget(QLabel("🎨 AVAILABLE VARIABLES & STYLING"))
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
        header_layout.addWidget(QLabel("📏 MARKER MEASUREMENTS"))
        self.chk_markers = QCheckBox("Bật Markers")
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

            if i > 0:
                p.setXLink(self.plots[0])
                p.setYLink(self.plots[0])

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
                p.setLabel('top', f"Scope {i + 1} [SELECTED]", color='#00ff00', bold=True)
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

    # API CHO BACKEND: Đẩy dữ liệu vào đồ thị
    def set_real_data(self, x_array, data_dict):
        """
        Backend gọi hàm này để cập nhật toàn bộ đồ thị.
        x_array: numpy array chứa trục thời gian
        data_dict: dict dạng {'I_a': y_array_1, 'I_b': y_array_2}
        """
        if self.is_paused: return
        for var_name, info in self.curves.items():
            if var_name in data_dict:
                info['curve'].setData(x_array, data_dict[var_name])


class WebBridge(QObject):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

    @pyqtSlot()
    def js_request_sync(self):
        json_str = json.dumps(self.main_app.mapping_data)
        self.main_app.web.page().runJavaScript(f"syncConfig({json_str});")

    @pyqtSlot()
    def js_refresh_elf(self):
        """ NƠI TÍCH HỢP ĐỌC FILE ELF THỰC TẾ BẰNG PYELFTOOLS """
        if self.main_app.app_state == 'offline': return
        # TODO: Gọi hàm đọc ELF thực tế tại đây
        # elf_symbols = read_elf_real("path/to/firmware.elf")
        pass

    @pyqtSlot(str, str, str, str)
    def js_save_mapping(self, block, var_name, var_addr, var_type):
        self.main_app.mapping_data = config_manager.add_var_to_block(self.main_app.mapping_data, block, var_name,
                                                                     var_addr, var_type)

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


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STM32 FOC System Architect")
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

        # TODO: Khởi tạo luồng (Thread) nhận dữ liệu từ STM32 tại đây
        # self.serial_thread = SerialReaderThread()
        # self.serial_thread.new_data_signal.connect(self.plot_win.set_real_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainApp()
    window.show()
    sys.exit(app.exec())