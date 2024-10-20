"""Command-line execution."""

import argparse

from .encoder import Encode, encodings
from .feistel import Encoder, FeistelCipher

_encodings = sorted(set(_ for _ in encodings.keys()))
_examples = """Example:
  Encode numbers 0 and 100 for given prime and salt.

  $ python -m obscure --demo {0} 0 100
  base32:   ['4PDQY40', 'MXSGVR0']
  base64:   ['JZt_EA', 'p3MN4A']
  hex:   ['259b7f10', 'a7730de0']
  num:   [630947600, 2809335264]

  Show decoded values for given prime and salt.
  $ python -m obscure {0} 2809335264
  100

  $ python -m obscure {0} --mode=base32 MXSGVR0
  100

  $ python -m obscure {0} --mode=base64 p3MN4A
  100
      """.format("-p 4999 -s 1357 -b 32")
# """.format("--prime=4999 --salt=1357 --bits=32")


def main(cmdline=None):
    """Command line execution."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--demo", action="store_true", help="show all modes")
    parser.add_argument("--decode", action="store_true")
    parser.add_argument(
        "--mode",
        dest="encoding",
        choices=_encodings,
        default="num",
        help="default(num)",
    )
    parser.add_argument(
        "-p",
        "--prime",
        type=int,
        metavar="NUM",
        help="cipher small prime, default(random)",
    )
    parser.add_argument(
        "-s", "--salt", metavar="NUM", type=int, help="cipher salt, default(random)"
    )
    parser.add_argument(
        "-b",
        dest="bits",
        type=int,
        choices=(32, 64),
        help="cipher bits in domain, default(64)",
        default=64,
    )
    parser.add_argument("values", nargs=argparse.REMAINDER)
    parser.epilog = _examples

    args = parser.parse_args(cmdline)
    if not args.values:
        parser.print_help()
        return

    if "num" != args.encoding:
        # Decode is implied. Needed as base32 and base64 could be all numbers
        args.decode = True
    else:
        # Encoding "num" requires int parameter not string
        args.values = [int(_) for _ in args.values]
        args.values = tuple(map(int, args.values))

    encoder = Encoder(FeistelCipher(args.salt, args.prime, args.bits), args.encoding)

    if not args.demo:
        coder = getattr(encoder, ("decode" if args.decode else "encode"))
        print(" ".join(str(coder(i)) for i in args.values))
    else:
        if args.decode or args.encoding != "num":
            print("Demo is only for encoding numbers.")
            return

        for encoding in _encodings:
            meth: Encode = encodings[encoding][0]
            values = [meth(encoder.transform(int(i))) for i in args.values]
            print(f"{encoding}:  ", values)


if __name__ == "__main__":  # pragma: no cover
    main()
