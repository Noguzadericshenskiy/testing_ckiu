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