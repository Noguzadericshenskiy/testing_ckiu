from loguru import logger

from .crc_16_ccitt import crc_ccitt_16_kermit_b, add_crc, indicate_send_b6


def cmd_93_bpk_06(sn):
    msg = bytearray(b"\xb6\x49\x33")
    msg.extend(sn.to_bytes((sn.bit_length() + 7) // 8, byteorder='little'))
    msg.extend(b"\x01")  # length
    msg.extend(b"\x93")  # command
    msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))
    msg = indicate_send_b6(msg)
    return msg


def cmd_91_bpk_06(sn, states):
    msg = bytearray(b"\xb6\x49\x33")
    msg.extend(sn.to_bytes((sn.bit_length() + 7) // 8, byteorder='little'))
    msg.extend(b"\x02")    # length
    msg.extend(b"\x91")  # command
    msg.append(states)
    msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))
    msg = indicate_send_b6(msg)
    return msg
