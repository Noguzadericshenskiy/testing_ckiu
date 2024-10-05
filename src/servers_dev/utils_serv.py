def get_bit(value: int, n: int) -> int:
    return (value >> n & 1) != 0

def set_bit(value: int, n: int) -> int:
    return value | (1 << n)


def clear_bit(value: int, n: int) -> int:
    return value & ~(1 << n)