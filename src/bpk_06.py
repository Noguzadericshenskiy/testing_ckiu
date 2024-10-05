from PySide6.QtCore import Slot
from PySide6.QtWidgets import QMessageBox
from servers_dev.bpk_server import ServerBPK

from loguru import logger


class BPK_06():
    def __init__(self, main_win, ports, server):
        super().__init__()
        self.main_win = main_win
        self.ports = ports
        self.server = server
        self.main_win.connect_ckiu_bpk_btn.clicked.connect(self._start)
        self.main_win.close_ckiu_bpk_btn_2.clicked.connect(self._stop)
        self.main_win.out_1_on_bpk_checkBox.checkStateChanged.connect(self._change_state_out)
        self.main_win.out_2_on_bpk_checkBox.checkStateChanged.connect(self._change_state_out)
        self.main_win.out_3_on_bpk_checkBox.checkStateChanged.connect(self._change_state_out)
        self.main_win.out_4_on_bpk_checkBox.checkStateChanged.connect(self._change_state_out)
        self.main_win.out_5_on_bpk_checkBox.checkStateChanged.connect(self._change_state_out)
        self.main_win.out_6_on_bpk_checkBox.checkStateChanged.connect(self._change_state_out)

    def _start(self):
        # port = None
        # sn = None
        # speed = None
        version = None

        speed = self.main_win.speed_comboBox.currentText()
        sn = self.main_win.sn_lineEdit.text()
        port_in = self.main_win.port_comboBox.currentText()
        port = self._get_port_name(self.ports, port_in)

        if not sn:
            logger.error("Not SN")
        else:
            sn = int(sn)
        if self.main_win.bpk_06_radioButton.isChecked():
            version = 1
        else:
            logger.error("Не выбрана версия")
        if not port_in:
            logger.error("Не выбран COM порт")

        self.server = ServerBPK(port=port,
                                speed=speed,
                                sn=sn,
                                states= [False, False, False, False, False, False],
                                version=version
                                )
        # self.server.sig_conn.connect(self._sig_connect)
        self.server.sig_bpk_analog_data.connect(self._analog_data)
        self.server.sig_bpk_states.connect(self._sig_states)
        self.server.start()

    def _stop(self):
        ...

    def _change_state_out(self):
        b1 = self.main_win.out_1_on_bpk_checkBox.isChecked()
        b2 = self.main_win.out_2_on_bpk_checkBox.isChecked()
        b3 = self.main_win.out_3_on_bpk_checkBox.isChecked()
        b4 = self.main_win.out_4_on_bpk_checkBox.isChecked()
        b5 = self.main_win.out_5_on_bpk_checkBox.isChecked()
        b6 = self.main_win.out_6_on_bpk_checkBox.isChecked()
        states = [b1, b2, b3, b4, b5, b6]
        self.server.set_state_out(states)

    def _get_port_name(self, ports, port_info):
        for port in ports:
            if port[1] == port_info:
                return port[0]

    @Slot(tuple)
    def _analog_data(self, analog_data):
        logger.info(analog_data)
        self.main_win.u_out_1_bpk_lcd.display(analog_data[6] / 100)
        self.main_win.u_out_2_bpk_lcd.display(analog_data[7] / 100)
        self.main_win.u_out_3_bpk_lcd.display(analog_data[8] / 100)
        self.main_win.u_out_4_bpk_lcd.display(analog_data[9] / 100)
        self.main_win.u_out_5_bpk_lcd.display(analog_data[10] / 100)
        self.main_win.u_out_6_bpk_lcd.display(analog_data[11] / 100)
        self.main_win.i_out_1_bpk_lcd.display(analog_data[0] / 100)
        self.main_win.i_out_2_bpk_lcd.display(analog_data[1] / 100)
        self.main_win.i_out_3_bpk_lcd.display(analog_data[2] / 100)
        self.main_win.i_out_4_bpk_lcd.display(analog_data[3] / 100)
        self.main_win.i_out_5_bpk_lcd.display(analog_data[4] / 100)
        self.main_win.i_out_6_bpk_lcd.display(analog_data[5] / 100)
        self.main_win.u_in_1_bpk_lcd.display(analog_data[12] / 100)
        self.main_win.u_in_2_bpk_lcd.display(analog_data[13] / 100)

    @Slot(tuple)
    def _sig_states(self, states):
        logger.info(states)
        st_ok = "QLabel {color: black; background-color : #07f73b; border:4px solid rgb(109, 109, 109)}"
        st_err = "QLabel {color: black; background-color : #f77b07; border:4px solid rgb(109, 109, 109)}"
        if states[0]:
            self.main_win.state_out_1_bpk_lbl.setText("Неисправность")
            self.main_win.state_out_1_bpk_lbl.setStyleSheet(st_err)
        else:
            self.main_win.state_out_1_bpk_lbl.setText("Норма")
            self.main_win.state_out_1_bpk_lbl.setStyleSheet(st_ok)
        if states[1]:
            self.main_win.state_out_2_bpk_lbl.setText("Неисправность")
            self.main_win.state_out_2_bpk_lbl.setStyleSheet(st_err)
        else:
            self.main_win.state_out_2_bpk_lbl.setText("Норма")
            self.main_win.state_out_2_bpk_lbl.setStyleSheet(st_ok)
        if states[2]:
            self.main_win.state_out_3_bpk_lbl.setText("Неисправность")
            self.main_win.state_out_1_bpk_lbl.setStyleSheet(st_err)
        else:
            self.main_win.state_out_3_bpk_lbl.setText("Норма")
            self.main_win.state_out_3_bpk_lbl.setStyleSheet(st_ok)
        if states[3]:
            self.main_win.state_out_4_bpk_lbl.setText("Неисправность")
            self.main_win.state_out_4_bpk_lbl.setStyleSheet(st_err)
        else:
            self.main_win.state_out_4_bpk_lbl.setText("Норма")
            self.main_win.state_out_4_bpk_lbl.setStyleSheet(st_ok)
        if states[4]:
            self.main_win.state_out_5_bpk_lbl.setText("Неисправность")
            self.main_win.state_out_5_bpk_lbl.setStyleSheet(st_err)
        else:
            self.main_win.state_out_5_bpk_lbl.setText("Норма")
            self.main_win.state_out_5_bpk_lbl.setStyleSheet(st_ok)
        if states[5]:
            self.main_win.state_out_6_bpk_lbl.setText("Неисправность")
            self.main_win.state_out_6_bpk_lbl.setStyleSheet(st_err)
        else:
            self.main_win.state_out_6_bpk_lbl.setText("Норма")
            self.main_win.state_out_6_bpk_lbl.setStyleSheet(st_ok)
        if states[6]:
            self.main_win.state_in_1_bpk_lbl.setText("Неисправность")
            self.main_win.state_in_1_bpk_lbl.setStyleSheet(st_err)
        else:
            self.main_win.state_in_1_bpk_lbl.setText("Норма")
            self.main_win.state_in_1_bpk_lbl.setStyleSheet(st_ok)
        if states[7]:
            self.main_win.state_in_2_bpk_lbl.setText("Неисправность")
            self.main_win.state_in_2_bpk_lbl.setStyleSheet(st_err)
        else:
            self.main_win.state_in_2_bpk_lbl.setText("Норма")
            self.main_win.state_in_2_bpk_lbl.setStyleSheet(st_ok)
