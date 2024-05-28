from crc_16_ccitt import revers_bytes

class HID:
    type: int
    sn: int


class Result:
    states = {}
    cmd: int
    state: str
    code: str

class ReadVarStructRequest:
    hid: HID
    len: int = 5
    cmd: int = 84
    seq: int
    addr: int
    num: int
    size: int


def hid_converter(data) -> HID:
    str_b = bytearray.fromhex(data)
    hid = HID()
    hid.type = int(str_b[0])
    lo = str_b[1]
    hi = str_b[2]
    hid.sn = hi * 256 + lo
    return hid


def result_cmd_81(data)-> Result:
    str_b = bytearray.fromhex(data)
    result = Result()
    result.cmd = int(str_b[0])
    result.state = int(str_b[1])
    result.code = int(str_b[2])
    return result


def get_value_variable():
    ...
