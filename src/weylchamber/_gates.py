"Quantum gates required for Weyl chamber calculations"""
import qutip
import numpy as np
from numpy import pi, sin, cos

__all__ = ['Qmagic', 'SxSx', 'SySy', 'SzSz', 'BGATE']


#: Transformation matrix to the "magic" Bell basis
Qmagic = (1.0/np.sqrt(2.0)) * qutip.Qobj(np.array(
    [[1,  0,  0,  1j],
     [0, 1j,  1,  0],
     [0, 1j, -1,  0],
     [1,  0,  0, -1j]],
    dtype=np.complex128),
    dims=[[2, 2], [2, 2]])


#: σx ⊗ σx gate
SxSx = qutip.Qobj(np.array(
    [[0,  0,  0,  1],
     [0,  0,  1,  0],
     [0,  1,  0,  0],
     [1,  0,  0,  0]],
    dtype=np.complex128),
    dims=[[2, 2], [2, 2]])


#: σy ⊗ σy gate
SySy = qutip.Qobj(np.array(
    [[+0,  0,  0, -1],
     [+0,  0,  1,  0],
     [+0,  1,  0,  0],
     [-1,  0,  0,  0]],
    dtype=np.complex128),
    dims=[[2, 2], [2, 2]])


#: σz ⊗ σz gate
SzSz = qutip.Qobj(np.array(
    [[1,  0,  0,  0],
     [0, -1,  0,  0],
     [0,  0, -1,  0],
     [0,  0,  0,  1]],
    dtype=np.complex128),
    dims=[[2, 2], [2, 2]])


#: BGATE
BGATE = qutip.Qobj(np.array(
    [[    cos(pi/8),               0,              0, 1j*sin(pi/8)],
     [            0,     cos(3*pi/8), 1j*sin(3*pi/8),            0],
     [            0,  1j*sin(3*pi/8),    cos(3*pi/8),            0],
     [ 1j*sin(pi/8),               0,              0,   cos(pi/8)]],
    dtype=np.complex128),
    dims=[[2, 2], [2, 2]])
