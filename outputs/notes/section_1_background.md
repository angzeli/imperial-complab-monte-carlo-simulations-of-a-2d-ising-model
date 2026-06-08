# Section 1 Background Notes

Sources:
- `Introduction.pdf`
- `script/1_introduction.pdf`

## Model Context

The 2D Ising model represents a square lattice of discrete spins, with each site
carrying `s_i = +1` or `s_i = -1`. It is a minimal model for ferromagnetic
phase behaviour because short-range nearest-neighbour interactions can generate
long-range order below a critical temperature.

## Hamiltonian

For nearest-neighbour interactions and an optional external field, the Ising
Hamiltonian is

```text
H = -J sum_<i,j> s_i s_j - sum_i h s_i
```

For this assignment the simulations use zero external field and ferromagnetic
coupling, so the working Hamiltonian is

```text
H = -J sum_<i,j> s_i s_j
```

With `J > 0`, aligned neighbouring spins lower the energy. In reduced units the
code takes `J = 1` and `k_B = 1`, so temperatures are reported as `k_B T / J`
and energies as multiples of `J`.

## Periodic Boundaries

Periodic boundary conditions remove edge sites by wrapping the lattice in both
directions. Every spin therefore has four nearest neighbours on the 2D square
lattice, including sites across the wrapped boundary. This supports a uniform
local environment and avoids special edge corrections in the energy.

## Magnetisation

The total magnetisation is

```text
M = sum_i s_i
```

At low temperature, aligned states have large absolute magnetisation. At high
temperature, thermal disorder drives the average magnetisation toward zero.

## Spontaneous Magnetisation

In zero external field, the nearest-neighbour interaction can produce a
spontaneously magnetised phase. Below the Curie temperature, the system can
settle into a state with non-zero magnetisation even though no field chooses the
direction. For finite simulations the sign may depend on the sampled history,
so `abs(M)` is useful when comparing order across runs.

## Critical Temperature Context

The Curie temperature is the highest temperature at which the infinite system
maintains spontaneous magnetisation. The 2D square-lattice Ising model with zero
field has an exact infinite-size critical temperature

```text
T_C = 2 / ln(1 + sqrt(2)) = 2.269185...
```

Finite lattices do not show a true divergence. Instead, heat capacity and
susceptibility peaks are broadened and their peak temperatures shift with
system size. The final analysis estimates `T_C,L` from these finite-size peaks
and extrapolates against `1/L`.

## Draft-Writing Notes

- Introduce the model as a nearest-neighbour lattice spin model for
  ferromagnetic ordering.
- State that the code uses periodic boundaries, zero external field, `J = 1`,
  and `k_B = 1`.
- Define total energy, total magnetisation, and per-spin normalisations.
- Explain that finite-size simulations locate an apparent `T_C,L`, not the
  true thermodynamic-limit transition directly.
