import sys
import serial


from PySide6 import QtGui
from PySide6.QtCore import Slot, QFile
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader

from src.main import Ui_MainWindow
from src.utilites import get_com_ports
from crc_16_ccitt import crc_ccitt_16_kermit_b, add_crc
from src.ckiu_02 import Server485


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тестер СКИУ")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.connect_btn.clicked.connect(self._connect_01)
        self.ui.close_btn.clicked.connect(self._close)
        self.ui.connect_ckiu_2_btn.clicked.connect(self._connect_02)
        self.ui.close_ckiu_2_btn.clicked.connect(self._close)
        self.ui.update_btn.clicked.connect(self._update_port)

        self.ports = []
        self.messages = []
        self.sn = None
        self._ports_out()
        self.speeds_out()
        self.conn = None
        self.server = None
        self.params = ["0"]
        self.count_err_conn = 0

        self._setup_param_default()

    def _setup_param_default(self):
        # ===================================
        self.ui.sn_lineEdit.setText("35690")
        self.ui.sn_lineEdit.setText("10411")
        # ===================================
        self.ui.version_old_ckiu_radioButton.setChecked(True)
        self.ui.in1_t_pos_imp_lineEdit.setText("0")
        self.ui.in1_t_neg_imp_lineEdit.setText("0")
        self.ui.in2_t_pos_imp_lineEdit.setText("0")
        self.ui.in2_t_neg_imp_lineEdit.setText("0")
        self.ui.in3_t_pos_imp_lineEdit.setText("0")
        self.ui.in3_t_neg_imp_lineEdit.setText("0")
        self.ui.in4_t_pos_imp_lineEdit.setText("0")
        self.ui.in4_t_neg_imp_lineEdit.setText("0")

    def _update_port(self):
        self.ui.port_comboBox.clear()
        self._ports_out()

    def _ports_out(self):
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
            self.server = None
            self.ui.state_lbl.setStyleSheet(
                "QLabel {background-color : #f01; border:4px solid rgb(109, 109, 109)}")
            self.ui.counter_err_conn_lcd.setStyleSheet(
                "QLCDNumber {background-color: #00557f;}")
            self.ui.counter_err_conn_lcd.display(0)
            self.count_err_conn = 0

    def _connect_02(self):
        """Запуск сканера для СКИУ-02"""
        self.count_err_conn = 0
        self.messages = []
        port_name = None
        port_in = self.ui.port_comboBox.currentText()
        self.sn = int(self.ui.sn_lineEdit.text())
        for port in self.ports:
            if port[1] == port_in:
                port_name = port[0]
        speed = self.ui.speed_comboBox.currentText()
        self.conn = serial.Serial(port=port_name, baudrate=speed, timeout=1)
        if self.conn.is_open:
            self.ui.state_lbl.setStyleSheet("QLabel {background-color: #36f207; border:4px solid rgb(109, 109, 109)}")
            self._request_version_ckiu_02()
            self._request_scan_ckiu_02()

            if self.ui.version_acp_radioButton.isChecked():
                self._request_acp_ckiu_02_old()
            if self.ui.version_ibp_radioButton.isChecked():
                self._request_acp_ckiu_02_ibp()
            if self.server == None:
                self.server = Server485(self. conn, port_name, speed, self.messages, self.params)
                self.server.sig.connect(self.update_version)
                self.server.sig1.connect(self.update_state)
                self.server.sig_disconnect.connect(self.counter_disconnect_ckiu)
                self.server.start()

        else:
            self.ui.state_lbl.setStyleSheet("QLabel {background-color : #f01; border:4px solid rgb(109, 109, 109)}")

    def _request_version_ckiu_02(self):
        msg = bytearray(b"\xb6\x49\x1b")
        # self.sn = int(self.ui.sn_lineEdit.text())
        msg.append(self.sn % 256)
        msg.append(self.sn // 256)
        msg.append(1)       # 01
        msg.append(128)     # 80
        msg = add_crc(msg, crc_ccitt_16_kermit_b(msg)) # +crc
        self.messages.append(msg)

    def _request_scan_ckiu_02(self):
        in1_t_pos_imp_lineEdit = int(self.ui.in1_t_pos_imp_lineEdit.text())
        in1_t_neg_imp_lineEdit = int(self.ui.in1_t_neg_imp_lineEdit.text())
        in2_t_pos_imp_lineEdit = int(self.ui.in2_t_pos_imp_lineEdit.text())
        in2_t_neg_imp_lineEdit = int(self.ui.in2_t_neg_imp_lineEdit.text())
        in3_t_pos_imp_lineEdit = int(self.ui.in3_t_pos_imp_lineEdit.text())
        in3_t_neg_imp_lineEdit = int(self.ui.in3_t_neg_imp_lineEdit.text())
        in4_t_pos_imp_lineEdit = int(self.ui.in4_t_pos_imp_lineEdit.text())
        in4_t_neg_imp_lineEdit = int(self.ui.in4_t_neg_imp_lineEdit.text())
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

    def _request_acp_ckiu_02_old(self):
        msg = bytearray(b"\xb6\x49\x1b")
        msg.append(self.sn % 256)
        msg.append(self.sn // 256)
        msg.append(1)  # 01
        msg.append(130)  # 82
        msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))  # +crc
        self.messages.append(msg)

    def _request_acp_ckiu_02_ibp(self):
        msg = bytearray(b"\xb6\x49\x1b")
        msg.append(self.sn % 256)
        msg.append(self.sn // 256)
        msg.append(1)  # 01
        msg.append(131)  # 83
        msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))  # +crc
        self.messages.append(msg)

    def _request_rebut_ckiu_02(self):
        msg = bytearray(b"\xb6\x49\x1b")
        msg.append(self.sn % 256)
        msg.append(self.sn // 256)
        msg.append(1)  # 01
        msg.append(209)  # D1
        msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))  # +crc
        self.messages.append(msg)

    def _request_str_debug(self):
        msg = bytearray(b"\xb6\x49\x1b")
        msg.append(self.sn % 256)
        msg.append(self.sn // 256)
        msg.append(1)  # 05
        msg.append(163)  # A3
        num_str = 0
        msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))  # +crc
        self.messages.append(msg)

    @Slot(tuple)
    def update_version(self, new_item):
        self.ui.version_ckiu2_lbl.setText(new_item[0])
        self.ui.sub_version_ckiu2_lbl.setText(new_item[1])

    @Slot(tuple)
    def update_state(self, new_item):
        style_norma = "QLabel {color: black; background-color : #07f73b; border:4px solid rgb(109, 109, 109)}"
        style_kz = "QLabel {color: black; background-color : #f70717; border:4px solid rgb(109, 109, 109)}"
        style_on = "QLabel {color: black; background-color : #026600; border:4px solid rgb(109, 109, 109)}"
        style_breakage = "QLabel {color: black; background-color : #f77b07; border:4px solid rgb(109, 109, 109)}"
        self.ui.u_in_lcd.display(new_item[0])
        self.ui.u_in_lcd.setStyleSheet("QLCDNumber {background-color: #2e2e2e; color: #07f73b;}")
        st_in_1 = int(new_item[1][0])
        st_in_2 = int(new_item[1][1])
        st_in_3 = int(new_item[1][2])
        st_in_4 = int(new_item[1][3])
        if st_in_1 == 0:
            self.ui.state_in_1_lbl.setText("Норма")
            self.ui.state_in_1_lbl.setStyleSheet(style_norma)
        elif st_in_1 == 1:
            self.ui.state_in_1_lbl.setText("КЗ")
            self.ui.state_in_1_lbl.setStyleSheet(style_kz)
        elif st_in_1 == 10:
            self.ui.state_in_1_lbl.setText("Включен")
            self.ui.state_in_1_lbl.setStyleSheet(style_on)
        elif st_in_1 == 11:
            self.ui.state_in_1_lbl.setText("Обрыв")
            self.ui.state_in_1_lbl.setStyleSheet(style_breakage)
        if st_in_2 == 0:
            self.ui.state_in_2_lbl.setText("Норма")
            self.ui.state_in_2_lbl.setStyleSheet(style_norma)
        elif st_in_2 == 1:
            self.ui.state_in_2_lbl.setText("КЗ")
            self.ui.state_in_2_lbl.setStyleSheet(style_kz)
        elif st_in_2 == 10:
            self.ui.state_in_2_lbl.setText("Включен")
            self.ui.state_in_2_lbl.setStyleSheet(style_on)
        elif st_in_2 == 11:
            self.ui.state_in_2_lbl.setText("Обрыв")
            self.ui.state_in_2_lbl.setStyleSheet(style_breakage)
        if st_in_3 == 0:
            self.ui.state_in_3_lbl.setText("Норма")
            self.ui.state_in_3_lbl.setStyleSheet(style_norma)
        elif st_in_3 == 1:
            self.ui.state_in_3_lbl.setText("КЗ")
            self.ui.state_in_3_lbl.setStyleSheet(style_kz)
        elif st_in_3 == 10:
            self.ui.state_in_3_lbl.setText("Включен")
            self.ui.state_in_3_lbl.setStyleSheet(style_on)
        elif st_in_3 == 11:
            self.ui.state_in_3_lbl.setText("Обрыв")
            self.ui.state_in_3_lbl.setStyleSheet(style_breakage)
        if st_in_4 == 0:
            self.ui.state_in_4_lbl.setText("Норма")
            self.ui.state_in_4_lbl.setStyleSheet(style_norma)
        elif st_in_4 == 1:
            self.ui.state_in_4_lbl.setText("КЗ")
            self.ui.state_in_4_lbl.setStyleSheet(style_kz)
        elif st_in_4 == 10:
            self.ui.state_in_4_lbl.setText("Включен")
            self.ui.state_in_4_lbl.setStyleSheet(style_on)
        elif st_in_4 == 11:
            self.ui.state_in_4_lbl.setText("Обрыв")
            self.ui.state_in_4_lbl.setStyleSheet(style_breakage)

    @Slot(bool)
    def counter_disconnect_ckiu(self):
        self.count_err_conn += 1
        self.ui.counter_err_conn_lcd.display(self.count_err_conn)
        if self.count_err_conn > 1:
            self.ui.counter_err_conn_lcd.setStyleSheet("QLCDNumber {background-color: #8c6501;}")


def include_style(app):
    with open("style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)


if __name__ == "__main__":
    app = QApplication([])
    widget = MainWindow()
    include_style(app)
    widget.show()
    sys.exit(app.exec())
