[![build status](https://travis-ci.org/jidn/obscure.svg?branch=master)](https://travis-ci.org/jidn/obscure.svg?branch=masterp)
![version](http://img.shields.io/pypi/v/obscure.svg)
![license](http://img.shields.io/pypi/l/obscure.svg)
![coverage](https://coveralls.io/repos/github/jidn/obscure/badge.svg?branch=master)
![downloads](http://img.shields.io/pypi/dm/obscure.svg)

# Obscure

Showing a steadily increasing sequence of integer IDs leaks information
to customers, competitors, or malicious entities about the number and
frequency of customers, inventory, or orders.  Some example include:

    /customer/123
    /order/308

From these, I would conclude that I am only your 123rd customer with the
308th order.  How a customer or competitor would feel about this would
differ.  However, the point is do I really want others to know this
information?  In addition, by creating another account or order, I can
estimate the rate of change within your systems.

This class will help obscure your sequential order by providing a
reversible transformation to your numbers.  By using different salts
your transformations will be unique.  In addition, the class gives some
output helpers for hex, base32, and base64.  There is one I call 'tame'
as it removes the letters i and u to elimination some common offensive
words.

# Install

By far the simplest method is to use pip:

```console
$ pip install obscure
```

# Example

   $python -m obscure --bits=64 --demo 0 1 2 3

```python
>>> from obscure import FeistelCipher, Encoder
>>> cipher = FeistelCipher(bits=64)
# For a consistant transformations between instances,give a
# salt and small prime for the Feistel cipher's round function
>>> cipher = FeistelCipher(0x1234, 0xc101, bits=64)
>>> numeric_id = 1234
>>> cipher(numeric_id)
249699227
# Reverse the transformation
>>> cipher(cipher(numeric_id))
1234
# Use an Encoder to wrap the Feistel cipher
>>> encoder = Encoder(Feistel, "base32")
>>> encoder.encode(numeric_id)
"XXX"
>>> encoder.decode('XXX")
1234
```
