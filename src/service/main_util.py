from serial.tools import list_ports_windows


def get_com_ports():
    "Получить список портов"
    usb_port = list_ports_windows.comports()
    return [(i_port.device, i_port.description) for i_port in usb_port]

