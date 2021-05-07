from functionalities import functionalities as func
from Config import Config as conf
import math
from charm.toolbox.integergroup import IntegerGroup
from charm.core.math.integer import *
import binascii
from backports.pbkdf2 import pbkdf2_hmac
import numpy as np
import pickle
import time


class testot:

	def test():
		
		G = IntegerGroup() # do this in config?
		G.paramgen(1024)
		g = G.randomGen()