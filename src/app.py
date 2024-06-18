import sys
import serial

from PySide6 import QtGui
from PySide6.QtCore import Slot, QFile
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader

from src.main import Ui_MainWindow
from src.utilites import get_com_ports
from crc_16_ccitt import crc_ccitt_16_kermit_b, add_crc
from src.ckiu_02_old import Server485
from src.сkiu import ServerCKIU


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Тестер устройст RS-485")
        # self.ui.connect_btn.clicked.connect(self._connect_01)
        self.ui.close_btn.clicked.connect(self._close)
        self.ui.connect_ckiu_2_btn.clicked.connect(self._start_ckiu_02)
        self.ui.close_ckiu_2_btn.clicked.connect(self._close)
        self.ui.update_btn.clicked.connect(self._update_port)

        self.ports = []
        self._ports_out()
        self._speeds_out()
        self.server = None
        self.params = ["0"]
        self.count_err_conn = 0

        self._setup_param_default()

    def _setup_param_default(self):
        # ===================================
        # self.ui.sn_lineEdit.setText("35690")
        self.ui.sn_lineEdit.setText("1234")
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

    def _speeds_out(self):
        self.ui.speed_comboBox.addItem("19200")
        self.ui.speed_comboBox.addItem("9600")

    def _close(self):
        if self.server != None:
            self.server.stop_server()
            self.server = None
            self.ui.state_lbl.setStyleSheet(
                "QLabel {background-color : #f01; border:4px solid rgb(109, 109, 109)}")
            self.ui.counter_err_conn_lcd.setStyleSheet(
                "QLCDNumber {background-color: #00557f;}")
            self.ui.counter_err_conn_lcd.display(0)
            self.count_err_conn = 0

    def _get_params_out_ckiu02(self):
        params = {
            "in1_pos": int(self.ui.in1_t_pos_imp_lineEdit.text()),
            "in1_neg": int(self.ui.in1_t_neg_imp_lineEdit.text()),
            "in2_pos": int(self.ui.in2_t_pos_imp_lineEdit.text()),
            "in2_neg": int(self.ui.in2_t_neg_imp_lineEdit.text()),
            "in3_pos": int(self.ui.in3_t_pos_imp_lineEdit.text()),
            "in3_neg": int(self.ui.in3_t_neg_imp_lineEdit.text()),
            "in4_pos": int(self.ui.in4_t_pos_imp_lineEdit.text()),
            "in4_neg": int(self.ui.in4_t_neg_imp_lineEdit.text()),
        }
        return params

    def _start_ckiu_02(self):
        """Запуск СКИУ02"""
        self.count_err_conn = 0
        # self.messages = []
        port_name = None
        port_in = self.ui.port_comboBox.currentText()
        sn = int(self.ui.sn_lineEdit.text())
        for port in self.ports:
            if port[1] == port_in:
                port_name = port[0]
        speed = self.ui.speed_comboBox.currentText()
        self.server = ServerCKIU(
            port=port_name,
            speed=speed,
            sn=sn,
            params=self._get_params_out_ckiu02()
        )

        if self.ui.version_old_ckiu_radioButton.isChecked():
            ...
        if self.ui.version_acp_radioButton.isChecked():
            ...
        if self.ui.version_ibp_radioButton.isChecked():
            ...

        self.server.sig_conn.connect(self._sig_connect)
        self.server.sig_u_acp.connect(self._update_u_acp)
        self.server.sig_count.connect(self._counter_disconnect_ckiu)
        self.server.sig_state.connect(self._update_state_out)
        self.server.sig_version.connect(self._update_version)

        self.server.start()

        # if self.conn.is_open:
        #     self.ui.state_lbl.setStyleSheet("QLabel {background-color: #36f207; border:4px solid rgb(109, 109, 109)}")
        #     self._request_version_ckiu_02()
        #     self._request_scan_ckiu_02()

        #     if self.ui.version_acp_radioButton.isChecked():
        #         self._request_acp_ckiu_02_old()
        #     if self.ui.version_ibp_radioButton.isChecked():
        #         self._request_acp_ckiu_02_ibp()
        #
        #
        #     if self.server == None:
        #         self.server = ServerCKIU(self.conn, port_name, speed, self.messages, self.params, self.sn)
        #         # self.server = Server485(self. conn, port_name, speed, self.messages, self.params)
        #         self.server.sig.connect(self._update_version)
        #         self.server.sig1.connect(self._update_state)
        #         self.server.sig_disconnect.connect(self._counter_disconnect_ckiu)
        #         self.server.sig_u_acp.connect(self._update_u_in)
        #         self.server.start()
        #
        # else:
        #     self.ui.state_lbl.setStyleSheet("QLabel {background-color : #f01; border:4px solid rgb(109, 109, 109)}")

    @Slot(tuple)
    def _update_version(self, new_item):
        self.ui.version_ckiu2_lbl.setText(new_item[0])
        self.ui.sub_version_ckiu2_lbl.setText(new_item[1])

    @Slot(tuple)
    def _update_state_out(self, new_item):
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

        match st_in_1:
            case 0:
                self.ui.state_in_1_lbl.setText("Норма")
                self.ui.state_in_1_lbl.setStyleSheet(style_norma)
            case 1:
                self.ui.state_in_1_lbl.setText("КЗ")
                self.ui.state_in_1_lbl.setStyleSheet(style_kz)
            case 10:
                self.ui.state_in_1_lbl.setText("Включен")
                self.ui.state_in_1_lbl.setStyleSheet(style_on)
            case 11:
                self.ui.state_in_1_lbl.setText("Обрыв")
                self.ui.state_in_1_lbl.setStyleSheet(style_breakage)
        match st_in_2:
            case 0:
                self.ui.state_in_2_lbl.setText("Норма")
                self.ui.state_in_2_lbl.setStyleSheet(style_norma)
            case 1:
                self.ui.state_in_2_lbl.setText("КЗ")
                self.ui.state_in_2_lbl.setStyleSheet(style_kz)
            case 10:
                self.ui.state_in_2_lbl.setText("Включен")
                self.ui.state_in_2_lbl.setStyleSheet(style_on)
            case 11:
                self.ui.state_in_2_lbl.setText("Обрыв")
                self.ui.state_in_2_lbl.setStyleSheet(style_breakage)
        match st_in_3:
            case 0:
                self.ui.state_in_3_lbl.setText("Норма")
                self.ui.state_in_3_lbl.setStyleSheet(style_norma)
            case 1:
                self.ui.state_in_3_lbl.setText("КЗ")
                self.ui.state_in_3_lbl.setStyleSheet(style_kz)
            case 10:
                self.ui.state_in_3_lbl.setText("Включен")
                self.ui.state_in_3_lbl.setStyleSheet(style_on)
            case 11:
                self.ui.state_in_3_lbl.setText("Обрыв")
                self.ui.state_in_3_lbl.setStyleSheet(style_breakage)
        match st_in_4:
            case 0:
                self.ui.state_in_4_lbl.setText("Норма")
                self.ui.state_in_4_lbl.setStyleSheet(style_norma)
            case 1:
                self.ui.state_in_4_lbl.setText("КЗ")
                self.ui.state_in_4_lbl.setStyleSheet(style_kz)
            case 10:
                self.ui.state_in_4_lbl.setText("Включен")
                self.ui.state_in_4_lbl.setStyleSheet(style_on)
            case 11:
                self.ui.state_in_4_lbl.setText("Обрыв")
                self.ui.state_in_4_lbl.setStyleSheet(style_breakage)

    @Slot(bool)
    def _sig_connect(self, item):
        if item:
            self.ui.state_lbl.setStyleSheet("QLabel {background-color: #36f207; border:4px solid rgb(109, 109, 109)}")
        else:
            self.ui.state_lbl.setStyleSheet("QLabel {background-color : #f01; border:4px solid rgb(109, 109, 109)}")

    @Slot(float)
    def _update_u_acp(self, item):
        self.ui.u_in_lcd.display(item)

    @Slot(bool)
    def _counter_disconnect_ckiu(self, item):
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
