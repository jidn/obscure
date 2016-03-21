#!/usr/bin/env python
import os, sys
from setuptools import setup, find_packages

PYVER = sys.version_info[:2]  # (3, 4)
BASEDIR = os.path.dirname(__file__)

# Get version without import and fresh install race condition.
for _ in open(os.path.join(BASEDIR, 'obscure.py')).readlines():
    if _.startswith('__version__'):
        exec(_.strip(), None)
        break


setup(
    name='obscure',
    author='Clinton James',
    author_email='clinton.james@anuit.com',
    url='https://www.github.com/jidn/obscure/',
    download_url='https://github.com/jidn/obscure/tarball/'+__version__,
    description='Stop leaking information by obscuring sequential ID numbers',
    license='Apache License 2.0',
    long_description=open(os.path.join(BASEDIR, 'README.md')).read(),
    version=__version__,
    keywords=['encrypt_id', 'REST', 'obfuscate'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    py_modules=['obscure'],
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    include_package_data=True,
)
