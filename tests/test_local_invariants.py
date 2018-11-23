import warnings

from weylchamber import closest_LI, c1c2c3
import qutip


def test_closest_LI_trivial_powell():
    """Test that a gate exactly at (c1, c2, c3) is in fact closest to itself"""
    warnings.filterwarnings(
        'ignore', message='the matrix subclass is not the recommended way')
    CNOT = qutip.gates.cnot()
    U = closest_LI(CNOT, *c1c2c3(CNOT), method='Powell')
    assert isinstance(U, qutip.Qobj)
    assert (CNOT - U).norm() < 1e-15


def test_closest_LI_trivial_leastsq():
    """Test that a gate exactly at (c1, c2, c3) is in fact closest to itself"""
    warnings.filterwarnings(
        'ignore', message='the matrix subclass is not the recommended way')
    CNOT = qutip.gates.cnot()
    U = closest_LI(CNOT, *c1c2c3(CNOT), method='leastsq')
    assert isinstance(U, qutip.Qobj)
    assert (CNOT - U).norm() < 1e-15
