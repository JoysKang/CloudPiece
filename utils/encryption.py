from Crypto.Cipher import AES
from Crypto import Random
import hashlib


class AESCipher:
    def __init__(self, key):
        self.bs = 32
        self.key = bytes.fromhex(hashlib.sha256(key.encode()).hexdigest())

    def encrypt(self, raw):
        content_padding = self._pad(raw).encode()
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypt_bytes = cipher.encrypt(content_padding)
        return (iv + encrypt_bytes).hex()

    def decrypt(self, enc):
        enc = bytes.fromhex(enc)
        iv = enc[:AES.block_size]
        enc = enc[AES.block_size:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypt_bytes = enc
        decrypt_bytes = cipher.decrypt(encrypt_bytes)
        return self._unpad(decrypt_bytes.decode('utf-8'))

    def _pad(self, s):
        return s + (self.bs - len(s.encode()) % self.bs) * chr(self.bs - len(s.encode()) % self.bs)

    def _unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]


if __name__ == "__main__":
    key = "UwO&fqEUiEZW%p7KP8)Xwv1qDxbfOmSD"
    text = "123"
    AES = AESCipher(key)
    etext = AES.encrypt(text)
    print(etext)
    print(AES.decrypt(etext))
