import numpy as np
from numpy import pi, sin

from .coordinates import _point_in_PE, weyl_region
from ._types import CTuple


__all__ = ['project_to_PE', 'F_PE', 'concurrence']


#: Dictionary of Weyl chamber region name to normal vectors for the
#: surface that separates the region from the polyhedron of perfect
#: entanglers (pointing outwards from the PE's). The three regions are:
#:
#: * 'W0': region from the origin point (O) to the PE polyhedron
#: * 'W0*': region from the A2 point to the PE polyhedron
#: * 'W1': region from the A2 point (SWAP gate) to the PE polyhedron
_normal = {
    'W0': (np.sqrt(2.0)/2.0)*np.array((-1, -1, 0)),
    'W0*': (np.sqrt(2.0)/2.0)*np.array((1, -1, 0)),
    'W1': (np.sqrt(2.0)/2.0)*np.array((0,  1, 1))}


#: Dictionary of anchor points for the normal vectors (i.e., an arbitrary
#: point on the surface that separates the region specified by the key
#: from the perfect entanglers polyhedron
_anchor = {
    'W0': np.array((0.5, 0, 0)),
    'W0*': np.array((0.5, 0, 0)),
    'W1': np.array((0.5, 0.5, 0))}


def project_to_PE(c1: float, c2: float, c3: float, check_weyl=True) -> CTuple:
    """Project onto the boundary surface of the perfect entanglers

    Return new tuple (c1', c2', c3') obtained by projecting the given input
    point (c1, c2, c3) onto the closest boundary of the perfect entanglers
    polyhedron. If the input point already is a perfect entangler, it will be
    returned unchanged

    Example:
        >>> from weylchamber.visualize import WeylChamber
        >>> print("%.2f, %.2f, %.2f" % tuple(project_to_PE(*WeylChamber.A3)))
        0.50, 0.25, 0.25
        >>> print("%.3f, %.3f, %.3f" % tuple(project_to_PE(0.5, 0.5, 0.25)))
        0.500, 0.375, 0.125
        >>> print("%.3f, %.3f, %.3f" % tuple(project_to_PE(0.25, 0, 0)))
        0.375, 0.125, 0.000
        >>> print("%.3f, %.3f, %.3f" % tuple(project_to_PE(0.75, 0, 0)))
        0.625, 0.125, 0.000
        >>> print("%.3f, %.3f, %.3f" % tuple(project_to_PE(0.3125, 0.0625, 0.01)))
        0.375, 0.125, 0.010
        >>> print("%.1f, %.1f, %.1f" % tuple(project_to_PE(0.5, 0, 0)))
        0.5, 0.0, 0.0
        >>> print("%.1f, %.1f, %.1f" % tuple(project_to_PE(0.5, 0.2, 0.2)))
        0.5, 0.2, 0.2
        >>> try:
        ...     project_to_PE(1.0, 0.5, 0)
        ... except ValueError as e:
        ...     print(e)
        (1, 0.5, 0) is not in the Weyl chamber
    """
    if _point_in_PE(c1, c2, c3):
        return c1, c2, c3
    else:
        region = weyl_region(c1, c2, c3, check_weyl=check_weyl)
        p = np.array((c1, c2, c3))
        n = _normal[region]
        a = _anchor[region]
        return p - np.inner((p-a), n) * n


def concurrence(c1: float, c2: float, c3: float) -> float:
    """Calculate the concurrence directly from the Weyl Chamber coordinates

    Example:
        >>> import qutip
        >>> from weylchamber.coordinates import c1c2c3
        >>> '%.1f' % concurrence(*c1c2c3(qutip.gates.swap()))
        '0.0'
        >>> '%.1f' % concurrence(*c1c2c3(qutip.gates.cnot()))
        '1.0'
        >>> '%.1f' % concurrence(*c1c2c3(qutip.gates.identity([2, 2])))
        '0.0'
    """
    if ((c1 + c2) >= 0.5) and (c1-c2 <= 0.5) and ((c2+c3) <= 0.5):
        # if we're inside the perfect-entangler polyhedron in the Weyl chamber
        # the concurrence is 1 by definition. the "regular" formula gives wrong
        # results in this case.
        return 1
    else:
        c1_c2_c3 = np.array([c1, c2, c3])
        c3_c1_c2 = np.roll(c1_c2_c3, 1)
        m = np.concatenate((c1_c2_c3 - c3_c1_c2, c1_c2_c3 + c3_c1_c2))
        res = np.max(abs(sin(pi * m)))
        if abs(res) < 1e-15:
            return 0
        elif abs(res - 1) < 1e-15:
            return 1
        return res


def F_PE(g1: float, g2: float, g3: float) -> float:
    """Evaluate the Perfect-Entangler Functional

    Example:
        >>> import qutip
        >>> from weylchamber.local_invariants import g1g2g3
        >>> "%.1f" % F_PE(*g1g2g3(qutip.gates.cnot()))
        '0.0'
        >>> "%.1f" % F_PE(*g1g2g3(qutip.gates.identity([2, 2])))
        '2.0'
    """
    return g3 * np.sqrt(g1**2 + g2**2) - g1 + 0.0
