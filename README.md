# 2D layer on a substrate: effective screening in GW and BSE

Electronic (GW) and optical (BSE) properties of a two-dimensional semiconductor physisorbed on a bulk substrate, with
the substrate included **effectively**, through its dielectric screening, instead of explicitly in the supercell.

## Goal

A 2D layer on a substrate is usually studied either free-standing, which misses the screening of the environment, or
in a large supercell that contains both the layer and the substrate, which is expensive and requires a common lattice.
In the simplest physical situation the two subsystems interact only through their mutual polarization: no charge
transfer and no hybridization. The substrate then changes the Coulomb interaction between the charges of the layer,

    v  ->  v~ = v + v_emb,

where the embedding term `v_emb` is the potential that the polarization of the substrate, induced by a charge of the
layer, produces back in the layer. The screening of the layer, the GW self-energy and the BSE kernel are then built
with `v~` in place of `v`.

The project develops this idea step by step:

1. **Theory**: response functions and screened interaction; the dressed interaction of a planar substrate; the
   screening of a polarizable layer on it; GW self-energy and BSE kernel with the substrate.
2. **Simple models** (python): image charges, Keldysh-type screened interaction, quasiparticle gap renormalization,
   exciton binding energies and their compensation; static versus dynamical substrate.
3. **Ab initio procedure**: DFT of the free-standing layer (Quantum ESPRESSO), then GW and BSE with Yambo, adding the
   substrate screening by acting on the Yambo screening databases at the python level; validation against an explicit
   heterostructure.

First target system: **germanene on hexagonal boron nitride**. The framework is meant to apply to other layers and
substrates.

## Approach and assumptions

- Layer and substrate do not overlap: the Kohn-Sham states of the layer are barely changed by the substrate, and the
  substrate enters only through its dielectric response.
- Electronic response of the substrate only (no ionic or phonon screening).
- The GW and BSE calculations of the layer are done with Yambo; the substrate screening is added to the Yambo
  databases with python, without modifying the code.
- Reference frame: the embedded GW formalism of Blase, Duchemin and coworkers (J. Chem. Phys. 159, 164107 (2023);
  J. Chem. Phys. 160, 154104 (2024); J. Chem. Theory Comput. (2024)).

## Status

*Last update: 2026-11-10.* The project is in the theory phase.

Technical notes (`Notes/`, LaTeX):

- Sec. 1: response functions and screened interaction (G0, chi0 in the RPA, Dyson equation, dielectric function, W),
  in real space and in the plane-wave (q, G) representation.
- Sec. 2: charges in a plane, described as charge waves, and their potential.
- Sec. 3: the substrate as a dielectric half-space; the dressed interaction `v~ = v + v_emb` and the effective
  dielectric function of the environment.
- Sec. 4: screening by a polarizable layer on the substrate; Keldysh form of W; a sheet of harmonic oscillators as a
  single-pole example (link with the plasmon-pole approximation).

Next steps: the polarization energy of a charge added to the layer (gap renormalization), the electron-hole pair
(exciton binding energy), and the GW formulation of the substrate screening.

## Repository layout

- `Notes/`: technical notes. Build with `latexmk -pdf main.tex` inside `Notes/`; figures from
  `python make_figures.py`.
- `docs/`: working notes in markdown (context, literature, plans).
- Notebooks for the models and the analysis will be added when the numerical work starts.

## Tools

Quantum ESPRESSO, Yambo, python (numpy, matplotlib).

## Author

Marco D'Alessandro
