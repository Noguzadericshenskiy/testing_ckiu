import time

from serial import Serial
from loguru import logger
from PySide6.QtCore import Signal, QThread

from src.crc_16_ccitt import crc_ccitt_16_kermit_b, add_crc
from serial.serialutil import PortNotOpenError

class ServerCKIU(QThread):
    sig_conn = Signal(bool)
    sig_count = Signal(bool)
    sig_u_acp = Signal(float)
    sig_state =Signal(tuple)
    sig_version = Signal(tuple)

    sig = Signal(tuple)
    sig1 = Signal(tuple)
    sig2 = Signal(tuple)

    def __init__(self, port, speed, sn, params):
        super().__init__()
        self.port = port
        self.speed = speed
        self.daemon = True
        self.sn = sn
        self.params = params

    def run(self) -> None:
        self.conn = Serial(
            port=self.port,
            baudrate=self.speed,
            timeout=0.3,
        )

        if self.conn.is_open:
            self.sig_conn.emit(True)
        else:
            self.sig_conn.emit(True)

        self._delete_config(self.sn)
        self._awaken()

        while True:
            self._get_u_acp()
            self._request_version_ckiu_02()

    def stop_server(self):
        self.conn.close()

    def _awaken(self):
        f_start = True
        while f_start:
            msg = bytearray(b"\xB6\x49\x1B")
            msg.extend(self.sn.to_bytes((self.sn.bit_length() + 7) // 8, byteorder='little'))
            msg.extend(bytearray(b"\x01\x83"))
            msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))
            msg = self._indicate_send_b6_b9(msg)
            self.conn.reset_input_buffer()
            self.conn.reset_output_buffer()
            self.conn.write(msg)
            self.conn.flush()
            if self.conn.read(60):
                f_start = False
                self.conn.reset_input_buffer()
                # logger.info(f"awaken in-{self.conn.in_waiting} out-{self.conn.out_waiting}")

    def _get_u_acp(self):
        f_start = True
        msg = bytearray(b"\xB6\x49\x1B")
        msg.extend(self.sn.to_bytes((self.sn.bit_length() + 7) // 8, byteorder='little'))
        msg.extend(bytearray(b"\x01\x83"))
        msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))
        msg = self._indicate_send_b6_b9(msg)
        self.conn.reset_input_buffer()
        self.conn.reset_output_buffer()
        self.conn.write(msg)
        self.conn.flush()
        while f_start:
            if self.conn.read() == b"\xB9" and self.conn.read() == b"\x46":
                f_start = False
                ans = bytearray(b"\xB9\x46")
                for _ in range(25):
                    b = self.conn.read()
                    if b == b"\xB9" or b == b"\xB6":
                        self.conn.read()
                    ans.extend(b)
                self.conn.reset_output_buffer()
                if crc_ccitt_16_kermit_b(ans) == 0:
                    self.sig_u_acp.emit(int.from_bytes(ans[9:11], "little") / 100)
                    logger.info("crc ok")
                else:
                    self.sig_count.emit(True)
                    logger.info(f"crc bad {crc_ccitt_16_kermit_b(ans[:27])} {int.from_bytes(ans[25:27], 'little')} {ans.hex()}")

    def _delete_config(self, sn):
        f_s = True
        while f_s:
            msg = bytearray(b"\xB6\x49\x1B")
            msg.extend(sn.to_bytes((sn.bit_length() + 7) // 8, byteorder='little')) #add sn
            msg.extend(b"\x01\xD1")
            msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))
            msg = self._indicate_send_b6_b9(msg)
            self.conn.reset_input_buffer()
            self.conn.write(msg)
            self.conn.write(msg)
            self.conn.flush()
            ans = self.conn.read(30)
            if ans:
                self.conn.reset_input_buffer()
                f_s = False
                start = time.time()
                while time.time() - start < 5:
                    ...


    def _indicate_send_b6_b9(self, array_bytes: bytearray):
        new_msg = bytearray(b"\xB6\x49")
        for i_byte in array_bytes[2:]:
            if i_byte == 182 or i_byte == 185:
                new_msg.append(i_byte)
                new_msg.append(0)
            else:
                new_msg.append(i_byte)
        return new_msg

    def _request_version_ckiu_02(self):
        f_start = True
        msg = bytearray(b"\xb6\x49\x1b")
        msg.extend(self.sn.to_bytes((self.sn.bit_length() + 7) // 8, byteorder='little'))
        msg.append(1)  # 01
        msg.append(128)  # 80
        msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))  # +crc
        self.conn.reset_output_buffer()
        self.conn.write(msg)
        self.conn.flush()
        while f_start:
            if self.conn.read() == b"\xB9" and self.conn.read() == b"\x46":
                f_start = False
                ans = bytearray(b"\xB9\x46")
                for _ in range(9):
                    b = self.conn.read()
                    if b == b"\xB9" or b == b"\xB6":
                        self.conn.read()
                    ans.extend(b)
                self.conn.reset_output_buffer()
                if crc_ccitt_16_kermit_b(ans) == 0:
                    self.sig_u_acp.emit((
                        str(int.from_bytes(ans[7:8], "little")),
                        str(int.from_bytes(ans[8:9], "little"))))
                    logger.info("crc ok")
                else:
                    self.sig_count.emit(True)
                    logger.info(f"crc bad {crc_ccitt_16_kermit_b(ans[:27])} {int.from_bytes(ans[25:27], 'little')} {ans.hex()}")



    # ===================================================================
    # def _request_version_ckiu_02(self):
    #     msg = bytearray(b"\xb6\x49\x1b")
    #     # self.sn = int(self.ui.sn_lineEdit.text())
    #     msg.append(self.sn % 256)
    #     msg.append(self.sn // 256)
    #     msg.append(1)       # 01
    #     msg.append(128)     # 80
    #     msg = add_crc(msg, crc_ccitt_16_kermit_b(msg)) # +crc
    #     self.messages.append(msg)

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