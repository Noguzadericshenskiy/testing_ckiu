import serial
import time
from crc_16_ccitt import crc_ccitt_16_kermit_b, revers_bytes


PORT = "COM6"
# STOPBIT =
# PARITY =
BITRATE = 19200

send_ = b"b649086a8b098100000000000000008aff"
send_0 = b"b649086a8b09810000000000000000"
send_1 = b"\xb6\x49\x08\x6a\x8b\x09\x81\x00\x00\x00\x00\x00\x00\x00\x00\x8a\xff"
send_2 = b"\xb6\x49\x08\x6a\x8b\x09\x81\x00\x00\x00\x00\x00\x00\x00\x00\x8a\xff"
send_3 = b"\xb6\x49\x08\x6a\x8b\x09\x81\x00\x00\x00\x00\x00\x00\x00\x00"

def send_data():
    with serial.Serial(port=PORT, baudrate=BITRATE, timeout=1) as ser:
        msg = bytearray(send_3)
        print(f"Начало посылки  {0}")
        # msg = send_3 + revers_bytes(crc_ccitt_16_kermit(send_0))
        crc = hex(crc_ccitt_16_kermit_b(msg))
        print(crc)
        msg.append(crc)
        # for _ in range(500):
        #     time.sleep(1)
        #     ser.write(msg)
        # msg.append(0x05)

        # if ser.read().hex() == b"\xb9".hex() and ser.read().hex() == b"\x46".hex():
        #     hw = ser.read(3).hex()
        #     l = int(ser.read().hex())
        #     data = ser.read(l).hex()
        #     crc = ser.read(2).hex()
        #     print(f"Начало ответа  {hw}  {l} {data} {crc}")


def skan_rs_485():
    # bytes.fromhex('deadbeef')
    with serial.Serial(port="COM6", baudrate=19200, timeout=1) as ser:
        # ser.open()
        while True:
            if ser.read().hex() == b"\xb6".hex() and ser.read().hex() == b"\x49".hex():
                hw = ser.read(3).hex()
                l = int(ser.read().hex())
                data = ser.read(l).hex()
                crc = ser.read(2).hex()
                type_dev = hw[0:2]
                sn = 0
                print(f"Начало посылки {hw} type_dev{type_dev} sn {sn}  {l} {data}  {crc}")
            if ser.read().hex() == b"\xb9".hex() and ser.read().hex() == b"\x46".hex():
                hw = ser.read(3).hex()
                l = int(ser.read().hex())
                data = ser.read(l).hex()
                crc = ser.read(2).hex()
                print(f"Начало ответа  {hw} type_dev{type_dev} {l} {data} {crc}")


# запрос    b6 49 08 6a 8b 09 81 00 00 00 00 00 00 00 00 8a ff
# ответ     b9 46 08 6a 8b 03 01 00 c4 de c4

# Начало посылки 086a8b type_dev08 sn 0  9 810000000000000000  8aff
# Начало ответа  086a8b type_dev08 3 0100c4 dec4



def byte_con():
    print(send_0)
    print(send_1)

if __name__ == "__main__":
    # skan_rs_485()
    # send_data()
    # print(revers_bytes(crc_ccitt_16_kermit(send_)))
