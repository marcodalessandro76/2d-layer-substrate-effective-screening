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

## 4. Validation ideas
- Trivial substrate (g = 0): the modified databases must reproduce the original ones bit by bit.
- Analytic limits: a point-like / Keldysh model of the layer with g = (eps-1)/(eps+1), compare with the simple models.
- Explicit benchmark: a layer on a few explicit substrate layers in the same cell (small, lattice-matched test system,
  e.g. hBN on hBN) vs the effective scheme with g(Q) of the same slab.
