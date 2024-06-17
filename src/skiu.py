import time

from serial import Serial
from loguru import logger
from PySide6.QtCore import Signal, QThread

from src.crc_16_ccitt import crc_ccitt_16_kermit_b, add_crc
from serial.serialutil import PortNotOpenError

class Server485V2(QThread):
    sig = Signal(tuple)
    sig1 = Signal(tuple)
    sig2 = Signal(tuple)
    sig_disconnect = Signal(bool)
    sig_u_acp = Signal(float)

    def __init__(self, conn, port, speed, msg, params, sn):
        super().__init__()
        self.port = port
        self.speed = speed
        self.commands = msg
        self.daemon = True
        self.conn = conn
        self.params = params
        self.sn = sn

    def run(self) -> None:
        # self.conn = serial.Serial(port=self.port, baudrate=self.speed, timeout=1)
        # self.conn = Serial(
        #     port=self.port,
        #     baudrate=self.speed,
        #     timeout=0.3,
        #     # rs485_mode=rs485.RS485Settings()
        # )
        # self._delete_config(self.sn)
        self.awaken()
        while True:
            # self.get_state()
            self.get_state2()

                # print(82, self.commands[82].hex())
                # time.sleep(0.1)
                # self.conn.write(self.commands[83])
                # self.handler_response()
                # time.sleep(0.1)
            # self.conn.write(self.commands[1])

    # $B6$49$1B$D2$04$01$D1$27$A0
    # $B6$49$1B$D2$04$01$83$B0$D1

    def awaken(self):
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


    def get_state(self):
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
        ans = bytearray(b"\xB9\x46")
        while f_start:
            if self.conn.read() == b"\xB9" and self.conn.read() == b"\x46":
                # logger.info(f"ans start in-{self.conn.in_waiting} out-{self.conn.out_waiting}")
                f_start = False
                type_dev = self.conn.read(1)
                sn = self.conn.read(2)
                len = self.conn.read(1)
                placeholder1 = self.conn.read(2)
                cod = self.conn.read(1)
                u_in = self.conn.read(2)
                data = self.conn.read(15)
                crc = self.conn.read(2)
                ans.extend(type_dev)
                ans.extend(sn)
                ans.extend(len)
                ans.extend(cod)
                ans.extend(placeholder1)
                ans.extend(u_in)
                ans.extend(data)
                ans.extend(crc)
                self.conn.reset_output_buffer()
                # logger.info(f'{int.from_bytes(u_in, "little")/100}   {u_in.hex()}  {ans.hex()}')
                self.sig_u_acp.emit(int.from_bytes(u_in, "little")/100)
                # crc_in = crc_ccitt_16_kermit_b(ans)
            # logger.info(f"end  in-{self.conn.in_waiting} out-{self.conn.out_waiting}")

    def get_state1(self):
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
                ans.extend(self.conn.read(30))
                logger.info(f"end {ans.hex()} in-{self.conn.in_waiting} out-{self.conn.out_waiting} ")
                self.conn.reset_output_buffer()
                self.sig_u_acp.emit(int.from_bytes(ans[9:11], "little") / 100)
                crc_in = crc_ccitt_16_kermit_b(ans)

    def get_state2(self):
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
                # logger.info(f"end {ans.hex()} in-{self.conn.in_waiting} out-{self.conn.out_waiting} ")
                if crc_ccitt_16_kermit_b(ans[:27]) == 0:
                    self.sig_u_acp.emit(int.from_bytes(ans[9:11], "little") / 100)
                else:
                    self.sig_disconnect.emit(True)
                    logger.info(f"end {crc_ccitt_16_kermit_b(ans[:27])} {int.from_bytes(ans[25:27], 'little')} {ans.hex()}")

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