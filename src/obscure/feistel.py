"""Feistel cipher

A Feistel cipher can reversibly tranform a number from one value to
another. A Feistel cipher with its F(x) function are included.
However, writing your own F(x) is a trivial matter.

[Left]        [Right]
   |             /
 (xor)<-- F(x)<--
   |
[Right]       [Left]/

Example:

    Create a 32-bit Feistel cipher using default F(x) with a
    random prime and salt.

    >>> f = FeistelCipher()

    Because the default F(x) is using a random prime and salt, the
    cipher will generate different transformation for the same input
    number each time.  This may not be what you want.  Instead you
    want a constant transformation across executions.  For this case
    specify the prime and salt.

    >>> f = FeistelCipher(0xC101, 0x1234, 64)

    Now, the algoritm will produce the same results every time.

Feistel algorithm:

    Partition the given value equally; (L[0], R[0])
    Let F(x, Optinal[K]) = a function taking a data block and a subkey
    and returns one output of the same size as the data block.
    For i in range(N):
        L[i] = R[i-1]
        R[i] = L[i] xor F(R[i-1]), Optional[K[i]])
    Ciphertext is (R[N], L[N])

Reference:
    https://en.wikipedia.org/wiki/Feistel_cipher
"""
import functools
import random
import typing

from .encoder import encodings

IntInt = typing.Callable[[int], int]
random.seed()


def feistel_fx(salt: int, prime: int, value: int) -> int:
    """A round function `F(x)` for a Feistel cipher.

    Args:
        prime: A small prime number. https://t5k.org/lists/small/1000.txt
        salt: A number making your transformations unique.
        value: The input value

    Returns:
        a mutated number
    """
    x = (salt ^ value) * prime
    return x >> (value & 0xF)


def FeistelFx(salt: int | None = None, prime: int | None = None) -> IntInt:
    """Create a Feistel round function `F(x)`

    Args:
        prime: A small prime number.
            If None, select one from a list of over a 100.
        salt: A number making your transformations unique.
            If None, use a random integer.

    Returns:
        A Feistel round function Callable[[int], int]
    """
    p = prime or random.choice(_primes)
    s = salt or random.randint(1, 0xFFFFFF)
    return functools.partial(feistel_fx, s, p)


def create_feistel_cipher(fx: IntInt, bits: int, rounds):
    if not isinstance(bits, int) or 1 == bits % 2:
        raise ValueError("bits must be an even integer, usually 32 or 64.")
    full_mask = (1 << bits) - 1
    mask = full_mask >> (full_mask.bit_length() // 2)

    def feistel_cipher(value: int) -> int:
        if value < 0 or value > full_mask:
            raise ValueError("value is not within domain")

        # Split the input value into two halves
        lefty = mask & (value >> mask.bit_length())
        righty = mask & value

        for _ in range(rounds):
            lefty, righty = (righty, (lefty ^ (mask & fx(righty))))

        return righty << mask.bit_length() | lefty

    return feistel_cipher


def FeistelCipher(
    salt: int | None = None,
    prime: int | None = None,
    bits: int = 32,
    rounds: int = 4,
) -> IntInt:
    """Return a Feistel cipher for int transformation.

    Args:
        salt: Any number to salt the `F(x)`. Random if None.
        prime: A small prime for `F(x)`. Random if None.
        bits: Bits in the number domain, default(32).
        rounds: The number of times `F(x)` is called, default(4).

    For bits > 64, you need a larger prime. If should be at least one
    fourth of the total domain bytes transforming small numbers.  For
    example if bits=128, the prime should be 8 bytes.

    Returns:
            A Feistel cipher function.

    Raises:
        ValueError: When value outside the domain.
    """
    return create_feistel_cipher(FeistelFx(salt, prime), bits, rounds)


class Encoder:
    def __init__(self, feistel: IntInt | None, encoding: str = ""):
        """Create an encoder/decoder using a Feistel cipher.

        Args:
            feistel: A Feistel cipher function or create a random cipher.
            encoding: One of "base32", "base64", or "hex"
            encoder: The encoder function, default(str)
            decoder: The decoder function, default(int)
            bits: Bits for creating a Feistel cipher, default(32)
        """

        if feistel is None:
            self.func = FeistelCipher(None, 32)
        elif callable(feistel):
            self.func = feistel
        else:
            raise ValueError("feistel is neither a FeistelCipher nor None")
        try:
            self.encoder, self.decoder = encodings[encoding]
        except KeyError as ex:
            raise ValueError(
                f"{ex!r} is not one of {[str(_) for _ in encodings.keys()]!r}"
            )

    def transform(self, number: int) -> int:
        """Reversibly transform an integer.

        Args:
            number: to transform

        Returns:
            The transformed number.
        """
        return self.func(number)

    def encode(self, number: int) -> str:
        """Return the number transformed and encoded.

        Args:
            number: to transform

        Returns:
            A string of the tranformed, encoded number.
        """
        return self.encoder(self.transform(number))

    def decode(self, text: str) -> int:
        """Return the decoded and transformed number.

        Args:
            text: The encoded string of the transformed number.

        Returns:
            The number.
        """
        return self.transform(self.decoder(text))


def Obscure(salt: int):
    """The version 1 simple Feistel version."""

    return Encoder(version1_feistel(salt), "num")


def version1_feistel(salt: int | None = None) -> IntInt:
    """Create the Feistel cipher used in version 1.

    Args:
        salt: A number making your transformations unique.
            If None, use a random integer.

    Example:

        >>> cipher = version1_feistel(4049)
        >>> [cipher(x) for x in (1, 0xFFFF, 0xFFFFFFFF)]
        [3363954640, 3034109006, 2074028977]
    """

    if salt is None:
        salt = random.randint(1, 0xFFFFFF)

    def feistel(value: int) -> int:
        """Version 1 Feistel cipher."""

        def mangle16(x):
            x = (salt ^ x) * 0xC101
            return x >> (x & 0xF) & 0xFFFF

        left = 0xFFFF & value
        right = 0xFFFF & (value >> 16) ^ mangle16(left)
        return ((left ^ mangle16(right)) << 16) | right

    return feistel


# https://t5k.org/lists/small/1000.txt
_primes = (
    4001,
    4003,
    4007,
    4013,
    4019,
    4021,
    4027,
    4049,
    4051,
    4057,
    4073,
    4079,
    4091,
    4093,
    4099,
    4111,
    4127,
    4129,
    4133,
    4139,
    4153,
    4157,
    4159,
    4177,
    4201,
    4211,
    4217,
    4219,
    4229,
    4231,
    4241,
    4243,
    4253,
    4259,
    4261,
    4271,
    4273,
    4283,
    4289,
    4297,
    4327,
    4337,
    4339,
    4349,
    4357,
    4363,
    4373,
    4391,
    4397,
    4409,
    4421,
    4423,
    4441,
    4447,
    4451,
    4457,
    4463,
    4481,
    4483,
    4493,
    4507,
    4513,
    4517,
    4519,
    4523,
    4547,
    4549,
    4561,
    4567,
    4583,
    4591,
    4597,
    4603,
    4621,
    4637,
    4639,
    4643,
    4649,
    4651,
    4657,
    4663,
    4673,
    4679,
    4691,
    4703,
    4721,
    4723,
    4729,
    4733,
    4751,
    4759,
    4783,
    4787,
    4789,
    4793,
    4799,
    4801,
    4813,
    4817,
    4831,
    4861,
    4871,
    4877,
    4889,
    4903,
    4909,
    4919,
    4931,
    4933,
    4937,
    4943,
    4951,
    4957,
    4967,
    4969,
    4973,
    4987,
    4993,
    4999,
    5003,
    5009,
    5011,
    5021,
    5023,
    5039,
    5051,
    5059,
    5077,
    5081,
    5087,
    5099,
    5101,
    5107,
    5113,
    5119,
    5147,
    5153,
    5167,
    5171,
    5179,
    5189,
    5197,
    5209,
    5227,
    5231,
    5233,
    5237,
    5261,
    5273,
    5279,
    5281,
    5297,
    5303,
    5309,
    5323,
    5333,
    5347,
    5351,
    5381,
    5387,
    5393,
    5399,
    5407,
    5413,
    5417,
    5419,
    5431,
    5437,
    5441,
    5443,
    5449,
    5471,
    5477,
    5479,
    5483,
    5501,
    5503,
    5507,
    5519,
    5521,
    5527,
    5531,
    5557,
    5563,
    5569,
    5573,
    5581,
    5591,
    5623,
    5639,
)
