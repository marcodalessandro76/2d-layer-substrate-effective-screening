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

## 5. Validation ideas
- Trivial substrate (g = 0): the modified databases must reproduce the original ones bit by bit.
- Analytic limits: a point-like / Keldysh model of the layer with g = (eps-1)/(eps+1), compare with the simple models.
- Explicit benchmark: a layer on a few explicit substrate layers in the same cell (small, lattice-matched test system,
  e.g. hBN on hBN) vs the effective scheme with g(Q) of the same slab.
