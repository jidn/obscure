"""Obscure numbers through reversable transformation.

Showing a steadly increasing sequence of integer IDs leaks information
to customers, competitors, or malicious entities about the number and
frequency of customers, inventory, or orders.  Some example include:

  /customer/123
  /order/308

From these, I would conclude that I am only your 123rd customer with the
308th order.  How a customer or competitor would feel about this would
differ.  However, the point is do I really want others to know this
information?  In addition, by creating another account or order, I can
estimate the rate of change within your systems.

This class will help obscure your sequential order by providing a
reverseable transformation to your numbers.  By using different salts
your transformations will be unique.  In addition, the class gives some
output helpers for hex, base32, and base64.  There is one I call 'tame'
as it removes the letters i and u to elimination some common offensive
words.

Example:
    >>> from obscure import Obscure
    >>> customer_id = 123
    >>> num = Obscure(0x1234)
    >>> num.transform(customer_id)
    249699227
    >>> num.transform(249699227)
    123
    >>> num.encode_hex(customer_id)
    '0ee21b9b'
    >>> num.encode_base32(customer_id)
    'B3RBXGY'
    >>> num.decode_base32(num.encode_base32(customer_id))
    123
    >>> num.encode_base64(customer_id)
    'DuIbmw'
    >>> num.encode_tame(customer_id)
    'D8WD4J5'
    >>> num.decode_tame(num.encode_tame(customer_id))
    123
"""
import sys
try:
    from string import maketrans as _maketrans
except ImportError:  # pragma: no cover
    _maketrans = str.maketrans
import struct
import base64

__version__ = '1.0.0'

_base32_normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
_base32_custom = "CDEFGHJKLMNPQRSTVWXYZ234567890AB"
_encode_trans = _maketrans(_base32_normal, _base32_custom)
_decode_trans = _maketrans(_base32_custom, _base32_normal)


class Obscure(object):
    """Obscure a number using Feistel ciper transformation.

    Transform an integer (such as database auto-increment IDs) and
    obscures them from simple detection.
    """

    def __init__(self, salt):
        """Obscure object with unique salt and prime.
        :param salt: an integer making your transformations unique.
        """
        self.salt = salt
        self.prime = 0xc101

    def _mangle16(self, i):
        """Produce an 16-bit mangled value based off a 16-bit integer.
        :param i: 16-bit integer
        :returns: 16-bit transformation.
        """
        i = (self.salt ^ i) * self.prime
        return i >> (i & 0xf) & 0xffff

    def transform(self, i):
        """Reversibly transform a 32-bit integer using Feistel cipher.
        :param i: integer
        :returns: transformed integer so transform(transform(i)) == i
        """
        l = i & 0xffff
        h = i >> 16 & 0xffff ^ self._mangle16(l)
        return ((l ^ self._mangle16(h)) << 16) + h

    def encode_hex(self, i):
        """Obscure an integer to hex string.
        :param i: integer
        :returns: 8-character hex string.
        """
        return "%08x" % self.transform(i)

    def decode_hex(self, s):
        """Decode an 8-character hex string, returning the original integer.
        :param s: encoded hex string
        :returns: original integer"""
        return self.transform(int(s, 16))

    def encode_base32(self, i):
        """Obscure an integer and return a base32 string.
        :param i: integer
        :returns: 7-character base32 string.
        """
        s = base64.b32encode(struct.pack('!L', self.transform(i)))
        if sys.version_info.major == 3:  # pragma: no cover
            s = s.decode('ascii')
        return s[:7]

    def decode_base32(self, s):
        """Decode a base32 string, returning the original integer.
        :param s: 7-character base32 string
        :returns: original integer
        """
        return self.transform(struct.unpack('!L', base64.b32decode(s + '='))[0])

    def encode_tame(self, i):
        """Obscure an integer and return a base32 string.
        The base32 alphabet without the letters I and U to eliminate
        common offensive words.
        :param i: integer
        :returns: 7-character custom alphabet base32 string.
        """
        s = self.encode_base32(i)
        return s.translate(_encode_trans)

    def decode_tame(self, s):
        """Decode a custom base32 string, returning the original integer.
        :param s: custom encoded, 7-character base32 string
        :returns: original integer
        """
        return self.decode_base32(s.translate(_decode_trans))

    def encode_base64(self, i):
        """Obscure an integer and return a 6-char base64 string.
        :param i: integer
        :returns: 6-character base64 string
        """
        s = base64.urlsafe_b64encode(struct.pack('!L', self.transform(i)))
        if sys.version_info.major == 3:  # pragma: no cover
            s = s.decode('ascii')
        return s[:6]

    def decode_base64(self, s):
        """Decode a base64 string, returning the original integer.
        :param s: 6-character base64 string
        :returns: oritinal integer
        """
        return self.transform(struct.unpack('!L',
                              base64.urlsafe_b64decode(s + '=='))[0])


if __name__ == "__main__":  # pragma: no cover
    import argparse
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group()
    g.add_argument('-s', nargs=2, type=int, metavar=('START', 'STOP'),
                   help='start stop of convert sequence')
    g.add_argument('-i', nargs='+', dest='int', type=int,
                   help='add number to covert')
    g.add_argument('-t', nargs='+', dest='str',
                   help='string to convert to number')
    p.add_argument('--mode', choices=('hex', 'tame', 'base32', 'base64'),
                   default='tame')
    p.add_argument('--salt', type=int, default=0x1235678)

    args = p.parse_args()
    o = Obscure(args.salt)
    meth = getattr(o, 'encode_' + args.mode)
    seq = None
    if args.s:
        seq = range(args.s[0], args.s[1])
    elif args.int:
        seq = args.int
    elif args.str:
        seq = args.str
        meth = getattr(o, 'decode_' + args.mode)
    if seq:
        for i in seq:
            print(meth(i)),
        print
