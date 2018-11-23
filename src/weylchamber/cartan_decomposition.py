import numpy as np
import qutip
from qutip import Qobj

from .coordinates import to_magic, from_magic, c1c2c3, canonical_gate
from ._types import Gate, Tuple

__all__ = ['cartan_decomposition']


def cartan_decomposition(U: Gate) -> Tuple[Qobj, Qobj, Qobj]:
    r"""Calculate the Cartan Decomposition of the given U in U(4)

    .. math::

        \Op{U} = \Op{k}_1  \Op{A}  \Op{k}_2

    up to a global phase factor $(\det \Op{U})^{\frac{1}{4}}$.

    Args:
        U: Two-qubit quantum gate. Must be unitary.

    Returns:
        tuple $(\Op{k}_1, \Op{A}, \Op{k}_2)$ where
        $\Op{k}_1$ is the left local operations in SU(2) x SU(2),
        $\Op{A}$ is non-local operations, in SU(4), and $\Op{k}_2$
        is the right local operations in SU(2) x SU(2).

    Notes:

        If you are working with a logical subspace, you should unitarize U
        before calculating the Cartan decomposition

    References:

        * D. Reich. Optimising the nonlocal content of a two-qubit gate.
          Diploma Thesis. FU Berlin, 2010. Appendix E

        * Zhang et al. PRA 67, 042313 (2003)
    """
    if isinstance(U, qutip.Qobj):
        U = U.full()
    U = np.array(U)                      # in U(4)
    Utilde = U / np.linalg.det(U)**0.25  # U in SU(4)

    found_branch = False
    # The fourth root has four branches; the correct solution could be in
    # any one of them
    for branch in range(4):

        UB = to_magic(Utilde).full()  # in Bell basis
        m = UB.T @ UB

        # The F-matrix can be calculated according to Eq (21) in PRA 67, 042313
        # It is a diagonal matrix containing the squares of the eigenvalues of
        # m
        c1, c2, c3 = c1c2c3(Utilde)
        F1 = np.exp(np.pi * 0.5j * (+c1 - c2 + c3))
        F2 = np.exp(np.pi * 0.5j * (+c1 + c2 - c3))
        F3 = np.exp(np.pi * 0.5j * (-c1 - c2 - c3))
        F4 = np.exp(np.pi * 0.5j * (-c1 + c2 + c3))
        Fd = np.array([F1, F2, F3, F4])
        F = np.array(np.diag(Fd))

        # Furthermore, we have Eq (22), giving the eigen-decomposition of the
        # matrix m. This gives us the matrix O_2.T of the eigenvectors of m
        Fsq, O_2_transposed = np.linalg.eig(m)

        ord1 = np.argsort(np.angle(Fd**2))  # sort according to complex phase
        ord2 = np.argsort(np.angle(Fsq))    # ... (absolute value is 1)
        diff = np.sum(np.abs((Fd**2)[ord1] - Fsq[ord2]))
        # Do Fd**2 and Fsq contain the same values (irrespective of order)?
        if diff < 1.0e-12:
            found_branch = True
            break
        else:
            Utilde *= 1.0j

    # double check that we managed to find a branch (just to be 100% safe)
    assert(found_branch), \
        "Couldn't find correct branch of fourth root in mapping U(4) -> SU(4)"

    # Getting the entries of F from Eq (21) instead of by taking the square
    # root of Fsq has the benefit that we don't have to worry about whether we
    # need to take the positive or negative root.
    # However, we do need to make sure that the eigenstates are ordered to
    # correspond to F1, F2, F3, F4
    # After reordering, we need to transpose to get O_2 itself
    reordered = np.array(np.zeros((4, 4)), dtype=np.complex128)
    order = []
    for i in range(4):
        for j in range(4):
            if (abs(Fd[i]**2 - Fsq[j]) < 1.0e-12):
                if j not in order:
                    order.append(j)
    assert len(order) == 4, "Couldn't order O_2"  # should not happen
    # Reorder using the order we just figured out, and transpose
    for i in range(4):
        reordered[:, i] = O_2_transposed[:, order[i]]
    O_2 = reordered.transpose()

    # Now that we have O_2 and F, completing the Cartan decomposition is
    # straightforward, following along Appendix E of Daniel's thesis
    k2 = from_magic(O_2)
    O_1 = UB @ O_2.transpose() @ F.conjugate().transpose()
    k1 = from_magic(O_1)
    A = canonical_gate(c1, c2, c3)

    # Check our results
    assert(np.max(np.abs(O_1 @ O_1.transpose() - np.identity(4))) < 1.0e-12), \
        "O_1 not orthogonal"
    assert(np.max(np.abs(O_2 @ O_2.transpose() - np.identity(4))) < 1.0e-12), \
        "O_2 not orthogonal"
    err = (k1 * A * k2 - qutip.Qobj(Utilde, dims=[[2, 2], [2, 2]])).norm()
    assert(err < 1e-12), "Cartan Decomposition Failed"
    return k1, A, k2
