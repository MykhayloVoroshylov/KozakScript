import hashlib

class HashModule:
    def sha256(self, text):
        return hashlib.sha256(text.encode()).hexdigest()

    def md5(self, text):
        return hashlib.md5(text.encode()).hexdigest()