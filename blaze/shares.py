from dataclasses import dataclass
import numpy as np

@dataclass
class angular_share:
	x1: np.uint64 = -1
	x2: np.uint64 = -1

@dataclass
class special_share:
	x1: np.uint64 = -1
	x2: np.uint64 = -1
	x3: np.uint64 = -1