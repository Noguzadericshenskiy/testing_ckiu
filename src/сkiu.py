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
    sig_state = Signal(tuple)
    sig_version = Signal(tuple)

    def __init__(self, port, speed, sn, params, version):
        super().__init__()
        self.port = port
        self.speed = speed
        self.daemon = True
        self.sn = sn
        self.params = params
        self.version = version
        self.conn = None

    def run(self) -> None:
        try:
            self.conn = Serial(
                port=self.port,
                baudrate=self.speed,
                timeout=0.3,
            )

            if self.conn.is_open:
                self.sig_conn.emit(True)
            else:
                self.sig_conn.emit(False)

            if self.version == 1:
                self._awaken()
                while True:
                    self._get_u_acp_old()
                    self._request_scan_ckiu_02()
            if self.version == 2:
                ...
            if self.version == 3:
                self._delete_config(self.sn)
                self._awaken()
                self._request_version_ckiu_02()
                while True:
                    self._request_scan_ckiu_02()
                    self._get_u_acp()
        except:
            ...

    def stop_server(self):
        self.conn.close()

    def _awaken(self):
        f_start = True
        while f_start and self.conn.is_open:
            msg = bytearray(b"\xB6\x49\x1B")
            msg.extend(self.sn.to_bytes((self.sn.bit_length() + 7) // 8, byteorder='little'))
            msg.extend(bytearray(b"\x01\x83"))
            msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))
            msg = _indicate_send_b6_b9(msg)
            self.conn.reset_input_buffer()
            self.conn.reset_output_buffer()
            self.conn.write(msg)
            self.conn.flush()
            if self.conn.read(60):
                f_start = False
                self.conn.reset_input_buffer()

    def _get_u_acp(self):
        f_start = True
        msg = bytearray(b"\xB6\x49\x1B")
        msg.extend(self.sn.to_bytes((self.sn.bit_length() + 7) // 8, byteorder='little'))
        msg.extend(bytearray(b"\x01\x83"))
        msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))
        msg = _indicate_send_b6_b9(msg)
        self.conn.reset_input_buffer()
        self.conn.reset_output_buffer()
        self.conn.write(msg)
        self.conn.flush()
        while f_start and self.conn.is_open:
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
                else:
                    self.sig_count.emit(True)

    def _get_u_acp_old(self):
# Запрос 0xB6, 0x49, 0x1B, <адрес lo>, <адрес hi>, 0x01, 0x82, <CRC16 lo>, <CRC16 h>
# Ответ: 0xB9, 0x46, 0x1B, <адрес lo>, <адрес hi>, 0x06, 0x02, < 0x00 >, < АЦПuвх1 >, < 0x00 >, < 0x00 >, < 0x00 >, <CRC16 lo>, <CRC16 h>

        f_start = True
        msg = bytearray(b"\xB6\x49\x1B")
        msg.extend(self.sn.to_bytes((self.sn.bit_length() + 7) // 8, byteorder='little'))
        msg.extend(bytearray(b"\x01\x82"))
        msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))
        msg = _indicate_send_b6_b9(msg)
        self.conn.reset_input_buffer()
        self.conn.reset_output_buffer()
        self.conn.write(msg)
        self.conn.flush()
        while f_start and self.conn.is_open:
            if self.conn.read() == b"\xB9" and self.conn.read() == b"\x46":
                f_start = False
                ans = bytearray(b"\xB9\x46")
                for _ in range(8):
                    b = self.conn.read()
                    if b == b"\xB9" or b == b"\xB6":
                        self.conn.read()
                    ans.extend(b)
                self.conn.reset_output_buffer()
                if crc_ccitt_16_kermit_b(ans) == 0:
                    # logger.info(f'ok {(int.from_bytes(ans[6:7], "little") * 132) / 1024}')
                    self.sig_u_acp.emit((int.from_bytes(ans[6:7], "little") * 132) / 1024)
                else:
                    self.sig_count.emit(True)
                    # logger.info("bad")


    def _delete_config(self, sn):
        f_s = True
        while f_s:
            msg = bytearray(b"\xB6\x49\x1B")
            msg.extend(sn.to_bytes((sn.bit_length() + 7) // 8, byteorder='little')) #add sn
            msg.extend(b"\x01\xD1")
            msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))
            msg = _indicate_send_b6_b9(msg)
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

    def _request_version_ckiu_02(self):
        f_start = True
        msg = bytearray(b"\xb6\x49\x1b")
        msg.extend(self.sn.to_bytes((self.sn.bit_length() + 7) // 8, byteorder='little'))
        msg.append(1)  # 01
        msg.append(128)  # 80
        msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))  # +crc
        msg = _indicate_send_b6_b9(msg)
        self.conn.reset_output_buffer()
        self.conn.write(msg)
        self.conn.flush()
        while f_start and self.conn.is_open:
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
                    self.sig_version.emit((
                        str(int.from_bytes(ans[7:8], "little")),
                        str(int.from_bytes(ans[8:9], "little"))))
                else:
                    self.sig_version.emit(True)

    def _request_scan_ckiu_02(self):
        f_start = True
        msg = bytearray(b"\xb6\x49\x1b")
        msg.extend(self.sn.to_bytes((self.sn.bit_length() + 7) // 8, byteorder='little'))
        msg.extend(bytearray(b"\x09\x81"))
        msg.append(self.params["in1_pos"])
        msg.append(self.params["in1_neg"])
        msg.append(self.params["in2_pos"])
        msg.append(self.params["in2_neg"])
        msg.append(self.params["in3_pos"])
        msg.append(self.params["in3_neg"])
        msg.append(self.params["in4_pos"])
        msg.append(self.params["in4_neg"])
        msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))  # +crc
        msg = _indicate_send_b6_b9(msg)
        self.conn.reset_input_buffer()
        self.conn.reset_output_buffer()
        self.conn.write(msg)
        self.conn.flush()
        while f_start and self.conn.is_open:
            if self.conn.read() == b"\xB9" and self.conn.read() == b"\x46":
                f_start = False
                ans = bytearray(b"\xB9\x46")
                for _ in range(10):
                    b = self.conn.read()
                    if b == b"\xB9" or b == b"\xB6":
                        self.conn.read()
                    ans.extend(b)
                self.conn.reset_output_buffer()
                if crc_ccitt_16_kermit_b(ans) == 0:
                    statuse_in = _update_status_in(ans[9:10])
                    self.sig_state.emit(((int.from_bytes(ans[8:9], "little") * 132) / 1024, statuse_in))
                else:
                    self.sig_version.emit(True)


def _update_status_in(statuses):
    status_b = bin(int.from_bytes(statuses, byteorder='big'))[2:].zfill(8)
    return (status_b[6:], status_b[4:6], status_b[2:4], status_b[:2])


def _indicate_send_b6_b9(array_bytes: bytearray):
    new_msg = bytearray(b"\xB6\x49")
    for i_byte in array_bytes[2:]:
        if i_byte == 182 or i_byte == 185:
            new_msg.append(i_byte)
            new_msg.append(0)
        else:
            new_msg.append(i_byte)
    return new_msg