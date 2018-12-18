"""Calculation of Weyl chamber coordinates"""

import numpy as np
from numpy import less, greater
from numpy import logical_and as And
from numpy import logical_or as Or
from numpy import less_equal as less_eq
from numpy import greater_equal as greater_eq
import qutip

from .gates import Qmagic, SxSx, SySy, SzSz
from .prec import DEFAULT_WEYL_PRECISSION
from ._types import Gate, CTuple

__all__ = [
    'c1c2c3', 'canonical_gate', 'from_magic', 'point_in_region',
    'point_in_weyl_chamber', 'random_gate', 'random_weyl_point', 'to_magic',
    'weyl_region']


def c1c2c3(U: Gate, ndigits=DEFAULT_WEYL_PRECISSION) -> CTuple:
    """Calculate Weyl chamber coordinates $(c_1, c_2, c_3)$

    Given U (in canonical basis), calculate the Weyl Chamber coordinates
    $(c_1, c_2, c_3)$, in units of π.

    In order to facility numerical stability, the resulting coordinates are
    rounded to the given precision (cf. `ndigits` parameter of the built-in
    `round` function). Otherwise, rounding errors would likely to result in
    points that are not in the Weyl chamber, e.g. (0.1, 0.0, 1.0e-13)

    Algorithm from Childs et al., PRA 68, 052311 (2003).

    Example:
        >>> print("%.2f %.2f %.2f" % c1c2c3(qutip.gates.cnot()))
        0.50 0.00 0.00
    """
    U = qutip.Qobj(U, dims=[[2, 2], [2, 2]])
    if U.shape != (4, 4):
        raise ValueError("Gates must have a 4×4 shape")
    U_tilde = SySy * U.trans() * SySy
    ev = np.linalg.eigvals(
        ((U * U_tilde).full())/np.sqrt(complex(np.linalg.det(U.full()))))
    two_S = np.angle(ev) / np.pi
    for i in range(len(two_S)):
        if two_S[i] <= -0.5:
            two_S[i] += 2.0
    S = np.sort(two_S / 2.0)[::-1]  # sort decreasing
    n = int(round(sum(S)))
    S -= np.r_[np.ones(n), np.zeros(4-n)]
    S = np.roll(S, -n)
    M = np.array([[1, 1, 0], [1, 0, 1], [0, 1, 1]])
    c1, c2, c3 = np.dot(M, S[:3])
    if c3 < 0:
        c1 = 1 - c1
        c3 = -c3
    return (round(c1+0.0, ndigits),  # adding 0.0 turns -0.0 into +0.0
            round(c2+0.0, ndigits),
            round(c3+0.0, ndigits))


def point_in_weyl_chamber(
        c1: float, c2: float, c3: float, raise_exception=False) -> bool:
    """Check if the coordinates $(c_1, c_2, c_3)$ are inside the Weyl chamber

    Examples:

        >>> BGATE = qutip.gates.berkeley()
        >>> point_in_weyl_chamber(*c1c2c3(BGATE))
        True
        >>> point_in_weyl_chamber(*c1c2c3(qutip.gates.identity([2, 2])))
        True

        The coordinates may also be array-like, in which case a boolean numpy
        array is returned.

        >>> res = point_in_weyl_chamber(
        ...     [0.0,0.5,0.8], [1.0,0.25,0.0], [1.0,0.25,0.0])
        >>> assert np.all(res == np.array([False,  True,  True]))

        If `raise_exception` is True, raise an :exc:`ValueError` if any values
        are outside the Weyl chamber.

        >>> try:
        ...     point_in_weyl_chamber(1.0, 0.5, 0, raise_exception=True)
        ... except ValueError as e:
        ...     print(e)
        (1, 0.5, 0) is not in the Weyl chamber
    """
    result = Or(
        And(And(
          less(c1, 0.5), less_eq(c2, c1)), less_eq(c3, c2)),
        And(And(
          greater_eq(c1, 0.5), less_eq(c2, 1.0-np.array(c1))), less_eq(c3, c2))
    )
    if raise_exception:
        if not np.all(result):
            if np.isscalar(c1):  # assume c2, c3 are scalar, too
                raise ValueError(
                    "(%g, %g, %g) is not in the Weyl chamber" % (c1, c2, c3))
            else:
                raise ValueError(
                    "Not all values (c1, c2, c3) are in the Weyl chamber")
    return result


def point_in_region(
        region: str, c1: float, c2: float, c3: float,
        check_weyl=False) -> bool:
    """Check if $(c_1, c_2, c_3)$ are in the given region of the Weyl chamber

    The regions are 'W0' (between origin O and perfect entanglers polyhedron),
    'W0*' (between point A1 and perfect entangler polyhedron), 'W1' (between A3
    point and perfect entanglers polyhedron), and 'PE' (inside perfect
    entanglers polyhedron)

    If the `check_weyl` parameter is given a True, raise a ValueError for any
    points outside of the Weyl chamber

    Examples:
        >>> from weylchamber.visualize import WeylChamber
        >>> point_in_region('W0', *WeylChamber.O)
        True
        >>> point_in_region('W0', 0.2, 0.05, 0.0)
        True
        >>> point_in_region('W0', *WeylChamber.L)
        False
        >>> point_in_region('W0', *WeylChamber.Q)
        False
        >>> point_in_region('PE', *WeylChamber.Q)
        True
        >>> point_in_region('W0*', *WeylChamber.A1)
        True
        >>> point_in_region('W0*', 0.8, 0.1, 0.1)
        True
        >>> point_in_region('W1', *WeylChamber.A3)
        True
        >>> point_in_region('W1', 0.5, 0.4, 0.25)
        True
        >>> point_in_region('W1', 0.5, 0.25, 0)
        False
        >>> point_in_region('PE', 0.5, 0.25, 0)
        True

        The function may be also applied against arrays::

        >>> res = point_in_region('W1', [0.5,0.5], [0.4,0.25], [0.25,0.0])
        >>> assert np.all(res == np.array([ True, False]))
    """
    regions = ['W0', 'W0*', 'W1', 'PE']
    if region == 'PE':
        return _point_in_PE(c1, c2, c3, check_weyl=check_weyl)
    else:
        in_weyl = point_in_weyl_chamber(c1, c2, c3, raise_exception=check_weyl)
        c1 = np.array(c1)
        c2 = np.array(c2)
        c3 = np.array(c3)
        if region == 'W0':
            return And(in_weyl, less(c1+c2, 0.5))
        elif region == 'W0*':
            return And(in_weyl, greater(c1-c2, 0.5))
        elif region == 'W1':
            return And(in_weyl, greater(c2+c3, 0.5))
        else:
            raise ValueError("region %s is not in %s" % (region, regions))


def _point_in_PE(c1, c2, c3, check_weyl=False):
    """Return True if the coordinates c1, c2, c3 are inside the
    perfect-entangler polyhedron

    >>> BGATE = qutip.gates.berkeley()
    >>> _point_in_PE(*c1c2c3(BGATE))
    True
    >>> _point_in_PE(*c1c2c3(qutip.gates.identity(4)))
    False

    >>> res = _point_in_PE([0.0, 0.5, 0.8], [1.0, 0.25, 0.0], [1.0, 0.25, 0.0])
    >>> assert np.all(res == np.array([False,  True, False]))
    """
    in_weyl = point_in_weyl_chamber(c1, c2, c3, raise_exception=check_weyl)
    c1 = np.array(c1); c2 = np.array(c2); c3 = np.array(c3)
    return And(in_weyl,
        And(And(
            greater_eq(c1+c2, 0.5), less_eq(c1-c2, 0.5)), less_eq(c2+c3, 0.5)
        )
    )


def weyl_region(c1: float, c2: float, c3: float, check_weyl=True) -> str:
    """Return the region of the Weyl chamber the given point is in.

    Returns:
        One of 'W0', 'W0*', 'W1', 'PE'

    Examples:

        >>> from weylchamber.visualize import WeylChamber
        >>> print(weyl_region(*WeylChamber.O))
        W0
        >>> print(weyl_region(*WeylChamber.A1))
        W0*
        >>> print(weyl_region(*WeylChamber.A3))
        W1
        >>> print(weyl_region(*WeylChamber.L))
        PE
        >>> print(weyl_region(0.2, 0.05, 0.0))
        W0
        >>> print(weyl_region(0.8, 0.1, 0.1))
        W0*
        >>> print(weyl_region(0.5, 0.25, 0))
        PE
        >>> print(weyl_region(0.5, 0.4, 0.25))
        W1
        >>> try:
        ...     weyl_region(1.0, 0.5, 0)
        ... except ValueError as e:
        ...     print(e)
        (1, 0.5, 0) is not in the Weyl chamber
        >>> print(weyl_region(1.0, 0.1, 0, check_weyl=False))
        W0*

    Only scalar values are accepted for c1, c2, c3
    """
    point_in_weyl_chamber(c1, c2, c3, raise_exception=check_weyl)
    if c1+c2 < 0.5:
        return 'W0'
    elif c1-c2 > 0.5:
        return 'W0*'
    elif c2+c3 > 0.5:
        return 'W1'
    else:
        return 'PE'


def to_magic(A: Gate) -> qutip.Qobj:
    """Convert `A` from the canonical basis to the the "magic" Bell basis"""
    if A.shape != (4, 4):
        raise ValueError("Gates must have a 4×4 shape")
    return Qmagic.dag() * qutip.Qobj(A, dims=[[2, 2], [2, 2]]) * Qmagic


def from_magic(A: Gate) -> qutip.Qobj:
    """ The inverse of :func:`.to_magic`"""
    if A.shape != (4, 4):
        raise ValueError("Gates must have a 4×4 shape")
    return Qmagic * qutip.Qobj(A, dims=[[2, 2], [2, 2]]) * Qmagic.dag()


def random_weyl_point(region=None) -> CTuple:
    """Return a random point $(c_1, c_2, c_3)$ in the Weyl chamber (units of π)

    If region is given in ['W0', 'W0*', 'W1', 'PE'], the point will be in the
    specified region of the Weyl chamber

    Example:
        >>> c1, c2, c3 = random_weyl_point()
        >>> point_in_weyl_chamber(c1, c2, c3)
        True
        >>> c1, c2, c3 = random_weyl_point(region='PE')
        >>> point_in_region('PE', c1, c2, c3)
        True
        >>> c1, c2, c3 = random_weyl_point(region='W0')
        >>> point_in_region('W0', c1, c2, c3)
        True
        >>> c1, c2, c3 = random_weyl_point(region='W0*')
        >>> point_in_region('W0*', c1, c2, c3)
        True
        >>> c1, c2, c3 = random_weyl_point(region='W1')
        >>> point_in_region('W1', c1, c2, c3)
        True
    """
    while True:
        c1 = np.random.rand()
        c2 = 0.5*np.random.rand()
        c3 = 0.5*np.random.rand()
        if point_in_weyl_chamber(c1, c2, c3):
            if region is None:
                return c1, c2, c3
            else:
                if point_in_region(region, c1, c2, c3):
                    return c1, c2, c3


def _U2(phi, theta, phi1, phi2):
    r"""Return a unitary gate as numpy array using the parametrization

    .. math::

        U = e^{i \phi} \begin{bmatrix}
             \cos\theta e^{ i\phi_1}  & \sin\theta e^{ i\phi_2}\\
            -\sin\theta e^{-i\phi_2}  & \cos\theta e^{-i\phi_1}\\
            \end{bmatrix}
    """
    from numpy import exp, sin, cos
    return exp(1j*phi) * np.array([
        [  cos(theta) * exp( 1j*phi1), sin(theta) * exp( 1j*phi2) ],
        [ -sin(theta) * exp(-1j*phi2), cos(theta) * exp(-1j*phi1) ]])


def _SQ_unitary(
        phi_left, theta_left, phi1_left, phi2_left, phi_right, theta_right,
        phi1_right, phi2_right):
    """Return a non-entangling two-qubit gate (a two-qubit gate locally
    equivalent to the identity)"""
    Id = np.identity(2)
    return qutip.Qobj(
        np.kron(_U2(phi_left, theta_left, phi1_left, phi2_left), Id).dot(
            np.kron(Id, _U2(phi_right, theta_right, phi1_right, phi2_right))),
        dims=[[2, 2], [2, 2]])


def canonical_gate(c1: float, c2: float, c3: float) -> qutip.Qobj:
    r"""Return the canonical gate for the given $(c_1, c_2, c_3)$

    The canonical gate is defined as

    .. math::

        \Op{A} = e^{i \frac{\pi}{2} \left(
            c_1 \Op{\sigma}_x \Op{\sigma}_x +
            c_2 \Op{\sigma}_y \Op{\sigma}_y +
            c_3 \Op{\sigma}_z \Op{\sigma}_z \right)}

    Example:
        >>> gate = qutip.Qobj(
        ...     [[0.707107+0.000000j, 0.000000+0.000000j, 0.000000+0.000000j, 0.000000+0.707107j],
        ...      [0.000000+0.000000j, 0.707107+0.000000j, 0.000000+0.707107j, 0.000000+0.000000j],
        ...      [0.000000+0.000000j, 0.000000+0.707107j, 0.707107+0.000000j, 0.000000+0.000000j],
        ...      [0.000000+0.707107j, 0.000000+0.000000j, 0.000000+0.000000j, 0.707107+0.000000j]],
        ... dims=[[2,2], [2,2]])
        >>> U = canonical_gate(0.5,0,0)
        >>> assert (U - gate).norm() < 1e-6
        >>> assert np.max(np.abs(
        ...     np.array(c1c2c3(U)) - np.array([0.5, 0, 0]))) < 1e-15
        """
    return (np.pi*0.5j * (c1 * SxSx + c2 * SySy + c3 * SzSz)).expm()


def random_gate(region=None) -> qutip.Qobj:
    """Return a random two-qubit gate

    If region is not None, the gate will be in the specified region of the Weyl
    chamber.  The following region names are allowed:

    * 'SQ': single qubit gates, consisting of the Weyl chamber points O, A2
    * 'PE': polyhedron of perfect entanglers
    * 'W0': region between point O and the PE polyhedron
    * 'W0*': region between point A2 and the PE polyhedron
    * 'W1': region between point A3 ([SWAP]) and the PE polyhedron
    """
    if region == 'SQ':
        p = 2.0 * np.pi * np.random.random(8)
        return _SQ_unitary(*p)
    else:
        A = canonical_gate(*random_weyl_point(region=region))  # Qobj
        p = 2.0 * np.pi * np.random.random(16)
        return _SQ_unitary(*p[:8]) * A * _SQ_unitary(*p[8:])
