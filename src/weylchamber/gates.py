r"""Quantum gates required for Weyl chamber calculations

**Module data:**

.. data:: Qmagic

    Transformation matrix to the "magic" Bell basis:

    .. math::

        \Op{Q} = \frac{1}{\sqrt{2}} \begin{pmatrix}
           1 & 0 &  0 &  i \\
           0 & i &  1 &  0 \\
           0 & i & -1 &  0 \\
           1 & 0 &  0 & -i
        \end{pmatrix}

    See "Theorem 1" in Y. Makhlin, Quantum Inf. Process. 1, 243 (2002)


.. data:: SxSx

    :math:`\Op{\sigma}_x \otimes \Op{\sigma}_x` gate


.. data:: SySy

    :math:`\Op{\sigma}_y \otimes \Op{\sigma}_y` gate


.. data:: SzSz

    :math:`\Op{\sigma}_z \otimes \Op{\sigma}_z` gate
"""
import qutip
import numpy as np

__all__ = [
    'Qmagic',
    'SxSx',
    'SySy',
    'SzSz',
    'bell_basis',
    'gate',
    'mapped_basis',
]


Qmagic = (1.0 / np.sqrt(2.0)) * qutip.Qobj(
    np.array(
        [[1,  0,  0,  1j],
         [0, 1j,  1,  0],
         [0, 1j, -1,  0],
         [1,  0,  0, -1j]],
        dtype=np.complex128,
    ),
    dims=[[2, 2], [2, 2]],
)


SxSx = qutip.Qobj(
    np.array(
        [[0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0]],
        dtype=np.complex128,
    ),
    dims=[[2, 2], [2, 2]],
)


SySy = qutip.Qobj(
    np.array(
        [[+0, 0, 0, -1], [+0, 0, 1, 0], [+0, 1, 0, 0], [-1, 0, 0, 0]],
        dtype=np.complex128,
    ),
    dims=[[2, 2], [2, 2]],
)


SzSz = qutip.Qobj(
    np.array(
        [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]],
        dtype=np.complex128,
    ),
    dims=[[2, 2], [2, 2]],
)


def bell_basis(canonical_basis):
    """Two-qubit Bell basis associated with the given canonical basis

    Example:

        >>> from qutip import ket
        >>> canonical_basis = [
        ...     ket(nums) for nums in [(0, 0), (0, 1), (1, 0), (1, 1)]
        ... ]
        >>> bell = bell_basis(canonical_basis)
        >>> _bell = [
        ...     (     ket((0, 0)) +      ket((1, 1))) / np.sqrt(2),
        ...     (1j * ket((0, 1)) + 1j * ket((1, 0))) / np.sqrt(2),
        ...     (     ket((0, 1)) -      ket((1, 0))) / np.sqrt(2),
        ...     (1j * ket((0, 0)) - 1j * ket((1, 1))) / np.sqrt(2),
        ... ]
        >>> assert (bell[0] - _bell[0]).norm() < 1e-15
        >>> assert (bell[1] - _bell[1]).norm() < 1e-15
        >>> for (a, b) in zip(bell, _bell):
        ...     assert (a - b).norm() < 1e-15, (a - b).norm()
    """
    return mapped_basis(Qmagic, canonical_basis)


def gate(basis, states):
    """Two-qubit gate that maps `basis` to `states`

    Example:

        >>> from qutip import ket
        >>> basis = [ket(nums) for nums in [(0, 0), (0, 1), (1, 0), (1, 1)]]
        >>> states = mapped_basis(qutip.gates.cnot(), basis)
        >>> U = gate(basis, states)
        >>> assert (U - qutip.gates.cnot()).norm() < 1e-15
    """
    if not (len(basis) == len(states) == 4):
        raise ValueError(
            "Both `basis` and `states` must be a list of four states"
        )
    U = np.zeros((4, 4), dtype=np.complex128)
    for j in range(4):
        for i in range(4):
            U[i, j] = basis[i].overlap(states[j])
    return qutip.Qobj(U, dims=[[2, 2], [2, 2]])


def mapped_basis(gate, basis):
    """Result of applying `gate` to `basis`

    Example:

        >>> from qutip import ket
        >>> basis = [ket(nums) for nums in [(0, 0), (0, 1), (1, 0), (1, 1)]]
        >>> states = mapped_basis(qutip.gates.cnot(), basis)
        >>> assert (states[0] - ket((0,0))).norm() < 1e-15
        >>> assert (states[1] - ket((0,1))).norm() < 1e-15
        >>> assert (states[2] - ket((1,1))).norm() < 1e-15  # swap (1, 1) ...
        >>> assert (states[3] - ket((1,0))).norm() < 1e-15  # ... and (1, 0)
    """
    return tuple(
        [
            sum([gate[i, j] * basis[i] for i in range(gate.shape[0])])
            for j in range(gate.shape[1])
        ]
    )
