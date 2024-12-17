class Message:
    def __init__(self, b=None):
        if b is None:
            self.header = bytes([0xAA, 0xAA])
            self.len = 0x00
            self.id = 0x00
            self.ctrl = 0x00
            self.params = bytes([])
            self.checksum = None
        elif len(b) >= 6:  # Minimalna długość wiadomości
            self.header = b[0:2]
            self.len = b[2]
            self.id = b[3]
            self.ctrl = b[4]
            self.params = b[5:-1]
            self.checksum = b[-1]
        else:
            raise ValueError("Invalid message format: Too few bytes")

    def __repr__(self):
        return f"Message(header={self.header}, id={self.id}, ctrl={self.ctrl}, len={self.len}, checksum={self.checksum})"

    def __str__(self):
        self.refresh()
        hex_header = " ".join(f"{byte:02x}" for byte in self.header)
        hex_params = " ".join(f"{byte:02x}" for byte in self.params)
        return f"{hex_header}:{self.len}:{self.id}:{self.ctrl}:{hex_params}:{self.checksum}".upper()

    def refresh(self):
        self.ctrl = self.ctrl.value if type(self.ctrl) != type(0) else self.ctrl
        self.id = self.id.value if type(self.id) != type(0) else self.id
        if self.checksum is None:
            self.checksum = self.id + self.ctrl
            for i in range(len(self.params)):
                if isinstance(self.params[i], int):
                    self.checksum += self.params[i]
                else:
                    self.checksum += int(self.params[i].encode('hex'), 16)
            self.checksum = self.checksum % 256
            self.checksum = 2 ** 8 - self.checksum
            self.checksum = self.checksum % 255 # TODO verify this
            self.len = 0x02 + len(self.params)

    
    def bytes(self):
        """
        Zwraca wiadomość jako ciąg bajtów.
        """
        self.refresh()
        command = bytearray([*self.header, self.len, self.id, self.ctrl])
        command.extend(self.params)
        command.append(self.checksum)
        return bytes(command)
