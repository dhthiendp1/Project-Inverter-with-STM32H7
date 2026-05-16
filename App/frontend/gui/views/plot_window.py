import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                             QComboBox, QSplitter, QPushButton, QCheckBox)
from PyQt6.QtCore import Qt


class PlotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCOPE")
        self.resize(1300, 800)
        self.setStyleSheet("background-color: #121212; color: #ddd;")

        self.is_paused = False
        self.active_scope_index = 0
        self.markers_enabled = False
        self._updating_table = False

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

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

        self.right_sidebar = QWidget()
        side_layout = QVBoxLayout(self.right_sidebar)
        side_layout.setContentsMargins(5, 0, 5, 5)

        side_layout.addWidget(QLabel("VARIABLES & STYLE"))
        self.tbl_vars = QTableWidget(0, 5)
        self.tbl_vars.setHorizontalHeaderLabels(["Var", "Plot", "Color", "Width", "Style"])
        self.tbl_vars.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tbl_vars.setColumnWidth(0, 80)
        self.tbl_vars.setColumnWidth(1, 40)
        self.tbl_vars.setColumnWidth(2, 80)
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
            m1.hide()
            m2.hide()

            p.addItem(m1)
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
        self.active_scope_index = idx
        self.highlight_selected_plot()
        self.update_marker_visibility()
        self.update_marker_results()
        self.update_var_table_checkboxes()

    def highlight_selected_plot(self):
        for i, p in enumerate(self.plots):
            is_sel = (i == self.active_scope_index)
            p.showAxis('top', show=False)
            p.showAxis('right', show=False)
            if is_sel:
                p.setLabel('top', f"Scope {i + 1} ", color='#00ff00', bold=True)
                p.vb.setBorder(pg.mkPen('#00ff00', width=3))
            else:
                p.setLabel('top', f"Scope {i + 1}", color='#888', bold=False)
                p.vb.setBorder(pg.mkPen('#333333', width=1))

    def toggle_markers(self, state):
        self.markers_enabled = (state == Qt.CheckState.Checked.value)
        self.update_marker_visibility()
        if not self.markers_enabled:
            self.setup_marker_table()
        else:
            self.update_marker_results()

    def update_marker_visibility(self):
        for i in range(4):
            is_sel = (i == self.active_scope_index)
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
        res = []
        for var_name, scope_curves in self.curves.items():
            if self.active_scope_index in scope_curves:
                curve = scope_curves[self.active_scope_index]
                x_data, y_data = curve.getData()
                if x_data is not None and len(x_data) > 0:
                    idx = (np.abs(x_data - x_val)).argmin()
                    res.append(f"{var_name}: {y_data[idx]:.4g}")
        return " | ".join(res) if res else "--"

    def update_marker_results(self):
        if not self.markers_enabled: return
        self._updating_table = True

        idx = self.active_scope_index
        t1 = self.cursors_m1[idx].value()
        t2 = self.cursors_m2[idx].value()
        dt = abs(t2 - t1)
        freq = 1 / dt if dt > 0 else 0

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
            self.gw.addItem(self.plots[0], row=0, col=0)
            self.gw.addItem(self.plots[1], row=1, col=0)
        else:
            self.gw.addItem(self.plots[0], row=0, col=0)
            self.gw.addItem(self.plots[1], row=0, col=1)
            self.gw.addItem(self.plots[2], row=1, col=0)
            self.gw.addItem(self.plots[3], row=1, col=1)
        self.highlight_selected_plot()

    def update_available_vars(self, var_name, is_checked):
        if is_checked:
            for row in range(self.tbl_vars.rowCount()):
                if self.tbl_vars.item(row, 0).text() == var_name: return

            rows = self.tbl_vars.rowCount()
            self.tbl_vars.insertRow(rows)
            self.tbl_vars.setItem(rows, 0, QTableWidgetItem(var_name))

            chk_box = QCheckBox()
            chk_widget = QWidget()
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.addWidget(chk_box)
            chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            self.tbl_vars.setCellWidget(rows, 1, chk_widget)

            chk_box.stateChanged.connect(lambda state, name=var_name: self.on_plot_toggled(name, state))

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

            if var_name in self.curves:
                for scope_idx, curve in list(self.curves[var_name].items()):
                    try:
                        self.plots[scope_idx].legend.removeItem(curve)
                    except:
                        pass
                    self.plots[scope_idx].removeItem(curve)
                del self.curves[var_name]

    def on_plot_toggled(self, var_name, state):
        scope_idx = self.active_scope_index
        if var_name not in self.curves:
            self.curves[var_name] = {}

        if state == 2:
            if scope_idx not in self.curves[var_name]:
                target_plot = self.plots[scope_idx]
                curve = target_plot.plot(name=var_name)
                self.curves[var_name][scope_idx] = curve
                self.update_curve_style(var_name)
        else:
            if scope_idx in self.curves[var_name]:
                old_plot = self.plots[scope_idx]
                old_curve = self.curves[var_name][scope_idx]
                try:
                    old_plot.legend.removeItem(old_curve)
                except:
                    pass
                old_plot.removeItem(old_curve)
                del self.curves[var_name][scope_idx]

            if len(self.curves[var_name]) == 0:
                del self.curves[var_name]

    def update_var_table_checkboxes(self):
        for row in range(self.tbl_vars.rowCount()):
            var_name = self.tbl_vars.item(row, 0).text()
            chk_widget = self.tbl_vars.cellWidget(row, 1)
            if chk_widget:
                chk_box = chk_widget.findChild(QCheckBox)
                if chk_box:
                    chk_box.blockSignals(True)
                    if var_name in self.curves and self.active_scope_index in self.curves[var_name]:
                        chk_box.setChecked(True)
                    else:
                        chk_box.setChecked(False)
                    chk_box.blockSignals(False)

    def update_curve_style(self, var_name):
        if var_name not in self.curves: return
        row = -1
        for i in range(self.tbl_vars.rowCount()):
            if self.tbl_vars.item(i, 0).text() == var_name:
                row = i
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

        for scope_idx, curve in self.curves[var_name].items():
            curve.setPen(pen)

    def set_real_data(self, x_array, data_dict):
        if self.is_paused: return

        for var_name, scope_curves in self.curves.items():
            if var_name in data_dict:
                y_array = data_dict[var_name]
                min_len = min(len(x_array), len(y_array))

                if min_len > 1:
                    x_plot = x_array[-min_len:]
                    y_plot = y_array[-min_len:]

                    for scope_idx, curve in scope_curves.items():
                        curve.setData(x=x_plot, y=y_plot)
                        target_plot = self.plots[scope_idx]
                        if len(x_plot) > 0:
                            current_x_max = x_plot[-1]
                            target_plot.setXRange(current_x_max - 5, current_x_max, padding=0)