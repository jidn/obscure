import argparse

from .encoder import Encode, encodings
from .feistel import Encoder, FeistelCipher, version1_feistel

_encodings = sorted(set(_ for _ in encodings.keys()))


def main(cmdline=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="show all modes")
    parser.add_argument("--decode", action="store_true")
    parser.add_argument(
        "--mode",
        dest="encoding",
        choices=_encodings,
        default="num",
        help="default(num)",
    )
    parser.add_argument("--prime", type=int, help="small prime for Feistel cipher")
    parser.add_argument("--salt", type=int, help="salt for Feistel cipher")
    parser.add_argument("--bits", type=int, help="default(64)", default=64)
    parser.add_argument("--v1", action="store_true", help="version 1 Feistel cipher")
    parser.add_argument("values", nargs=argparse.REMAINDER)

    args = parser.parse_args(cmdline)
    if not args.values:
        parser.print_help()
        return

    if "num" == args.encoding:
        # Encoding "num" requires int parameter not string
        args.values = [int(_) for _ in args.values]
        args.values = tuple(map(int, args.values))

    # Create the obscure.Encoder
    if args.v1:
        encoder = Encoder(version1_feistel(args.salt), args.encoding)
    else:
        encoder = Encoder(
            FeistelCipher(args.salt, args.prime, args.bits), args.encoding
        )

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
