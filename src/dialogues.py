from PySide6.QtWidgets import QMessageBox

def err_connect(parent):
    QMessageBox.critical(
        parent,
        "Error connect line RS-485",
        "Потеря связи"
        "Не верная CRC пакета.\n",
        buttons=QMessageBox.Discard,
        defaultButton=QMessageBox.Discard,
    )

def err_port_close(parent):
    QMessageBox.critical(
        parent,
        "Error COM port",
        "Закрывать нечего\n"
        "Порт отключен.",
        buttons=QMessageBox.Discard,
        defaultButton=QMessageBox.Discard,
    )