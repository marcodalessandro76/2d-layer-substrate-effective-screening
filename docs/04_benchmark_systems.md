# 04 — Benchmark systems: explicit vs effective GW (2026-11-11)

Goal (user, 2026-11-11): a layer + substrate system on which GW can be done both explicitly (whole system in the
supercell) and with the effective scheme of the notes (Sec. 2: chi0 = chi0^L + chi0^S, vt = v + v chi^S v), to test
the procedure. Criteria: small commensurate cell, van der Waals coupling without charge transfer, references
(calculations and/or experiments). The static limit of chi^S is not required: the user prefers to test the method in
general (dynamical chi^S).

## Decision (user, 2026-11-11): start with bilayer hBN
The second hBN layer plays the role of the substrate (Sec. 2.1 makes no assumption on a semi-infinite substrate; the
planar formula of Sec. 2.2 also holds for a finite slab below the layer).
- Cheapest possible: 4 atoms, identical lattices, no strain, no commensurate supercell.
- chi0^S is the chi0 of the monolayer translated by d along z (a phase e^{-i(Gz - Gz') d} in the plane-wave basis):
  layer and "substrate" come from the same monolayer databases.
- Reference with the same codes: Guo, Xu, Rocca, Ping, PRB 102, 205113 (2020) [arXiv:2007.07982]: explicit GW of
  bilayer hBN (AA' and AB, d = 3.33 A) and hBN/SnS2 with QE + Yambo (PBE, ONCV, 80 Ry, Godby-Needs PPA, 20 A vacuum, 2D
  cutoff). Their "chi_eff-sum" is equivalent in the RPA to the chi0-sum (our scheme): within ~0.2 eV of the explicit
  results; adding the interface DFT eigenvalues ("GSC") improves by ~50 meV, eigenvalues + wavefunctions ("FWF") within
  ~10 meV. Summing the interacting chi of the two subsystems ("chi-sum", no interlayer Coulomb coupling) is ~0.6 eV off
  for hBN/SnS2. Neglecting in-plane off-diagonal elements (eps^-1-diag): within ~40-50 meV; neglecting out-of-plane
  off-diagonal elements: 0.2-0.8 eV errors. Monolayer hBN gap ~7 eV; bilayer reduction ~0.2 eV (read from the text).
- Caveats: (1) static limit not valid (same excitation energies): use the dynamical chi^S, keep the static one only to
  measure its error; (2) in a homobilayer the degenerate states of the two layers mix even for weak coupling
  (bonding/antibonding pairs): compare quantities insensitive to this (e.g. averages of the split pairs) and state the
  splitting; do AA' (stronger coupling) and AB; (3) the DFT bands of monolayer vs bilayer measure the change of the
  ground state (assumption 2 of Sec. 2.1) before any GW.

Plan (to be detailed and agreed before any run):
1. DFT of monolayer and bilayer (AA', AB) with the same alat, box, cutoffs; compare the bands. Notebook
   `hBN_bilayer/DFT_Analysis.ipynb` (2026-11-11): SG15 ONCV PBE SR, no SOC, a = 2.504 A (experimental, fixed),
   d = 3.33 A (fixed), bilayer at z = +-d/2, monolayer at z = +d/2 (top layer).
2. Explicit GW of the bilayer (Yambo, slab cutoff, PPA or full frequency).
3. Effective GW of the monolayer: (a) full matrix, chi0^S = translated monolayer chi0 in the same basis (no-overlap
   only, Umklapp included; equivalent to Guo's chi_eff-sum); (b) planar formula with g(Q, w) (Umklapp neglected).
   (a) vs explicit tests assumptions 1-2; (b) vs (a) tests the Umklapp neglect; static vs dynamic chi^S.
4. Compare with Guo et al. to validate the setup.

## Other candidates (for later)
- **SnS2 on hBN** (1-3 hBN layers): ~30 atoms per hBN layer (2x2 SnS2 on 3x3 hBN with ~1.5% strain: our inference
  from the lattice constants 3.70 / 2.51 A of Guo et al.); explicit QE+Yambo precedent (Guo et al., with hBN as the
  layer); substrate gap well above the layer gap (tests the static limit); few experiments on hBN.
- **MoS2 on hBN**: 4x4 MoS2 on 5x5 hBN (~100 atoms per hBN layer). Adeniran & Liu, PRMaterials 7, 054001 (2023)
  [arXiv:2212.01676]: dielectric-embedding G0W0 (BerkeleyGW) vs direct G0W0 for MoS2 on monolayer hBN within ~50 meV
  on the gap (0.1 eV on single levels); screening saturates with ~4 hBN layers (gap 2.41 eV on 4L hBN, ~0.4 eV
  renormalization); dropping the in-plane local fields of the hBN chi0 costs ~0.2 eV. Experiments: hBN-encapsulated
  MoS2, free-particle gap 2.160 eV and 1s binding energy 221 meV (Goryca et al., Nat. Commun. 10, 4172 (2019); two-sided
  hBN).
- **MoS2 on SiO2**: application of the effective scheme with g = beta (eps_inf ~ 2.1, beta ~ 0.35; values quoted from
  memory), NOT an explicit benchmark (amorphous substrate, surface model, hundreds of atoms, small effect ~0.1-0.25 eV,
  disorder-dominated experiments: STS apparent gap ~2.1 eV vs absorption onset ~2.44 eV, Klein et al.). Theory:
  Zibouche, Schlipf, Giustino, PRB 103, 125401 (2021) [arXiv:2008.03980] (continuum model, gap reduced by up to
  250 meV); Naik & Jain [arXiv:1710.09569] (free-standing gap 2.7 eV, nearly unchanged on BN or SiO2).
- **Graphene on hBN 1x1**: cheapest, but its substrate gap (~0.1 eV commensurate, Kharche & Nayak, Nano Lett. 2011)
  comes from the ground-state sublattice potential, which the scheme does not contain; Dirac analogue of germanene.
- **Germanene on hBN**: the final target, with the effective scheme only.
- Other literature to read: Winther et al. arXiv:1703.03188 (Delta-W / QEH vs full GW); Steinke, Wehling, Rösner,
  PRB 102, 115111 (2020) (dynamical substrate screening in TMDs).
