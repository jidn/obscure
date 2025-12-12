"""Obscure a number with reversible algorithm.

The "obscure" package is a Python library designed to provide a secure
and reversible transformation for numeric IDs. It employs the Feistel
cipher algorithm to obscure numerical values, making it more challenging
for outsiders to discern sensitive information from numeric identifiers.

Main Components:
----------------
Feistel Cipher:
  The core of "obscure" package is a Feistel cipher implementation.
  The Feistel cipher is a symmetric-key block cipher that iteratively
  transforms input data using a series of rounds. This cryptographic
  technique ensures both security and reversibility.

Feistel Cipher Round Function, F(x):
  Within the Feistel cipher, a round function is applied to each block
  of data. This round function is carefully designed to ensure that
  the transformation is both secure and can be reversed without loss
  of information

Reversible String Encoders:
 Obscure provides a set of reversible string encoders that allow
 transformed numbers to be represented in different formats, such as
 hexadecimal (hex), base32 using Crockford's alphabet, and base64.

 These encoders ensure the transformed data remains human-readable
 and can be decoded back to its original numeric form when needed.

Usage Example:
--------------
  Here's a basic example of how to use the "obscure" package:

  import obscure

  # Initialize a Feistel cipher with random values for FeistelFx.
  # Each instance will tranform inputs differently.
  cipher = obscure.FeistelCipher(bits=128)

  # Initialize Fesitel cipher with specific transformation values.
  # Each instance will transform input identically.
  cipher = obscure.FeistelCipher(obscure.FeistelFx(prime=49409, salt=4049))

  # Transform a numeric ID (e.g., 12345)
  numeric_id = 12345
  transformed_data = cipher(numeric_id)

  # Encode the transformed data in base32.
  encoded = obscure.base32_encode(transformed_data)

  # To reverse the process:
  # Decode the hexadecimal representation
  decoded_data = obscure.base32_decode(encoded)

  # Decrypt the transformed data back to the original numeric ID
  original_numeric_id = cipher(decoded_data)

  print("Original numeric ID: ", numeric_id)
  print("Transformed numeric ID: ", transformed_data)
  print("Transformed data (base32): ", encoded)
  print("Decoded data: ", decoded_data)
  print("Decrypted Numeric ID: ", original_numeric_id)

A Peek Behind the Scenes: Feistel Cipher
----------------------------------------
Now, let's take a magical look at what happens in the inner workings
of out Feistel cipher and how number transformation is accomplished.

Picture it like a magician performing a card trick. You start with a
deck of cards (the bits of number number) you want to shuffle securely.
This magician has a magic box that transforms a group of cards while
also using a different group of cards for inspiration, the F(x) or
round function.

Split and Shuffle:
  The magician takes a card and splits it into two halves, and puts
  one half to the left, called "Lefty" and the other to the right,
  who we will obviously call "Righty".

Transformation:
  Lefty travels to the magic box, where it encounters an enchanting
  transformation spell that uses Righty as inspiration. The spell
  scrambles Lefty in a way only the magic box knows. This is the
  secret sauce of our cipher.

  Righty, on the other hand, watches from the sidelines, oblivious
  to Lefty's transformation.

  Now the magician has Lefty and Righty change places.  The magic
  box uses the same transformation spell on Righty while using the
  transformed Lefty as inspiration. Finally, the transformed Righty
  goes back to the magician.

Repeat and Combine:
  The magician repeats this process for several rounds, making sure
  to keep Lefty and Righty switching places and undergoing the same
  spellbinding transformations.

  In the end, when all the rounds are done, combine Lefty and Righty
  and you're left with a deck of cards (your number) that's been
  thoroughly mixed up by these magical boxes.

The beauty of it all is that this magic show can be reversed! By
running the process backward, you can unscramble your cards and reveal
the original order.

Our Feistel cipher's round function F(x) is the magician's magic box,
working its sorcery to transform your data in a way that's secure and,
most importantly, reversible. It's this enchanting dance between Lefty
and Righty that keeps your data safe and sound.

So, while your data may seem like a deck of cards lost in a magical
whirlwind, fear not—our Feistel cipher knows the trick to bring them
back, just as good as new!
"""

from .encoder import (
    encodings,
    # base32_decode,
    # base32_encode,
    # base64_decode,
    # base64_encode,
    # hex_decode,
    # hex_encode,
)
from .feistel import Encoder, FeistelCipher, FeistelFx

__all__ = ['Encoder', 'FeistelCipher', 'FeistelFx', 'encodings']
