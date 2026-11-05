# 01 — Context and literature (framing phase, 2026-11-05)

Status: framing only. The three embedding papers were read in full by sub-agents (no SI available); equations and
pages below come from those readings and must be re-checked on the PDFs before being used in derivations or code.
Everything marked **[assessment]** is our own reasoning, not the papers'.

## 1. The three reference papers (Blase–Duchemin group, BeDeft code, Gaussian basis + RI)

All three share one exact starting point (no wavefunction overlap between subsystem S and environment E):

    chi0 = chi0^S + chi0^E                                 (block diagonal, "fragment approximation")
    W^-1 = v^-1 - chi0^S - chi0^E = vt^-1 - chi0^S
    vt(w) = v + v_reac(w),   v_reac(w) = v chi^E(w) v       (chi^E: interacting response of E alone)
    W = vt + vt chit^S vt,   chit^S = chi0^S + chi0^S vt chit^S

i.e. the environment only "dresses" the bare Coulomb interaction; the GW calculation of S runs as an isolated GW with
vt in place of v. Note that the internal screening of S is itself renormalized by v_reac (chit^S built with vt).

### Amblard, Blase, Duchemin, JCP 159, 164107 (2023) — very large environments made affordable
- Atomistic ab initio environment (QM/QM', RPA), up to ~2e5 atoms (fcc C60, surfaces, slabs). Dyson equation over
  fragments: X^-1 = sum_I X_g^(I)^-1 - sum_{I!=J} V^(IJ) (Eqs. 9-11): fragments coupled only by Coulomb.
- Cost reduction: each environment fragment's chi is compressed to a small "polarization basis" fitted to reproduce
  the reaction field it produces (Eqs. 13-19), constrained to keep monopole/dipole polarizabilities (Eq. 17);
  ~1e2 fewer vectors, meV accuracy.
- Static only: Delta-COHSEX polarization energies P_n (Eqs. 20-21) added to gas-phase evGW.
- Results: C60 bulk -1.69 eV, (111) surface -1.40 eV (exp. 1.1-1.4); slabs converge slowly (~1/n in the number of
  layers, 5 layers ~85%). No BSE.

### Amblard, Blase, Duchemin, JCP 160, 154104 (2024) — static vs dynamical environments
- Compares fully dynamical chi^E(w) with the adiabatic limit. Key point (p. 3): putting w -> 0 in v_reac inside
  Sigma = iGW keeps only the screened-exchange (SEX) part and **loses the Coulomb-hole (COH) part**. The correct static
  limit is a single-pole model with the pole sent to infinity after the frequency integral (Eq. 7, App. A).
- Recommended "QM_GW/QM_COHSEX" scheme (Eq. 18-20): dynamical GW of S with the static vt, plus the static v_reac
  treated as COHSEX: Sigma_SEX = -sum_occ phi phi* v_reac(0), Sigma_COH = 1/2 sum_n phi phi* v_reac(0)
  = 1/2 delta(r-r') v_reac(r,r). The older Delta-COHSEX scheme is NOT recommended (17.5% error vs 2.9%).
- Table I: the direct reaction-field terms alone overestimate the gap closing by ~40%: the renormalization of the
  subsystem's own screening (chit^S) is essential.
- Static error small (few %) when the environment's neutral excitations are well above the subsystem's; worse for
  metallic environments (individual levels off by tenths of eV). For smooth fields: P_SEX(empty) = 0,
  P_COH = -P_SEX/2 for occupied levels (Neaton–Hybertsen–Louie limit).
- Cites Amblard et al., PRMater 6, 064008 (2022): fragmented **hBN** sheets keep short and long-range response.

### Duchemin, Amblard, Blase, JCTC (2024), arXiv:2409.01669 — PCM and GW
- Same partition with a continuum (IEF-PCM, double layer) solvent: vt(w) = v + v_reac(w) (Eqs. 9-14).
- Fast vs slow polarization: eps_0 (static, incl. nuclear) only for the DFT ground state; GW uses the electronic
  eps_inf / eps_opt(w). Using eps_inf at all frequencies gives the wrong high-frequency limit of W (p. 7).
- PCM_PP (Eq. 17): v_reac(w) = v_reac(0) f(w; Omega_p), single pole; error few meV vs full PCM(w).
  BO limit (Eq. 23, App. A): Sigma_C = iG[Wt - vt(0)] - sum_occ phi phi* v_reac(0) + 1/2 sum_n phi phi* v_reac(0);
  error ~ -50 meV (5%) on the levels, partly cancelling in the gap.
- Σx uses the bare v; the reaction-field SEX is in Σ_C. No BSE (BSE/PCM only as outlook).
- Points to: Kim et al. JPCL 2022 (GW of 2D materials in water), Kim et al. JPCL 2024 (BSE + implicit solvation for
  2D), Neaton et al. PRL 97, 216405 (2006).
- Other prior works cited in these papers: Liu et al., JCTC 2019 and Xuan, Chen, Quek, JCTC 2019 (plane-wave
  "substrate screening" GW); Andersen–Latini–Thygesen (QEH); Winther–Thygesen (G-Delta-W).

## 2. Translation to a 2D layer on a semi-infinite substrate [assessment]

### 2.1 The substrate enters only through a surface response function
For a periodic layer at height z above the substrate and in-plane wave vector Q = |q + G_par|, outside the substrate
charge the reaction potential obeys Laplace's equation, so (substrate surface reference z_s = 0):

    v_reac(Q; z, z'; w) = -(2 pi / Q) g(Q, w) exp(-Q z) exp(-Q z')            (z, z' > 0)

- g(Q, w) is the surface response function (Persson–Zaremba). Local dielectric half-space: g = beta =
  (eps - 1)/(eps + 1); uniaxial (hBN): eps -> sqrt(eps_par eps_perp); metal: g -> 1.
- Separable: **rank 1 in G_z for each (q, G_par)**, diagonal in G_par. Low-rank updates (Sherman–Morrison/Woodbury)
  of the Dyson equation become cheap.
- Umklapp components of the substrate response (reciprocal vectors of hBN, |G| ~ 2.9 1/Å) reach the layer damped by
  exp(-|G| d) ~ 1e-4 for d ~ 3.3 Å: only the macroscopic in-plane component (but with its full Q dependence) matters.
  Hence g(Q, w) can be computed ab initio in the **substrate's own primitive cell** (hBN slab) and interpolated on the
  layer's Q: the lattice mismatch problem (germanene a ~ 4.0 Å vs hBN 2.5 Å) disappears.
- The "image plane" position and the failure of a local eps at ~3 Å are absorbed in the Q dependence of g.
- Caveat: requires the layer charge to lie outside the substrate charge (density tails at d ~ 3.3 Å overlap a bit).

### 2.2 What this means in a plane-wave GW/BSE code (Yambo)
- Replace v by vt(0) = v + v_reac(0) in the Dyson equation for eps^-1 / W: vt is no longer diagonal in G_z, so the
  usual symmetrized eps~ = 1 - v^1/2 chi0 v^1/2 must be generalized (rank-1 correction per G_par).
- Keep Σx with the bare v; **add the COH term by hand**: Delta Sigma_COH = 1/2 v_reac(r, r) (a local potential, the
  classical image potential, -beta/[4(z - z_s)] for a local half-space). Without it absolute levels/band offsets are
  wrong by ~|v_reac|/2 (the gap less, COH nearly cancels there).
- q -> 0: the head goes as (2 pi/Q)(1 - g(0)) = (2 pi/Q) 2/(eps + 1): slab cutoff and RIM/RIM-W must be adapted.
- Coulomb truncation: the image term must be added once (not replicated along z) and only for z > z_s.
- BSE: the direct kernel uses static W anyway -> W built with vt(0). Open question: exchange kernel with v or vt.
- Electronic vs ionic response of hBN (polar, eps_0 != eps_inf, LO phonons ~0.17-0.20 eV): GW uses the electronic
  part. For small-energy excitations (germanene excitons, binding energies of tens of meV) the lattice may follow ->
  ionic screening could matter: beyond the electronic-only framework of the three papers.

### 2.3 DFT level
With a neutral, non-polar layer, no charge transfer and no hybridization, the ground-state reaction field
(eps_0) is very weak: the KS bands are essentially those of the free-standing layer. The substrate physics lives in
correlation (GW) and in W (BSE). The DFT step is therefore mainly: free-standing layer + an explicit-heterostructure
DFT check of the assumptions (feasible at DFT level, not at GW level). ESM (Otani–Sugino) is not essential under these
assumptions (its standard boundary conditions are vacuum/metal; finite-eps extensions to be checked).

### 2.4 Germanene on hBN: specific issues
- Germanene is a buckled Dirac material with a SOC gap of only tens of meV (24-33 meV in the literature): not a
  conventional semiconductor. Its own screening is quasi-metallic at small Q (r0 ~ 1/gap), so the substrate competes
  with a very strong intrinsic screening; exciton radii are large.
- Brunetti, Berman, Kezerashvili, PLA 383, 482 (2019) (user's library): Rytova–Keldysh model predicts an excitonic
  insulator phase in free-standing Xenes that is destroyed on hBN/SiO2 (kappa_hBN = 4.89). A fully ab initio treatment
  of the substrate screening is the natural test of this kind of prediction.
- Sublattice asymmetry: the hBN crystal field can open a mass gap (as in graphene/hBN), possibly comparable with the
  SOC gap. This is NOT a polarization effect: it depends on stacking/commensuration and must be checked at DFT level.
- Classical image estimate beta/(2d) with eps_eff ~ 3.8 (electronic), d ~ 3.3 Å gives ~1.3 eV gap closing: a gross
  overestimate for delocalized Bloch states in a strongly polarizable layer; it shows why the layer's own screening
  (chit^S) and the Q dependence of g are essential.
