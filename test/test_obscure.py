import sys
import pytest
import context
import obscure
if sys.version_info.major >= 3:
    xrange = range


@pytest.fixture(scope='function')
def ob():
    return obscure.Obscure(0x3c96)


def test_transform(ob):
    for i in xrange(0, 0x10000, 0xFF):
        x = ob.transform(i)
        assert x < 0xFFFFffff
        assert i == ob.transform(x)


def test_unique_low(ob):
    transformed = {ob.transform(i) for i in xrange(100)}
    assert 100 == len(transformed)
    assert all([x < 0xFFFFffff for x in transformed])


def test_unique_high(ob):
    transformed = {ob.transform(i) for i in xrange(0xFFFF, 0xFF90, -1)}
    assert 0xFFFF - 0xff90 == len(transformed)
    assert all([x < 0xFFFFffff for x in transformed])


def count_bits(integer):
    return len([_ for _ in bin(integer) if _ is '1'])


def test_bits_changed(ob):
    """Verify the transformation drastically changes bits."""
    for i in xrange(0, 0x10000, 0xFF):
        x = ob.transform(i)
        changed = count_bits(i ^ x)
        assert 8 <= changed


def test_salts(ob):
    """Verify a different salt drastically changes results."""
    ob2 = obscure.Obscure(0x4321)
    for i in xrange(0, 0x10000, 0xFF):
        x1 = ob.transform(i)
        x2 = ob2.transform(i)
        changed = count_bits(x1 ^ x2)
        assert 10 <= changed


@pytest.mark.parametrize('method,size', (('hex', 8), ('base64', 6),
                                         ('base32', 7), ('tame', 7)))
def test_encoding(method, size):
    """Try the different encoder/decoder"""
    ob = obscure.Obscure(0xc3c3)
    encoder = getattr(ob, 'encode_' + method)
    decoder = getattr(ob, 'decode_' + method)
    for i in xrange(0, 0x1000, 0xFF):
        s = encoder(i)
        assert size == len(s)
        v = decoder(s)
        assert i == v


def test_hex(ob):
    all_hex = set(iter("0123456789abcdef"))
    for i in xrange(0, 0x1000, 0xFF):
        s = ob.encode_hex(i)
        assert 8 == len(s)
        assert set(iter(s)).issubset(all_hex)


def test_base32(ob):
    all_base32 = set(iter(obscure._base32_normal))
    for i in xrange(0, 0x1000, 0xff):
        s = ob.encode_base32(i)
        assert 7 == len(s)
        assert set(iter(s)).issubset(all_base32)


def test_tame(ob):
    all_tame = set(iter(obscure._base32_custom))
    for i in xrange(0, 0x1000, 0xff):
        s = ob.encode_tame(i)
        assert 7 == len(s)
        assert set(iter(s)).issubset(all_tame)


def test_base64(ob):
    for i in xrange(0, 0x1000, 0xff):
        s = ob.encode_base64(i)
        assert 6 == len(s)
