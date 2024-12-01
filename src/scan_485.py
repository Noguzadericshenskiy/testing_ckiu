import serial
from src.service.crc_16_ccitt import crc_ccitt_16_kermit_b
from utilites import result_cmd_81


PORT = "COM20"
# STOPBIT =
# PARITY =
BITRATE = 19200

send_ = b"b649086a8b098100000000000000008aff"
send_0 = b"b649086a8b09810000000000000000"
send_1 = b"\xb6\x49\x08\x6a\x8b\x09\x81\x00\x00\x00\x00\x00\x00\x00\x00\x8a\xff"
send_2 = b"\xb6\x49\x08\x6a\x8b\x09\x81\x00\x00\x00\x00\x00\x00\x00\x00\x8a\xff"
send_3 = b"\xb6\x49\x08\x6a\x8b\x09\x81\x00\x00\x00\x00\x00\x00\x00\x00"
resp_var_1 = b"\xb6\x49\x08\x6a\x8b\x84\x00"


def skan_rs_485():
    # bytes.fromhex('deadbeef')
    with serial.Serial(port=PORT, baudrate=BITRATE, timeout=1) as ser:
        # ser.open()
        while True:
            try:
                if ser.read().hex() == b"\xb6".hex() and ser.read().hex() == b"\x49".hex():
                    msg_in = bytearray(b"\xb6\x49")
                    hid = ser.read(3)
                    length = int(ser.read().hex())
                    data = ser.read(int.from_bytes(length, "little")).hex()

                    crc = ser.read(2).hex()
                    msg_in.append(int.from_bytes(hid, "little"))
                    msg_in.append(int.from_bytes(length, "little"))
                    msg_in.append(int.from_bytes(data, "little"))
                    msg_in.append(int.from_bytes(crc, "little"))
                    print(msg_in.hex())

                if ser.read().hex() == b"\xb9".hex() and ser.read().hex() == b"\x46".hex():
                    hid = ser.read(3).hex()
                    length = int(ser.read().hex())
                    res = ser.read(lenght).hex()
                    result = result_cmd_81(res)
                    crc = ser.read(2).hex()
                    # if result.cmd != 1:
                    print(f"Ответ  hid-{hid}  lenght-{length}  result-{res} {result.cmd}|{result.state}|{result.code}  crc-{crc}")
            except:
                IndexError("Неверный байт")
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
    # send_data()
    # byte_con()
    skan_rs_485()
    # print(revers_bytes(crc_ccitt_16_kermit(send_)))
