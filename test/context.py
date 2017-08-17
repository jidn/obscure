"""
Import code modules
I always forget how to do this.  I finally nailed it down.
Below is my source of information.
https://www.kennethreitz.org/essays/repository-structure-and-python
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
