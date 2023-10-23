import pytest

import tests.shared_data as data
from obscure.__main__ import main

_FEISTEL = f"--bits=32 --prime={data.prime} --salt={data.salt}"
_V1 = f"--salt={data.salt} --v1"


def test_main_help(capsys):
    """Help is shown in the expected places."""
    main("")
    out = capsys.readouterr().out
    assert "show this help message and exit" in out


def test_main_ex_demo_for_encoding(capsys):
    """The --demo option demonstrates encoding a value, not decoding."""
    main("--decode --demo 101038".split())
    out = capsys.readouterr().out
    assert "only for encoding" in out


def test_main_encode(capsys):
    main(f"{_FEISTEL} 0".split())
    out = capsys.readouterr().out.strip()
    assert data.fx[0] == int(out)


def test_main_decode(capsys):
    # "--bits=32 --prime=49049 --salt=4049"
    main(f"{_FEISTEL} --decode {data.fx[0]}".split())
    out = capsys.readouterr().out.strip()
    assert 0 == int(out)


def test_main_encode_v1(capsys):
    main(f"{_V1} 0".split())
    out = capsys.readouterr().out.strip()
    assert data.v1[0] == int(out)


@pytest.mark.parametrize("cmdline", ("--v1 0", "0"))
def test_main_random_cipher_args(capsys, cmdline):
    main(cmdline.split())
    out = capsys.readouterr().out.strip()
    assert 0 <= int(out)


def test_main_decode_v1(capsys):
    main(f"{_V1} --decode {data.v1[0]}".split())
    out = capsys.readouterr().out.strip()
    assert "0" == out


def test_main_demo(capsys):
    """Use make_fx() to verify output."""
    main(f"{_FEISTEL} --demo 0".split())
    out = capsys.readouterr().out

    expected = {
        "num": str(data.fx[0]),
        "hex": "80d14980",
        "base32": "G38MK00",
        "base64": "gNFJgA",
    }
    for line in out.split("\n"):
        if not line:
            continue
        mode, value = line.split()
        # Strip tailing ':' from mode and [' value ']
        assert expected[mode[:-1]] == value[1:-1].strip("'")
