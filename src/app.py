import sys
import time

import serial

from PySide6 import QtGui
from PySide6.QtCore import Slot, QFile
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader

from loguru import logger

from src.main import Ui_MainWindow
from src.utilites import get_com_ports
from crc_16_ccitt import crc_ccitt_16_kermit_b, add_crc
from src.ckiu_02_old import Server485
from src.сkiu import ServerCKIU
from src.dialogues import err_port_close


style_norma = "QLabel {color: black; background-color : #07f73b; border:4px solid rgb(109, 109, 109)}"
style_kz = "QLabel {color: black; background-color : #f70717; border:4px solid rgb(109, 109, 109)}"
style_on = "QLabel {color: black; background-color : #026600; border:4px solid rgb(109, 109, 109)}"
style_breakage = "QLabel {color: black; background-color : #f77b07; border:4px solid rgb(109, 109, 109)}"



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
        self.start_out = time.time()

        self._setup_param_default()

    def _setup_param_default(self):
        # ===================================
        # self.ui.sn_lineEdit.setText("35690")
        self.ui.sn_lineEdit.setText("1234")
        # ===================================
        self.ui.version_ckiu2_lbl.setText("0")
        self.ui.sub_version_ckiu2_lbl.setText("0")
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
        style_breakage = "QLabel {color: black; background-color : #f77b07; border:4px solid rgb(109, 109, 109)}"
        if self.server is not None:
            self.server.stop_server()
            self.server = None
            self.ui.state_lbl.setStyleSheet(
                "QLabel {background-color : #f01; border:4px solid rgb(109, 109, 109)}")
            self.ui.counter_err_conn_lcd.setStyleSheet(
                "QLCDNumber {background-color: #00557f;}")
            self.ui.counter_err_conn_lcd.display(0)
            self.ui.state_in_1_lbl.setText("")
            self.ui.state_in_1_lbl.setStyleSheet(style_breakage)
            self.ui.state_in_2_lbl.setText("")
            self.ui.state_in_2_lbl.setStyleSheet(style_breakage)
            self.ui.state_in_3_lbl.setText("")
            self.ui.state_in_3_lbl.setStyleSheet(style_breakage)
            self.ui.state_in_4_lbl.setText("")
            self.ui.state_in_4_lbl.setStyleSheet(style_breakage)
            self.count_err_conn = 0
            self.ui.version_ckiu2_lbl.setText("")
            self.ui.sub_version_ckiu2_lbl.setText("")
            self.ui.u_in_lcd.display(0)
            self.server.stop_server()
            self.server = None



        else:
            err_port_close(self)

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
        if self.server is None:
            version = None
            port_name = None
            self.count_err_conn = 0
            port_in = self.ui.port_comboBox.currentText()
            sn = int(self.ui.sn_lineEdit.text())

            for port in self.ports:
                if port[1] == port_in:
                    port_name = port[0]
            speed = self.ui.speed_comboBox.currentText()

            if self.ui.version_old_ckiu_radioButton.isChecked():
                version = 1
            if self.ui.version_acp_radioButton.isChecked():
                version = 2
            if self.ui.version_ibp_radioButton.isChecked():
                version = 3

            self.server = ServerCKIU(
                port=port_name,
                speed=speed,
                sn=sn,
                params=self._get_params_out_ckiu02(),
                version=version
            )

            self.server.sig_conn.connect(self._sig_connect)
            self.server.sig_u_acp.connect(self._update_u_acp)
            self.server.sig_count.connect(self._counter_disconnect_ckiu)
            self.server.sig_state.connect(self._update_state_out)
            self.server.sig_version.connect(self._update_version)
            self.server.start()

    @Slot(tuple)
    def _update_version(self, new_item):
        logger.info(new_item)
        self.ui.version_ckiu2_lbl.setText(new_item[0])
        self.ui.sub_version_ckiu2_lbl.setText(new_item[1])

    @Slot(tuple)
    def _update_state_out(self, new_item):
        style_norma = "QLabel {color: black; background-color : #07f73b; border:4px solid rgb(109, 109, 109)}"
        style_kz = "QLabel {color: black; background-color : #f70717; border:4px solid rgb(109, 109, 109)}"
        style_on = "QLabel {color: black; background-color : #026600; border:4px solid rgb(109, 109, 109)}"
        style_breakage = "QLabel {color: black; background-color : #f77b07; border:4px solid rgb(109, 109, 109)}"
        # self.ui.u_in_lcd.display(new_item[0])
        # self.ui.u_in_lcd.setStyleSheet("QLCDNumber {background-color: #2e2e2e; color: #07f73b;}")
        st_in_1 = int(new_item[1][0])
        st_in_2 = int(new_item[1][1])
        st_in_3 = int(new_item[1][2])
        st_in_4 = int(new_item[1][3])
        logger.info(f"st_in_1- {st_in_1} st_in_2- {st_in_2} st_in_3- {st_in_3} st_in_4- {st_in_4}")

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
        if time.time() - self.start_out > 0.1:
            self.ui.u_in_lcd.display(item)
            self.start_out = time.time()

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
