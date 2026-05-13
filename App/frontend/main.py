import sys
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
import zmq

class ZmqReceiverThread(QThread):
    data_received = pyqtSignal(object)

    def run(self):
        context = zmq.Context()
        subscriber = context.socket(zmq.SUB)
        subscriber.connect("tcp://127.0.0.1:5555")
        subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
        print("[Frontend] ZMQ Subscriber connected.")

        while not self.isInterruptionRequested():
            try:
                # Dùng NOBLOCK để Thread không bị treo nếu C++ dừng gửi
                raw_message = subscriber.recv(flags=zmq.NOBLOCK)
                
                # Zero-copy buffer parsing (STM32 là Little Endian, PC cũng vậy -> Ép kiểu trực tiếp)
                data_array = np.frombuffer(raw_message, dtype=np.float32)
                self.data_received.emit(data_array)
                
            except zmq.Again:
                self.msleep(1) # Nghỉ 1ms nếu chưa có data

class RealTimePlotter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SVPWM Real-Time Monitor (STM32H7)")
        self.resize(1200, 700)

        # UI Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Plot Widget Cấu hình cho High Performance
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground('#1e1e1e')
        self.graph_widget.showGrid(x=True, y=True, alpha=0.3)
        self.graph_widget.setYRange(-150, 150) # Giới hạn biên độ động cơ
        layout.addWidget(self.graph_widget)

        # Bút vẽ (Pen) mượt mà
        self.plot_curve = self.graph_widget.plot(pen=pg.mkPen(color='#00ff00', width=1.5))

        # Khởi tạo Ring Buffer (Lưu 10,000 điểm trên màn hình)
        self.display_size = 10000
        self.ring_buffer = np.zeros(self.display_size, dtype=np.float32)

        # Biến đệm tạm thời chứa data từ ZMQ trước khi Timer kéo ra vẽ
        self.new_data_buffer = np.array([], dtype=np.float32)

        # Thread nhận Data
        self.zmq_thread = ZmqReceiverThread()
        self.zmq_thread.data_received.connect(self.on_data_received)
        self.zmq_thread.start()

        # Timer vẽ đồ thị ở 60 FPS (~16ms)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(16)

    def on_data_received(self, data_array):
        # Dồn data mới vào bộ đệm tạm (Thread-safe cơ bản của Python GIL)
        self.new_data_buffer = np.append(self.new_data_buffer, data_array)

    def update_plot(self):
        n = len(self.new_data_buffer)
        if n == 0:
            return

        # Đẩy data vào Ring Buffer
        if n >= self.display_size:
            self.ring_buffer[:] = self.new_data_buffer[-self.display_size:]
        else:
            self.ring_buffer[:-n] = self.ring_buffer[n:]
            self.ring_buffer[-n:] = self.new_data_buffer
        
        # Xóa đệm tạm
        self.new_data_buffer = np.array([], dtype=np.float32)

        # Cập nhật đồ thị (Rất nhẹ vì chỉ gán lại tham chiếu mảng)
        self.plot_curve.setData(self.ring_buffer)

    def closeEvent(self, event):
        self.zmq_thread.requestInterruption()
        self.zmq_thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RealTimePlotter()
    window.show()
    sys.exit(app.exec())