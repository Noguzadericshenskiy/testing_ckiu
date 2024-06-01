import serial
import time

from threading import Thread
from src.crc_16_ccitt import crc_ccitt_16_kermit_b


class Server485(Thread):
    """Эмулятор адресных устройств АШ Сигма
        передается конфигурация 1 ряда согласно порта из списка.
    :param name: название сетевого контроллера
    :param devices: адресные устройства
    """
    def __init__(self, conn, port, speed, msg):
        super().__init__()
        self.port = port
        self.speed = speed
        self.commands = msg
        self.daemon = True
        self.conn = conn
        self.state = True

    def run(self) -> None:
        # self.conn = serial.Serial(port=self.port, baudrate=self.speed, timeout=1)
        while self.state:
            self.conn.write(self.commands[0])
            self.handler_response()
            # print("start scan")
            time.sleep(0.2)
        # self.conn.write(self.commands[1])

    def stop_server(self):
        self.state = False

    def handler_response(self):
        if self.conn.read().hex() == b"\xb9".hex() and self.conn.read().hex() == b"\x46".hex():
            type_dev = self.conn.read()
            sn_lo = self.conn.read()
            sn_hi = self.conn.read()
            lenght_b = self.conn.read()
            cmd = self.conn.read()

            print(type(type_dev), type_dev)

            ans_msg = bytearray(b"\xb9\x46")

            # print(type(q))
            # ans_msg.append(q)
            # ans_msg.append(int(sn_lo))
            # ans_msg.append(int(sn_hi))
            # ans_msg.append(int(lenght_b))
            # ans_msg.append(int(cmd))

            # if cmd.hex() == "00":
            #     version_po = self.conn.read()
            #     ans_msg.append(version_po)
            #     sub_version_po = self.conn.read()
            #     ans_msg.append(sub_version_po)
            #     crc = self.conn.read(2)
            #     print(ans_msg)
        #         crc_in = crc_ccitt_16_kermit_b(ans_msg)
        #         # if crc == crc_in:
        #         #     print("crc is ok")
        #         print(version_po, sub_version_po)
        #         # self.ui.version_ckiu2_lbl.setText(str(version_po))
        #         # self.ui.sub_version_ckiu2_lbl.setText(str(sub_version_po))
        #         # else:
        #         print("crc not ok")
        #     elif cmd.hex() == "01":
        #         ...
        #     elif cmd.hex() == b"02":
        #         ...
        #     elif cmd.hex() == b"03":
        #         ...
        #     elif cmd.hex() == b"23":
        #         ...
        #     elif cmd.hex() == b"d1":
        #         ...
        #     elif cmd.hex() == b"e0":
        #         ...

    def get_version(self):
        self.conn.write(self.commands[0])
        print(self.commands[0])

