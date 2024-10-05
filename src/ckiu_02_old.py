
from loguru import logger
from PySide6.QtCore import Signal, QThread

from src.service.crc_16_ccitt import crc_ccitt_16_kermit_b
from serial.serialutil import PortNotOpenError


class Server485(QThread):
    """Эмулятор адресных устройств АШ Сигма
        передается конфигурация 1 ряда согласно порта из списка.
    :param name: название сетевого контроллера
    :param devices: адресные устройства
    """
    sig = Signal(tuple)
    sig1 = Signal(tuple)
    sig2 = Signal(tuple)
    sig_disconnect = Signal(bool)

    def __init__(self, conn, port, speed, msg, params):
        super().__init__()
        self.port = port
        self.speed = speed
        self.commands = msg
        self.daemon = True
        self.conn = conn
        self.params = params

    def run(self) -> None:
        # self.conn = serial.Serial(port=self.port, baudrate=self.speed, timeout=1)
        try:
            while True:
                for msg in self.commands:
                    self.conn.reset_input_buffer()

                    self.conn.write(msg)
                    if not self.handler_response():
                        self.sig_disconnect.emit(True)
                self.conn.flush()

                # print(82, self.commands[82].hex())
                # time.sleep(0.1)
                # self.conn.write(self.commands[83])
                # self.handler_response()
                # time.sleep(0.1)
            # self.conn.write(self.commands[1])
        except:
            PortNotOpenError()

    def handler_response(self):
        if self.conn.read().hex() == b"\xb9".hex() and self.conn.read().hex() == b"\x46".hex():
            type_dev = self.conn.read()
            sn_lo = self.conn.read()
            sn_hi = self.conn.read()
            length = self.conn.read()
            cmd = self.conn.read()
            ans_msg = bytearray(b"\xb9\x46")
            ans_msg.append(int.from_bytes(type_dev, "little"))
            ans_msg.append(int.from_bytes(sn_lo, "little"))
            ans_msg.append(int.from_bytes(sn_hi, "little"))
            ans_msg.append(int.from_bytes(length, "little"))
            ans_msg.append(int.from_bytes(cmd, "little"))
            if cmd.hex() == "00" and int.from_bytes(length, "little") != 4:
                version_po = self.conn.read()
                sub_version_po = self.conn.read()
                ans_msg.append(int.from_bytes(version_po, "little"))
                ans_msg.append(int.from_bytes(sub_version_po, "little"))
                crc = self.conn.read(2)
                crc_in = crc_ccitt_16_kermit_b(ans_msg)
                if int.from_bytes(crc, "little") == crc_in:
                    self.sig.emit((str(int.from_bytes(version_po, "little")),
                                   str(int.from_bytes(sub_version_po, "little"))))
                    return True
                else:
                    return False
                    # print("crc is ok", int.from_bytes(version_po, "little"), int.from_bytes(sub_version_po, "little"))

            elif cmd.hex() == "01" and int.from_bytes(length, "little") == 4:
                # elif (cmd.hex() == "01" or cmd.hex() == "00") and int.from_bytes(length, "little") == 4:
                zero_byte = self.conn.read()
                u_in = self.conn.read()
                states_out = self.conn.read()
                crc = self.conn.read(2)
                ans_msg.append(int.from_bytes(zero_byte, "little"))
                ans_msg.append(int.from_bytes(u_in, "little"))
                ans_msg.append(int.from_bytes(states_out, "little"))
                crc_in = crc_ccitt_16_kermit_b(ans_msg)
                if int.from_bytes(crc, "little") == crc_in:
                    u = (int.from_bytes(u_in, "little") * 132) / 1024
                    # u1 = int.from_bytes(u_in, "little") / 10
                    # self.params[0] = u_in.hex()
                    statuse_in = self.update_status_in(states_out)
                    self.sig1.emit((u, statuse_in))
                    return True
                else:
                    return False
            # print(f"zero_byte-{zero_byte.hex()}, u_in-{u_in.hex()}|{u}, states_out-{states_out.hex()} msg-{ans_msg.hex()}")

            elif cmd.hex() == "02":
                zero_byte = self.conn.read()
                acp_u_in_1 = self.conn.read()
                acp_u_in_2 = self.conn.read()
                acp_u_in_3 = self.conn.read()
                acp_u_in_4 = self.conn.read()
                crc = self.conn.read(2)
                ans_msg.append(int.from_bytes(zero_byte, "little"))
                ans_msg.append(int.from_bytes(acp_u_in_1, "little"))
                ans_msg.append(int.from_bytes(acp_u_in_2, "little"))
                ans_msg.append(int.from_bytes(acp_u_in_3, "little"))
                ans_msg.append(int.from_bytes(acp_u_in_4, "little"))
                crc_in = crc_ccitt_16_kermit_b(ans_msg)
                if int.from_bytes(crc, "little") == crc_in:
                    acp_u1 = (int.from_bytes(acp_u_in_1, "little") * 132) / 1024
                    self.sig2.emit((acp_u1, acp_u_in_2.hex(), acp_u_in_3.hex(), acp_u_in_4.hex()))
                    return True
                else:
                    return False

                #     print(f"zero_byte-{zero_byte.hex()}, u_in-{u}, acp_u_in_x-> {acp_u_in_1} | {acp_u_in_2} | {acp_u_in_3} | {acp_u_in_4}")

#         0xB6, 0x49, 0x1B, <адрес мл. байт>, <адрес ст. байт>, 0x01, 0x82, <CRC16 мл. байт>, <CRC16 ст. байт>
# Ответ:  0xB9, 0x46, 0x1B, <адрес мл. байт>, <адрес ст. байт>, 0x06, 0x02, <0x00>, <АЦПuвх1>, <0x00>, <0x00>, <0x00>, <CRC16 мл. байт>, <CRC16 ст. байт>
            elif cmd.hex() == "03":
                ans = self.conn.read_all()
                logger.info(f"ans 03 {ans.hex()}")
                # zero_byte = self.conn.read(2)
                # u_in_lo = self.conn.read()
                # u_in_hi = self.conn.read()
                # zero_byte2c = self.conn.read(14)

                # logger.info(f"cmd 03 {zero_byte.hex()}{zero_byte.hex()}{zero_byte.hex()}")

            # elif cmd.hex() == "23":
            #     ...
            # elif cmd.hex() == "d1":
            #     ...
            # elif cmd.hex() == "e0":
            #     ...
            elif cmd.hex() == "e0" and int.from_bytes(length, "little") == 2:
                logger.info("Неизвесная команда")
                return False

    # 0xB6, 0x49, 0x1B, < адрес мл.байт >, < адрес ст.байт >, 0x01, 0x83, < CRC16 мл.байт >, < CRC16 ст.байт >
    # Ответ: 0xB9, 0x46, 0x1B, < адрес мл.байт >, < адрес ст.байт >, 0x13, 0x03, 0x00, 0x00, < uвх1 мл. >, < uвх1 ст. >, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, < CRC16 мл.байт >, < CRC16 ст.байт >
    # Uвх1 = uвх1 / 100 В

    def update_status_in(self, statuses):
        status_b = bin(int.from_bytes(statuses, byteorder='big'))[2:].zfill(8)
        return (status_b[6:], status_b[4:6], status_b[2:4], status_b[:2])