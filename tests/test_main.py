import tests.shared_data as data
from obscure.__main__ import main
from obscure.encoder import hex_encode

_FEISTEL = f"--prime={data.prime} --salt={data.salt} -b 32"


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


def test_main_decode_implied(capsys):
    encoded = hex_encode(data.fx[0])
    main(f"{_FEISTEL} --mode hex {encoded}".split())
    out = capsys.readouterr().out.strip()
    assert 0 == int(out)


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
