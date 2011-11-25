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
        code = rsa.encrypt(word.word.encode('utf-8'), self.public_key)
        tohex = '{0:02x}'.format
        return ''.join(tohex(ord(c)) for c in code)

    def decrypt_word(self, encrypted_word):
        if not isinstance(encrypted_word, str):
            raise TypeError('encrypted_word must be a UTF-8 encoded str, not '
                            + repr(encrypted_word))
        count = len(encrypted_word)
        if count % 2:
            raise ValueError('invalid encrypted_word: its length must be '
                             'even')
        code = ''.join(chr(int(encrypted_word[i:i + 2], base=16))
                       for i in xrange(0, count, 2))
        word = rsa.decrypt(code, self.private_key).decode('utf-8')
        return Word.get_by_key_name(word)

