"""Type hints"""
from typing import Union, Tuple

from qutip import Qobj
import numpy as np

Gate = Union[Qobj, np.ndarray]
CTuple = Tuple[float, float, float]
GTuple = Tuple[float, float, float]
