import qutip
import numpy as np
from numpy import pi, sin

from .coordinates import _point_in_PE, weyl_region, c1c2c3, from_magic
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
        >>> '%.1f' % concurrence(*c1c2c3(qutip.qip.operations.swap()))
        '0.0'
        >>> '%.1f' % concurrence(*c1c2c3(qutip.qip.operations.cnot()))
        '1.0'
        >>> '%.1f' % concurrence(*c1c2c3(qutip.identity([2, 2])))
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
        >>> "%.1f" % F_PE(*g1g2g3(qutip.qip.operations.cnot()))
        '0.0'
        >>> "%.1f" % F_PE(*g1g2g3(qutip.identity([2, 2])))
        '2.0'
    """
    return g3 * np.sqrt(g1 ** 2 + g2 ** 2) - g1 + 0.0


def make_PE_krotov_chi_constructor(canonical_basis, unitarity_weight=0):
    r"""Return a constructor for the χ's in a PE optimization.

    Return a `chi_constructor` that determines the boundary condition of the
    backwards propagation in an optimization towards a perfect entangler in
    Krotov's method, based on the foward-propagtion of the Bell states. In
    detail, the function returns a callable function that calculates

    .. math::

        \ket{\chi_{i}}
        =
        \frac{\partial F_{PE}}{\partial \bra{\phi_i}}
        \Bigg|_{\ket{\phi_{i}(T)}}

    for all $i$ with $\ket{\phi_{0}(T)}, ..., \ket{\phi_{3}(T)}$ the forward
    propagated Bell states at final time $T$, cf. Eq. (33b) in Ref. [1].
    $F_{PE}$ is the perfect-entangler functional
    :func:`~weylchamber.perfect_entanglers.F_PE`. For the details of the
    derivative see Appendix G in Ref. [2].

    References:

    [1] `M. H. Goerz, et al., Phys. Rev. A 91, 062307 (2015)
    <https://doi.org/10.1103/PhysRevA.91.062307>`_

    [2] `M. H. Goerz, Optimizing Robust Quantum Gates in Open Quantum Systems.
    PhD thesis, University of Kassel, 2015
    <https://michaelgoerz.net/research/diss_goerz.pdf>`_

    Args:
        canonical_basis (list[qutip.Qobj]): A list of four basis states that
            define the canonical basis $\ket{00}$, $\ket{01}$, $\ket{10}$, and
            $\ket{11}$ of the logical subspace.
        unitarity_weight (float): A weight in [0, 1] that determines how much
            emphasis is placed on  maintaining population in the logical
            subspace.

    Returns:
        callable: a function ``chi_constructor(fw_states_T, **kwargs)`` that
        receives the result of a foward propagation of the Bell states
        (obtained from `canonical_basis` via
        :func:`weylchamber.gates.bell_basis`), and returns a list of statex
        $\ket{\chi_{i}}$ that are the boundary condition for the backward
        propagation in Krotov's method. Positional arguments beyond
        `fw_states_T` are ignored.
    """

    bell_basis = get_bell_basis(canonical_basis)

    w = unitarity_weight
    if w < 0:
        w = 0
    if w > 1:
        w = 1

    def chi_constructor(fw_states_T, **kwargs):
        # *args is ignored, it exists so that the chi_constructor fits the
        # krotov API directly
        UB = construct_gate(bell_basis, fw_states_T)
        A = (Qmagic * _get_a_kl_PE(UB)) / 2

        chis = apply_gate(A, canonical_basis)

        # unitarity corrections
        n = len(fw_states_T)
        chis_out = []
        for i in range(n):
            bell_proj = qutip.Qobj(np.zeros(shape=fw_states_T[i].shape))
            for j in range(n):
                bell_proj += bell_basis[j].overlap(fw_states_T[i])            \
                             * bell_basis[j]
            chis_out.append((1.0-w) * chis[i] + 0.25*w * bell_proj)
        return chis_out

    return chi_constructor


def _get_a_kl_PE(UB):
    """Return the 4×4 `A_kl` coefficient matrix (:class:`qutip.Qobj`)
    for the perfect-entanglers functional, for a given gate `UB` in the Bell
    basis.
    """

    # Compute auxiliary scalar quantities
    detU = _cmat4_det(UB)
    rcdetU1 = 1.0 / detU
    mU = UB.trans() * UB
    tr_mU = mU.tr()
    tr_mU_sq = (mU*mU).tr()
    g3 = 0.25 * (tr_mU**2 - tr_mU_sq)
    Re2Tr = np.real(tr_mU)**2 / 16.0 # This contains already the 1/16 factor
    Im2Tr = np.imag(tr_mU)**2 / 16.0 # This contains already the 1/16 factor
    Tr2 = tr_mU**2 / 16.0            # This contains already the 1/16 factor

    # `alpha` and `beta` are the real and imaginary part of `UB`, respectively
    alpha = np.zeros(shape=(4,4))
    beta  = np.zeros(shape=(4,4))
    for i in range(4):
        for j in range(4):
            alpha[i,j] = np.real(UB[i,j])
            beta[i,j]  = np.imag(UB[i,j])
    alpha = qutip.Qobj(alpha)
    beta  = qutip.Qobj(beta)

    # The c1c2c3 function expects `UB` to be given in the canonical basis, thus
    # we have to convert it from the Bell basis on input
    c1, c2, c3 = c1c2c3(from_magic(UB))

    drcdetU1dAlpha = np.zeros(shape=(4,4), dtype=complex)
    drcdetU1dBeta  = np.zeros(shape=(4,4), dtype=complex)
    dg3dAlpha      = np.zeros(shape=(4,4), dtype=complex)
    dg3dBeta       = np.zeros(shape=(4,4), dtype=complex)
    dRe2TrdAlpha   = np.zeros(shape=(4,4))
    dRe2TrdBeta    = np.zeros(shape=(4,4))
    dIm2TrdAlpha   = np.zeros(shape=(4,4))
    dIm2TrdBeta    = np.zeros(shape=(4,4))
    dTr2dAlpha     = np.zeros(shape=(4,4), dtype=complex)
    dTr2dBeta      = np.zeros(shape=(4,4), dtype=complex)

    # Compute auxiliary matrix quantities
    for a in range(4):
        for b in range(4):

            drcdetU1dAlpha[a,b] = - _dDetUdAlpha(UB,a,b) / detU**2
            drcdetU1dBeta[a,b]  = - _dDetUdBeta(UB,a,b)  / detU**2

            for k in range(4):
                for i in range(4):
                    dg3dAlpha[a,b] = dg3dAlpha[a,b]                           \
                                 +       alpha[a,b] * alpha[k,i] * alpha[k,i] \
                                 -       alpha[a,b] * beta[k,i]  * beta[k,i]  \
                                 - 2.0 * beta[a,b]  * alpha[k,i] * beta[k,i]  \
                                 -       alpha[k,i] * alpha[a,i] * alpha[k,b] \
                                 +       alpha[k,b] * beta[a,i]  * beta[k,i]  \
                                 + 2.0 * beta[k,b]  * alpha[a,i] * beta[k,i]
                    dg3dBeta[a,b]  = dg3dBeta[a,b]                            \
                                 +       beta[a,b]  * beta[k,i]  * beta[k,i]  \
                                 -       beta[a,b]  * alpha[k,i] * alpha[k,i] \
                                 - 2.0 * alpha[a,b] * alpha[k,i] * beta[k,i]  \
                                 -       beta[k,i]  * beta[a,i]  * beta[k,b]  \
                                 +       beta[k,b]  * alpha[a,i] * alpha[k,i] \
                                 + 2.0 * alpha[k,b] * beta[a,i]  * alpha[k,i]
                    dg3dAlpha[a,b] = dg3dAlpha[a,b] + 1j * (                  \
                                 +       beta[a,b]  * alpha[k,i] * alpha[k,i] \
                                 -       beta[a,b]  * beta[k,i]  * beta[k,i]  \
                                 + 2.0 * alpha[a,b] * alpha[k,i] * beta[k,i]  \
                                 -       alpha[a,i] * alpha[k,i] * beta[k,b]  \
                                 -       alpha[k,b] * alpha[k,i] * beta[a,i]  \
                                 -       alpha[k,b] * alpha[a,i] * beta[k,i]  \
                                 +       beta[a,i]  * beta[k,i]  * beta[k,b]  \
                                 )
                    dg3dBeta[a,b]  = dg3dBeta[a,b] + 1j * (                   \
                                 -       alpha[a,b] * beta[k,i]  * beta[k,i]  \
                                 +       alpha[a,b] * alpha[k,i] * alpha[k,i] \
                                 - 2.0 * beta[a,b]  * beta[k,i]  * alpha[k,i] \
                                 +       beta[a,i]  * beta[k,i]  * alpha[k,b] \
                                 +       beta[k,b]  * beta[k,i]  * alpha[a,i] \
                                 +       beta[k,b]  * beta[a,i]  * alpha[k,i] \
                                 -       alpha[a,i] * alpha[k,i] * alpha[k,b] \
                                 )

            for k in range(4):
                for i in range(4):
                    dTr2dAlpha[a,b] = dTr2dAlpha[a,b]                         \
                                + 0.25 * alpha[a,b] * alpha[k,i] * alpha[k,i] \
                                - 0.25 * alpha[a,b] * beta[k,i]  * beta[k,i]  \
                                - 0.50 * beta[a,b]  * alpha[k,i] * beta[k,i]
                    dTr2dBeta[a,b]  = dTr2dBeta[a,b]                          \
                                + 0.25 * beta[a,b]  * beta[k,i]  * beta[k,i]  \
                                - 0.25 * beta[a,b]  * alpha[k,i] * alpha[k,i] \
                                - 0.50 * alpha[a,b] * beta[k,i]  * alpha[k,i]
                    dTr2dAlpha[a,b] = dTr2dAlpha[a,b] + 1j * (                \
                                + 0.25 * beta[a,b]  * alpha[k,i] * alpha[k,i] \
                                - 0.25 * beta[a,b]  * beta[k,i]  * beta[k,i]  \
                                + 0.50 * alpha[a,b] * alpha[k,i] * beta[k,i]  \
                                )
                    dTr2dBeta[a,b]  = dTr2dBeta[a,b] + 1j * (                 \
                                - 0.25 * alpha[a,b] * beta[k,i]  * beta[k,i]  \
                                + 0.25 * alpha[a,b] * alpha[k,i] * alpha[k,i] \
                                - 0.50 * beta[a,b]  * beta[k,i]  * alpha[k,i] \
                                )

            for k in range(4):
                for i in range(4):
                    dRe2TrdAlpha[a,b] = dRe2TrdAlpha[a,b] + np.real(          \
                                  0.25 * alpha[a,b] * alpha[k,i] * alpha[k,i] \
                                - 0.25 * alpha[a,b] * beta[k,i] * beta[k,i]   \
                                )
                    dRe2TrdBeta[a,b]  = dRe2TrdBeta[a,b] + np.real(           \
                                   0.25 * beta[a,b] * beta[k,i] * beta[k,i]   \
                                 - 0.25 * beta[a,b] * alpha[k,i] * alpha[k,i] \
                                 )
                    dIm2TrdAlpha[a,b] = dIm2TrdAlpha[a,b] + np.real(          \
                                    0.50 * alpha[k,i] * beta[a,b] * beta[k,i] \
                                    )
                    dIm2TrdBeta[a,b]  = dIm2TrdBeta[a,b] + np.real(           \
                                   0.50 * beta[k,i] * alpha[a,b] * alpha[k,i] \
                                   )

    # Construct the a_kl coefficients with the previously computed quantities
    a_kl_coeffs = np.zeros(shape=(4,4), dtype=complex)
    for l in range(4):
        for k in range(4):
            a_kl_coeffs[k,l] =                                                \
            np.real(                                                          \
              - drcdetU1dAlpha[k,l] * g3 * Re2Tr                              \
              - rcdetU1 * dg3dAlpha[k,l] * Re2Tr                              \
              - rcdetU1 * g3 * dRe2TrdAlpha[k,l]                              \
              - drcdetU1dAlpha[k,l] * g3 * Im2Tr                              \
              - rcdetU1 * dg3dAlpha[k,l] * Im2Tr                              \
              - rcdetU1 * g3 * dIm2TrdAlpha[k,l]                              \
              + drcdetU1dAlpha[k,l] * Tr2                                     \
              + rcdetU1 * dTr2dAlpha[k,l])                                    \
            + 1j *                                                            \
            np.real(                                                          \
              - drcdetU1dBeta[k,l] * g3 * Re2Tr                               \
              - rcdetU1 * dg3dBeta[k,l] * Re2Tr                               \
              - rcdetU1 * g3 * dRe2TrdBeta[k,l]                               \
              - drcdetU1dBeta[k,l] * g3 * Im2Tr                               \
              - rcdetU1 * dg3dBeta[k,l] * Im2Tr                               \
              - rcdetU1 * g3 * dIm2TrdBeta[k,l]                               \
              + drcdetU1dBeta[k,l] * Tr2                                      \
              + rcdetU1 * dTr2dBeta[k,l])

    if (c2 + c3 > 0.5):
        # UB is in the W1 region of the Weyl chamber (between the PE polyhedron
        # and the SWAP gate at the A3 point). In this region, the PE-functional
        # has the wrong sign (cf. Fig 6.1 in Goerz, PhD Thesis, Kassel).
        a_kl_coeffs = -a_kl_coeffs
        # Without this corrections, gates would be pushed towards [SWAP]

    return a_kl_coeffs


def _cmat4_det(m):
    """Calculates the complex determinant of a 4x4 matrix.

    Args:
        m (qutip.Qobj): A 4x4 quantum gate for a two-qubit system

    Returns:
        float: The determinant $\det(m)$
    """
    d =   m[0,3]*m[1,2]*m[2,1]*m[3,0] - m[0,2]*m[1,3]*m[2,1]*m[3,0]           \
        - m[0,3]*m[1,1]*m[2,2]*m[3,0] + m[0,1]*m[1,3]*m[2,2]*m[3,0]           \
        + m[0,2]*m[1,1]*m[2,3]*m[3,0] - m[0,1]*m[1,2]*m[2,3]*m[3,0]           \
        - m[0,3]*m[1,2]*m[2,0]*m[3,1] + m[0,2]*m[1,3]*m[2,0]*m[3,1]           \
        + m[0,3]*m[1,0]*m[2,2]*m[3,1] - m[0,0]*m[1,3]*m[2,2]*m[3,1]           \
        - m[0,2]*m[1,0]*m[2,3]*m[3,1] + m[0,0]*m[1,2]*m[2,3]*m[3,1]           \
        + m[0,3]*m[1,1]*m[2,0]*m[3,2] - m[0,1]*m[1,3]*m[2,0]*m[3,2]           \
        - m[0,3]*m[1,0]*m[2,1]*m[3,2] + m[0,0]*m[1,3]*m[2,1]*m[3,2]           \
        + m[0,1]*m[1,0]*m[2,3]*m[3,2] - m[0,0]*m[1,1]*m[2,3]*m[3,2]           \
        - m[0,2]*m[1,1]*m[2,0]*m[3,3] + m[0,1]*m[1,2]*m[2,0]*m[3,3]           \
        + m[0,2]*m[1,0]*m[2,1]*m[3,3] - m[0,0]*m[1,2]*m[2,1]*m[3,3]           \
        - m[0,1]*m[1,0]*m[2,2]*m[3,3] + m[0,0]*m[1,1]*m[2,2]*m[3,3]
    return d


def _dDetUdAlpha(U,a,b):
    """Calculates

    .. math::

        \partial \det(U) / \partial \\alpha_{a,b} = \det(U'_{a,b})

    where $U'$ is constructed from $U$ by replacing the row $a$ with the unit
    vector $b$ and $\\alpha$ is the real part of $U$.

    Args:
        U (qutip.Qobj): A 4x4 quantum gate for a two-qubit system
        a (integer): An integer specifying the derivative
        b (integer): An integer specifying the derivative

    Returns:
        float: The derivative as specified by $a$ and $b$
    """
    U_prime = np.zeros(shape=(4,4), dtype=complex)
    for i in range(4):
        for j in range(4):
            if i==a:
                U_prime[i,j] = 0
            else:
                U_prime[i,j] = U[i,j]
    U_prime[a,b] = 1
    return _cmat4_det(qutip.Qobj(U_prime))


def _dDetUdBeta(U,a,b):
    """Calculates

    .. math::

        \partial \det(U) / \partial \\beta_{a,b} = \det(U'_{a,b})

    where $U'$ is constructed from $U$ by replacing the row $a$ with the unit
    vector $b$ and $\\beta$ is the imaginary part of $U$.

    Args:
        U (qutip.Qobj): A 4x4 quantum gate for a two-qubit system
        a (integer): An integer specifying the derivative
        b (integer): An integer specifying the derivative

    Returns:
        float: The derivative as specified by $a$ and $b$
    """
    return 1j*_dDetUdAlpha(U,a,b)
