from IsingLattice import IsingLattice
from matplotlib import pyplot as plt
import numpy as np

n_rows = 8
n_cols = 8
il = IsingLattice(n_rows, n_cols)
il.lattice = np.ones((n_rows, n_cols))

# recalculate the energy after changing the lattice
current_energy = il.energy()
current_magnetisation = il.magnetisation()
il.E_tally = current_energy
il.E2_tally = current_energy**2
il.M_tally = current_magnetisation
il.M2_tally = current_magnetisation**2
il.n_steps = 0

spins = n_rows * n_cols
runtime = 100000
times = range(runtime)
temps = np.arange(1.5, 3.5, 0.1)
energies = []
magnetisations = []
energysq = []
magnetisationsq = []
heat_capacities = []
for t in temps:
    for i in times:
        if i % 1000 == 0:
            print(t, i)
        energy, magnetisation = il.montecarlostep(t)
    aveE, aveE2, aveM, aveM2, n_steps = il.statistics()
    energies.append(aveE)
    energysq.append(aveE2)
    magnetisations.append(aveM)
    magnetisationsq.append(aveM2)
    heat_capacities.append((aveE2 - aveE**2) / (spins * t**2))
    # reset the IL object for the next cycle
    current_energy = il.current_energy
    current_magnetisation = il.current_magnetisation
    il.E_tally = current_energy
    il.E2_tally = current_energy**2
    il.M_tally = current_magnetisation
    il.M2_tally = current_magnetisation**2
    il.n_steps = 0
fig = plt.figure()
enerax = fig.add_subplot(3, 1, 1)
enerax.set_ylabel("Energy per spin")
enerax.set_xlabel("Temperature")
enerax.set_ylim((-2.1, 0.1))
magax = fig.add_subplot(3, 1, 2)
magax.set_ylabel("Magnetisation per spin")
magax.set_xlabel("Temperature")
magax.set_ylim((-1.1, 1.1))
heatax = fig.add_subplot(3, 1, 3)
heatax.set_ylabel("Heat capacity per spin")
heatax.set_xlabel("Temperature")
enerax.plot(temps, np.array(energies) / spins)
magax.plot(temps, np.array(magnetisations) / spins)
heatax.plot(temps, heat_capacities)
plt.show()

curie_temperature = temps[int(np.argmax(heat_capacities))]
print("Estimated Curie temperature = {}".format(curie_temperature))

final_data = np.column_stack(
    (
        temps,
        np.array(energies) / spins,
        np.array(energysq) / spins**2,
        np.array(magnetisations) / spins,
        np.array(magnetisationsq) / spins**2,
        heat_capacities,
    )
)
np.savetxt(f"{n_rows}x{n_cols}.dat", final_data)
