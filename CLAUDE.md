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
  Figures: `Notes/make_figures.py` (registry `FIGURES`, run from `Notes/` with the miniconda python, saves jpeg in
  `Notes/Figures/`, included with `\includegraphics{Figures/<name>.jpeg}`).
  State (2026-11-09; the introduction was removed by the user's request, so the sections start at 1):
  Sec. 1 "Charges in a plane: charge waves and their potential" (`sec:charge_wave`; read and found clear by the
  user): intro with quasi-static limit and units, finite sheet of area A with Born-von Karman conditions (discrete Q,
  limit A -> inf), lattice periodicity (N_c cells, Q = q + G_par, lattice fixes G_par and BZ, sheet size fixes the q
  grid; from here on the layer has a lattice; homogeneous plane = limit A_c -> 0); 1.1 charge waves (rho in charge
  waves, only Q = 0 carries net charge, point charge, periodic density sigma_Q = N_c sigma_G delta_{q,0}); 1.2
  potential of a charge wave (Poisson per wave, matching conditions, Q = 0 uniform plane and neutrality, Q != 0).
  Sec. 2 "The substrate: dressed Coulomb interaction" (`sec:image`): static local dielectric half-space; terminology
  (user, 2026-11-09): "sheet" = charged plane at z = d, "surface of the substrate" = z = 0; waves independent because
  eps depends only on z (substrate-lattice coupling Q -> Q + G neglected, stated); image construction; sigma_pol on
  the surface (eq:sigma_pol); phi_Q(d) = potential of the wave + that of the polarization charge (eq:phi_sheet);
  vt = v + v_emb with v(Q) = 1/(2 eps0 Q) and v_emb = -beta e^{-2Qd}/(2 eps0 Q), both explained (eq:vt_sheet);
  eps_env from vt/v; real-space vt from the images (short sentence, simplified by the user's request); limits.
  The (Q;z,z') forms v = e^{-Q|z-z'|}/(2 eps0 Q), v_emb = -beta e^{-Qz} e^{-Qz'}/(2 eps0 Q) were removed (user,
  2026-11-09): introduce them where finite thickness is treated.
  Sec. 3 "Screening by a polarizable layer on the substrate" (`sec:layer_screening`): 3.1 generic layer response
  chi0 (no local fields): eps_sh = 1 - vt chi0, W = vt/eps_sh = vt + vt chit vt ("structure of the RPA with v -> vt");
  insulating layer chi0 = -Q^2 chi_2D, r0 = chi_2D/(2 eps0), static Keldysh W; 3.2 example: Lorentz oscillators,
  chi_2D = n alpha, single pole eps^-1 = 1 + Omega_Q^2/(w^2 - w_L^2) = plasmon-pole form (substrate moves pole and
  weight via eps_env), modes bullets, short "Discreteness" paragraph; 3.3 summary.
  No citations at present: `\bibliographystyle`/`\bibliography` are commented out at the end of main.tex, to be
  restored with the first \cite (biblio.bib kept).
  Planned (user, 2026-11-09, not now): a section that defines chi and all the needed quantities and analyses the
  effect of the substrate in the GW language (v_emb = v chi^S v, link with the Blase-Duchemin papers and their
  "reaction field"); the removed introduction (goal of the notes, chi0 = chi0^L + chi0^S, eq. vt = v + v chi^S v) is
  recoverable from git history.
  Figures: `sheet_modes` only. Removed on 2026-11-09 at the user's request (recoverable from git history): figures
  `charge_wave_field` and `sheet_potential` (potential profiles of a charge wave above the substrate); the old section on the Coulomb interaction in the plane (point-charge Fourier
  transform, mixed representation, bullets on range, long wavelengths and polarization waves).
- `docs/`: working notes in markdown (context, literature, plans); `01_context_and_literature.md`,
  `02_python_route_yambo_databases.md`.
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
   then implementation and validation (see `docs/02_python_route_yambo_databases.md`).
6. BSE with the substrate-screened W; optical spectra, binding energies, gap/E_b compensation.
7. Full procedure, convergence, applications.

## Open points
- Physics target (layer and observables): to be defined during the analysis.
- Exchange kernel of the BSE with v or vt.
- Content and conventions of the Yambo screening databases: to be verified on the Lumen source (cluster) before any
  implementation.

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
