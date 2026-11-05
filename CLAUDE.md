# Effective screening — 2D layer on a bulk substrate (DFT -> GW+BSE): notes for Claude Code

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
- Local git repo (branch `main`, created 2026-11-05). No GitHub remote yet: create it only when the user asks.
- `Notes/`: technical notes, LaTeX, same style as LiF (`main.tex` with `\input{header.tex}`, notation macros in
  `header.tex`, `biblio.bib` with keys from the library catalogue `REFERENCES/_Catalog/library.bib`, bibtex unsrt).
  After each change build `Notes/main.pdf` in place with `latexmk -pdf` and check the log (errors, Overfull \hbox,
  undefined references); the PDF is not tracked. Do not refer to sections that do not exist yet.
- `docs/`: working notes in markdown (context, literature, plans); `01_context_and_literature.md`,
  `02_python_route_yambo_databases.md`.
- Notebooks: to be created when the models/analysis start.

## Roadmap (provisional, to be agreed step by step)
1. Framing and literature (in progress): the three embedding papers (done, first reading); still to read: Neaton
   2006, Liu 2019 / Xuan 2019 (plane-wave substrate screening), QEH, G-Delta-W, Brunetti 2018/2019, Kim 2022/2024.
2. Theory: derive v_reac / g(Q,w) for a semi-infinite substrate (local, anisotropic, Q-dependent, dynamic); GW
   self-energy with vt (COH + SEX + renormalized screening of the layer); BSE kernel with vt; q -> 0 and truncation.
3. Simple models (python): image charge; Keldysh-type W(q) with eps_env(q) = [1 - g e^{-2qd}]^-1; Wannier–Mott / Dirac
   excitons; dependence on eps, d, layer screening r0; static vs dynamic substrate.
4. DFT: free-standing germanene (SOC); explicit germanene/hBN heterostructure to test the assumptions.
5. GW with substrate screening via modified Yambo databases (python): study of the database format on the source,
   then implementation and validation (see `docs/02_python_route_yambo_databases.md`).
6. BSE with the substrate-screened W; optical spectra, binding energies, gap/E_b compensation.
7. Full procedure, convergence, applications.

## Open points
- Physics target (layer and observables): to be defined during the analysis.
- Exchange kernel of the BSE with v or vt.
- Content and conventions of the Yambo screening databases: to be verified on the Lumen source (cluster) before any
  implementation.

## Rules
- Step by step, agreeing with the user before moving on. Explicit assumptions, units (Hartree atomic units unless
  stated), limit checks (d -> 0, eps -> 1, eps -> inf, q -> 0).
- Always separate what is verified (derived, or checked on the source) from what is an assumption or quoted from
  memory/sub-agent readings. Verify a literature formula on the PDF before using it in derivations or code.

## Notation
q, q_par in-plane wave vector; Q = |q + G_par|; z out of plane; d layer–substrate distance; z_s substrate reference
plane; eps_s (eps_inf, eps_0) substrate dielectric function; g(Q,w) surface response function, beta = (eps-1)/(eps+1);
chi0, chi independent/interacting response; v bare Coulomb, v_reac reaction field, vt = v + v_reac; W screened
interaction; r0 = 2 pi chi_2D.

## Decision log
- 2026-11-05: project started; goal and roadmap drafted.
- 2026-11-05: user's context added (QE + Yambo/Lumen, MPPI, LiF-style workflow); target system germanene/hBN with
  mutual polarization only; three embedding papers read (first pass) -> `docs/01_context_and_literature.md`.
  CLAUDE.md switched to English (convention of the user's projects).
- 2026-11-05: decisions above (electronic response, python route on the Yambo databases, LiF-like organization);
  git repo, `Notes/` skeleton (introduction only, builds cleanly) and `docs/02_...` created.
