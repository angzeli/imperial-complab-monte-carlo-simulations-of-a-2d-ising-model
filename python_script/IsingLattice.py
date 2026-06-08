import numpy as np


class IsingLattice:
    def __init__(self, n_rows, n_cols, burn_in_cycles=0):
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.lattice = np.random.choice([-1, 1], size=(n_rows, n_cols))
        self.burn_in_cycles = burn_in_cycles
        self.burn_in_steps = int(burn_in_cycles * n_rows * n_cols)
        self.total_steps = 0

        current_en = self.energy()
        current_mag = self.magnetisation()

        self.attempted_moves = 0
        self.accepted_moves = 0
        self.reset_statistics(include_current=self.burn_in_steps == 0)

    def energy(self):
        """Return the total energy of the current lattice configuration."""
        energy = -np.sum(self.lattice * np.roll(self.lattice, 1, axis=0))
        energy -= np.sum(self.lattice * np.roll(self.lattice, 1, axis=1))
        self.current_energy = float(energy)
        return self.current_energy

    def magnetisation(self):
        """Return the total magnetisation of the current lattice configuration."""
        self.current_magnetisation = float(np.sum(self.lattice))
        return self.current_magnetisation

    def montecarlostep(self, temp):
        """A single Monte-Carlo trial move. Attempts to flip a random spin.
        Returns a tuple with the energy and magnetisation of the new configuration.
        """
        energy = self.current_energy
        magnetisation = self.current_magnetisation
        # Select the coordinates of the random spin.
        random_i = np.random.randint(self.n_rows)
        random_j = np.random.randint(self.n_cols)
        # The following line will choose for you a random number in the range [0,1)
        random_number = np.random.random()
        spin = self.lattice[random_i, random_j]
        delta_en = self.delta_energy(random_i, random_j)
        accept = delta_en <= 0.0
        if not accept and temp > 0.0:
            accept = random_number < np.exp(-delta_en / temp)
        if accept:
            self.lattice[random_i, random_j] = -spin
            energy += delta_en
            magnetisation += -2 * spin
            self.current_energy = energy
            self.current_magnetisation = magnetisation
            self.accepted_moves += 1

        self.attempted_moves += 1
        self.total_steps += 1
        if self.total_steps > self.burn_in_steps:
            self.E_tally += energy
            self.E2_tally += energy**2
            self.M_tally += magnetisation
            self.M2_tally += magnetisation**2
            self.n_steps += 1
        return energy, magnetisation

    def acceptance_rate(self):
        """Return the fraction of attempted moves that have been accepted."""
        if self.attempted_moves == 0:
            return 0.0
        return self.accepted_moves / self.attempted_moves

    def reset_statistics(self, include_current=True):
        """Reset running statistics, optionally including the current state."""
        if include_current:
            current_en = self.current_energy
            current_mag = self.current_magnetisation
            self.E_tally = current_en
            self.E2_tally = current_en**2
            self.M_tally = current_mag
            self.M2_tally = current_mag**2
            self.n_steps = 0
            self._initial_sample_included = True
        else:
            self.E_tally = 0.0
            self.E2_tally = 0.0
            self.M_tally = 0.0
            self.M2_tally = 0.0
            self.n_steps = 0
            self._initial_sample_included = False

    def statistics(self):
        """Returns the averaged values of energy, energy squared, magnetisation,
        magnetisation squared, and the current step, in this order."""
        n_samples = self.n_steps + int(self._initial_sample_included)
        if n_samples == 0:
            return (0.0, 0.0, 0.0, 0.0, self.n_steps)
        return (
            self.E_tally / n_samples,
            self.E2_tally / n_samples,
            self.M_tally / n_samples,
            self.M2_tally / n_samples,
            self.n_steps,
        )

    def delta_energy(self, i, j):
        """Return the change in energy if the spin at (i,j) were to be flipped."""
        nearest_neighbours = (
            self.lattice[(i - 1) % self.n_rows, j]
            + self.lattice[(i + 1) % self.n_rows, j]
            + self.lattice[i, (j - 1) % self.n_cols]
            + self.lattice[i, (j + 1) % self.n_cols]
        )
        return 2.0 * self.lattice[i, j] * nearest_neighbours
