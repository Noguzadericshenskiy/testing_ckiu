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
        self._delete_config(self.sn)

        while True:
            self.get_state()

                # print(82, self.commands[82].hex())
                # time.sleep(0.1)
                # self.conn.write(self.commands[83])
                # self.handler_response()
                # time.sleep(0.1)
            # self.conn.write(self.commands[1])

    # $B6$49$1B$D2$04$01$D1$27$A0
    # $B6$49$1B$D2$04$01$83$B0$D1

    def get_state(self):
        f_start = True
        msg = bytearray(b"\xB6\x49\x1B")
        msg.extend(self.sn.to_bytes((self.sn.bit_length() + 7) // 8, byteorder='little'))
        msg.extend(bytearray(b"\x01\x83"))
        msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))
        msg = self._indicate_send_b6_b9(msg)
        self.conn.reset_input_buffer()
        self.conn.write(msg)
        self.conn.flush()
        ans = bytearray(b"\xB9\x46")
        while f_start:
            # добаить стартовую последовательность
            logger.info(f"ans start in-{self.conn.in_waiting} out-{self.conn.out_waiting}")
            if self.conn.read() == b"\xB9" and self.conn.read() == b"\x46":
                type_dev = self.conn.read(1)
                sn = self.conn.read(2)
                len = self.conn.read(1)
                data = self.conn.read(19)
                crc = self.conn.read(2)
                ans.extend(type_dev)
                ans.extend(sn)
                ans.extend(len)
                ans.extend(data)
                ans.extend(crc)
                logger.info(f"ans {ans.hex()}")
                f_start = False
            logger.info(f"end  in-{self.conn.in_waiting} out-{self.conn.out_waiting}")



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