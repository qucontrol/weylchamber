import warnings

from weylchamber import random_gate, concurrence, c1c2c3, cartan_decomposition
import qutip
import numpy as np

import pytest


@pytest.mark.xfail
def test_cartan_decomposition_random():
    U = random_gate()
    phasefactor = np.linalg.det(U.full())**0.25
    assert abs(np.linalg.det(U.full()) - 1) < 1e-15
    C = concurrence(*c1c2c3(U))
    k1, A, k2 = cartan_decomposition(U)
    assert ((phasefactor * k1 * A * k2) - U).norm() < 1e-15
    assert concurrence(*c1c2c3(k1)) == 0
    assert concurrence(*c1c2c3(k2)) == 0
    assert abs(concurrence(*c1c2c3(A)) - C) < 1e-15


def test_cartan_decomposition_cnot():
    warnings.filterwarnings(
        'ignore', message='the matrix subclass is not the recommended way')
    U = qutip.gates.cnot()
    phasefactor = np.linalg.det(U.full())**0.25
    C = concurrence(*c1c2c3(U))
    assert C == 1
    k1, A, k2 = cartan_decomposition(U)
    assert ((phasefactor * k1 * A * k2) - U).norm() < 1e-15
    assert concurrence(*c1c2c3(k1)) == 0
    assert concurrence(*c1c2c3(k2)) == 0
    assert abs(concurrence(*c1c2c3(A)) - C) < 1e-15
