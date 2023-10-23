import sys
import timeit
from obscure.feistel import Obscure

COUNT = 10
RANGE = 100000
g = Obscure(0x382231AC)
if sys.version_info.major == 3:
    xrange = range


def samples():
    meths = (g.encode_hex, g.encode_tame, g.encode_base32, g.encode_base64)
    for x, X in zip(xrange(10), xrange(100000, 1000010)):
        print((x, tuple(f(x) for f in meths)), (X, tuple(f(X) for f in meths)))


def transform_test():
    for i in xrange(RANGE):
        txt = g.transform(i)
        integer = g.transform(txt)
        assert i == integer


def b32_test():
    for i in xrange(RANGE):
        txt = g.encode_base32(i)
        integer = g.decode_base32(txt)
        assert i == integer


def b64_test():
    for i in xrange(RANGE):
        txt = g.encode_base64(i)
        integer = g.decode_base64(txt)
        assert i == integer


def tame_test():
    for i in xrange(RANGE):
        txt = g.encode_tame(i)
        integer = g.decode_tame(txt)
        assert i == integer


def show_results(result):
    global COUNT, RANGE
    per_pass = 1000000 * (result / COUNT)
    print("  %.2f usec/pass" % per_pass)
    per_item = per_pass / RANGE
    print("  %.2f usec/item" % per_item)


if __name__ == "__main__":
    if True:
        samples()
        print("obscure-transform")
        t = timeit.Timer(transform_test)
        show_results(t.timeit(number=COUNT))
        print("obscure-base64")
        t = timeit.Timer(b64_test)
        show_results(t.timeit(number=COUNT))
        print("obscure-base32")
        t = timeit.Timer(b32_test)
        show_results(t.timeit(number=COUNT))
        print("obscure-tame")
        t = timeit.Timer(tame_test)
        show_results(t.timeit(number=COUNT))

    if False:
        print("pack/unpack")
        t = timeit.Timer(
            "unpack('!L', pack('!L', 0xc101))", "from struct import pack, unpack"
        )
        show_results(t.timeit())

        print("base32 encode/decode")
        t = timeit.Timer(
            "b32decode(b32encode(pack('!L', 0xc101)))",
            "from struct import pack, unpack; "
            "from base64 import b32decode, b32encode",
        )
        show_results(t.timeit())

        print("base64 encode/decode")
        t = timeit.Timer(
            "b64decode(b64encode(pack('!L', 0xc101), '-_'), '-_')",
            "from struct import pack, unpack; "
            "from base64 import b64decode, b64encode",
        )
        show_results(t.timeit())

        print("base64 urlsafe encode/decode")
        t = timeit.Timer(
            "urlsafe_b64decode(urlsafe_b64encode(pack('!L', 0xc101)))",
            "from struct import pack, unpack; "
            "from base64 import urlsafe_b64decode, urlsafe_b64encode",
        )
        show_results(t.timeit())
