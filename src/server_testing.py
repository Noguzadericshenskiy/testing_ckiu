

# способы передачи пакетов========================================================================

def get_state0(self):
    f_start = True
    msg = bytearray(b"\xB6\x49\x1B")
    msg.extend(self.sn.to_bytes((self.sn.bit_length() + 7) // 8, byteorder='little'))
    msg.extend(bytearray(b"\x01\x83"))
    msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))
    msg = self._indicate_send_b6(msg)
    self.conn.reset_input_buffer()
    self.conn.reset_output_buffer()
    self.conn.write(msg)
    self.conn.flush()
    ans = bytearray(b"\xB9\x46")
    while f_start:
        if self.conn.read() == b"\xB9" and self.conn.read() == b"\x46":
            # logger.info(f"ans start in-{self.conn.in_waiting} out-{self.conn.out_waiting}")
            f_start = False
            type_dev = self.conn.read(1)
            sn = self.conn.read(2)
            len = self.conn.read(1)
            placeholder1 = self.conn.read(2)
            cod = self.conn.read(1)
            u_in = self.conn.read(2)
            data = self.conn.read(15)
            crc = self.conn.read(2)
            ans.extend(type_dev)
            ans.extend(sn)
            ans.extend(len)
            ans.extend(cod)
            ans.extend(placeholder1)
            ans.extend(u_in)
            ans.extend(data)
            ans.extend(crc)
            self.conn.reset_output_buffer()
            # logger.info(f'{int.from_bytes(u_in, "little")/100}   {u_in.hex()}  {ans.hex()}')
            self.sig_u_acp.emit(int.from_bytes(u_in, "little" ) /100)
            # crc_in = crc_ccitt_16_kermit_b(ans)
        # logger.info(f"end  in-{self.conn.in_waiting} out-{self.conn.out_waiting}")
#
def get_state1(self):
    f_start = True
    msg = bytearray(b"\xB6\x49\x1B")
    msg.extend(self.sn.to_bytes((self.sn.bit_length() + 7) // 8, byteorder='little'))
    msg.extend(bytearray(b"\x01\x83"))
    msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))
    msg = self._indicate_send_b6(msg)
    self.conn.reset_input_buffer()
    self.conn.reset_output_buffer()
    self.conn.write(msg)
    self.conn.flush()
    while f_start:
        if self.conn.read() == b"\xB9" and self.conn.read() == b"\x46":
            f_start = False
            ans = bytearray(b"\xB9\x46")
            ans.extend(self.conn.read(30))
            logger.info(f"end {ans.hex()} in-{self.conn.in_waiting} out-{self.conn.out_waiting} ")
            self.conn.reset_output_buffer()
            self.sig_u_acp.emit(int.from_bytes(ans[9:11], "little") / 100)
            crc_in = crc_ccitt_16_kermit_b(ans)


def get_state2(self):
    f_start = True
    msg = bytearray(b"\xB6\x49\x1B")
    msg.extend(self.sn.to_bytes((self.sn.bit_length() + 7) // 8, byteorder='little'))
    msg.extend(bytearray(b"\x01\x83"))
    msg = add_crc(msg, crc_ccitt_16_kermit_b(msg))
    msg = self._indicate_send_b6(msg)
    self.conn.reset_input_buffer()
    self.conn.reset_output_buffer()
    self.conn.write(msg)
    self.conn.flush()
    while f_start:
        if self.conn.read() == b"\xB9" and self.conn.read() == b"\x46":
            f_start = False
            ans = bytearray(b"\xB9\x46")
            for _ in range(25):
                b = self.conn.read()
                if b == b"\xB9" or b == b"\xB6":
                    self.conn.read()
                ans.extend(b)

            self.conn.reset_output_buffer()
            # logger.info(f"end {ans.hex()} in-{self.conn.in_waiting} out-{self.conn.out_waiting} ")
            if crc_ccitt_16_kermit_b(ans[:27]) == 0:
                self.sig_u_acp.emit(int.from_bytes(ans[9:11], "little") / 100)
                logger.info("crc ok")
            else:
                self.sig_disconnect.emit(True)
                logger.info(f"end {crc_ccitt_16_kermit_b(ans[:27])} {int.from_bytes(ans[25:27], 'little')} {ans.hex()}")
