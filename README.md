[![build status](https://travis-ci.org/jidn/obscure.svg?branch=master)](https://travis-ci.org/jidn/obscure.svg?branch=masterp)
![version](http://img.shields.io/pypi/v/obscure.svg)
![license](http://img.shields.io/pypi/l/obscure.svg)
![coverage](https://coveralls.io/repos/github/jidn/obscure/badge.svg?branch=master)
![downloads](http://img.shields.io/pypi/dm/obscure.svg)

# Obscure

Showing a steadly increasing sequence of integer IDs leaks information
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
reverseable transformation to your numbers.  By using different salts
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

```python
>>> from obscure import Obscure
>>> customer_id = 123
>>> num = Obscure(0x1234)
>>> num.transform(customer_id)
249699227
>>> num.transform(249699227)
123
>>> num.encode_hex(customer_id)
'0ee21b9b'
>>> num.encode_base32(customer_id)
'B3RBXGY'
>>> num.decode_base32(num.encode_base32(customer_id))
123
>>> num.encode_base64(customer_id)
'DuIbmw'
>>> num.encode_tame(customer_id)
'JB4XFK5'
>>> num.decode_tame(num.encode_tame(customer_id))
123
```
