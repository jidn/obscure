import typing

import pytest

import obscure
import tests.shared_data as data
from obscure.feistel import Encoder, FeistelCipher


def test_feistel_domain_boundary(feistel32):
    sequence = [feistel32(i) for i in range(100)]
    sequence.extend(feistel32(i) for i in range(0xFFFFFFFF, 0xFFFFFF7F, -1))
    is_uniform_distribution(sequence, 0xFFFFFFFF)


def test_feistel_make_fx():
    f = FeistelCipher(data.salt, data.prime)
    assert all(data.fx[x] == f(x) for x in (0, 101038, 0xFFFFFFFF))


def test_feistel_random_salt_prime():
    f = FeistelCipher(None, None)
    assert all(0 <= f(x) for x in (0, 101038))


def test_feistel_ex_bits_invalid():
    with pytest.raises(ValueError) as ex:
        FeistelCipher(None, None, bits=31)
    assert 'must be an even int' in str(ex)


def test_feistel_ex_not_in_domain():
    with pytest.raises(ValueError) as ex:
        FeistelCipher(None, None, bits=32)(-1)
    assert 'not within domain' in str(ex)


def test_encoder():
    encoder = Encoder(None, 'base32')
    assert 101038 == encoder.decode(encoder.encode(101038))


def test_encoder_ex_parameter_feistel():
    with pytest.raises(ValueError) as ex:
        Encoder(typing.cast(None, 123), 'num')
    assert 'is neither a FeistelCipher' in str(ex)


def test_encoder_ex_parameter_encoding():
    with pytest.raises(ValueError) as ex:
        Encoder(None, 'unknown')
    assert 'is not one of' in str(ex)


@pytest.mark.parametrize('domain_bits', (16, 32, 64, 128))
def test_feistel_uniform_distribution(domain_bits):
    func = obscure.FeistelCipher(0xC101, 0x3C96, bits=domain_bits)
    transformed: typing.List[int] = []
    mask = (1 << domain_bits) - 1
    for i in range(0, mask, max(1, mask // 10000)):
        x = func(i)
        assert x <= mask
        assert i == func(x)
        transformed.append(x)
    is_uniform_distribution(transformed, mask)


def is_uniform_distribution(sequence: typing.Sequence[int], domain: int):
    """I the given sequence a uniform distribution.

    Use a simplified chi-squared test accross eight buckets.

    Args:
        sequence: A sequence of unsigned ints within domain.

    Returns:
        bool: High confidence sequence approximates a uniform distribution.
    """
    if not sequence:
        return False  # Empty sequence cannot be tested.

    num_bins = 8
    # Calculate the expected frequency for each bin in a uniform distribution.
    expected = len(sequence) / num_bins

    # Initialize a dictionary to count the observed frequency in each bin.
    observed = dict.fromkeys(range(num_bins), 0)

    # Calculate the observed frequency in each bin.
    per_bin = domain // num_bins

    for value in sequence:
        bin_index = value // (per_bin + 1)
        observed[bin_index] += 1

    # Calculate the chi-squared statistic.
    chi_squared_statistic = sum(
        ((observed[i] - expected) ** 2) / expected for i in range(num_bins)
    )

    # If the p-value is less than the significance level, then the sequence
    # is not a uniform distribution.
    # significance_level = 0.05

    # Compare the chi-squared statistic to a critical value. If it's greater
    # than the critical value, reject the null hypothesis (not uniformly
    # distributed). Otherwise, accept the null hypothesis (uniformly distributed).

    # from scipy.stats import chi2
    # critical_value = chi2.ppf(1 - significance_level, df=num_bins - 1)

    critical_value = 14.067140449340169
    return chi_squared_statistic <= critical_value
