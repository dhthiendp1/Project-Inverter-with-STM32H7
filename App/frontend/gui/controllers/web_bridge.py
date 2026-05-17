import json
import os
import zmq
from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtWidgets import QFileDialog, QMessageBox

import config_manager
from utils.elf_parser import ElfParser


class WebBridge(QObject):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

    def _get_json_path(self):
        """Lấy đường dẫn tuyệt đối của block_mapping.json để chống lỗi Path Mismatch khi khởi động lại"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        return os.path.join(parent_dir, "block_mapping.json")

    def _save_json(self):
        """Hàm dùng chung để lưu ngay cấu trúc mapping xuống ổ cứng chuẩn xác"""
        json_path = self._get_json_path()
        try:
            with open(json_path, 'w') as f:
                json.dump(self.main_app.mapping_data, f, indent=4)
        except Exception as e:
            print(f"[Lỗi] Không thể ghi file JSON: {e}")

    @pyqtSlot()
    def js_request_sync(self):
        # FIX LỖI MẤT BIẾN KHI KHỞI ĐỘNG LẠI:
        # Ép đọc trực tiếp từ đường dẫn tuyệt đối để đè lên dữ liệu có thể bị lỗi của config_manager
        json_path = self._get_json_path()
        try:
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    self.main_app.mapping_data = json.load(f)
        except Exception as e:
            print(f"[Cảnh báo] Lỗi đọc JSON đồng bộ: {e}")

        json_str = json.dumps(self.main_app.mapping_data)
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

            self.main_app.mapping_data = config_manager.sync_addresses_with_elf(self.main_app.mapping_data, elf_symbols)
            self._save_json()  # Đồng bộ xong cũng phải lưu
            elf_json = json.dumps(elf_symbols)
            self.main_app.web.page().runJavaScript(f"syncElf({elf_json});")
            self.js_request_sync()
            QMessageBox.information(self.main_app, "Thành công",
                                    f"Đã nạp file ELF:\n{os.path.basename(file_path)}\nTìm thấy {len(elf_symbols)} biến.")

    @pyqtSlot(str)
    def js_add_block(self, block_id):
        if block_id not in self.main_app.mapping_data:
            self.main_app.mapping_data[block_id] = []
            self._save_json()
            print(f"[Backend] Đã tạo Block mới: {block_id}")

    @pyqtSlot(str)
    def js_remove_block(self, block_id):
        if block_id in self.main_app.mapping_data:
            del self.main_app.mapping_data[block_id]

        # Bắt buộc lưu đè file JSON để xóa triệt để
        self._save_json()
        try:
            self.main_app.cmd_socket.send_string("RELOAD")
        except Exception:
            pass
        print(f"[Backend] Đã xóa hoàn toàn Block: {block_id}")

    @pyqtSlot(str, str, str, str)
    def js_save_mapping(self, block, var_name, var_addr, var_type):
        self.main_app.mapping_data = config_manager.add_var_to_block(self.main_app.mapping_data, block, var_name,
                                                                     var_addr, var_type)
        self._save_json()  # Bắt buộc phải lưu khi thêm biến
        try:
            self.main_app.cmd_socket.send_string("RELOAD")
        except Exception as e:
            print(f"[Python GUI] Lỗi gửi lệnh RELOAD: {e}")

    @pyqtSlot(str, str)
    def js_remove_mapping(self, block, var_name):
        self.main_app.mapping_data = config_manager.remove_var_from_block(self.main_app.mapping_data, block, var_name)
        self._save_json()  # Bắt buộc phải lưu khi xóa biến

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
            x_data = self.main_app.x_history
            y_data = self.main_app.y_history

            if not x_data:
                QMessageBox.warning(self.main_app, "Trống", "Biểu đồ đang trống, không có dữ liệu để lưu!")
                return

            headers = ["Time (s)"] + list(y_data.keys())

            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                for i in range(len(x_data)):
                    row = [x_data[i]]
                    for var_name in y_data.keys():
                        row.append(y_data[var_name][i] if i < len(y_data[var_name]) else 0.0)
                    writer.writerow(row)

            QMessageBox.information(self.main_app, "Thành công", f"Đã xuất thành công {len(x_data)} dòng dữ liệu!")
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
        except Exception as e:
            print(f"Lỗi gửi lệnh ghi: {e}")