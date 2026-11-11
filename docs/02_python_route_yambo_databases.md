# 02 — Python route: substrate screening by editing the Yambo databases (2026-11-05)

Decision (user, 2026-11-05): include the substrate by modifying the Yambo databases in python, without modifying the
Lumen source. This file collects the plan and the points to verify. **Nothing here has been checked on the Yambo
source yet** (cluster unreachable on 2026-11-05): every statement on the database content is a hypothesis.

## 1. What has to change (theory, see 01_context_and_literature.md)
With chi0 = chi0^L + chi0^S and only the electronic substrate response:

    vt = v + v_reac,   v_reac(Q; z, z') = -(2 pi / Q) g(Q) e^{-Q z} e^{-Q z'}          (static, z_s = 0)
    W  = vt + vt chit^L vt,   chit^L = chi0^L + chi0^L vt chit^L

GW (Amblard 2024, Eq. 18; Duchemin 2024, Eq. 23), linear in W:

    Sigma = Sigma_x[v]                      (unchanged: bare v)
          + i G [W - vt]                    (dynamical screening of the layer, built with vt)
          + Sigma_SEX[v_reac] + Sigma_COH[v_reac]   (static reaction field, COHSEX)
    Sigma_SEX = - sum_occ phi phi* v_reac(0),   Sigma_COH = 1/2 delta(r - r') v_reac(r, r)

BSE: static W (built with vt) in the direct kernel; exchange kernel with the bare v (to be discussed).

## 2. Mapping onto Yambo runs (hypotheses to verify)
1. **Free-standing layer**: QE scf/nscf -> p2y -> setup, slab Coulomb cutoff along z, as usual.
2. **Symmetries**: the substrate breaks the z -> -z operations (germanene D3d -> C3v). The databases are stored in the
   IBZ and Yambo unfolds them with the symmetries of the SAVE: the SAVE must contain only symmetries compatible with
   the substrate (e.g. `ypp` fixsyms with a field along z, keeping time reversal), otherwise the unfolding would put
   the substrate on the wrong side for part of the q points.
3. **Screening database** (`ndb.em1s` static, `ndb.pp` plasmon pole, `ndb.em1d` full frequency): believed to store,
   per q in the IBZ, the symmetrized matrix eps~^-1_{GG'}(q, w) (or eps~^-1 - delta) with v^{1/2}(q+G) factors and
   the cutoff Coulomb. From it, python can
   - recover the layer response: v^{1/2} chi0^L v^{1/2} = 1 - (eps~^-1)^-1 (any frequency stored);
   - redo the Dyson equation with vt (vt is diagonal in G_par, rank-1 correction in G_z for each G_par: Woodbury);
   - write back an eps~^-1 that encodes W - v (or W - vt, see 4) in the same symmetrized form.
4. **GW with plasmon pole**: the static v_reac cannot be fitted by the pole of each matrix element. Since Sigma is
   linear in W, split it: run Yambo with a database encoding W - vt only (a genuine dynamical screening, PPA is
   fine), and compute the static v_reac COHSEX separately (python from wavefunctions/oscillators, or a second
   Yambo run with a database encoding v_reac with a very high pole, which reproduces COHSEX in the limit). COH is
   best computed with closure, 1/2 <n|v_reac(r,r)|n>, not by a sum over bands.
5. **BSE**: the kernel reads the static screening (`ndb.em1s`): write W(0) = v + v_reac + vt chit^L vt there.
6. **q -> 0 and RIM**: the head of vt goes as (2 pi/Q)(1 - g(0)); check how Yambo treats head and wings of eps^-1
   and the RIM / RIM-W integration with the slab cutoff, and correct them consistently.
7. **Consistency checks** on the database headers (parameters, cutoffs, number of G vectors, fragments per q),
   so that Yambo accepts the modified files.

## 3. Points to verify on the Lumen source (`~/Applications/Lumen/src` on ismhpc) or on the public Yambo source
- exact content and normalization of `ndb.em1s` / `ndb.pp` / `ndb.em1d` (eps^-1 or eps^-1 - 1; symmetrization;
  which v: cutoff, RIM; frequencies stored for PPA; fragments; real/complex layout);
- how the self-energy and the BSE kernel read them (head/wings, q -> 0 direction, RIM-W);
- how the symmetries rotate the stored matrices;
- whether yambopy readers (e.g. the static screening database class) can be reused for reading/writing.

## 4. Points to analyse in detail in the computational step (noted 2026-11-11, at the user's request)
These are flagged now and are to be worked out when the explicit computations start; nothing is decided yet.

**A. Which Coulomb interaction goes where (Notes, Sec. 2.1, last paragraph).** The substitution v -> vt concerns
the screened interaction W only. The ground state of the layer and the bare exchange Sigma_x = iGv stay those of the
free-standing layer; the substrate enters the correlation part through W - v = v_emb + vt chit^L vt, where v_emb is
the polarization of the substrate by the added electron or hole. To analyse in detail (user: "very important"):
- how Yambo splits Sigma into Sigma_x (bare v) and Sigma_c (W - v), and which database each part reads;
- how to write W - v with the substrate (v_emb + vt chit^L vt) into the screening databases, consistently with the
  split of item 2.4 (dynamical part W - vt with PPA, static v_emb as COHSEX with the COH term added explicitly);
- the same question for the BSE kernel (direct term with W(0); exchange term with v or vt, open point).

**B. Coulomb cutoff of the 2D supercell.** In GW for 2D systems the layer lies in the xy plane of a box of height L_z,
and the periodic boundary conditions (needed for the plane-wave expansion) create fictitious replicas of the layer at
z = d + n L_z. The bare interaction is truncated along z (slab cutoff) to remove the interaction between replicas. To
understand how to combine it, correctly and consistently, with the embedding term:
- v_emb describes a single substrate below the physical layer: it must not be replicated, nor act between replicas;
  its representation in the supercell basis (q + G_par, G_z) has to be built for the cell containing the layer only
  (rank one in G_z at each q + G_par, from v_emb ~ g e^{-Qz} e^{-Qz'});
- the position of the substrate surface (z = 0) and of the images (at -z') with respect to the box and to the cutoff
  length (e.g. the image distance 2d versus L_z/2);
- whether the Dyson equation of the layer is to be solved with vt = v_cut + v_emb, v_cut the truncated interaction;
- the head and wings at q -> 0 (v_emb ~ 1/Q at small Q changes the head) and the RIM / RIM-W integration with the
  cutoff (see item 2.6).
The 2D formulation of Sec. 1 (mixed representation, supercell, truncation, small-q behaviour), the next step of the
notes, is meant to prepare this analysis.

**B, checked on the Lumen source (2026-11-11, branch `bug-fixes`, `~/Applications/Lumen/src`, commit 5ec7644).**
- `CUTGeo='slab z'` -> `src/coulomb/cutoff_slab.F` (called by `cutoff_driver.F`, from `col_driver.F`): bare_qpg
  (= |q+G|, v = 4pi/bare_qpg^2) is divided by sqrt(prefactor), i.e.
  v_cut(q+G) = 4pi/|q+G|^2 [1 - e^{-|q_par+G_par| L/2} cos((q_z+G_z) L/2)],  L = cell height (alat(idir(1)), z here).
  This is the Ismail-Beigi / Rozzi slab truncation: the Fourier transform over one cell of 1/|r - r'| set to zero for
  |z - z'| > L/2 (the sin term of the general transform vanishes because q_z + G_z = 2pi n/L). The truncation acts on
  the RELATIVE coordinate z - z' only: it is translation invariant along z, so there is NO centring of the cutoff
  with respect to the cell origin and the position of the layers in the cell (our bilayer at z = +-d/2) does not
  matter. Condition of validity: all the charge of the system (occupied densities, and the transition densities
  phi_occ phi_empty that enter chi0) within a window of width L/2 along z, so that within one cell |z - z'| < L/2 and
  every replica is at |z - z'| > L/2. For the bilayer with c = L = 40 bohr: L/2 = 10.6 A vs an extent of about
  d + 2 x (density tail). CHECKED (2026-11-11, DFT_Analysis.ipynb, planar-averaged valence density from the
  G_par = 0 components of charge-density.dat; pp.x is not compiled on ismhpc): bilayer density < 1e-4 of its maximum
  for |z| > 4.7 A (width 9.4 A), < 1e-5 for |z| > 5.4 A; charge outside the L/2 window 3e-6; weight of the charge
  pairs at |z - z'| > L/2 ~ 1e-9. With c = 40 bohr the slab cutoff is safe for bilayers and monolayers.
- q -> 0 (iq = 1, G = 0) without RIM: bare_qpg(1,1) from an analytic average of v_cut over a disc of area equal to
  the q-cell (series in R_circle * L/2). With RIM: `rim_integrate_v.F` integrates the same v_cut over random points.
- RIM_W (`rim_integrate_w.F`): implemented ONLY with the slab cutoff (error otherwise). It integrates
  v f v / (1 - v f) over the q-cell, with sqrt(v_cut) of the same form and f a quadratic-in-q fit of the screening
  (coefficients `f_coeff` built in `qp/QP_interpolate_W.F` from vX of the em1d database; "eq. 14 + 16 of npj Comput.
  Mater. 9, 44 (2023)", Guandalini et al. [reference as written in the source comment]). Relevant for us: RIM_W
  rebuilds W near q = 0 from the stored screening assuming W = v/(1 - v f) with the bare v_cut, so a vt-based screening
  written in the databases would be partly overwritten in the q-cell around Gamma unless RIM_W is adapted or
  switched off -> to analyse with item A.
- Existing environment option: input variable `EpsEnv` (verbosity RL, default 1; `INIT_load.F`): in `col_driver.F`
  bare_qpg *= sqrt(eps_env) and RIM_qpg /= eps_env, i.e. v -> v/eps_env UNIFORMLY (all q, G, also in the bare exchange
  and in the screening); the analogous rescaling in `rim_integrate_w.F` and `QP_interpolate_W.F` is commented out.
  This is a constant, q-independent dielectric rescaling of the whole Coulomb interaction, not our vt = v + v_emb
  (which acts only in W and depends on Q and z, z'): not usable as is, but it shows where the code changes v.
- Consequence for the effective scheme: since v_cut depends only on z - z', the term v_cut chi^S v_cut built with the
  chi0 of the "substrate" monolayer computed in the same box (ML_bot) gives the same interlayer interaction as in the
  explicit bilayer, with the same truncation; the replicas of both layers are removed in the same way. The cutoff
  condition must hold for the WHOLE bilayer (layer + substrate), not for the layer alone. For a semi-infinite
  substrate (planar formula, g(Q, w)) the question of B remains open.

## 5. Validation ideas
- Trivial substrate (g = 0): the modified databases must reproduce the original ones bit by bit.
- Analytic limits: a point-like / Keldysh model of the layer with g = (eps-1)/(eps+1), compare with the simple models.
- Explicit benchmark: a layer on a few explicit substrate layers in the same cell (small, lattice-matched test system,
  e.g. hBN on hBN) vs the effective scheme with g(Q) of the same slab.
