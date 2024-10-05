import time

from serial import Serial
from loguru import logger
from PySide6.QtCore import Signal, QThread

from src.service.crc_16_ccitt import crc_ccitt_16_kermit_b, add_crc, indicate_send_b6
from src.service.commands import cmd_91_bpk_06, cmd_93_bpk_06
from .utils_serv import get_bit, set_bit, clear_bit


class ServerBPK(QThread):
    sig_bpk_conn = Signal(bool)
    sig_bpk_count = Signal(bool)
    sig_bpk_analog_data = Signal(tuple)
    sig_bpk_states = Signal(tuple)

    def __init__(self, port, speed, sn, states, version):
        super().__init__()
        self.port = port
        self.speed = speed
        self.sn = sn
        self.version = version
        self.states = states
        self.daemon = True
        self.conn = None
        self.stop = False
        self.states_byte = 0

    def run(self) -> None:
        time_send_ai_msg = time.time() * 1000
        logger.info("start server БПК-06Д")
        self.conn = Serial(port=self.port,
                           baudrate=self.speed,
                           timeout=0.3,)

        if self.conn.is_open:
            self.sig_bpk_conn.emit(True)
        else:
            self.sig_bpk_conn.emit(False)

        if self.version == 1:
            self._awaken()
            while True:
                if self.stop:
                    self.conn.close()
                    self.sig_bpk_conn.emit(False)
                else:
                   self._scan()
                   if time.time() * 1000 - time_send_ai_msg > 300:
                        self._acp()
                        time_send_ai_msg = time.time() * 1000

    def set_state_out(self, states):
        new_state = 0
        if states[0]:
            new_state = set_bit(new_state, 0)
        if states[1]:
            new_state = set_bit(new_state, 1)
        if states[2]:
            new_state = set_bit(new_state, 2)
        if states[3]:
            new_state = set_bit(new_state, 3)
        if states[4]:
            new_state = set_bit(new_state, 4)
        if states[5]:
            new_state = set_bit(new_state, 5)

        self.states_byte = new_state


    def _acp(self):
        msg = cmd_93_bpk_06(self.sn)
        ans = self._send_msg(msg, 37)
        self._acp_out(ans)

    def _scan(self):
        msg = cmd_91_bpk_06(self.sn, self.states_byte)
        ans = self._send_msg(msg, 10)
        self._scan_out(ans)

    def _send_msg(self, msg, len_ans):
        self.conn.reset_input_buffer()
        self.conn.write(msg)
        self.conn.flush()
        # f_ans = False
        while True:
            if self.conn.read() == b"\xB9" and self.conn.read() == b"\x46":
                ans = bytearray(b"\xB9\x46")
                for _ in range(len_ans - 2):
                    b = self.conn.read()
                    if b == b"\xB9" or b == b"\xB6":
                        self.conn.read()
                    ans.extend(b)
                self.conn.reset_output_buffer()
                if crc_ccitt_16_kermit_b(ans) == 0:
                    # f_ans = True
                    return ans

    def _awaken(self):
        f_start = True
        while f_start:
            msg = cmd_91_bpk_06(self.sn, self.states_byte)
            self.conn.reset_input_buffer()
            self.conn.reset_output_buffer()
            self.conn.write(msg)
            self.conn.flush()
            if self.conn.read(20):
                f_start = False
                self.conn.reset_input_buffer()

    def _acp_out(self, msg):
        # logger.info(f"acp  {msg.hex(sep=' ')}")
        # b9 46 33 e8 04 1d 93 | 03 00 4f 0b 00 00 53 0b 00 00 43 0b 00 00 46 0b 01 00 3b 0b 02 00 53 0b 4e 0b 00 00 | 59 f0
        # 0  1  2   3  4  5  6            10             15             20             25             30
        i_out_1 = int.from_bytes(msg[7:9], "little")
        i_out_2 = int.from_bytes(msg[11:13], "little")
        i_out_3 = int.from_bytes(msg[15:17], "little")
        i_out_4 = int.from_bytes(msg[19:21], "little")
        i_out_5 = int.from_bytes(msg[23:25], "little")
        i_out_6 = int.from_bytes(msg[27:29], "little")
        u_out_1 = int.from_bytes(msg[9:11], "little")
        u_out_2 = int.from_bytes(msg[13:15], "little")
        u_out_3 = int.from_bytes(msg[17:19], "little")
        u_out_4 = int.from_bytes(msg[21:23], "little")
        u_out_5 = int.from_bytes(msg[25:27], "little")
        u_out_6 = int.from_bytes(msg[29:31], "little")
        u_in_1 = int.from_bytes(msg[31:33], "little")
        u_in_2 = int.from_bytes(msg[33:35], "little")
        # logger.info(f"i[{i_out_1}-{i_out_2}-{i_out_3}-{i_out_4}-{i_out_5}-{i_out_6}]")
        # logger.info(f"u[{u_out_1}-{u_out_2}-{u_out_3}-{u_out_4}-{u_out_5}-{u_out_6}] in[{u_in_1}-{u_in_2}]")
        analog_data = (i_out_1, i_out_2, i_out_3, i_out_4, i_out_5, i_out_6,
                       u_out_1, u_out_2, u_out_3, u_out_4, u_out_5, u_out_6, u_in_1, u_in_2)
        self.sig_bpk_analog_data.emit(analog_data)

    def _scan_out(self, msg):
        # b9 46 33 e8 04 02 91 00 18 68
        # logger.info(f"scan  {msg.hex(sep=' ')}")
        states_byte = int.from_bytes(msg[7:8])
        out_1 = get_bit(states_byte, 0)
        out_2 = get_bit(states_byte, 1)
        out_3 = get_bit(states_byte, 2)
        out_4 = get_bit(states_byte, 3)
        out_5 = get_bit(states_byte, 4)
        out_6 = get_bit(states_byte, 5)
        in_1 = get_bit(states_byte, 6)
        in_2 = get_bit(states_byte, 7)
        # logger.info(f"i[{out_1}-{out_2}-{out_3}-{out_4}-{out_5}-{out_6}] [{in_1}-{in_2}]")
        states = (out_1, out_2, out_3, out_4, out_5, out_6, in_1, in_2)
        self.sig_bpk_states.emit(states)
