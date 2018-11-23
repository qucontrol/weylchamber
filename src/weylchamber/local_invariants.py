import numpy as np
from numpy import sin, cos, pi
import scipy
from scipy.optimize import leastsq
import logging
import qutip

from .prec import DEFAULT_WEYL_PRECISSION
from ._types import Gate, GTuple
from .coordinates import to_magic, c1c2c3, _SQ_unitary
from .cartan_decomposition import canonical_gate

__all__ = ['g1g2g3', 'g1g2g3_from_c1c2c3', 'J_T_LI', 'closest_LI']


def g1g2g3(U: Gate, ndigits=DEFAULT_WEYL_PRECISSION) -> GTuple:
    """Calculate local invariants $(g_1, g_3, g_3)$

    Given a two-qubit gate, calculate local invariants $(g_1, g_2, g_3)$.
    U must be in the canonical basis. For numerical stability, the resulting
    values are rounded to the given precision, cf. the `ndigits` parameter of
    the built-in :func:`round` function.

    >>> print("%.2f %.2f %.2f" % g1g2g3(qutip.gates.cnot()))
    0.00 0.00 1.00
    """
    # mathematically, the determinant of U and UB is the same, but
    # we seem to get better numerical accuracy if we calculate detU with
    # the rotated U
    UB = to_magic(U).full()  # instance of np.ndarray
    detU = np.linalg.det(UB)
    m = UB.T @ UB
    g1_2 = (np.trace(m))**2 / (16.0 * detU)
    g3 = (np.trace(m)**2 - np.trace(m@m)) / (4.0 * detU)
    g1 = round(g1_2.real + 0.0, ndigits)  # adding 0.0 turns -0.0 into +0.0
    g2 = round(g1_2.imag + 0.0, ndigits)
    g3 = round(g3.real + 0.0, ndigits)
    return (g1, g2, g3)


def g1g2g3_from_c1c2c3(
        c1: float, c2: float, c3: float,
        ndigits=DEFAULT_WEYL_PRECISSION) -> GTuple:
    """Calculate local invariants from the Weyl chamber coordinates

    Calculate the local invariants $(g_1, g_2, g_3)$ from the Weyl chamber
    coordinates $(c_1, c_2, c_3)$, in units of π. The result is rounded to the
    given precision, in order to enhance numerical stability (cf. `ndigits`
    parameter of the built-in :func:`round` function)

    Example:
        >>> CNOT = qutip.gates.cnot()
        >>> print("%.2f %.2f %.2f" % g1g2g3_from_c1c2c3(*c1c2c3(CNOT)))
        0.00 0.00 1.00
    """
    c1 *= pi
    c2 *= pi
    c3 *= pi
    g1 = round(
        cos(c1)**2 * cos(c2)**2 * cos(c3)**2 -
        sin(c1)**2 * sin(c2)**2 * sin(c3)**2 + 0.0,
        ndigits)
    g2 = round(0.25 * sin(2*c1) * sin(2*c2) * sin(2*c3) + 0.0, ndigits)
    g3 = round(4*g1 - cos(2*c1) * cos(2*c2) * cos(2*c3) + 0.0, ndigits)
    return g1, g2, g3


def J_T_LI(O: Gate, U: Gate, form='g'):
    """Calculate value of the local-invariants functional

    Args:
        O: The optimal gate
        U: The achieved gate
        form (str): form of the functional to use, 'g' or 'c'
    """
    if form == 'g':
        return np.sum(np.abs(np.array(g1g2g3(O)) - np.array(g1g2g3(U)))**2)
    elif form == 'c':
        delta_c = np.array(c1c2c3(O)) - np.array(c1c2c3(U))
        return np.prod(cos(np.pi * (delta_c) / 2.0))
    else:
        raise ValueError("Illegal value for 'form'")


def closest_LI(
        U: Gate, c1: float, c2: float, c3: float, method='leastsq',
        limit=1.0e-6):
    """Find the closest gate that has the given Weyl chamber coordinates

    The `c1`, `c2`, `c3` are given in units of π
    """
    A = canonical_gate(c1, c2, c3)

    def f_U(p):
        return _SQ_unitary(*p[:8]) * A * _SQ_unitary(*p[8:])

    return _closest_gate(U, f_U, n=16, method=method, limit=limit)


def _closest_gate(U, f_U, n, x_max=2*pi, method='leastsq', limit=1.0e-6):
    """Find the closest gate to U that fulfills the parametrization implied by
    the function f_U

    Args:
        U (Gate): Target gate
        f_U (callable): function that takes an array of n values and returns an
            gate.
        n (integer): Number of parameters (size of the argument of f_U)
        x_max (float): Maximum value for each element of the array passed as an
            argument to f_U. There is no way to have different a different
            range for the different elements
        method (str): Name of mimimization method, either 'leastsq' or any of
            the gradient-free methods implemented by scipy.optimize.mimize
        limit (float): absolute error of the distance between the target gate
            and the optimized gate for convergence. The limit is automatically
            increased by an order of magnitude every 100 iterations
    """
    logger = logging.getLogger(__name__)
    logger.debug("_closests_gate with method %s", method)
    from scipy.optimize import minimize
    if method == 'leastsq':
        def f_minimize(p):
            d = _vectorize(f_U(p)-U)
            return np.concatenate([d.real, d.imag])
    else:
        def f_minimize(p):
            return _norm(U - f_U(p))
    dist_min = None
    iter = 0
    while True:
        iter += 1
        if iter > 100:
            iter = 0
            limit *= 10
            logger.debug("_closests_gate limit -> %.2e", limit)
        p0 = x_max * np.random.random(n)
        success = False
        if method == 'leastsq':
            p, info = leastsq(f_minimize, p0)
            U_min = f_U(p)
            if info in [1, 2, 3, 4]:
                success = True
        else:
            res = minimize(f_minimize, p0, method=method)
            U_min = f_U(res.x)
            success = res.success
        if success:
            dist = _norm(U_min - U)
            logger.debug("_closests_gate dist = %.5e", dist)
            if dist_min is None:
                dist_min = dist
                logger.debug("_closests_gate dist_min -> %.5e", dist_min)
            else:
                logger.debug("_closests_gate delta_dist = %.5e",
                             abs(dist-dist_min))
                if abs(dist-dist_min) < limit:
                    return U_min
                else:
                    if dist < dist_min:
                        dist_min = dist
                        logger.debug("_closests_gate dist_min -> %.5e",
                                     dist_min)


def _vectorize(a, order='F'):
    """Return vectorization of multi-dimensional numpy array or matrix `a`

    Examples:
        >>> a = np.array([1,2,3,4])
        >>> _vectorize(a)
        array([1, 2, 3, 4])

        >>> a = np.array([[1,2],[3,4]])
        >>> _vectorize(a)
        array([1, 3, 2, 4])

        >>> _vectorize(a, order='C')
        array([1, 2, 3, 4])
    """
    if isinstance(a, qutip.Qobj):
        a = a.full()
    N = a.size
    return np.squeeze(np.asarray(a).reshape((1, N), order=order))


def _norm(v):
    """Calculate the norm of a vector or matrix `v`, matching the inner product
    defined in the `inner` routine. An algorithm like
    Gram-Schmidt-Orthonormalization will only work if the choice of norm and
    inner product are compatible.

    If `v` is a vector, the norm is the 2-norm (i.e. the standard Euclidian
    vector norm).

    If `v` is a matrix, the norm is the Hilbert-Schmidt (aka Frobenius) norm.
    Note that the HS norm of a matrix is identical to the 2-norm of any
    vectorization of that matrix (e.g. writing the columns of the matrix
    underneat each other). Also, the HS norm of the m x 1 matrix is the same as
    the 2-norm of the equivalent m-dimensional vector.
    """
    if isinstance(v, qutip.Qobj):
        v = v.data
    if isinstance(v, scipy.sparse.spmatrix):
        return scipy.sparse.linalg.norm(v)
    else:
        return scipy.linalg.norm(v)
