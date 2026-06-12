import json
import os
import zmq
import subprocess
from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from utils.elf_parser import ElfParser


class WebBridge(QObject):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

    def _get_json_path(self):
        return os.path.join(self.main_app.data_dir, "block_mapping.json")

    def _save_json(self):
        json_path = self._get_json_path()
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.main_app.mapping_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[Lỗi] Không thể ghi file JSON: {e}")

    def _ensure_default_blocks(self):
        defaults = ['blk_pi_spd', 'blk_pi_iq', 'blk_pi_id', 'blk_cp', 'blk_svpwm', 'blk_inv', 'blk_pmsm', 'blk_sensor',
                    'blk_inv_cp']
        mod = False
        for b in defaults:
            if b not in self.main_app.mapping_data:
                self.main_app.mapping_data[b] = []
                mod = True
        if mod:
            self._save_json()

    @pyqtSlot()
    def js_toggle_backend(self):
        if self.main_app.backend_process is None:
            exe_path = os.path.join(self.main_app.base_dir, "backend_bin", "FOC_Backend_STM32.exe")
            if not os.path.exists(exe_path):
                QMessageBox.critical(self.main_app, "Lỗi",
                                     f"Không tìm thấy file:\n{exe_path}\n\nVui lòng copy FOC_Backend_STM32.exe vào thư mục backend_bin")
                return

            mapping_json_path = self._get_json_path()

            try:
                self.main_app.backend_process = subprocess.Popen([exe_path, mapping_json_path])
                self.main_app.web.page().runJavaScript("updateConnectBtn(true);")
            except Exception as e:
                QMessageBox.critical(self.main_app, "Lỗi", f"Không thể chạy file: {e}")
        else:
            try:
                self.main_app.backend_process.terminate()
                self.main_app.backend_process.wait(timeout=2)
            except Exception:
                self.main_app.backend_process.kill()
            self.main_app.backend_process = None
            self.main_app.web.page().runJavaScript("updateConnectBtn(false);")

    @pyqtSlot()
    def js_request_sync(self):
        json_path = self._get_json_path()
        try:
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.main_app.mapping_data = json.load(f)
            else:
                self.main_app.mapping_data = {}
        except Exception:
            self.main_app.mapping_data = {}

        self._ensure_default_blocks()
        json_str = json.dumps(self.main_app.mapping_data, ensure_ascii=False)
        self.main_app.web.page().runJavaScript(f"syncConfig({json_str});")

    @pyqtSlot()
    def js_load_elf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_app, "Chọn file Firmware ELF", "", "ELF Files (*.elf *.out);;All Files (*)"
        )
        if file_path:
            elf_symbols = ElfParser.parse_elf_file(file_path)
            if not elf_symbols:
                QMessageBox.warning(self.main_app, "Lỗi", "Không tìm thấy biến toàn cục nào trong file ELF này.")
                return

            for block, vars_list in self.main_app.mapping_data.items():
                for v in vars_list:
                    var_name = v['id']
                    if var_name in elf_symbols:
                        v['addr'] = elf_symbols[var_name]['addr']
                        v['type'] = elf_symbols[var_name]['type']

            self._save_json()
            elf_json = json.dumps(elf_symbols, ensure_ascii=False)
            self.main_app.web.page().runJavaScript(f"syncElf({elf_json});")
            self.js_request_sync()
            QMessageBox.information(self.main_app, "Thành công",
                                    f"Đã nạp file ELF:\n{os.path.basename(file_path)}\nTìm thấy {len(elf_symbols)} biến.")

    @pyqtSlot(str, str, str, str)
    def js_save_mapping(self, block, var_name, var_addr, var_type):
        if block not in self.main_app.mapping_data:
            self.main_app.mapping_data[block] = []
        exists = False
        for v in self.main_app.mapping_data[block]:
            if v['id'] == var_name:
                exists = True
                break
        if not exists:
            self.main_app.mapping_data[block].append({"id": var_name, "addr": var_addr, "type": var_type})

        self._save_json()
        try:
            self.main_app.cmd_socket.send_string("RELOAD")
        except Exception:
            pass

    @pyqtSlot(str, str)
    def js_remove_mapping(self, block, var_name):
        if block in self.main_app.mapping_data:
            self.main_app.mapping_data[block] = [v for v in self.main_app.mapping_data[block] if v['id'] != var_name]
        self._save_json()

        is_still_exist = False
        for blk_name, vars_list in self.main_app.mapping_data.items():
            for v in vars_list:
                if v.get('id') == var_name:
                    is_still_exist = True
                    break
            if is_still_exist: break

        if not is_still_exist:
            self.main_app.plot_win.update_available_vars(var_name, False)

        try:
            self.main_app.cmd_socket.send_string("RELOAD")
        except Exception:
            pass

    @pyqtSlot(str, bool)
    def js_toggle_var_to_plot(self, var_name, is_checked):
        self.main_app.plot_win.update_available_vars(var_name, is_checked)
        # Đồng bộ lại danh sách đã xác nhận từ plot_win về JS
        # Tránh JS lệch trạng thái nếu plot_win từ chối hoặc giới hạn số kênh
        try:
            current_vars = list(self.main_app.plot_win.get_plotted_vars())
            vars_json = json.dumps(current_vars)
            self.main_app.web.page().runJavaScript(f"syncPlottedVars({vars_json});")
        except Exception:
            pass

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
        file_path, _ = QFileDialog.getSaveFileName(self.main_app, "Lưu dữ liệu Scope", "FOC_Scope_Data.csv",
                                                   "CSV Files (*.csv)")
        if not file_path: return
        try:
            import csv
            temp_path = getattr(self.main_app, "temp_log_path", None)
            if not temp_path or not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                QMessageBox.warning(self.main_app, "Trống", "Không có dữ liệu nào được ghi nhận để lưu!")
                return

            keys = set()
            with open(temp_path, 'r') as f:
                for line in f:
                    record = json.loads(line)
                    keys.update(record.get("d", {}).keys())

            headers = ["Time (s)"] + sorted(list(keys))
            row_count = 0

            with open(file_path, mode='w', newline='') as out_f:
                writer = csv.writer(out_f)
                writer.writerow(headers)
                with open(temp_path, 'r') as in_f:
                    for line in in_f:
                        record = json.loads(line)
                        row = [record.get("t", 0.0)]
                        data_dict = record.get("d", {})
                        for k in headers[1:]:
                            row.append(data_dict.get(k, 0.0))
                        writer.writerow(row)
                        row_count += 1

            QMessageBox.information(self.main_app, "Thành công", f"Đã xuất thành công {row_count} dòng dữ liệu!")
        except Exception as e:
            QMessageBox.critical(self.main_app, "Lỗi", f"Không thể lưu file CSV: {e}")

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
            payload = json.dumps({"addr": addr_hex, "val_str": val_str, "type": data_type})
            self.main_app.cmd_socket.send_string("WRITE", zmq.SNDMORE)
            self.main_app.cmd_socket.send_string(payload)
        except Exception:
            pass