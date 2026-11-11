# 03 — MPPI workflow, clusters and convergence procedures for 2D systems (2026-11-11)

Collected from `D:\Projects\Research\MPPI\CLAUDE.md` (MPPI v1.3), from the user's notebooks
`SIMULATIONS/TMDs/MoS2/{DFT,GW}_Analysis.ipynb` (2022-2025, ismhpc and m100) and
`SIMULATIONS/Xenes/Germanene/{DFT,GW}_Analysis.ipynb` (2025, Leonardo) for the physics and the convergence protocol,
and from the production notebook `SIMULATIONS/LiF/NL_Chi/YamboNL_Analysis.ipynb` (2026-10, ismhpc, MPPI v1.3) and the
LiF CLAUDE.md for the CURRENT way of driving the codes (Sec. 1.3: it supersedes the older notebooks where they
differ). Read on the laptop, code and markdown cells only. Nothing here has been re-run.

## 1. MPPI in short
Flow: `InputFiles` (PwInput, YamboInput) -> `Calculators` (QeCalculator, YamboCalculator, configured by `RunRules`;
scheduler `direct` or `slurm`) -> `Datasets` (many runs, `run()`, `fetch_results`, post-processing functions in
`Datasets.PostProcessing`) -> `Parsers` (PwParser on data-file-schema.xml, Yambo parsers on o-* files and ndb.*) ->
`Utilities` (BandStructure, Dos, LatticeUtils, Constants). Tutorials in `MPPI/sphinx_source/tutorials` are the
de-facto documentation.

Standard imports of the notebooks:

    from mppi import InputFiles as I, Calculators as C, Datasets as D, Parsers as P, Utilities as U
    from mppi.Calculators import Tools
    from mppi.Datasets import PostProcessing as PP
    from mppi.Utilities import Constants as Const, LatticeUtils as LL

### QE (pw.x) pattern
    inp = I.PwInput()
    inp.set_scf(force_symmorphic=True, conv_thr=1e-7)      # force_symmorphic is now the default, keep it explicit
    inp.set_num_bnds(30); inp.set_pseudo_dir(pseudo_dir=...); inp.set_spinorbit()   # SOC with FR pseudos
    inp.add_atom(atom='Ge', pseudo_name='Ge_ONCV_PBE_FR-1.0.upf', mass=72.64); inp.set_atoms_number(2)
    inp.set_atomic_positions([['Ge', Ge1], ['Ge', Ge2]], type='alat')
    inp.set_lattice(ibrav=4, celldm1=alat, celldm3=c/alat)  # hexagonal, c = cell height (vacuum) in bohr
    inp.set_energy_cutoff(ecut); inp.set_kpoints(type='automatic', points=[k, k, 1])
    study = D.Dataset(run_dir=run_dir, num_tasks=N)
    inp.set_prefix(D.name_from_id(idd)); study.append_run(id=idd, input=inp, runner=code)
    study.set_postprocessing_function(PP.pw_parse_data)    # or PP.pw_get_energy
    results = study.run(); study.fetch_results(id={'k': k}, attribute='energy')
    r.get_gap(verbose=False)['direct_gap']; r.get_evals()[ik][ib]
- nscf on regular grids: `inp.set_nscf(nbnds, force_symmorphic=True, conv_thr=1e-6)`, `append_run(...,
  source_dir='DFT_analysis/gs_converged.save')`; prefixes like `kpoints_18-nbnds_800`.
- bands on a path: `Tools.build_pw_kpath(G, Mp, Kp, G, numstep=60)`, `inp.set_bands(nb, force_symmorphic=True)`,
  `set_kpoints(type='tpiba_b', klist=klist)`, `U.BandStructure.from_Pw(results, high_sym)`.
- High-symmetry points with ibrav=4 (units 2pi/alat): K' = (1/3, 1/sqrt3), M' = (0, 1/sqrt3); IBZ = Gamma-K'-M'.

### Yambo pattern
- SAVE: `Tools.init_yambo_dir(yambo_dir=run_dir, input_dir='DFT_analysis/<prefix>.save',
  p2y_command='OMP_NUM_THREADS=1 mpirun -np 1 p2y', yambo_command='OMP_NUM_THREADS=1 mpirun -np 1 yambo')`
  (current API; the MoS2 notebooks use the removed `make_p2y` + `init_yambo_run_dir` / `build_SAVE`).
  The nscf for p2y MUST use `force_symmorphic=True` (otherwise this Lumen yambo silently activates no runlevel).
  The new p2y exits with MPI_ABORT after writing the wavefunctions, but the SAVE works.
- Inputs: `I.YamboInput(args='yambo -r -x -V all', folder=run_dir)` (HF) or
  `args='yambo -r -rw -k hartee -dyson n -gw0 p -V all'` (GW PPA with RIM_W; `-rw` = RIM_W, or
  `inp.activate_RIM_W()` / `deactivate_RIM_W()`); `inp.set_extendOut()`; `set_bandRange(b1, b2)`;
  `set_kRange(ik, ik)`; `set_scalar_variables(CUTGeo='slab z')`; `set_array_variables(units='Ha', EXXRLvcs=x,
  VXCRLvcs=x)` (same cutoff on both, they are subtracted); `set_array_variables(RandQpts=5e6)`;
  `set_array_variables(units='RL', RandGvec=..., RandGvecW=...)`; `NGsBlkXp` (units 'Ha'), `BndsRnXp`, `GbndRnge`,
  `GTermKind='BG'`, `LongDrXp=[1,1,0]` (in-plane field direction for the q -> 0 limit of a 2D system).
- Parallelization (example): `SE_ROLEs='q.qp.b'`, `SE_CPU='2.1.16'` (1 ismhpc node, 32 MPI) or `'1.1.16'` (4
  Leonardo nodes); `X_and_IO_ROLEs='q.g.k.c.v'`, `X_and_IO_CPU='1.1.1.nc.nv'`; `DIP_ROLEs='k.c.v'`,
  `DIP_CPU='1.nc.nv'` with nc*nv = number of MPI tasks (nc = 8 or 16).
- Runs (as in the old GW notebooks): `study.append_run(id=idd, input=inp, runner=code, run_dir=run_dir,
  jobname=[idd, 'ndbs', 'ndb_em1d-ngsblkxp_10.0-bndsrnxp_600'])`. The list `jobname` (yambo `-J` with several
  folders) makes yambo read/write databases in shared folders (RIM/cutoff, HF, screening em1d, dipoles), so the
  screening is computed once and reused by the runs at different k or GbndRnge. The old notebooks also passed
  `reformat=False`: no longer needed, see Sec. 1.3.
- Post-processing: `PP.yambo_parse_data`; `r.data.get_gap(k_full=ik, band_full=b1, verbose=False)`;
  `P.YamboOutputParser.from_file('.../o-<name>.qp')['qp']['E0' | 'E']`;
  `P.YamboDftParser('SAVE/ns.db1').get_kpoints(use_scalar_alat=True)`.
- Index of K in the yambo IBZ list of a hexagonal k x k x 1 grid (from the notebooks): 18 -> 37, 30 -> 91,
  42 -> 169, 60 -> 331, 72 -> 469, 81 -> 588; Gamma -> 1.

### 1.3 Current conventions (LiF production notebook, MPPI v1.3; they supersede the older notebooks)
- Keep `reformat=True` (default): yambo regenerates the input with the `-V` verbosity of `args` (use `-V all`),
  dropping the other variables; units with `set_array_variables(units=...)`. Do not pass `reformat=False`.
- A small factory function builds the calculator of each section, e.g.

      module = '/home/dalessandro/module_script/yambo_module'
      def yambo_code(nodes=1, partition='all12h', executable='yambo'):
          rr = C.RunRules(scheduler='slurm', partition=partition, memory='125000', nodes=nodes,
                          ntasks_per_node=32, cpus_per_task=1, omp_num_threads=1,
                          pre_processing=module)
          return C.YamboCalculator(rr, executable=executable, activate_BeeOND=True)

  Each notebook section starts with the cell that defines its calculator and run folder, so sections are independent;
  a markdown "How to run" at the top. Input builders as functions (`build_..._input(folder, ...)`).
- `append_run(id=..., input=..., runner=code, run_dir=folder, name=run_name, jobname=[run_name, <shared dbs>],
  skip=True)`: `id` is the dataset key, `name` the run name (input, output and database folder); `skip=True` does not
  recompute runs whose results exist (cells can be re-executed safely). Without skip, MPPI's default clean restart
  deletes the job output and the run folder before running. Restart of a run that must read its own databases:
  `skip=False, clean_restart=False, activate_BeeOND=False` (with BeeOND MPPI copies the job folder content to the
  scratch root while yambo looks in `<scratch>/<jobname>`, so its databases would not be found); back up report, LOG
  and job output first (MPPI deletes the job output, yambo rewrites report and logs).
- yambo truncates the job string (`-J`) at 100 characters: `assert len(idd) <= 100` on every run name.
- Several runs of one dataset in parallel with `num_tasks`; the run log prints the `mpirun ... -F <name>.in -J ...
  -C <name>` command and the `sbatch` submission.

## 2. Clusters and RunRules
- **ismhpc** (ssh `ismhpc`, jump through `narro`; drive it from the laptop with
  `ssh -o BatchMode=yes -o ClearAllForwardings=yes ismhpc '...'`; CentOS 7, VS Code Remote-SSH does not work).
  `pw.x` qe-7.0 (Intel MPI + MKL) and `yambo` Lumen fork 2.1.0 (OpenMPI): different environments, loaded through
  module files passed as `RunRules(pre_processing=...)`: `/home/dalessandro/module_script/qe_module` and
  `.../yambo_module`. MPPI on the cluster: `~/Applications/MPPI` (editable install, `git pull` only). Lumen sources
  `~/Applications/Lumen/src`. 32 cores per node (ntasks_per_node * cpus_per_task = 32).
  Production RunRules (MPPI CLAUDE.md): `partition='all12h', memory='125000'`, BeeOND on;
  QE `time='11:59:00', ntasks_per_node=16, cpus_per_task=2, omp_num_threads=2`, `QeCalculator(rr,
  activate_BeeOND=True)`; Yambo `ntasks_per_node=32, cpus_per_task=1, omp_num_threads=1`,
  `YamboCalculator(rr, activate_BeeOND=True)`. Other partitions seen in the MoS2 notebooks: `slownodes`,
  `fastnodes`; `debug` (2 h) for tests. Small direct runs (mpi 2-4, omp 1) on the login node are acceptable only for
  tiny tests; never heavy runs there.
  Cluster rules from the LiF project (2026-10): at most three nodes in use at the same time (datasets of 1-node runs
  with `num_tasks` <= 3, counting the other running jobs); always `all12h` (also for tests; `debug` not used);
  `slownodes` (2 days) for runs longer than 12 h; home
  quota 19.5 GB (runs on the BeeOND scratch). Since 2026-10-23 the default yambo in the PATH is the Lumen `bug-fixes`
  build (`~/Applications/Lumen/bug-fixes-gcc_10.2`: yambo, ypp, p2y, yambo_nl; yambo_rt still from the master build;
  details in `~/sysadmin/CLAUDE.md` on ismhpc): restart shells/kernels after PATH changes. SAVE setup databases written
  by older yambo versions (ndb.gops, ndb.kindx, ndb.kpts) must be removed and the setup redone (`yambo` without
  arguments). Claude submits slurm jobs only when the user asks or for agreed tests; Claude can work from the laptop
  (ssh) or directly on the cluster (Claude Code CLI in tmux, started in the project folder, as for LiF in `~/work/LiF`).
  The germanene GW runs used yambo 5.3.0 on Leonardo: check the input generated by the ismhpc build (`-V all`) before
  reusing its variables (names and defaults may differ in the Lumen fork).
- **Leonardo** (CINECA, GPU booster, used for germanene): slurm `partition='boost_usr_prod'`, 4 GPUs per node,
  `ntasks_per_node=4, cpus_per_task=8, omp_num_threads=8, gres_gpu=4, pe=8, omp_places='cores',
  omp_proc_bind='close', map_by='socket', rank_by='core'`, module files `qe_gpu` and `yambo-5.3.0_gpu` in the user's
  Leonardo home; account and paths in the first cells of the germanene notebooks (not copied here: public repo).
- **m100** (CINECA, old, MoS2): similar GPU RunRules.
- Always ask the user before launching QE/Yambo runs (p2y included).

## 3. Ground-state convergence for a 2D layer (both notebooks)
Control quantities: total energy, direct gap (at K) and gap at Gamma.
1. Hexagonal cell `ibrav=4`, `celldm3 = c/alat` with c the cell height (vacuum + layer), FR pseudos with SOC.
2. **ecut x k grid**: Dataset over k in {12, 15, 18} and ecut in {60...90} Ry (germanene) / {40...120} Ry (MoS2).
   Chosen: germanene 70 Ry, 12x12x1; MoS2 80 Ry, 12x12x1.
3. **Lattice constant and buckling**: 5 x 5 grid of +-1% variations, quadratic fits of the energy. Germanene:
   alat = 7.6557 bohr, buckling delta = 0.0842 alat. MoS2: alat 5.9014 bohr (later SG15 FR: 6.014).
4. **Vacuum**: c in {10, 15, 20, 25, 30, 40} a.u.; germanene converged at c = 25 a.u.; MoS2 used 40 a.u. (30 a.u. in
   the later runs at the experimental lattice constant).
5. `assume_isolated='2D'` at the DFT level: no impact on the MoS2 bands (the 2D cutoff matters in GW).
6. Final scf, bands on G-M-K-G, nscf on regular grids with many empty bands (germanene 18x18 with 800 bands,
   60x60 and 72x72 with 600; HF tests on grids with 30 bands; MoS2 250-400 bands on 18/30/42).

## 4. GW convergence for a 2D layer (MoS2 notebook = full procedure, germanene = recent update)
Always with `CUTGeo='slab z'`; tests on the gaps at Gamma and K (separate runs with `set_kRange`).
1. **HF level, RIM for the cutoff Coulomb** (MoS2, 18x18x1): RandGvec in {15...200}, RandQpts in {1e6...8e6}. The
   gaps converge (1 meV at RandQpts 5e6) much faster than the single states. Chosen RandGvec = 100 (germanene 200),
   RandQpts = 5e6.
2. **HF, exchange cutoff** EXXRLvcs = VXCRLvcs: MoS2 30 Ha, germanene 50 Ha.
3. **HF vs k grid** (18 ... 81).
4. **PPA screening** (18x18x1, `LongDrXp=[1,1,0]` in germanene): NGsBlkXp scan (MoS2 6 Ha, 8 safer; germanene 10 Ha,
   5 meV), then BndsRnXp (MoS2 250; germanene 600), then GbndRnge with and without the Bruneval-Gonze terminator
   `GTermKind='BG'` (MoS2: 250 not enough, ~400; germanene 400 with BG).
5. **RIM_W** (RandGvecW in {1, 2, 10, 20}): 10 chosen; RIM_W makes the PPA gap converge much faster with the k grid.
6. **k grid in PPA** with RIM_W (germanene 18, 60, 72) and exponential extrapolation of the gap at K
   (`m exp(-t N_k) + b`).
7. **QP bands**: one run per k point near the path (selected with `U.Utils.is_point_near_line`), bands from the o-*.qp
   files (`E0`, `E`), plotted with `U.BandStructure`; germanene on 72x72x1, bands 25-32. MoS2: a "new Yambo release"
   section reran the full-BZ GW to fix a code error affecting the GW bands (reusing the old screening); also G1W0 tests.
- Reference value: the germanene GW band plot (72x72x1) is annotated with a 108 meV gap at K (read from the plotting
  cell, not re-checked).

## 5. What this implies for the bilayer-hBN benchmark (see 04_...)
- Same protocol for monolayer and bilayer hBN, with the SAME alat, box height, ecut, k grids, bands and GW cutoffs, so
  that the explicit and the effective calculations differ only by the method. No SOC needed for hBN (light atoms).
- The vacuum/box height must be converged with the slab cutoff for the bilayer; the effective scheme needs the
  position of the "substrate" layer inside the same box (translation by d along z).
- Open technical point (docs/02, Sec. 4 B): consistency of `CUTGeo='slab z'` and RIM/RIM_W with v_emb.
