import pytest
import obscure.encoder as change


def test_hex():
    all_hex = set("0123456789abcdef")
    for i in range(0, 0x1000, 0xFF):
        txt = change.hex_encode(i)
        assert set(txt).issubset(all_hex)
        assert i == change.hex_decode(txt)


def test_base32_round_trip():
    """Test encode/decode round trip."""
    alphabet = set(change._b32_crockford.decode("utf-8"))
    for i in range(0, 0x1F000, 0x1FF):
        b32_str = change.base32_encode(i)
        # Is it reversable
        assert i == change.base32_decode(b32_str)
        # Is the base32 using the expected alphabet
        assert set(b32_str).issubset(alphabet)


def test_base32_0():
    """Make sure we see '00' the Crockford alphabet. 'AA' is RFC 4648."""
    assert "00" == change.base32_encode(0)
    assert 0 == change.base32_decode("00")


def test_base64_round_trip():
    """Test encode/decode round trip."""
    alphabet = set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_")
    seen = set()
    for i in range(0, 0xFFFFFFFF, 0xFFFFF):
        b64_str = change.base64_encode(i)
        assert i == change.base64_decode(b64_str)
        # Is the base64 str using the expected alphabet
        assert set(b64_str).issubset(alphabet)
        seen.update(set(b64_str))
    assert alphabet == seen


def test_encode_base32_ex_bad_input():
    with pytest.raises(ValueError):
        change.base32_encode(-1)


def test_decode_base32_ex():
    with pytest.raises(ValueError):
        change.base32_decode("AEIOU-1")


def test_encode_base64_ex_bad_input():
    with pytest.raises(ValueError):
        change.base64_encode(-1)


def test_decode_base64_ex():
    with pytest.raises(ValueError):
        change.base64_decode("0==")
