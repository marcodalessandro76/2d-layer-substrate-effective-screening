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
  (slownodes > 12 h; no node excluded in this project; THIS PROJECT: at most 2 nodes at a time, user 2026-11-11,
  i.e. num_tasks=2 for 1-node runs); default yambo = Lumen `bug-fixes` build since 2026-10-23.
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
  (`sec:embedding_planar`), REWRITTEN 2026-11-12 at the user's request (no generic kernel K; physical chain; figure):
  Title "Planar geometry" since 2026-11-12 (user: layer and substrate both infinite in the xy plane; it was "A planar
  substrate"; label unchanged). The opening of Sec. 2 no longer says that the planar substrate "simplifies the
  result" (user 2026-11-12): it says that the relations of Sec. 2.1 (eq:W_LL, the ones to implement) hold for any
  geometry and that the planar geometry enters only in Sec. 2.2. "What we compute" (added 2026-11-12, user: state the goal first; self-contained, without relying on models.tex):
  by Sec. 2.1 the substrate enters only through vt = v + v_emb = potential produced in the layer by a charge of the
  layer when the substrate polarizes and the layer does not (the layer's own polarization added afterwards by chi0^L
  in eq:W_LL); the charge of the layer decomposed in charge waves e^{iQ.r_par}, Q = q + G_par of the layer; question:
  how the potential of a charge wave changes in the presence of the substrate (v in vacuum, v_emb added); the answer
  closes the subsection after eq:vemb_planar: vt(Q;z,z';w) = v + v_emb, and for zero thickness
  vt(Q,w) = [1 - g e^{-2Qd}]/(2 eps0 Q) (displayed, unnumbered; g = beta gives eq:vt_sheet of 2.3);
  "Geometry" (substrate = slab -t < z < 0 of finite thickness t, e.g. a second layer, t -> inf semi-infinite: user
  2026-11-12, in view of the applications; it only sets the integration range; layer around z = d; assumption:
  the plane z = 0 separates the charges, chi^S nonzero only at z1, z2 < 0 incl. density tails = planar form of
  no-overlap; chain z' (layer) -> z2 -> z1 (substrate) -> z (layer)); Fig. `fig:planar` (TikZ in main.tex: (a)
  geometry and chain v chi^S v with the points z', z2, z1, z; (b) potential along z of a charge wave at z' = d, bare v
  dashed = incident wave in the substrate, v_emb solid = reflected wave, sketch Qd = 0.7, g = 0.7); "In-plane waves"
  (the definition of the charge waves and of Q = q + G_par moved to "What we compute"; chain in three bullets: v keeps Q,
  substrate answers at Q and Q + G^S, return decay e^{-|Q+G^S|(z-z1)}; G^S != 0 terms <= e^{-|G^S| d} by
  Q + |Q+G^S| >= |G^S|, ~1e-4 for hBN; layer sees a laterally averaged substrate; numbered eq:chiS_Q = expansion of
  chi^S diagonal in Q, which DEFINES chi^S(Q;z1,z2;w); then, in prose: mismatch, rotation, registry irrelevant, no
  strain/common cell; registry and moire only in the neglected terms, small also for commensurate lattices (user's
  question)); "The embedding term" (rewritten twice on 2026-11-12, user: first the bullets of the "Reflection of a
  potential wave" version, then the details between the v and g equations were too many): eq:v_Qz first = the in-plane
  Fourier transform of v, same expansion as eq:chiS_Q, exact (no Poisson derivation, no range discussion);
  then (user 2026-11-12) a paragraph stating that v_emb(r,r') is needed only with BOTH arguments in the layer (vt in
  eq:W_LL stands next to chi0^L or chit^L, or at the outer arguments of W, needed only in the layer), the integration
  points r1, r2 run over the substrate, and v_emb(Q;z,z') is the in-plane Fourier transform of v_emb with the same
  expansion as eq:chiS_Q (product of three Q-diagonal factors; in-plane integrals over r1, r2 select the same Q);
  eq:vemb_chain v_emb(Q;z,z') = int_{-t}^0 int_{-t}^0 v chi^S v for z, z' > 0; factorization in one line;
  eq:vemb_planar (integrals from -t to 0) with g = surface response function, cited as Pitarke et al.
  Rep. Prog. Phys. 70, 1 (2007) Eqs. (230)-(231) (`pitarke2007theory`; same expressions in a.u.: W = v - (2pi/q)
  e^{-q(z+z')} g, g = -(2pi/q) int int e^{q(z1+z2)} chi; verified 2026-11-12 on the arXiv version cond-mat/0611257
  through ar5iv, two reads; equation numbers of the arXiv version; the PDF is NOT in the REFERENCES library); then the
  incident/reflected-wave reading in prose; zero thickness z = z' = d: v_emb = -g e^{-2Qd}/(2 eps0 Q) (the user asked
  whether to assume zero thickness: kept general, it costs nothing and is needed for the G_z structure in Yambo);
  bullets: single function g (any structure and thickness); static g > 0; dielectric half-space g = beta, anisotropic
  eps -> (eps_par eps_perp)^(1/2) (derived); dielectric slab of thickness t: g = beta (1 - e^{-2Qt})/(1 - beta^2
  e^{-2Qt}) (derived 2026-11-12), -> beta for Qt >> 1, ~ (eps^2 - 1) Qt/(2 eps) -> 0 for Qt << 1: a thin substrate
  does not screen at long wavelengths (relevant to the hBN bilayer benchmark: the second layer is a thin substrate);
  general Q, w dependence; reference plane: z = 0 need not be the top of the substrate, moving it by z0 gives
  g e^{-2Qz0}, dielectric with surface at z_s has g = beta e^{2Q z_s}, real substrate -> Q dependence at small Q, the
  distance that matters is from the plane of the induced charge; g computable in the substrate's own cell. 2.3 "Example: a dielectric half-space and an
  insulating layer" (`sec:embedding_example`, 2026-11-11, from the old Secs. 4-5): image construction in one sentence
  (details in models.tex), v_emb = -beta e^{-Q(z+z')}/(2 eps0 Q), i.e. g = beta; vt(Q) and eps_env (eq:vt_sheet);
  real-space vt with the image (eq:vt_real, the user's "Eq. 34", kept on purpose; the sentence after it names the
  two terms as v and v_emb = v chi^S v = image term, i.e. the vt of eq:W_LL, user 2026-11-12); limit bullets; Fig. `vt_ratio`;
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
  doctype/keywords/file fields); pitarke2007theory (Sec. 2.2, 2026-11-12) is NOT in the library catalogue: entry
  written by hand from the arXiv page (DOI 10.1088/0034-4885/70/1/R01); add the PDF to REFERENCES if wanted.
  Planned (user, 2026-11-09, not now): the analysis of the effect of the substrate in the GW language (v_emb =
  v chi^S v, link with the Blase-Duchemin papers and their "reaction field"), building on Sec. 1; the removed
  introduction (goal of the notes, chi0 = chi0^L + chi0^S, eq. vt = v + v chi^S v) is recoverable from git history.
  Figures: main.tex `fig:response` (TikZ, Sec. 1), `fig:planar` (TikZ, Sec. 2.2) and `vt_ratio` (make_figures.py,
  Sec. 2.3); models.tex
  `sheet_modes` (make_figures.py, both panels). Removed on 2026-11-09 at the user's request (recoverable from git history): figures
  `charge_wave_field` and `sheet_potential` (potential profiles of a charge wave above the substrate); the old section on the Coulomb interaction in the plane (point-charge Fourier
  transform, mixed representation, bullets on range, long wavelengths and polarization waves).
- `docs/`: working notes in markdown (context, literature, plans); `01_context_and_literature.md`,
  `02_python_route_yambo_databases.md` (python route on the Yambo databases; Sec. 4 = points to analyse in the
  computational step), `03_mppi_workflow_and_2D_convergence.md` (MPPI, clusters, convergence protocol),
  `04_benchmark_systems.md` (explicit vs effective GW benchmark: bilayer hBN first, other candidates, literature).
- `pseudos/` (tracked): SG15 ONCV PBE scalar-relativistic v1.2 `B_ONCV_PBE-1.2.upf`, `N_ONCV_PBE-1.2.upf`
  (downloaded 2026-11-11 from quantum-simulation.org/potentials/sg15_oncv/upf/, no NLCC; user's choice: no SOC).
- RESULTS vs CALCULATIONS (user, 2026-11-13): the computational notebooks (DFT_Analysis, GW_Analysis, ...) are the
  lab book (runs, convergence, checks); each ends with an "Export of the reference results" section that writes small
  JSON files in `<system>/results/` (TRACKED in git; metadata block with description, units, source runs, date;
  energies in eV rounded to 0.1 meV; helper `write_json` keeps number lists on one line). `<system>/Results.ipynb`
  (one per system, DFT + MB together) builds its tables and figures ONLY from these JSON files (numpy + matplotlib,
  no MPPI, no run folders: runs on the laptop too); it is short, physics only, and the base for the notes and for the
  figures of a paper (the JSON files are the data to share). hBN_bilayer (2026-11-13): `dft_ground_state.json`
  (parameters, lattice, atoms of the 5 systems, energies, gaps on the k = 12 grid), `dft_bands.json` (KS bands
  ML_bot/AA1/AB on G-M-K-G, 181 k, from the VBM on the path), `dft_layer_character.json`; Results.ipynb sections:
  systems/setup + 3D perspective plot of the stackings (bottom and top planes with dashed hexagons, one top hexagon projected vertically: AA' B over N and N over B, AB B over N and N over hexagon centres; user 2026-11-13), DFT ground state, DFT bands (+ ML vs BL overlay, band edges at G/M/K), layer
  character, GW bands (user 2026-11-13: one panel per system DFT vs GW with the exact grid points, then GW ML vs AA'
  and ML vs AB, gap table) from `gw_bands.json` (KS and QP bands on the path, zero at the KS VBM of the k = 18 grid,
  exact QP at the 17 grid points on the path). gw_bands.json written so far (ML, AA') by the code of the future
  GW_Analysis section, run as a script (scratchpad `gw_export_cells.py`) while nbconvert executes GW_Analysis: insert
  those cells in GW_Analysis when nbconvert ends and AB is done, re-run, re-export (same content + AB).
- `hBN_bilayer/DFT_Analysis.ipynb` (created 2026-11-11, NOT yet run; setup cells dry-checked): calculator factory
  `qe_code()` (all12h, 16 MPI x 2 OMP, qe_module, BeeOND, no exclude), `hbn_positions(system)` for the bilayers
  'AA1' (AA'), 'AB' and the monolayers 'ML' = 'ML_bot' (bottom layer alone), 'ML_top_AA1', 'ML_top_AB' (top layer of
  each bilayer alone, in its own position: chi0 of layer and substrate directly from Yambo, no rotation/translation
  of the databases; AA' top = bottom rotated by 180 deg, AB top = bottom translated in plane),
  `build_input(system, ecut, k, c)`; sections: ML ecut x k (k 9-18, ecut 50-100 Ry), alat scan (check only),
  cell height c on ML and AA' (30-50 bohr), DFT-D3 scan of d (check only), converged scf of the 5 systems
  (prefix `gs_converged-<system>`), bands G-M-K-G (ML_bot, AA1, AB; prefix `bands-<system>`) and ML vs BL overlays,
  AB with dipole correction (check: AB has an out-of-plane dipole, C3v, not in the effective scheme; AA' is D3d),
  nscf for Yambo (placeholder). Run folder `DFT_analysis/` (5.5 GB, on /work = BeeGFS, not in the home quota).
  RUN AND COMPLETED 2026-11-11 (executed in place with nbconvert; results in markdown cells). Converged: ecut 80 Ry,
  k 12x12x1, c = 40 bohr (gaps within 1 meV; gap at Gamma, NFE state, within 2.4 meV); PBE a = 2.508 A (check);
  PBE+D3 d = 3.44 A for both stackings (check). PBE gaps: ML 4.714 eV direct at K (CB at Gamma, NFE, within 1 meV);
  AA' 4.541 (K->M), direct 4.765; AB 4.536 (K->M), direct 4.585. At K the AA' states stay degenerate (direct gap
  +22 meV vs ML); AB splits them by 0.11/0.16 eV; at M and Gamma pi* and NFE states hybridize (splittings 0.5-0.67 eV,
  CBM moves to M): the bilayer gap reduction is a DFT hybridization effect. => The no-overlap assumption holds at K
  (AA'), fails for conduction states at M/Gamma: compare explicit vs effective GW on the QP corrections at K, AA'
  first. AB dipole 0.0155 D/cell, dipole correction changes gaps by 5-8 meV: negligible, databases without it.
  k check on the bilayers (k = 6, 12, 18, 24, grids with K and M; user's request): energy converged from k = 12; AB
  gaps stable; AA' gaps drop at k = 24 (-15/-29 meV) because the AA' VBM is off K (0.033 2pi/a towards Gamma, 29 meV
  above K) and the minimum direct gap too (4.709 eV, on M-K): k = 12 kept; compare quantities AT K.
  Benchmark logic (agreed with the user, 2026-11-11): the effective scheme keeps the KS states of the free-standing
  layer, so it cannot reproduce the DFT ML -> BL differences (hybridization); its target is the GW correction
  (QP - KS) from the screening of the second layer, compared at K. AA' and AB: the effective scheme gives almost the
  same result for both (registry only in the G_par != 0 terms of v chi^S v, ~ e^{-|G_par| d}); AA' = clean test of
  the scheme, explicit AA' vs AB = size of the stacking/hybridization effect at K that the scheme misses.
  NSCF + SAVEs (2026-11-11, user's choices): ML_bot k = 18, 30, 42 with 250 bands; AA1, AB k = 18 with 400 bands
  (other grids and ML_top_* after the first GW runs); prefix `kpoints_<k>-nbnds_<n>-<system>`; diagonalization `cg`
  (Davidson stopped with "S matrix not positive definite"; cg leaves 1-5 eigenvalues per k slightly above the very
  tight threshold, gap at K identical on the three grids). Band windows: 250 bands reach ~100 eV above the VBM, 400 in
  the bilayer ~130 eV (at high energy the states are vacuum NFE states, set by the cell VOLUME, the same for ML and BL:
  the bilayer does NOT need twice the bands for the same window, only 4 more). SAVEs in `MB_analysis/<prefix>/` built
  by `GW_Analysis.ipynb` with `Tools.init_yambo_dir`, p2y + setup directly on the login node, 1 MPI 1 OMP (user;
  `srun p2y` hangs at start-up). Yambo symmetries: 12 for all (ML_bot and AB: 6 spatial + T-rev, the ML sigma_h is lost
  because the layer is off z = 0 and force_symmorphic drops it; AA1: 12 spatial, D3d).
  GW settings (user, 2026-11-11): CUTGeo='slab z' and RIM on v in every run (RandQpts 5e6, RandGvec 100, from MoS2);
  HF with RIM only; every GW (PPA) run with RIM_W, RandGvecW = 10.
  SHARED YAMBO DATABASES (user's rule, 2026-11-11): yambo writes new databases only in the FIRST folder of the -J
  list and reads from all of them. Runs that share databases (RIM/cutoff, HF, screening em1d, dipoles, ...) are
  organized so that the FIRST run completes alone; then the common databases are moved into a separate folder
  (e.g. `ndb_rim_cutoff`, `ndb_em1d-ngsblkxp_<x>-bndsrnxp_<n>`) and that folder is passed in the `jobname` list of
  the other runs; never let two concurrent runs compute the same database. (RIM: a dedicated `yambo -r` run with
  name/job `ndb_rim_cutoff` writes directly in the shared folder.) HF parallelism: `SX_ROLEs='q.qp.b'`, the role b
  has only as many elements as the highest corrected band: put the MPI on q and qp (e.g. SX_CPU='8.4.1').
  HF on ML_bot, k = 18 (2026-11-11): Sx converged at 40 Ha (states within 3 meV); with EXXRLvcs = VXCRLvcs the
  results drift above 40 Ha because the TRUNCATED Vxc is cutoff dependent (NFE conduction state at Gamma: 0.2 eV).
  Choice (user): EXXRLvcs = VXCRLvcs = all the density G vectors (24949 RL, default): Vxc is then the KS one (not a
  convergence parameter; differs from the MoS2 protocol EXX = VXC); EXX full = EXX 40 Ha within 0.3 meV, 17 s per HF
  run at k = 18. HF gaps (k = 18): K 13.321 eV, Gamma 12.863 eV.
  HF vs k (ML_bot, full cutoffs, RIM per grid in `ndb_rim_cutoff`): gap at K 13.321 / 13.335 / 13.338 eV, at Gamma
  12.863 / 12.871 / 12.873 eV for k = 18 / 30 / 42 (3.5 and 2 meV from 30 to 42): HF analysis done.
  GW PPA (GW_Analysis.ipynb, 2026-11-12): input from `yambo -r -rw -k hartee -dyson n -gw0 p -V all` (the RIM_W
  runlevel MUST be in the command: with `inp.activate_RIM_W()` only, the MPPI reformat drops RIM_W and RandGvecW;
  RandGvec/RandGvecW rounded by yambo to 101/11 RL); LongDrXp [1,1,0]; PPAPntXp default 27.2 eV; parallel
  X_and_IO_CPU 1.1.4.8.1 (q.g.k.c.v), DIP_CPU 4.8.1, SE_CPU 2.2.8 (q.qp.b). The PPA screening database is `ndb.pp`
  (+ fragments), not `ndb.em1d`: shared folders `ndb_pp-ngsblkxp_<x>-bndsrnxp_<n>` hold `ndb.pp*` and `ndb.RIM_W`.
  RULE (user, 2026-11-12): in every convergence run the QP corrections are computed ONLY at the checked points
  (Gamma and K, bands 4-5: two `QPkrange` rows, `inp['variables']['QPkrange'] = [[[1,1,4,5],[37,37,4,5]], '']`);
  full-IBZ QP only for production runs (Sigma for the 74 IBZ states was 71 of the 93 min of the 6 Ha run).
  RULE (user, 2026-11-13): before every full-IBZ QP run ASK the user how many bands to correct (decided system by
  system; Sigma cost ~ number of states). For hBN the plots show 3 valence + 3 conduction bands per layer (ML 2-7,
  BL 3-14; the ML run has 2-8); in a bilayer count per layer and do not split degenerate pairs.
  NGsBlkXp scan (BndsRnXp = GbndRnge = 250, k = 18): gap at K 7.228 / 7.221 / 7.263 / 7.265 eV, at Gamma
  7.795 / 8.010 / 8.161 / 8.182 eV for 2 / 4 / 6 / 8 Ha (K converged from 6 Ha; Gamma moves by 21 meV 6 -> 8 Ha
  through the deep valence state; Ec(Gamma), NFE, within 1 meV; indirect K -> Gamma ~6.54 eV). Choice (user):
  NGsBlkXp = 6 Ha (10 Ha run cancelled, 12 Ha only if needed).
  BndsRnXp scan (6 Ha, GbndRnge 250): gap at K 7.278 / 7.265 / 7.264 / 7.263 eV for 100 / 150 / 200 / 250 (converged
  from 150; single QP energies at K still shift ~18 meV 200 -> 250, cancelling in the gap). Choice (user): 200.
  GbndRnge scan (BndsRnXp 200; 100-250): without terminator the gap at K grows by 16 meV 200 -> 250 (slow 1/N); with
  the BG terminator (`GTermKind='BG'`, default GTermEn) it converges from above: 7.362 / 7.344 / 7.337 / 7.335 eV,
  2.6 meV 200 -> 250, consistent with the a + b/N extrapolation (7.32-7.33) of the runs without terminator: no nscf
  with more bands needed. Choice (user): GbndRnge = 200 + BG. Runs that only change Sigma read the screening from
  `ndb_pp-ngsblkxp_6.0-bndsrnxp_200` (2-5 min each, two at a time).
  RandGvecW scan (1, 10, 20, 30 -> 1, 11, 25, 37 RL): 10 converged (< 0.5 meV to 30), 1 RL (head only) off by 60 meV.
  Yambo reuses a shared `ndb.RIM_W` with MORE components than requested (first components; element-wise integral, so
  exact: checked) and recomputes it in the run folder (`*ERR* Screening RL components`) when MORE are requested.
  k grid (nscf at k = 24 added, 6 min): GW gap at K 7.337 / 7.334 / 7.336 eV, at Gamma 8.315 / 8.313 / 8.315 eV for
  k = 18 / 24 / 30 (no trend, no extrapolation; single QP energies at K within 2-4 meV; HF gap +14 meV 18 -> 30,
  compensated by the correlation): k = 18 is enough with RIM_W, 42 not needed. Costs (1 node): GW 27 min (k = 18),
  1 h 14 min (24), 2 h 30 min (30), dominated by Xo ~ N_q(IBZ) x N_k(BZ). HF at k = 24: gap at K 13.329 eV.
  CONVERGED GW PARAMETERS (ML_bot, 2026-11-12): k = 18, NGsBlkXp = 6 Ha, BndsRnXp = 200, GbndRnge = 200 + BG,
  RandGvecW = 10 RL, RIM 5e6/100, EXXRLvcs = VXCRLvcs = all G; GW gap at K 7.337 eV (KS 4.714), at Gamma 8.315 eV,
  indirect K -> Gamma 6.668 eV. Run of reference: `kpoints_18-nbnds_250-ML_bot/pp-ngsblkxp_6.0-bndsrnxp_200-gbndrnge_200-bg`.
  With BG the absolute ML gap at K rises by 20 meV from 6 to 8 Ha (7.339 -> 7.359, 250 bands; without BG +2 meV):
  ~20 meV uncertainty on absolute gaps, none on BL - ML differences (below).
  ML_top_AA1, ML_top_AB (2026-11-13): nscf k = 18, 250 bands, SAVE, GW at the converged parameters: reproduce ML_bot
  within 0.5 meV (geometry check passed); screening in `ndb_pp-ngsblkxp_6.0-bndsrnxp_200` of each folder (database
  for the embedding still to choose: ndb.pp holds the PPA eps^-1, not chi0).
  BILAYERS: bands chosen for the SAME energy window as ML (KS states below the mean energy of ML band n at k = 18):
  ML 200 -> BL 212, ML 250 -> BL 262 (the second layer adds ~8-12 layer bands up to 40-90 eV, not only 4). QP bands
  7-10 (16 electrons). AA' checks (k = 18, BG): (6 Ha, 212), (6 Ha, 262), (8 Ha, 262) vs ML (6, 200), (6, 250),
  (8, 250): BL - ML QP corrections at K v +0.170 / +0.171 / +0.172, c -0.200 / -0.198 / -0.198, gap correction
  -0.370 / -0.369 / -0.369 eV (converged within 2 meV; absolute corrections move by up to 50 meV, equally in BL and ML).
  GW gap at K: AA' 7.018 vs ML 7.337 eV (-0.319 = -0.370 GW + 0.051 KS). Choice: bilayers at 6 Ha, 212 bands, BG.
  Costs (1 node): 43 min, 1 h 02 min, 1 h 52 min.
  AB GW (6 Ha, 212, BG; 53 min): states at K split already in KS (valence 0.113, conduction 0.157 eV); QP corrections
  at K b7..b10 = -1.118 / -1.127 / +1.062 / +1.083 eV (AA' -1.150 / -1.149 / +1.104 / +1.105, ML -1.320 / +1.304):
  BL - ML v +0.19/+0.20, c -0.22/-0.24 eV (AA' +0.17, -0.20): the stacking changes the substrate effect on the single
  corrections by 20-40 meV. GW gap at K: AB 6.774 (KS 4.585), AA' 7.018 (KS 4.765), ML 7.337 (KS 4.714); at Gamma
  8.010 / 8.064 / 8.315 eV. Explicit side of the benchmark at k = 18 complete (ML_bot, ML_top_AA1, ML_top_AB, AA', AB).
  LAYER CHARACTER (2026-11-13, DFT_Analysis.ipynb, `DFT_analysis/layer_character/`): projwfc.x is unusable (SG15 ONCV
  pseudos have no atomic wavefunctions); used pp.x plot_num = 7 (|psi_nk|^2, nscf k = 18) + average.x along z,
  weight in z < 0 (bottom) vs z > 0 (top). AB at K: b7, b9 on the bottom layer, b8, b10 on the top (98-99%): the KS gap
  b9 - b8 is INTERLAYER; layer gaps at K: bottom b9 - b7 (KS 4.697, GW 6.878), top b10 - b8 (KS 4.741, GW 6.952). AB at
  Gamma: valence pair b7, b8 on the top layer, NFE conduction states on both. AA': degenerate pairs, 50/50 (equal
  corrections within 1 meV, any combination has the same correction). Layer-resolved gap correction BL - ML at K:
  AA' -0.370; AB bottom -0.444 (v +0.202, c -0.242), top -0.414 (v +0.193, c -0.221) eV: stacking effect 45-75 meV,
  what the effective scheme (same result for both stackings) misses.
  QP BAND STRUCTURES (2026-11-13, user: standard method): full-IBZ QP runs at k = 18 (converged parameters, bands
  2-8 ML, 3-14 BL; `<converged name>-full_ibz-b<b0>_<b1>`, SE_CPU 1.32.1; 1 node: ML 3 h 20 min, AA' 4 h 50 min, AB
  ~5 h; Sigma dominates) + ypp `-s b` BOLTZ with `CIRCUIT_E_DB_path` = SAVE of the pw.x bands run made with
  `p2y -nowf` (`MB_analysis/bands_path-<system>`, 40 kB): ypp interpolates only dE = E - Eo (checked in the source,
  FILL_SEED_E) and adds it to the exact KS bands of the path. Direct interpolation of the energies is NOT usable for
  hBN: 200-300 meV errors at the band crossings (pi/sigma, pi*/NFE), independent of INTERP_Shell_Fac. ypp output with
  QP carries a RIGID offset (alignment of the circuit DB on the first band at the first k; 592.5 meV ML, 390.6 meV
  AA'): remove it by matching the QP top valence at K to the yambo o-*.qp value; then ypp = yambo within 0.1 meV at K
  and 4 meV at Gamma. dE of the conduction bands jumps between pi* (+1.1-1.3 eV) and NFE (+0.5-0.6 eV) states: between
  grid points near crossings the interpolation can be off by 0.2-0.3 eV (plot the exact grid points). Results: ML GW
  gap K 7.338, Gamma 8.312, fundamental K -> Gamma 6.666 eV; AA' K 7.018, Gamma 8.062, fundamental 6.449 eV (VBM near
  K -> Gamma; in DFT the CBM is at M, GW moves it to the NFE state at Gamma). AB pending (job 60900).
  Next: embedding, starting from the choice of the Lumen database that gives chi0 of ML_bot and ML_top
  (docs/02 Sec. 4).

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
- LAYER-PROJECTED BAND STRUCTURE OF THE FULL SYSTEM (user, 2026-11-13, "fundamental point"): the effective scheme
  describes ONLY the states of the layer (KS states of the free-standing layer + QP corrections with vt); the full
  system (bilayer, in general layer + substrate) also has the substrate states. In the bilayer each ML band appears
  twice, one copy per layer; the splittings between the copies come from hybridization (M, Gamma: 0.5-0.67 eV in DFT)
  or from inequivalent layers (AB at K: 0.11/0.16 eV in DFT), both ground-state effects outside the scheme by
  construction. Hence (user): to compare the ML bands corrected with v_emb with the full system, the band structure
  of the full system must be PROJECTED on the states of the layer. Our assessment (to discuss and verify):
  (i) justification: under no overlap, Sigma_nn = <n|iGW|n> for a layer state has no contribution from the substrate
  states of G (overlap densities psi^L* psi^S = 0), so Sigma = i G^L W with W from chi0^L + chi0^S: the scheme is exact
  (within G0W0 + no overlap) for the layer states, i.e. half of the bilayer bands; not yet written in the notes;
  (ii) projections: (a) spatial layer weight w_nk = int_layer |psi_nk|^2 along the whole path (fat bands; so far only
  at G and K, pp.x + average.x); (b) overlap with the ML states in the same cell, P_nk(m) = |<psi^ML_mk|psi^BL_nk>|^2
  (ML_top_* are computed in the exact position of each layer: same cell, cutoff, k grid; gives also which ML band m
  each bilayer state comes from); in G0W0 the QP states are the KS ones, so the KS weights also project the QP
  bands; (iii) for hybridized pairs (weights ~0.5, M and Gamma) the comparable quantity is probably the weighted
  mean (first moment of the layer-projected spectral function A_L(k,w) = sum_n w_nk delta(w - E_nk)): to verify;
  (iv) for a real substrate (germanene/hBN, possibly a mismatched supercell) the projection must be combined with
  band unfolding to the BZ of the layer (Ku, Berlijn, Lee PRL 104, 216401 (2010), read on arXiv; Popescu-Zunger PRB
  85, 085201 (2012), citation only). Method and implementation (python on the QE wavefunctions vs QE/yambo tools) to
  decide with the user.
  Literature (2026-11-13, web search by a sub-agent; the items marked "checked" were read by Claude on the arXiv
  text): Liu, JCP 152, 054103 (2020) (checked): Eq. 2, <phi_tot|Sigma[G_tot W_tot]|phi_tot> ~ <phi_mol|Sigma[G_tot
  W_tot]|phi_mol> ("molecular projection", Tamblyn et al. PRB 84, 201402 (2011)) ~ <phi_mol|Sigma[G_mol W~_tot]|phi_mol>
  (embedding), the last step dropping the substrate terms of G under small overlap = our point (i); interface state
  identified by the largest |<phi_tot|phi_mol>|^2. Xuan, Chen, Quek, JCTC 15, 3824 (2019) (checked): graphene/hBN,
  full GW vs the component-wavefunction scheme (XA(noF), our type): at K (states fully on hBN) within 0.1 eV; at Gamma
  (CBM 66% on hBN) off by 1.3 eV (6.33 vs 7.59 eV), and at short distance most of the error is the DFT gap: same
  picture as our bilayer (compare at K). Amblard et al. JCP 160, 154104 (2024) (read on the PDF): reference = fully
  dynamical FRAGMENT-embedded GW, no full-system GW; compared quantities = polarization energies (shift of HOMO/LUMO/
  gap from the gas phase); for C60 at the crystal surface the fragment scheme gives the PEAK-TO-PEAK gap (centres of
  the HOMO/LUMO bands, no band formation from overlap) -> supports the first moment for hybridized states. Others
  (sub-agent, not checked by Claude): Chen-Weinert PRB 98, 245421 (2018) layer k-projection with a z window; Reho et
  al. PRB 110, 035118 (2024) layer-projected GW bands of MoS2/WS2 with QE+Yambo; Winther-Thygesen G-Delta-W 2D Mater.
  4, 025059 (2017) and Leon...Thygesen PRB 112, 115128 (2025) add the DFT hybridization of the full system separately
  (E_DFT(HS) - E_DFT(ML)) to the screening correction; Naik-Jain PRM 2, 084002 (2018) overlaps with the free-standing
  layer states. Our note: the first moment sum_n |<phi_ML|n>|^2 E_n = <phi_ML|H|phi_ML> exactly (KS), and for QP with
  Sigma diagonal in the KS basis it is Liu's molecular-projection quantity.
  CONCLUSIONS AND PLAN (Claude, 2026-11-13, user: "record them"): (1) projection by OVERLAP with the ML states is the
  method of choice: it maps each full-system state onto the layer state of the effective scheme and gives at the same
  time the weighted (fat) bands and the comparable quantity also for hybridized states; the spatial z-window weight
  only as a check; no unfolding for bilayer hBN (lattice matched), needed for germanene/hBN. (2) For the hBN bilayer:
  overlaps |<psi^ML_mk|psi^BL_nk>|^2 with the states of ML_bot (bottom layer) and ML_top_AA1 / ML_top_AB (top layer),
  already in the same cell, cutoff and grid (path: bands runs of ML_top_* still to do, QE runs to ask). (3) Benchmark
  quantities: (a) QP corrections of the states with layer weight ~1 (K): the quantity compared in all the
  explicit-vs-effective works (Liu, Xuan, Neaton); (b) for hybridized states (M, Gamma) the first moment of the
  layer-projected spectral function, i.e. <phi_ML|H_QP|phi_ML> (Liu's molecular projection, Amblard's peak-to-peak
  centres), to compare with the effective QP level; (c) plots of the full-system KS and GW bands weighted by the
  projection on the layer, over the ML/effective bands. (4) Expectation from Xuan et al.: agreement within ~0.1 eV at
  K, large deviations at Gamma dominated by the DFT hybridization (outside the scheme by construction).
  Kept arXiv PDFs (user, 2026-11-13; the others deleted): 1903.01847 (Xuan 2019), 1912.00875 (Liu 2020), 2404.17182
  (Reho 2024), 1002.4218 (Ku 2010), 1409.5343 (Medeiros 2015), 2505.17292 (Leon...Thygesen 2025), in the session
  scratchpad `/tmp/claude-1125/-work-dalessandro-2d-layer-substrate-effective-screening/d4b43a65-a94d-4243-bb4f-d8560dfd42f0/scratchpad/pdfs_lit`
  (temporary, not tracked): the user copies them with scp to the laptop REFERENCES library.
- Physics target (layer and observables): to be defined during the analysis.
- Exchange kernel of the BSE with v or vt.
- Content and conventions of the Yambo screening databases: to be verified on the Lumen source (cluster) before any
  implementation.
- Slab cutoff checked on the Lumen source (2026-11-11, docs/02 Sec. 4 B): `cutoff_slab.F` = Ismail-Beigi/Rozzi,
  v_cut = 4pi/|q+G|^2 [1 - e^{-Q L/2} cos(G_z L/2)], truncation in z - z' (translation invariant: no centring issue,
  layer position in the cell irrelevant); condition: whole system (both layers) within L/2 = 10.6 A for c = 40 bohr:
  CHECKED on the planar density (bilayer density < 1e-4 max beyond |z| = 4.7 A; pairs at |z-z'| > L/2 ~ 1e-10): safe.
  Method (user, 2026-11-11: QE tools, one clean way): pp.x (plot_num 0) + average.x (dir 3), driven from
  DFT_Analysis.ipynb (`run_density_profiles` writes inputs and a slurm job, `sbatch --wait`, skips existing
  `avg_<system>.dat`; `read_density_profile`), folder `hBN_bilayer/DFT_analysis/density_profile/`. QE PP tools built
  2026-11-11 at the user's request (~/sysadmin/CLAUDE.md); with Intel MPI use `average.x -inp`, window > 0. RIM_W only with slab; it replaces the static W - v
  for EVERY q and G, G' <= RandGvecW by the q-cell average of v f v/(1 - v f) (bare v_cut, f = element-wise chi0
  extracted from the database), also in the BSE (checked 2026-11-12, docs/02 Sec. 4 B). Fine for explicit runs and for
  a database in standard form with chi0 = chi0^L + chi0^S in the same cell (hBN benchmark); inconsistent with a
  vt-based database (planar g(Q) substrate): there RIM_W off + q average in python, or an equivalent chi0^S. `EpsEnv` input = uniform v -> v/eps_env
  everywhere (also Sigma_x): not our vt.
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
- 2026-11-12: Sec. 2.2 rewritten (user: the generic kernels were never introduced and the section was hard to read):
  physical chain layer -> substrate -> layer, g as the reflection coefficient of potential waves, schematic figure
  `fig:planar`; Sec. 2.3 now calls the image potential the reflected wave of Sec. 2.2. Same day (user): the embedding
  term rebuilt explicitly from v chi^S v (no bullets), g cited from Pitarke et al. 2007; substrate of finite thickness
  t (slab -t < z < 0), with the dielectric-slab g as an example.
- 2026-11-11: move to the computational analysis (user). Benchmark candidates searched in the literature
  (docs/04): bilayer hBN chosen as the first test (cheap, same lattice, explicit QE+Yambo reference by Guo et al. 2020;
  the static limit does not hold there, which the user accepts: test of the general, dynamical scheme); then SnS2/hBN
  or MoS2/hBN; MoS2/SiO2 only as an application with g = beta. MPPI usage and the 2D convergence protocol of the
  user's MoS2 and germanene notebooks recorded in docs/03 (account names of Leonardo not copied: public repo).
- 2026-11-11: project folder moved by the user from THEORY to `SIMULATIONS\2d Layer Substrate Effective Screening`
  (memory copied to the new key); planned layout with one subfolder per system (hBN_bilayer first); cluster clone
  without spaces to be set up later.
- 2026-11-11: repository cloned on ismhpc in `~/work/2d-layer-substrate-effective-screening` (user's request).
- 2026-11-11: hBN_bilayer DFT setup agreed (user): `hBN_bilayer/` with DFT_Analysis/GW_Analysis notebooks and
  untracked run folders; SG15 ONCV PBE SR pseudos (no SOC); SAME alat for ML and BL (experimental bulk a = 2.504 A;
  PBE scan only as a check) and same ecut, k, cell height; d = 3.33 A fixed (Guo et al.), D3 scan only as a check;
  bilayer centred at z = 0 (layers at +-d/2), monolayer at z = +d/2 (= top layer; "substrate" = bottom layer);
  centring of the yambo slab cutoff to check on the Lumen source before GW. RunRules: all12h for DFT, slownodes for
  GW if needed; `exclude='wnode07'` dropped. AB stacking defined as top B over bottom N, top N over hexagon centre:
  to check against the AB variant of Guo et al. Monolayers computed in the exact position of each layer of each
  bilayer (ML_bot, ML_top_AA1, ML_top_AB). The user authorised Claude to run autonomously all the DFT runs needed
  to complete hBN_bilayer/DFT_Analysis.ipynb (at most 2 nodes at a time).
