import pytest

from obscure import FeistelCipher


@pytest.fixture(scope="session")
def feistel32():
    """32-bit encoder with fx having randomized prime and salt.

    Use the same Encoder for all tests to provide consistant results
    within a suite execution.
    """
    return FeistelCipher()
