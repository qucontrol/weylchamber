import numpy as np
from numpy import pi, sin

from .coordinates import _point_in_PE, weyl_region
from .gates import (
    Qmagic,
    bell_basis as get_bell_basis,
    gate as construct_gate,
    mapped_basis as apply_gate,
)
from ._types import CTuple


__all__ = [
    'project_to_PE',
    'F_PE',
    'concurrence',
    'make_PE_krotov_chi_constructor',
]


#: Dictionary of Weyl chamber region name to normal vectors for the
#: surface that separates the region from the polyhedron of perfect
#: entanglers (pointing outwards from the PE's). The three regions are:
#:
#: * 'W0': region from the origin point (O) to the PE polyhedron
#: * 'W0*': region from the A2 point to the PE polyhedron
#: * 'W1': region from the A2 point (SWAP gate) to the PE polyhedron
_normal = {
    'W0': (np.sqrt(2.0) / 2.0) * np.array((-1, -1, 0)),
    'W0*': (np.sqrt(2.0) / 2.0) * np.array((1, -1, 0)),
    'W1': (np.sqrt(2.0) / 2.0) * np.array((0, 1, 1)),
}


#: Dictionary of anchor points for the normal vectors (i.e., an arbitrary
#: point on the surface that separates the region specified by the key
#: from the perfect entanglers polyhedron
_anchor = {
    'W0': np.array((0.5, 0, 0)),
    'W0*': np.array((0.5, 0, 0)),
    'W1': np.array((0.5, 0.5, 0)),
}


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
        return p - np.inner((p - a), n) * n


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
    if ((c1 + c2) >= 0.5) and (c1 - c2 <= 0.5) and ((c2 + c3) <= 0.5):
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
    return g3 * np.sqrt(g1 ** 2 + g2 ** 2) - g1 + 0.0


def make_PE_krotov_chi_constructor(canonical_basis, unitarity_weight=0):
    r"""Return a constructor for the χ's in a PE optimization.

    Return a `chi_constructor` that determines the boundary condition of the
    backwards propagation in an optimization towards a perfect entangler in
    Krotov's method, based on the foward-propagtion of the Bell states.

    Args:
        canonical_basis (list[qutip.Qobj]): A list of four basis states that
            define the canonical basis $\ket{00}$, $\ket{01}$, $\ket{10}$, and
            $\ket{11}$ of the logical subspace.
        unitarity_weight (float): A weight in [0, 1] that determines how much
            emphasis is placed on  maintaining population in the logical
            subspace.

    Returns:
        callable: a function ``chi_constructor(fw_states_T, *args)`` that
        receive the result of a foward propagation of the Bell states (obtained
        from `canonical_basis` via :func:`weylchamber.gates.bell_basis`), and
        returns a list of statex $\ket{\chi}$ that are the boundary condition
        for the backward propagation in Krotov's method. Positional arguments
        beyond `fw_states_T` are ignored.
    """
    # TODO: the docstring should give some equations, and include a reference
    # to the derivation of the of the χ

    bell_basis = get_bell_basis(canonical_basis)
    # TODO: take into account `unitarity_weight`

    def chi_constructor(fw_states_T, *args):
        # *args is ignored, it exists so that the chi_constructor fits the
        # krotov API directly
        UB = construct_gate(bell_basis, fw_states_T)
        A = (Qmagic * _get_a_kl_PE(UB)) / 2
        return apply_gate(A, bell_basis)

    return chi_constructor


def _get_a_kl_PE(UB):
    """Return the 4×4 `A_kl` coefficient matrix (:class:`qutip.Qobj`)
    for the perfect-entanglers functional, for a given gate `UB` in the Bell
    basis.
    """
    raise NotImplementedError()
