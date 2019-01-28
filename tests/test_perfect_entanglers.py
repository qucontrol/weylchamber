import warnings

import os
import qutip
import numpy as np
from weylchamber import perfect_entanglers


def test_pe_chi_construction_uni(request):
    """Test the co-state construction for the perfect-entanglers functional
    in case of unitary dymanics in the 4x4 subspace"""
    testdir = os.path.splitext(request.module.__file__)[0]
    fw = [0 for i in range(4)]
    chi_exp = [0 for i in range(4)]
    for i in range(4):
        file = os.path.join(testdir, 'fw_{}_uni.dat'.format(i + 1))
        fw[i] = qutip.Qobj(
            np.loadtxt(file, usecols=[0], unpack=True)
            + 1j * np.loadtxt(file, usecols=[1], unpack=True)
        )
        file = os.path.join(testdir, 'chis_{}_uni.dat'.format(i + 1))
        chi_exp[i] = qutip.Qobj(
            np.loadtxt(file, usecols=[0], unpack=True)
            + 1j * np.loadtxt(file, usecols=[1], unpack=True)
        )
        chi_exp[i] = qutip.Qobj(chi_exp[i])
    psi_00 = qutip.Qobj(np.array([1, 0, 0, 0]))
    psi_01 = qutip.Qobj(np.array([0, 1, 0, 0]))
    psi_10 = qutip.Qobj(np.array([0, 0, 1, 0]))
    psi_11 = qutip.Qobj(np.array([0, 0, 0, 1]))
    chi_constructor = perfect_entanglers.make_PE_krotov_chi_constructor(
        [psi_00, psi_01, psi_10, psi_11]
    )
    chi_out = chi_constructor(fw)
    for i in range(4):
        assert abs((chi_out[i] - chi_exp[i]).norm()) < 1e-12


def test_pe_chi_construction_nonuni(request):
    """Test the co-state construction for the perfect-entanglers functional
    in case of non-unitary dymanics in the 4x4 subspace"""
    testdir = os.path.splitext(request.module.__file__)[0]
    fw = [0 for i in range(4)]
    chi_exp = [0 for i in range(4)]
    for i in range(4):
        file = os.path.join(testdir, 'fw_{}_nonuni.dat'.format(i + 1))
        fw[i] = qutip.Qobj(
            np.loadtxt(file, usecols=[0], unpack=True)
            + 1j * np.loadtxt(file, usecols=[1], unpack=True)
        )
        file = os.path.join(testdir, 'chis_{}_nonuni.dat'.format(i + 1))
        chi_exp[i] = qutip.Qobj(
            np.loadtxt(file, usecols=[0], unpack=True)
            + 1j * np.loadtxt(file, usecols=[1], unpack=True)
        )
        chi_exp[i] = qutip.Qobj(chi_exp[i])
    psi_00 = qutip.Qobj(np.array([1, 0, 0, 0, 0]))
    psi_01 = qutip.Qobj(np.array([0, 1, 0, 0, 0]))
    psi_10 = qutip.Qobj(np.array([0, 0, 1, 0, 0]))
    psi_11 = qutip.Qobj(np.array([0, 0, 0, 1, 0]))
    chi_constructor = perfect_entanglers.make_PE_krotov_chi_constructor(
        [psi_00, psi_01, psi_10, psi_11], unitarity_weight=0.1
    )
    chi_out = chi_constructor(fw)
    for i in range(4):
        assert abs((chi_out[i] - chi_exp[i]).norm()) < 1e-12
