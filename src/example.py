"""Example.

>>> import obscure

# Initialize Fesitel cipher with specific transformation values.
# Each instance will transform input identically.
>>> cipher = obscure.FeistelCipher(salt=4049, prime=49409, bits=64)

# Transform a numeric ID (e.g., 12345)
>>> original_int = 12345
>>> transformed_int = cipher(original_int)
>>> transformed_int
16526555549533242699

# Encode the transformed number in base32. This is what you display to
# any user facing URL query string or JWT token.
>>> encoded = obscure.encoder.base32_encode(transformed_int)
>>> encoded
'WND1XDFTP22MP'

# To reverse the process:
# Decode the hexadecimal representation
>>> decoded_int = obscure.encoder.base32_decode(encoded)
>>> decoded_int
16526555549533242699

# Decrypt the transformed data back to the original number.
>>> original_original_int = cipher(decoded_int)
>>> original_original_int
12345


# When using encoding, the transformed number is part of the process
# but not of much interest.
# Simplify by using an Encoder with base32 encoding and the cipher.
>>> encoder = obscure.Encoder(cipher, "base32")
>>> encoded = encoder.encode(12345)
>>> encoded
'WND1XDFTP22MP'

# Use the encoded value as part of a URL query string or JWT token.
# When the value returns, decode and get the original value.
>>> encoder.decode(encoded)
12345
"""
