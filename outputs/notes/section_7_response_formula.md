# Section 7 Response-Function Formula Notes

The assignment uses reduced units with `k_B = 1`.

For heat capacity,

```text
C = d<E>/dT = Var(E) / T^2
```

where

```text
Var(E) = <E^2> - <E>^2
```

The plotted per-spin heat capacity is therefore

```text
C_per_spin = (<E^2> - <E>^2) / (N_spins T^2)
```

For susceptibility,

```text
chi = beta Var(M)
beta = 1 / T
Var(M) = <M^2> - <M>^2
```

The plotted per-spin susceptibility is therefore

```text
chi_per_spin = (<M^2> - <M>^2) / (N_spins T)
```

The code clips tiny negative variances to zero before plotting. These values can
arise from floating-point roundoff when the sampled state is effectively fixed.
