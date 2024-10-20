"""Encoding/Decoding numbers."""

import base64
import typing

Encode = typing.Callable[[int], str]
Decode = typing.Callable[[str], int]
_b32_alphabet_rfc4348: bytes = base64._b32alphabet  # type: ignore
# Crockford eliminates some letter/number confusion
_b32_crockford = b"0123456789ABCDEFGHJKMNPQRSTVWXYZ"  # Excludes 'ILOU'
_b32_crockford_encode = bytes.maketrans(_b32_alphabet_rfc4348, _b32_crockford)
_b32_crockford_decode = bytes.maketrans(_b32_crockford, _b32_alphabet_rfc4348)


def hex_encode(number: int) -> str:
    """Return a string all hex no '0x' prefix."""
    return "%x" % number


def hex_decode(text: str) -> int:
    """Return int from hex string."""
    return int(text, 16)


def _get_minimum_num_bytes(number: int) -> int:
    """Return minimum number of bytes needed to represent the given number.

    Args:
        number: The int value to be represented.

    Returns:
        The minimum number of bytes needed to represent the int value.
    """
    return max(1, (number.bit_length() + 7) // 8)


def _add_padding(text: str, base: int) -> str:
    """Add padding to an encoded string if needed.

    Args:
        text: The Base32/Base64 encoded string to pad.
        base: Either 32, or 64

    Returns:
        The encoded string with padding added, if necessary.
    """
    mod = 8 if 32 == base else 4
    last_block_width = len(text) % mod
    if last_block_width != 0:
        text += (mod - last_block_width) * "="
    return text


def base32_encode(number: int) -> str:
    """Encode number to base32 using the Crockford alphabet.

    Example:
        >>> base32_encode(0)
        '00'
    """
    if number < 0:
        raise ValueError("Non-negative number is required.")
    return (
        base64.b32encode(number.to_bytes(_get_minimum_num_bytes(number), "big"))
        .translate(_b32_crockford_encode)
        .decode("utf-8")
        .rstrip("=")
    )


def base32_decode(text: str) -> int:
    """Decode base32 string using the Crockford alphabet.

    Example:
        >>> base32_decode('00')
        0
    """
    btext = _add_padding(text, 32).encode("utf-8")
    btext = btext.translate(_b32_crockford_decode)

    try:
        return int.from_bytes(base64.b32decode(btext), "big")
    except ValueError:
        # Handle invalid base32 strings
        raise ValueError("Invalid base32 string")


def base64_encode(number: int) -> str:
    """Encode number to base64.

    Example:
        >>> base64_encode(101038)
        'AYqu'
    """
    if number < 0:
        raise ValueError("Non-negative number is required.")
    return (
        base64.urlsafe_b64encode(number.to_bytes(_get_minimum_num_bytes(number), "big"))
        .decode("utf-8")
        .rstrip("=")
    )


def base64_decode(text: str) -> int:
    """Decode base64 string.

    Example:
        >>> base64_decode('AYqu')
        101038
    """
    btext = _add_padding(text, 64).encode("utf-8")
    try:
        return int.from_bytes(base64.urlsafe_b64decode(btext), "big")
    except ValueError:
        # Handle invalid base64 strings
        raise ValueError("Invalid base64 string")


encodings: typing.Dict[str, typing.Tuple[Encode, Decode]] = {
    "num": (typing.cast(Encode, int), typing.cast(Decode, int)),
    "hex": (hex_encode, hex_decode),
    "base32": (base32_encode, base32_decode),
    "base64": (base64_encode, base64_decode),
}
