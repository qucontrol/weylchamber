import qutip
from weylchamber import concurrence, random_gate, weyl_region, c1c2c3

def test_random_gate():
    G = random_gate("SQ")
    assert isinstance(G, qutip.Qobj)
    assert G.dims == [[2, 2], [2, 2]]
    assert concurrence(*c1c2c3(G)) == 0
    G = random_gate("PE")
    assert isinstance(G, qutip.Qobj)
    assert G.dims == [[2, 2], [2, 2]]
    assert concurrence(*c1c2c3(G)) == 1
    assert weyl_region(*c1c2c3(random_gate("W0"))) == 'W0'
    assert weyl_region(*c1c2c3(random_gate("W0*"))) == 'W0*'
    assert weyl_region(*c1c2c3(random_gate("W1"))) == 'W1'
