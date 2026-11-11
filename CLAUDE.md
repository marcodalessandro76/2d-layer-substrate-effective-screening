# 2D layer on a substrate: effective screening (DFT -> GW+BSE): notes for Claude Code

The user (Marco D'Alessandro) writes in Italian: reply in Italian. Files (this CLAUDE.md, notes, code, docstrings,
commit messages) are in English, as in the user's other projects. Living document: update it at every step
(decisions, results, open points); keep long material in `docs/` and point to it from here.

## Goal
Electronic (GW) and optical (BSE) properties of a 2D semiconductor layer **physisorbed** on a **bulk** substrate,
with the substrate treated **effectively** (not explicitly in the supercell). Simplest physical situation (user,
2026-11-05): layer and substrate interact only through **mutual polarization**; no charge transfer, no hybridization.
First target system: **germanene on hexagonal BN**. Path, step by step: theory -> simple models -> full ab initio
computational procedure (possibly a code implementation).

## Working context (from the user's other projects)
- Codes: Quantum ESPRESSO (`pw.x`, 7.0) + Yambo (the Lumen fork, built from source by the user on the cluster: code
  modifications are possible). Workflow and post-processing with the user's package **MPPI**
  (`D:\Projects\Research\MPPI`, own CLAUDE.md): PwInput/YamboInput -> QeCalculator/YamboCalculator (RunRules,
  slurm) -> Dataset -> parsers -> analysis. Changes to MPPI go to that repository, in a separate session.
- Example of a research project and of the user's way of working: `D:\RICERCA\DFT AND MANY BODY\SIMULATIONS\LiF`
  (own CLAUDE.md): git repo synced laptop <-> cluster, notebooks driving MPPI, technical notes in LaTeX
  (`Notes/main.tex` + `header.tex`, English, explicit derivations, built with latexmk), analytical models used to
  validate every analysis formula before applying it to ab initio data.
- Machines: Windows laptop (no QE/Yambo; python `C:/Users/Marco/miniconda3/python.exe`) for theory, notes, models,
  analysis; cluster `ismhpc` (ssh, slurm) for QE/Yambo. Ask the user before launching any QE/Yambo run.
- Literature library: `D:\RICERCA\DFT AND MANY BODY\REFERENCES` (catalogue and reading notes in `_Catalog/`, own
  CLAUDE.md). Key folders: `03 Equilibrium MBPT - GW and BSE`, `11 2D materials`.

## Computational workflow (MPPI, clusters) -- details in `docs/03_mppi_workflow_and_2D_convergence.md`
- MPPI (`D:\Projects\Research\MPPI`, v1.3; on ismhpc `~/Applications/MPPI`, editable install, git pull only):
  PwInput/YamboInput -> QeCalculator/YamboCalculator(RunRules) -> Dataset(run, fetch_results, PostProcessing) ->
  parsers. Patterns, variable names and parallelization roles in docs/03, Sec. 1.
- Key rules: nscf for p2y with `force_symmorphic=True` (otherwise Lumen yambo silently runs nothing); SAVE with
  `Tools.init_yambo_dir(yambo_dir, input_dir, p2y_command='OMP_NUM_THREADS=1 mpirun -np 1 p2y', yambo_command=...)`
  (p2y ends with MPI_ABORT but the SAVE works); 2D: `CUTGeo='slab z'` + RIM (RandQpts, RandGvec) + RIM_W
  (RandGvecW), `LongDrXp=[1,1,0]`; shared databases through the `jobname` list. Current conventions (LiF production
  notebook, they supersede the older GW notebooks; docs/03 Sec. 1.3): keep `reformat=True` (no `reformat=False`),
  calculator factory per section, `append_run(..., name=..., jobname=[...], skip=True)`, run names <= 100 chars,
  restarts with `skip=False, clean_restart=False, activate_BeeOND=False`. ismhpc rules: <= 3 nodes at a time, all12h
  (slownodes > 12 h), exclude wnode07; default yambo = Lumen `bug-fixes` build since 2026-10-23.
- ismhpc: QE and yambo need different environments, through `RunRules(pre_processing=
  '/home/dalessandro/module_script/qe_module' | '.../yambo_module')`; production RunRules in docs/03, Sec. 2
  (all12h, 32 cores/node, BeeOND). Leonardo (GPU) RunRules in the germanene notebooks. Drive ismhpc from the laptop
  with `ssh -o BatchMode=yes -o ClearAllForwardings=yes ismhpc '...'`. Ask the user before ANY QE/Yambo/p2y run.
- Convergence protocol for 2D layers (from the MoS2 and germanene notebooks, docs/03 Secs. 3-4): DFT ecut x k, alat
  and buckling, vacuum; GW: HF with RIM, EXXRLvcs = VXCRLvcs, k; PPA NGsBlkXp -> BndsRnXp -> GbndRnge (+ BG
  terminator) -> RandGvecW -> k grid with extrapolation; QP bands per k point.
- Cluster copy: `~/work/2d-layer-substrate-effective-screening` on ismhpc (cloned 2026-11-11; `~/work` is a link to
  `/work/dalessandro`), remote `git@github.com:...` over SSH as for LiF. Old git there (1.8.3: no `git -C`, use `cd`).
- Working from the cluster (user, 2026-11-11: in general the work goes on from a Claude Code session on ismhpc, in
  tmux, driven also from the laptop app through Remote Control): Claude Code CLI in the conda env `tools` (tmux is
  there too), session started in `~/work/2d-layer-substrate-effective-screening`; commands are then local (no ssh
  prefix). Claude's memory is per machine: everything that must survive goes in this file. NOT available on the
  cluster: LaTeX (no latexmk/pdflatex: build `Notes/*.pdf` from a laptop session, or ask the user), the literature
  library `REFERENCES` (literature checks on the PDFs from the laptop), the laptop paths `D:\...`. Available there:
  the earlier MoS2 and germanene runs in `~/work/TMDs/MoS2` and `~/work/Xenes/Germanene` (pseudos, inputs, SAVEs),
  MPPI in `~/Applications/MPPI`, python `~/miniconda3/bin/python`.

## Framing (details, equations and page references in `docs/01_context_and_literature.md`)
- Reference works (Blase–Duchemin group): Amblard et al. JCP 159, 164107 (2023); Amblard et al. JCP 160, 154104
  (2024); Duchemin et al. JCTC 2024 (arXiv:2409.01669). Common exact frame for non-overlapping subsystems:
  chi0 = chi0^S + chi0^E  =>  v -> vt = v + v_reac,  v_reac = v chi^E v,  W = vt + vt chit^S vt.
- Planar substrate [our assessment]: v_reac(Q;z,z') = -(2pi/Q) g(Q,w) e^{-Qz} e^{-Qz'} (surface response function g;
  local half-space g = (eps-1)/(eps+1)). Rank 1 in G_z per (q, G_par); substrate Umklapp terms negligible at the layer,
  so g(Q,w) can be computed in the substrate's own cell -> no lattice-matching supercell needed.
- Lessons from the papers: (i) a static v_reac inserted in Sigma = iGW gives only SEX: the COH term
  1/2 v_reac(r,r) must be added explicitly; (ii) the layer's own screening must be computed with vt (Delta-COHSEX
  corrections are not recommended); (iii) GW uses the electronic (eps_inf) response, eps_0 only for the ground state;
  (iv) static environment is accurate (few %) when its excitations lie well above those of the subsystem (hBN vs
  germanene: favourable for the electronic part).
- DFT level: under our assumptions the substrate barely changes the KS states; DFT is used for the free-standing
  layer and for an explicit-heterostructure check of the assumptions (hybridization, sublattice-asymmetry gap).
- Germanene specifics: Dirac material with a SOC gap of tens of meV, quasi-metallic intrinsic screening; hBN is polar
  (ionic screening possibly relevant for low-energy excitons); excitonic-insulator question (Brunetti et al. PLA 383,
  482, 2019).

## Decisions (user, 2026-11-05)
- Physics target: to be clarified during the analysis; the fixed goal is the effective inclusion of the substrate in
  GW+BSE. Germanene/hBN is the first example, not a constraint.
- Substrate response: **electronic only** (no ionic/phonon screening).
- Implementation: **python, acting on the Yambo databases** (screening databases for GW and BSE); the Lumen source
  is NOT modified. Plan and points to verify: `docs/02_python_route_yambo_databases.md`.
- Organization: same structure as the LiF project: git repo, technical notes in LaTeX, analysis and models in python
  notebooks (MPPI).

## Repository
- Git repo (branch `main`, created 2026-11-05), public on GitHub since 2026-11-10:
  `origin` = github.com/marcodalessandro76/2d-layer-substrate-effective-screening (name chosen by the user). Push
  only when the user asks.
- Local folder (laptop): `D:\RICERCA\DFT AND MANY BODY\SIMULATIONS\2d Layer Substrate Effective Screening`.
  History: created as `...\THEORY\Effective screening`, renamed on 2026-11-10 to `...\THEORY\2d Layer Substrate
  Effective Screening`, MOVED BY THE USER on 2026-11-11 to `SIMULATIONS` (the project now runs calculations;
  SIMULATIONS is organized by material, this project is a cross-material one with one subfolder per system).
  The Claude memory was copied to the key of the new path,
  `D--RICERCA-DFT-AND-MANY-BODY-SIMULATIONS-2d-Layer-Substrate-Effective-Screening`. The old memory keys
  (`...-THEORY-Effective-screening`, `...-THEORY-2d-Layer-Substrate-Effective-Screening`) are kept for now (they
  hold the transcripts of the sessions started there): delete them only if the user asks. At the first session in
  the new folder, check that `...\THEORY\2d Layer Substrate Effective Screening` no longer exists (or is an
  identical, clean copy that the user wants removed).
- Planned layout for the calculations (agreed 2026-11-11): one subfolder per system, each with its notebooks
  (DFT_Analysis, GW_Analysis, Embedding_Analysis, ...) and run folders (DFT_analysis/, MB_analysis/, not tracked):
  `hBN_bilayer/` (first benchmark), later `SnS2_hBN/`, `MoS2_hBN/`, `Germanene_hBN/` (application); common
  `pseudos/`; later the python code that edits the Yambo databases. The earlier MoS2 and germanene studies stay in
  `SIMULATIONS/TMDs/MoS2` and `SIMULATIONS/Xenes/Germanene` (own git repos): reuse their parameters and pseudos.
- Cluster copy: `/home/dalessandro/work/2d-layer-substrate-effective-screening` on ismhpc (cloned on 2026-11-11 at
  the user's request; named as the GitHub repo, no spaces: MPPI `run_job` uses `os.system('rm ...')`, which breaks on
  paths with spaces). Remote over SSH (`git@github.com:marcodalessandro76/2d-layer-substrate-effective-screening.git`).
  Sync as in LiF: commit/push on one machine, pull on the other. Data stay on the cluster, only notebooks/notes in git.
- `README.md`: public description of goals, approach, status and layout; it evolves with the project. Update its
  "Status" section (with the date) when the notes or the work reach a new stage.
- `Notes/`: technical notes, LaTeX, same style as LiF (`main.tex` with `\input{header.tex}`, notation macros in
  `header.tex`, `biblio.bib` with keys from the library catalogue `REFERENCES/_Catalog/library.bib`, bibtex unsrt).
  After each change build `Notes/main.pdf` (and `Notes/models.pdf` if models.tex changed) in place with
  `latexmk -pdf` and check the log (errors, Overfull \hbox, undefined references); the PDFs are not tracked. Do not refer to sections that do not exist yet.
  Figures: `Notes/make_figures.py` (registry `FIGURES`, run from `Notes/` with the miniconda python, saves jpeg in
  `Notes/Figures/`, included with `\includegraphics{Figures/<name>.jpeg}`).
  State (2026-11-10; no introduction, by the user's request):
  Sec. 1 "Response functions and screened interaction" (`sec:response`; first draft written 2026-11-10 at the user's
  request, to be revised with the user): schematic definitions in r space, logic after Strinati 1988 pp. 7-10
  (total classical potential Eq. 3.15, eps^-1 = dV/dU, chi, irreducible polarizability, eps, W) and Blase 2018 p. 18
  (charge induced by a test charge, W = v + v chi v); also Golze 2019 Sec. 4.1, Amblard 2024 Sec. II A, Gatti 2010
  slide 14 (read, not cited). Paragraphs: opening (one question: response to an external charge; external vs total
  potential); conventions (quasi-static, SI/a.u. units moved here from the old Sec. 1, fixed nuclei, linear response
  local in w, kernels integrated over r'); external charge and chi (eq:phi_ext; short remark, user 2026-11-10, on
  rho_ext(r,w): time-dependent charge decomposed in frequency components, charge at rest = w = 0, sudden charge = all
  frequencies, v instantaneous; eq:chi_def, stated as the definition of chi; eq:chain = Eq. 1 inserted in Eq. 2,
  chain r'' -> r' -> r, user's request; closing remark: non-polarizable system -> rho_ind = 0, chi = 0, not
  rho_ind = rho_ext (user's question, 2026-11-10)); Fig. `fig:response` (TikZ in main.tex, not in make_figures.py; user's suggestion): (a) the chain of
  eq:chain in the electron system, (b) block diagram of the self-consistent loop phi -> chi0 -> rho_ind -> v -> phi,
  referred to in the Dyson paragraph; total potential
  (eq:phi_tot; second term named the Hartree potential of the induced charge and stated to be local, i.e.
  multiplicative on psi(r), vs the nonlocal exchange / GW self-energy, user's question 2026-11-10); "Response to the
  total potential" (eq:chi0_def: rho_ind = int chi0 phi directly, user 2026-11-10; text: writing chi0 there is the
  RPA; the exact response to phi is the irreducible polarizability P, Strinati, which contains exchange and
  correlation, not the Hartree feedback; relations below valid for P with P in place of chi0; no mention of
  excitons/BSE here, user 2026-11-10); "Non-interacting Green's function" (opens with "From here on, in this
  section, we set hbar = e = 1", user 2026-11-11: units not of interest at this stage; Eqs. 6-8, 13-14 and the
  table written with hbar = e = 1; SI prefactors were e^2 hbar in eq:chi0_G0 and e^2 in eq:chi0_KS, eq:chi0_qG)
  (eq:G0, time-ordered KS G0 as in Golze Eq. 24, propagation of added electron/hole, poles at KS energies vs QP
  energies of the interacting G); "Independent-particle response" (motivation in 3 lines, user 2026-11-10:
  n(1) = -iG(1,1+), first-order delta G = G0 dV G0, so chi0(1,2) = -i G0(1,2) G0(2,1) = Strinati Eq. 3.26 without
  vertex, checked on the PDF; then eq:chi0_G0: chi0 = -i int dw'/2pi
  G0(r,r';w+w') G0(r',r;w'), Golze Eq. 27, trace over spin; residues -> Adler-Wiser
  eq:chi0_KS, retarded; contour integral checked by hand: gives Golze Eq. 28; the user trimmed the electron-hole
  pair sentence, the Strinati-3.26 sentence and the units bullet) and bullets (poles, static chi0 < 0, eq:chi0_G0
  time-ordered vs eq:chi0_KS retarded). The
  split chi0 = chi0^L + chi0^S from a block-diagonal G0 (no hybridization) was proposed but NOT written: keep for
  the substrate analysis. Eqs. 1-4 are written
  with explicit integrals over r' and the w argument (user, 2026-11-10: to see the structure of the operators); a
  "Compact notation" paragraph after the chi0 bullets then introduces the product shorthand (example chi0 v chi with
  the double integral) used from the Dyson equation on; Dyson (eq:dyson_chi, series as feedback);
  eps and eps^-1 (eq:eps; derivation spelled out, user 2026-11-10: Eq. 4 with rho_ind = chi phi_ext gives
  eps^-1 = 1 + v chi, with rho_ind = chi0 phi gives eps = 1 - v chi0, both read in the two directions; explicit
  r-space kernels delta +/- int v chi (chi0), delta = external potential, integral = Hartree of the induced charge;
  eps eps^-1 = 1 checked with Dyson; inverse kernels); W = eps^-1 v = v + v chi v = v + v chi0 W (eq:W), Sigma = iGW,
  dynamics, G0W0 = G0 and W from chi0; summary table (booktabs + array, ragged last column; rows G0, chi0, chi,
  eps, W); periodic systems (extended 2026-11-10 at the user's request, to see the dependence on w, q, G and
  bands, also in view of the chi0 split layer/substrate): expansion convention eq:A_qG
  A(r,r') = (1/V) sum_q sum_GG' e^{i(q+G)r} A_GG'(q) e^{-i(q+G')r'} (V = N_k Omega; products -> matrix products in
  G,G' at each q, w; v diagonal, v(k) = 1/(eps0 k^2)); Bloch states with plane-wave coefficients c_nk(G); G0 in the
  Bloch basis (eq:G0_bloch, diagonal in n k, plus G0_GG'(k,w) = sum_n c c* G0_nk); chi0_GG'(q,w) (eq:chi0_qG,
  (1/V) sum_k sum_nm (f_nk - f_mk+q) rho_nm(k,q,G) rho*_nm(k,q,G') / (w - (e_mk+q - e_nk) + i eta),
  rho_nm = <nk|e^{-i(q+G)r}|m k+q>; derived here from eq:chi0_KS with this convention) with bullets on w, q (momentum
  conservation, pair at k and k+q), G (Fourier components of the transition density), bands (summed, empty bands =
  convergence parameter); eps_GG', eps^-1_GG', W_GG' (eq:eps_W_qG) with bullets (matrix inversion per q, w; local
  fields; eps_M = 1/eps^-1_00 from Gatti slide 16; W has no band index; head diverges as 1/q^2; truncation for a
  layer in a supercell). Yambo's own storage convention (e.g. symmetrized v^1/2 chi v^1/2) NOT written: to verify on
  the Lumen source; "In the following" (Sec. 2 = layer + substrate, substrate only through vt; Secs. 3-5 = planar
  model, no local fields).
  Sec. 2 "Layer and substrate: separating the responses" (`sec:embedding`, written 2026-11-11 at the user's request,
  after Amblard 2024 Sec. II B, Eqs. 8-16 checked on the PDF): 2.1 general (`sec:embedding_general`): assumptions
  (no overlap of any KS state, occupied or empty -- the delicate point, to check on the explicit heterostructure;
  KS states of each subsystem = those of the subsystem alone; RPA; what matters is the subsystem of each state, not
  its energy: the user's idea of splitting by band index was discussed and dropped, levels interleave and the split
  is by pairs incl. empty states); chi0 = chi0^L + chi0^S (eq:chi0_split) derived from the Adler-Wiser sum (user
  2026-11-11): sum_nm split in four blocks LL, SS, LS, SL; mixed blocks vanish (transition density zero), chi0^L =
  same sum over pairs of the layer = chi0 of the free-standing layer, nonzero only for r, r' in the layer; G0
  argument kept as a bullet (the user later removed the bullets after eq:chi0_split); localization made precise
  (user's question 2026-11-11): each term of chi0^L has an occupied layer state at r and at r', so chi0^L vanishes
  outside the region of the layer's electrons even if empty states extend into vacuum (stated before eq:W_LL);
  no-overlap assumption reformulated: occupied states of one subsystem do not overlap with any state of the other; W^-1 = vt^-1 - chi0^L,
  vt^-1 = v^-1 - chi0^S (eq:W_inverse); vt = v + v_emb, v_emb = v chi^S v, chi^S = substrate alone (eq:vt_general;
  user 2026-11-11: v_emb defined at once, the separate "embedding term" paragraph and eq:vemb_general merged into the
  text after it: explicit integral over the substrate, chain reading, = v_reac of Amblard, static if the substrate
  gap >> layer gap); W = vt + vt chi0^L W (eq:W_layer); W in the layer closed on the layer: W = vt + vt chit^L vt, chit^L = chi0^L +
  chi0^L vt chit^L, eps~ = 1 - vt chi0^L (eq:W_LL, Amblard Eqs. 11, 15-16). Paragraph rewritten 2026-11-11 (user)
  as the result of the section: GW and BSE on the layer alone, substrate through vt; two changes vs free-standing
  (screening built with vt; vt also in the outer factors of W); what comes from each subsystem (layer: KS states,
  G0^L, chi0^L; substrate: v_emb); v -> vt only in W: ground state and bare exchange iGv unchanged, substrate in the
  correlation W - v = v_emb + vt chit^L vt. COH static subtlety and BSE exchange kernel (v or vt) deliberately left
  to the later GW/BSE part. Revised again 2026-11-11 (user): no "points in the layer" wording; the region is selected
  by products of layer states (occupied states in chi0^L; bound states of interest in the Sigma and BSE matrix
  elements); eq:W_LL now also shows vt = v + v_emb, v_emb = v chi^S v, so the two ingredients chi0^L and chi^S are
  visible. Sec. 2.1 makes no geometric assumption (general, as Amblard); geometry enters only in Sec. 2.2. 2.2 planar substrate
  (`sec:embedding_planar`): substrate z < 0, layer z > 0 around d; substrate Umklapp Q -> Q + G^S neglected (decay
  e^{-|Q+G^S| z}, |G^S| d ~ 10 for hBN at d ~ 3 A); mixed representation K(Q;z,z'); v(Q;z,z') = e^{-Q|z-z'|}/(2 eps0 Q);
  v_emb(Q;z,z';w) = -g(Q,w) e^{-Qz} e^{-Qz'}/(2 eps0 Q), g = -(1/(2 eps0 Q)) int int e^{Qz1} chi^S e^{Qz2}
  (eq:vemb_planar, derived here): rank one at each Q, static g > 0, dielectric half-space g = beta (eps_inf) gives
  eq:vt_sheet, g computable in the substrate's own cell; made self-contained on 2026-11-11 (in-plane expansion and
  v(Q;z,z') stated in place, no reference to the moved sections). 2.3 "Example: a dielectric half-space and an
  insulating layer" (`sec:embedding_example`, 2026-11-11, from the old Secs. 4-5): image construction in one sentence
  (details in models.tex), v_emb = -beta e^{-Q(z+z')}/(2 eps0 Q), i.e. g = beta; vt(Q) and eps_env (eq:vt_sheet);
  real-space vt with the image (eq:vt_real, the user's "Eq. 34", kept on purpose); limit bullets; Fig. `vt_ratio`;
  insulating layer: zero thickness, chi0^L(Q;z,z') = chi0(Q) delta(z-d) delta(z'-d), eq:W_LL reduces to numbers,
  chi0 = -Q^2 chi_2D, eps~ = 1 + r0 Q/eps_env, static Keldysh W (eq:W_keldysh).
  `Notes/models.tex` (companion notes, standalone, same header.tex, built separately with `latexmk -pdf models.tex`;
  created 2026-11-11 by moving the old Secs. 3-5 of main.tex unchanged, plus a short intro with units and the link
  g = beta to the main notes; numbering there: 1 = old Sec. 3, 2 = old Sec. 4, 3 = old Sec. 5). Its content:
  Sec. 3 "Charges in a plane: charge waves and their potential" (`sec:charge_wave`; read and found clear by the
  user): intro (units now in Sec. 1), finite sheet of area A with Born-von Karman conditions (discrete Q,
  limit A -> inf), lattice periodicity (N_c cells, Q = q + G_par, lattice fixes G_par and BZ, sheet size fixes the q
  grid; from here on the layer has a lattice; homogeneous plane = limit A_c -> 0); 3.1 charge waves (rho in charge
  waves, only Q = 0 carries net charge, point charge, periodic density sigma_Q = N_c sigma_G delta_{q,0}); 2.2
  potential of a charge wave (Poisson per wave, matching conditions, Q = 0 uniform plane and neutrality, Q != 0;
  the small-Q expansion of phi_Q and the remark on the 1/Q constant were removed by the user's request, 2026-11-10).
  Sec. 4 "The substrate: dressed Coulomb interaction" (`sec:image`): static local dielectric half-space; terminology
  (user, 2026-11-09): "sheet" = charged plane at z = d, "surface of the substrate" = z = 0; waves independent because
  eps depends only on z (substrate-lattice coupling Q -> Q + G neglected, stated); image construction; sigma_pol on
  the surface (eq:sigma_pol); phi_Q(d) = potential of the wave + that of the polarization charge (eq:phi_sheet);
  vt = v + v_emb with v(Q) = 1/(2 eps0 Q) and v_emb = -beta e^{-2Qd}/(2 eps0 Q), both explained (eq:vt_sheet);
  eps_env from vt/v; real-space vt from the images (short sentence, simplified by the user's request); limit
  bullets labelled short/long wavelengths and reduced to the essentials (user, 2026-11-09; real-space constant and
  metal dipole-dipole tail dropped).
  The (Q;z,z') forms v = e^{-Q|z-z'|}/(2 eps0 Q), v_emb = -beta e^{-Qz} e^{-Qz'}/(2 eps0 Q) were removed (user,
  2026-11-09): introduce them where finite thickness is treated.
  Sec. 5 "Screening by a polarizable layer on the substrate" (`sec:layer_screening`): opening rewritten (user,
  2026-11-09): in Sec. 4 the sheet charges feel vt but do not redistribute, now the layer polarizes too; zero
  thickness, local fields (Q -> Q + G mixing) neglected; 5.1 chi0 defined explicitly before eq:chi0_layer (response
  to the total potential, property of the layer alone, independent of the substrate, static chi0 < 0), then the
  external charge and the self-consistent potential; W = potential of a unit external wave, chit = response to the
  external potential vt sigma_ext (depends on the substrate); eps_sh = 1 - vt chi0, W = vt/eps_sh = vt + vt chit vt ("structure of the RPA with v -> vt");
  insulating layer chi0 = -Q^2 chi_2D, r0 = chi_2D/(2 eps0), static Keldysh W; 5.2 example: Lorentz oscillators,
  chi_2D = n alpha, single pole with finite damping eps^-1 = 1 + Omega_Q^2/(w^2 + i gamma w - w_L^2) (user,
  2026-11-10: no gamma -> 0 discussion), single-pole structure of the PPA (substrate moves position and weight via
  eps_env, not the width gamma), modes bullets; 5.3 summary. The "Discreteness" paragraph (single-oscillator image shift,
  lattice sums) and its summary bullet were removed (user, 2026-11-10): no main result depended on them.
  (End of the models.tex content.) The repetition of Secs. 1-2 in the old Sec. 5.1 is resolved by the move: main.tex
  keeps only the planar example (Sec. 2.3). The next step of main.tex is the 2D form (layer in a supercell: in-plane
  waves and box counting, to be taken back from models.tex Sec. 1 as needed; mixed representation; slab truncation;
  small-q behaviour).
  Bibliography restored (2026-11-10) with the first citations (Sec. 1): strinati1988application,
  blase2018introduction, golze2019gw, amblard2024static (entries copied from the catalogue without the
  doctype/keywords/file fields).
  Planned (user, 2026-11-09, not now): the analysis of the effect of the substrate in the GW language (v_emb =
  v chi^S v, link with the Blase-Duchemin papers and their "reaction field"), building on Sec. 1; the removed
  introduction (goal of the notes, chi0 = chi0^L + chi0^S, eq. vt = v + v chi^S v) is recoverable from git history.
  Figures: main.tex `fig:response` (TikZ, Sec. 1) and `vt_ratio` (make_figures.py, Sec. 2.3); models.tex
  `sheet_modes` (make_figures.py, both panels). Removed on 2026-11-09 at the user's request (recoverable from git history): figures
  `charge_wave_field` and `sheet_potential` (potential profiles of a charge wave above the substrate); the old section on the Coulomb interaction in the plane (point-charge Fourier
  transform, mixed representation, bullets on range, long wavelengths and polarization waves).
- `docs/`: working notes in markdown (context, literature, plans); `01_context_and_literature.md`,
  `02_python_route_yambo_databases.md` (python route on the Yambo databases; Sec. 4 = points to analyse in the
  computational step), `03_mppi_workflow_and_2D_convergence.md` (MPPI, clusters, convergence protocol),
  `04_benchmark_systems.md` (explicit vs effective GW benchmark: bilayer hBN first, other candidates, literature).
- Notebooks: to be created when the models/analysis start.

## Roadmap (provisional, to be agreed step by step)
1. Framing and literature (in progress): the three embedding papers (done, first reading); still to read: Neaton
   2006, Liu 2019 / Xuan 2019 (plane-wave substrate screening), QEH, G-Delta-W, Brunetti 2018/2019, Kim 2022/2024.
2. Theory: derive v_emb / g(Q,w) for a semi-infinite substrate (local, anisotropic, Q-dependent, dynamic); GW
   self-energy with vt (COH + SEX + renormalized screening of the layer); BSE kernel with vt; q -> 0 and truncation.
3. Simple models (python): image charge; Keldysh-type W(q) with eps_env(q) = [1 - g e^{-2qd}]^-1; Wannier–Mott / Dirac
   excitons; dependence on eps, d, layer screening r0; static vs dynamic substrate.
4. DFT: free-standing germanene (SOC); explicit germanene/hBN heterostructure to test the assumptions.
5. GW with substrate screening via modified Yambo databases (python): study of the database format on the source,
   then implementation and validation (see `docs/02_python_route_yambo_databases.md`). First benchmark (user,
   2026-11-11): bilayer hBN, explicit GW vs monolayer + second layer as effective substrate (`docs/04_...`).
6. BSE with the substrate-screened W; optical spectra, binding energies, gap/E_b compensation.
7. Full procedure, convergence, applications.

## Open points
- Physics target (layer and observables): to be defined during the analysis.
- Exchange kernel of the BSE with v or vt.
- Content and conventions of the Yambo screening databases: to be verified on the Lumen source (cluster) before any
  implementation.
- TO ANALYSE IN THE COMPUTATIONAL STEP (user, 2026-11-11, "very important"; details in `docs/02_...`, Sec. 4):
  (A) which Coulomb interaction goes where: v -> vt only in W; ground state and Sigma_x = iGv of the free-standing
  layer; substrate in the correlation W - v = v_emb + vt chit^L vt (last paragraph of Notes Sec. 2.1); how this maps
  onto Yambo's Sigma_x / Sigma_c split, the PPA and the static COH of v_emb, and the BSE kernel. (B) the Coulomb
  cutoff of the 2D supercell (layer in the xy plane, replicas at z = d + n L_z from the periodic boundary conditions,
  slab truncation along z): how to combine the truncated v with v_emb (single substrate, not replicated; position of
  the surface and of the images vs the box and the cutoff; Dyson with vt = v_cut + v_emb; head at q -> 0 and RIM).

## Rules
- Step by step, agreeing with the user before moving on. Explicit assumptions, units, limit checks (d -> 0,
  eps -> 1, eps -> inf, q -> 0).
- Notes style (user, 2026-11-06): physical explanations first; elementary math steps in one short clause, full
  derivations only for the non-trivial steps or when the user asks.
- Units (user, 2026-11-06): electrostatics in SI form with eps0 explicit, nabla^2 phi = -rho/eps0 (so
  v(r) = 1/(4 pi eps0 r), v(Q) = 1/(2 eps0 Q)); Hartree atomic units recovered with e = m = hbar = 4 pi eps0 = 1,
  i.e. 1/eps0 -> 4 pi (v(Q) -> 2 pi/Q). State the a.u. form where it helps the link with GW codes.
- Always separate what is verified (derived, or checked on the source) from what is an assumption or quoted from
  memory/sub-agent readings. Verify a literature formula on the PDF before using it in derivations or code.

## Notation
q, q_par in-plane wave vector; Q = |q + G_par| (bold Q the vector; Fourier components labelled by the vector,
sigma_Q, phi_Q(z), with box normalization (1/A) sum_Q over the area A); z out of plane; d layer–substrate distance; z_s substrate reference
plane; eps_s (eps_inf, eps_0) substrate dielectric function; g(Q,w) surface response function, beta = (eps-1)/(eps+1);
chi0, chi independent/interacting response; v bare Coulomb, v_emb embedding term (= v_reac, "reaction field", of the
Blase-Duchemin papers and of docs/; renamed by the user 2026-11-09), vt = v + v_emb dressed interaction; W screened
interaction; r0 = 2 pi chi_2D.

## Decision log
- 2026-11-05: project started; goal and roadmap drafted.
- 2026-11-05: user's context added (QE + Yambo/Lumen, MPPI, LiF-style workflow); target system germanene/hBN with
  mutual polarization only; three embedding papers read (first pass) -> `docs/01_context_and_literature.md`.
  CLAUDE.md switched to English (convention of the user's projects).
- 2026-11-05: decisions above (electronic response, python route on the Yambo databases, LiF-like organization);
  git repo, `Notes/` skeleton (introduction only, builds cleanly) and `docs/02_...` created.
- 2026-11-06: the user wants to understand the physics with simple classical models first (then GW formulas, then
  python/Lumen). Agreed sequence of models: A = sheet of oscillators above a static dielectric (neutral excitations,
  collective modes; shows that the optical mode is not shifted and that the substrate only dresses the Coulomb
  coupling); B = test charge in the sheet (quasiparticle-like image renormalization, screened by the sheet);
  C = electron-hole pair (exciton, gap/binding-energy compensation). Model A written in the notes (Sec. 2), to be
  discussed with the user before B and C.
- 2026-11-06: first comments of the user on Sec. 2.1: SI-form electrostatics (nabla^2 phi = -rho/eps0, applied to
  the whole Sec. 2); start from rho(r) written in the charge-wave basis; treat the Q = 0 term (net charge)
  separately; explain the jump condition on phi'. Sec. 2.1 rewritten accordingly, with the field-line figure
  `charge_wave_field`. Next: discuss the "features" bullets of Sec. 2.1 (range out of the plane, long wavelengths,
  polarization waves), then the rest of model A.
- 2026-11-06: further comments on Sec. 2.1: removed the az term and the finite-sheet remark; made explicit that
  sigma_0 = 0 follows from neutrality (electrons vs nuclei), not from periodicity (Q != 0 waves carry no net charge);
  crystal bullet now separates Q = G_par (average G_par = 0, modulation G_par != 0) from q != 0 (perturbations).
  For later: in a layer of finite thickness the G_par = 0 component is a profile rho(z) with zero integral
  (average potential across the layer; a step outside only if there is a dipole).
- 2026-11-06: box/lattice counting added to Sec. 2.1, very concisely and without a figure (user: do not drift from
  the goal of the notes): the box is a supercell of N_c cells; Q = q + G_par; the lattice fixes the G_par and the BZ,
  the box fixes the grid of allowed q (N_c points in the BZ, as many as the cells: the q grid of the codes); sigma_Q = N_c sigma_G delta_{q,0}; continuum limit
  sum_G int_BZ d^2q/(2pi)^2.
- 2026-11-09: the user found Sec. 2.1 clear and asked to reorganize: charges in a plane became Sec. 2 (with an intro
  on box/periodic conditions and lattice periodicity, then the layer is taken periodic), the substrate (vt) Sec. 3,
  the oscillator sheet Sec. 4. Our assessment, given to the user: the charge-wave description and vt / v_reac are the building blocks also of
  the later, extended model (ab initio layer response, finite thickness, g(Q,w), charged excitations).
- 2026-11-09: the user asked whether the oscillator model is still useful; agreed to keep it reframed and trimmed:
  Sec. 4 now starts from a generic layer response (substrate only through vt, eps = 1 - vt chi0, W = vt/eps; Keldysh
  for an insulating layer), with the oscillators as the single-pole example (link with the plasmon-pole
  approximation, relevant to the PPA issue in docs/02); the single-oscillator subsection was reduced to a paragraph
  and the depolarization-field equation removed. To add when we reach germanene: the Dirac-layer chi0 (proportional
  to -Q, Q-independent screening) and the crossover set by the small SOC gap (qualitative assessment, to verify).
- 2026-11-09: old Sec. 2.3 (Coulomb interaction in the plane) removed by the user's request; Sec. 3 made clearer:
  names the two planes (sheet at z = d, surface of the substrate at z = 0), explains why the waves stay independent,
  writes phi_Q(d) as the potential of the wave plus that of the polarization charge and defines vt from it.
  v_reac renamed v_emb ("embedding term") in the notes.
- 2026-11-09: introduction removed (user): the GW-language formulation (chi, v_emb = v chi^S v, papers) will be a
  later, dedicated section; the reference to v_emb = v chi^S v after eq:vt_sheet and in Sec. 3.1 removed too.
- 2026-11-10: new Sec. 1 (user's request): schematic definitions of chi0 (KS, IP), chi (Dyson), eps, W in r space,
  with the logic of Strinati's total classical potential and Blase's test charge; k, G forms deferred until needed.
  The old Secs. 1-3 are now Secs. 2-4. First draft, to be revised with the user. Committed (cafe2a0) before the
  chi0/G0 rewrite, at the user's request.
- 2026-11-10: chi0 part of Sec. 1 rewritten (user): Eq. 5 now defines the exact irreducible polarizability P,
  approximated in the RPA by chi0 = -i G0 G0 of non-interacting KS electrons; G0 introduced (relevant to GW and to
  the later substrate analysis); Adler-Wiser form obtained from the G0 G0 integral.
- 2026-11-10: public GitHub repository created at the user's request, name chosen by the user:
  2d-layer-substrate-effective-screening ("effective" kept on purpose); README.md rewritten as the public description
  of goals, approach and status.
- 2026-11-11: new Sec. 2 (embedding, layer + substrate) written after Sec. 1, at the user's request; old Secs. 2-4 are
  now Secs. 3-5. Agreed order for the next steps: link of the general v_emb with Sec. 4 (largely done: g = beta), 2D
  form of Sec. 1 (mixed representation, supercell, truncation, small-q behaviour), then revision of Sec. 5.1 and of
  the older parts. Sec. 1 now uses hbar = e = 1 in the many-body formulas.
- 2026-11-11: commit faae171 before restructuring (user). Old Secs. 3-5 moved unchanged to `Notes/models.tex`
  (companion classical models); main.tex now = Sec. 1 + Sec. 2 with a new example Sec. 2.3 (dielectric half-space,
  eq:vt_sheet, eq:vt_real, eps_env, limits, Keldysh W of an insulating layer); figure split: `vt_ratio` (main),
  `sheet_modes` (models). Sec. 2.2 made self-contained; it will be analysed in detail together with the computational
  step (user).
- 2026-11-11: move to the computational analysis (user). Benchmark candidates searched in the literature
  (docs/04): bilayer hBN chosen as the first test (cheap, same lattice, explicit QE+Yambo reference by Guo et al. 2020;
  the static limit does not hold there, which the user accepts: test of the general, dynamical scheme); then SnS2/hBN
  or MoS2/hBN; MoS2/SiO2 only as an application with g = beta. MPPI usage and the 2D convergence protocol of the
  user's MoS2 and germanene notebooks recorded in docs/03 (account names of Leonardo not copied: public repo).
- 2026-11-11: project folder moved by the user from THEORY to `SIMULATIONS\2d Layer Substrate Effective Screening`
  (memory copied to the new key); planned layout with one subfolder per system (hBN_bilayer first); cluster clone
  without spaces to be set up later.
- 2026-11-11: repository cloned on ismhpc in `~/work/2d-layer-substrate-effective-screening` (user's request).
