from dataclasses import dataclass
from gmpy2 import mpz

@dataclass
class angular_share:
	x1: mpz = -1
	x2: mpz = -1

@dataclass
class special_share:
	x1: mpz = -1
	x2: mpz = -1
	x3: mpz = -1