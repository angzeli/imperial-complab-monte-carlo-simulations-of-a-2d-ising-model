# This file contains test for different functionality of your IsingLattice program.
# This is not meant for data analysis, only to check if your code is performing
# tasks as expected. Test are run through the pytest framework installed by default
# with Anaconda.

from IsingLattice import IsingLattice

import numpy as np


def test_energy_all_up():
    n = 10
    il = IsingLattice(n, n)
    il.lattice = np.ones((n, n))

    assert il.energy() == -2 * n**2


def test_energy_all_down():
    n = 10
    il = IsingLattice(n, n)
    il.lattice = -np.ones((n, n))

    assert il.energy() == -2 * n**2


def test_mag_all_up():
    n = 10
    il = IsingLattice(n, n)
    il.lattice = np.ones((n, n))

    assert il.magnetisation() == n**2


def test_mag_all_down():
    n = 10
    il = IsingLattice(n, n)
    il.lattice = -np.ones((n, n))

    assert il.magnetisation() == -(n**2)


def test_delta_energy():
    n = 10
    il = IsingLattice(n, n)

    rand_i = np.random.choice(range(0, n))
    rand_j = np.random.choice(range(0, n))

    deltaE = il.delta_energy(rand_i, rand_j)

    en0 = il.energy()
    il.lattice[rand_i, rand_j] *= -1
    en1 = il.energy()

    assert en1 - en0 == deltaE


def test_delta_mag():
    n = 10
    il = IsingLattice(n, n)

    rand_i = np.random.choice(range(0, n))
    rand_j = np.random.choice(range(0, n))

    deltaM = -2 * il.lattice[rand_i, rand_j]

    mn0 = il.magnetisation()
    il.lattice[rand_i, rand_j] *= -1
    mn1 = il.magnetisation()

    assert mn1 - mn0 == deltaM


def test_random():
    """
    Creates a random lattice by flipping n*n random spins and
    tracking the changes in energy.
    """

    n = 10
    il = IsingLattice(n, n)
    il.lattice = np.ones((n, n))
    en = il.energy()

    for _ in range(n**2):
        rand_i = np.random.choice(range(0, n))
        rand_j = np.random.choice(range(0, n))

        en += delta_energy(il, rand_i, rand_j)

        il.lattice[rand_i, rand_j] *= -1

    print(en, il.energy())
    assert en == il.energy()


def test_burn_in_cycles_are_ignored():
    np.random.seed(123)
    il = IsingLattice(2, 2, burn_in_cycles=1)

    for _ in range(4):
        il.montecarlostep(1.0)

    assert il.statistics() == (0.0, 0.0, 0.0, 0.0, 0)

    il.montecarlostep(1.0)

    assert il.statistics()[-1] == 1


def test_reset_statistics_includes_current_state():
    n = 4
    il = IsingLattice(n, n)
    il.lattice = np.ones((n, n))
    il.energy()
    il.magnetisation()
    il.reset_statistics()

    aveE, aveE2, aveM, aveM2, n_steps = il.statistics()

    assert aveE == -2 * n**2
    assert aveE2 == (-2 * n**2) ** 2
    assert aveM == n**2
    assert aveM2 == n**4
    assert n_steps == 0


def delta_energy(il, i, j):
    "Return the change in energy if the spin at (i,j) is flipped."
    return (
        2
        * il.lattice[i, j]
        * (
            il.lattice[i, (j - 1) % il.n_cols]
            + il.lattice[i, (j + 1) % il.n_cols]
            + il.lattice[(i - 1) % il.n_rows, j]
            + il.lattice[(i + 1) % il.n_rows, j]
        )
    )
    return delta_energy
