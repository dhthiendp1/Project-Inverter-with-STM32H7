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

    @pyqtSlot()
    def js_request_sync(self):
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
        except Exception as e:
            print(f"[Python GUI] Lỗi gửi lệnh RELOAD: {e}")

    @pyqtSlot(str, str)
    def js_remove_mapping(self, block, var_name):
        self.main_app.mapping_data = config_manager.remove_var_from_block(self.main_app.mapping_data, block, var_name)

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
        except Exception as e:
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
        QMessageBox.information(self.main_app, "SAVE DATA", "SCOPE EXPORT CSV SUCCESS!")

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