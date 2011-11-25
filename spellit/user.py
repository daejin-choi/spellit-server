from google.appengine.ext import db
import rsa
from .word import Word


class User(db.Model):

    db_public_key = db.ByteStringProperty(name='public_key', required=True)
    db_private_key = db.ByteStringProperty(name='private_key', required=True)
    name = db.StringProperty(required=True)

    def __init__(self, *args, **kwargs):
        if not ('public_key' in kwargs and 'private_key' in kwargs):
            pub, priv = rsa.newkeys(128)
            kwargs.update(public_key=pub.save_pkcs1(),
                          private_key=priv.save_pkcs1())
        super(User, self).__init__(*args, **kwargs)

    @property
    def public_key(self):
        return rsa.PublicKey.load_pkcs1(self.db_public_key)

    @public_key.setter
    def public_key(self, key):
        self.db_public_key = key.save_pkcs1()

    @property
    def private_key(self):
        return rsa.PrivateKey.load_pkcs1(self.db_private_key)

    @private_key.setter
    def private_key(self, key):
        self.db_private_key = key.save_pkcs1()

    def encrypt_word(self, word):
        if not isinstance(word, Word):
            raise TypeError('word must be a spellit.word.Word, not ' +
                            repr(word))
        word = word.word.encode('utf-8')
        chunks = []
        for i in xrange(0, len(word), 5):
            chunk = word[i:i + 5]
            code = rsa.encrypt(chunk, self.public_key)
            tohex = '{0:02x}'.format
            chunks.append(''.join(tohex(ord(c)) for c in code))
        return '-'.join(chunks)

    def decrypt_word(self, encrypted_word):
        if not isinstance(encrypted_word, str):
            raise TypeError('encrypted_word must be a UTF-8 encoded str, not '
                            + repr(encrypted_word))
        chunks = encrypted_word.split('-')
        word = []
        for chunk in chunks:
            count = len(chunk)
            if count % 2:
                raise ValueError('invalid encrypted_word')
            code = ''.join(chr(int(chunk[i:i + 2], base=16))
                           for i in xrange(0, count, 2))
            chunk = rsa.decrypt(code, self.private_key)
            word.append(chunk)
        return Word.get_by_key_name(''.join(word).decode('utf-8'))

