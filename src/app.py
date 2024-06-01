import sys
import serial
import time
import PySide6


from PySide6.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QTableWidgetItem
from src.main import Ui_MainWindow
from src.utilites import get_com_ports
from crc_16_ccitt import crc_ccitt_16_kermit_b, revers_bytes, add_crc
from src.server import Server485


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тестер СКИУ")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_param_default()
        self.ui.connect_btn.clicked.connect(self._connect_01)
        self.ui.close_btn.clicked.connect(self._close)
        self.ui.connect_ckiu_2_btn.clicked.connect(self._connect_02)
        self.ui.close_ckiu_2_btn.clicked.connect(self._close)
        self.ports = []
        self.messages = []
        self.sn = None
        self.ports_out()
        self.speeds_out()
        self.conn = None
        self.server = None

    def setup_param_default(self):
        # ===================================
        self.ui.sn_lineEdit.setText("35690")
        self.ui.sn_lineEdit.setText("10411")
        # ===================================

        self.ui.in1_t_pos_imp_lineEdit.setText("0")
        self.ui.in1_t_neg_imp_lineEdit.setText("0")
        self.ui.in2_t_pos_imp_lineEdit.setText("0")
        self.ui.in2_t_neg_imp_lineEdit.setText("0")
        self.ui.in3_t_pos_imp_lineEdit.setText("0")
        self.ui.in3_t_neg_imp_lineEdit.setText("0")
        self.ui.in4_t_pos_imp_lineEdit.setText("0")
        self.ui.in4_t_neg_imp_lineEdit.setText("0")

    def ports_out(self):
        self.ports = get_com_ports()
        for port in self.ports:
            self.ui.port_comboBox.addItem(port[1])

    def speeds_out(self):
        self.ui.speed_comboBox.addItem("19200")
        self.ui.speed_comboBox.addItem("9600")

    def _connect_01(self):
        ...
        # port_name = None
        # port_in = self.ui.port_comboBox.currentText()
        # for port in self.ports:
        #     if port[1] == port_in:
        #         port_name = port[0]
        # speed = self.ui.speed_comboBox.currentText()
        # conn = serial.Serial(port=port_name, baudrate=speed, timeout=1)
        # self.sn = int(self.ui.sn_lineEdit.text())
        # if conn.is_open:
        #     self.conn = conn
        #     self.ui.state_lbl.setStyleSheet("QLabel {background-color: #36f207;}")
        #     self.ui.connect_btn.setStyleSheet("QLabel {background-color: #36f207;}")
        #     msg = bytearray(b"\xb6\x49\x08\x6a\x8b\x09\x81\x0a\x0a\x00\x00\x00\x00\x00\x00")
        #     crc = crc_ccitt_16_kermit_b(msg)
        #     c = add_crc(msg, crc)
        #     for _ in range(100):
        #         # Вывести в отдельный тред и уменьшить частоту отправки пакета
        #         self.conn.write(c)
        # else:
        #     self.ui.state_lbl.setStyleSheet("QLabel {background-color : #f01;}")

    def _close(self):
        if self.conn != None:
            self.conn.close()
            self.ui.state_lbl.setStyleSheet("QLabel {background-color : #f01;}")

    def _connect_02(self):
        """Запуск сканера для СКИУ-02"""
        port_name = None
        port_in = self.ui.port_comboBox.currentText()
        self.sn = int(self.ui.sn_lineEdit.text())
        for port in self.ports:
            if port[1] == port_in:
                port_name = port[0]
        speed = self.ui.speed_comboBox.currentText()
        self.conn = serial.Serial(port=port_name, baudrate=speed, timeout=1)
        if self.conn.is_open:
            self.ui.state_lbl.setStyleSheet("QLabel {background-color: #36f207;}")
            self.request_version_ckiu_02()
            self.request_scan_ckiu_02()
            if self.ui.version_acp_radioButton.isChecked():
                self.request_acp_ckiu_02_old()
            if self.ui.version_ibp_radioButton.isChecked():
                self.request_acp_ckiu_02_ibp()
            self.server = Server485(self. conn, port_name, speed, self.messages)
            self.server.start()
        else:
            self.ui.state_lbl.setStyleSheet("QLabel {background-color : #f01;}")

    def request_version_ckiu_02(self):
        msg = bytearray(b"\xb6\x49\x1b")
        # self.sn = int(self.ui.sn_lineEdit.text())
        msg.append(self.sn % 256)
        msg.append(self.sn // 256)
        msg.append(1)       # 01
        msg.append(128)     # 80
        msg = add_crc(msg, crc_ccitt_16_kermit_b(msg)) # +crc
        self.messages.append(msg)
        # print(msg.hex())

    def request_scan_ckiu_02(self):
        in1_t_pos_imp_lineEdit = int(self.ui.in1_t_pos_imp_lineEdit.text()) * 100
        in1_t_neg_imp_lineEdit = int(self.ui.in1_t_neg_imp_lineEdit.text()) * 100
        in2_t_pos_imp_lineEdit = int(self.ui.in2_t_pos_imp_lineEdit.text()) * 100
        in2_t_neg_imp_lineEdit = int(self.ui.in2_t_neg_imp_lineEdit.text()) * 100
        in3_t_pos_imp_lineEdit = int(self.ui.in3_t_pos_imp_lineEdit.text()) * 100
        in3_t_neg_imp_lineEdit = int(self.ui.in3_t_neg_imp_lineEdit.text()) * 100
        in4_t_pos_imp_lineEdit = int(self.ui.in4_t_pos_imp_lineEdit.text()) * 100
        in4_t_neg_imp_lineEdit = int(self.ui.in4_t_neg_imp_lineEdit.text()) * 100
        msg = bytearray(b"\xb6\x49\x1b")
        # self.sn = int(self.ui.sn_lineEdit.text())
        msg.append(self.sn % 256)
        msg.append(self.sn // 256)
        msg.append(9)  # 09
        msg.append(129)  # 81
        msg.append(in1_t_pos_imp_lineEdit)    #
        msg.append(in1_t_neg_imp_lineEdit)    #
        msg.append(in2_t_pos_imp_lineEdit)    #
        msg.append(in2_t_neg_imp_lineEdit)    #
        msg.append(in3_t_pos_imp_lineEdit)    #
        msg.append(in3_t_neg_imp_lineEdit)    #
        msg.append(in4_t_pos_imp_lineEdit)    #
        msg.append(in4_t_neg_imp_lineEdit)    #
        msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))  # +crc
        self.messages.append(msg)
        # print(msg.hex())

    def request_acp_ckiu_02_old(self):
        msg = bytearray(b"\xb6\x49\x1b")
        msg.append(self.sn % 256)
        msg.append(self.sn // 256)
        msg.append(1)  # 01
        msg.append(130)  # 82
        msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))  # +crc
        self.messages.append(msg)
        # print(msg.hex())

    def request_acp_ckiu_02_ibp(self):
        msg = bytearray(b"\xb6\x49\x1b")
        msg.append(self.sn % 256)
        msg.append(self.sn // 256)
        msg.append(1)  # 01
        msg.append(131)  # 83
        msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))  # +crc
        self.messages.append(msg)
        # print(msg.hex())

    def request_rebut_ckiu_02(self):
        msg = bytearray(b"\xb6\x49\x1b")
        msg.append(self.sn % 256)
        msg.append(self.sn // 256)
        msg.append(1)  # 01
        msg.append(209)  # D1
        msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))  # +crc
        self.messages.append(msg)
        # print(msg.hex())

    def request_str_debug(self):
        msg = bytearray(b"\xb6\x49\x1b")
        msg.append(self.sn % 256)
        msg.append(self.sn // 256)
        msg.append(1)  # 05
        msg.append(163)  # A3
        num_str = 0
        msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))  # +crc
        self.messages.append(msg)
        # print(msg.hex())

    def handler_responses_ckiu_02(self):
        ...

    def run_process(self):
        ...



if __name__ == "__main__":
    app = QApplication([])
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())