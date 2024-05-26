import serial
import time
from crc_16_ccitt import crc_ccitt_16_kermit_b, revers_bytes, add_crc


PORT = "COM9"
# STOPBIT =
# PARITY =
BITRATE = 19200



class RequestReadVariable84:
    hid: int         # Идентификатор оборудования
    len: int = 5     # 5
    cmd: int = 84    # 84
    seq: []          # 0- новый запрос. Значение, полученное в предыдущем ответе - чтение результата
    addr: int        # Короткий адрес устройства
    num: int         # Номер переменной
    size: int        # Размерность. 1 - байт, >1 - 4 байта
# Примечание: Если значение поля seq не 0, то в запросе поля addr, num, size игнорируются.


kod_rezalt = {("RC_OK",), ("RC_LEN",), ("RC_BADARG",)}
kod_write = {0: "идёт запись", 1: "значение записано и проверено", 2: "значение записано, но не проверено"}


class DeviseResponse:
    addr: int       # Короткий адрес устройства
    num: int        # Номер переменной
    res: kod_write  # Результат записи.
    size: int       # размер
    value: int      # Считанное значение


class ResponseReadVariable84:
    hid: int            # Идентификатор оборудования
    len: int = 5        # 5
    res: kod_rezalt     # Результат выполнения команды
    seq: int            # Значение, которое необходимо указать при чтении результата
    var: DeviseResponse


def send_data():
    send_2 = b"\xb6\x49\x08\x6a\x8b\x09\x81\x00\x00\x00\x00\x00\x00\x00\x00\x8a\xff"
    send_3 = b"\xb6\x49\x08\x6a\x8b\x09\x81\x00\x00\x00\x00\x00\x00\x00\x00"
    send_4 = b"\xb6\x49\x08\x6a\x8b\x01\x81"

    with serial.Serial(port=PORT, baudrate=BITRATE, timeout=1) as ser:
        msg = bytearray(send_3)
        # print(f"Начало отправки {msg}")
        crc = crc_ccitt_16_kermit_b(msg)

        c = add_crc(msg, crc)

        for _ in range(20):
            time.sleep(0.5)
            ser.write(c)


def byte_con():
    msg = bytearray(b"\xb6\x49")
    msg.append(11)
    crc = crc_ccitt_16_kermit_b(msg)
    print(crc)
    lo = crc % 256
    hi = crc // 256
    msg.append(hi)
    msg.append(lo)


if __name__ == "__main__":
    send_data()
