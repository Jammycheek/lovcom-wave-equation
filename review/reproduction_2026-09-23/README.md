# Reviewer reproduction artifacts — synthetic recovery benchmark (2026-09-23)

**Status: diagnostic replay only. Not the canonical runtime, not acceptance evidence, not calibration data.**
All 40 scenario/seed pairs here are the already-exposed block (seeds 260901–260920, both default
scenarios). Under `NUMERICAL_RECOVERY_ACCEPTANCE_PLAN_v0.1.md` and V2.1 candidate 12 they are
retrospective audit data and must not be used to choose any threshold, tolerance, start set or band.

These are the raw files behind the reviewer observations recorded as F-09 and F-10.

## Runs

| Directory | Generated at commit | Host | Python | NumPy | SciPy | BLAS |
|---|---|---|---|---|---|---|
| `linux_py311_numpy2.4.6_scipy1.17.1/` | `a0e2fa9` | Linux x86_64, 4 logical CPUs, glibc 2.39 | 3.11.15 | 2.4.6 | 1.17.1 | scipy-openblas |
| `linux_py312_numpy2.5.3_scipy1.18.1_pinned/` | `b338ec0` | same host | 3.12.3 | 2.5.3 | 1.18.1 | scipy-openblas 0.3.34 |

Commands (from the repository root; both runs used `--seed-base 260901 --replicates 20`):

```text
# first run (pre-v0.2 runner, --workers 8)
python scripts/run_synthetic_recovery.py --replicates 20 --seed-base 260901 --workers 8 --output <dir>
# pinned run
python scripts/run_synthetic_recovery.py --replicates 20 --seed-base 260901 --workers 4 --allow-nonreference-runtime --output <dir>
```

The first run predates the v0.2 runner, so its `config.json`/`summary.json` lack the later
`acceptance_status`, `convergence_diagnostic` and runtime-provenance fields. The fit and forecast
code path is numerically unchanged between `a0e2fa9` and `b338ec0` (only a diagnostic property was
added); the two Linux runs are bit-identical, which confirms this. Per-replicate checkpoint files of
the pinned run were omitted; `run.log` shows their completion order.

## Comparisons (`comparisons/`, produced by `scripts/compare_synthetic_runs.py`)

| Left | Right | v0.1 `converged` flips | max \|ΔFIT LL\| | max \|Δ per-IE holdout μ\| |
|---|---|---|---|---|
| committed (Windows, 3.12.14, 2.5.3/1.18.1) | Linux 3.11 / 2.4.6 / 1.17.1 | 10/40 | 1.11e-11 | 9.08e-08 |
| committed (Windows, 3.12.14, 2.5.3/1.18.1) | Linux 3.12 / 2.5.3 / 1.18.1 (pinned) | 10/40 | 1.11e-11 | 9.08e-08 |
| Linux pinned | Linux older | 0/40 | 0 | 0 (bit-identical) |

Reading: on this Linux host, changing NumPy 2.4.6→2.5.3 and SciPy 1.17.1→1.18.1 changed nothing.
Pinning the canonical package versions did not reduce the Windows↔Linux differences at all. The
residual comes from the platform side (OS, Python patch release, CPU/libm/BLAS kernel dispatch);
these three factors are **not** separated by these runs.

Reproduce a comparison:

```text
python scripts/compare_synthetic_runs.py results/synthetic_recovery review/reproduction_2026-09-23/linux_py312_numpy2.5.3_scipy1.18.1_pinned
```

## File checksums (SHA-256)

```text
37fee5e03aca80fd56cf2a17b286c6a1523ee0cd68d3ca4e4c4558755207e326  ./comparisons/committed_windows_vs_linux_py311_np246_sp1171.json
15f8a29c0143d85869fb67408db100132019d1f2870c138cf48656b0716abba4  ./comparisons/committed_windows_vs_linux_py312_np253_sp1181_pinned.json
175c982c89ec2f75c08f291b822780e2e53669ae30f12e60ff0d1214218c4004  ./comparisons/linux_pinned_vs_linux_older.json
ffbc2acbc358ea4a27e9d4ac0cdae71f6702a783f217a45da1e896fe2d9597b7  ./linux_py311_numpy2.4.6_scipy1.17.1/REPORT.md
6a3f15e243bba9e10589764725b87764b0e60878d50355b4469412819b5ebfc5  ./linux_py311_numpy2.4.6_scipy1.17.1/config.json
d1856c272aa15d843f615496ddd276855f621d7682c6555defc9bfc6ae8759cf  ./linux_py311_numpy2.4.6_scipy1.17.1/environment.json
9d5a5c7e892bdcb40d45e4762e97cb2467b6c29c867c67443848b1f5d8034b47  ./linux_py311_numpy2.4.6_scipy1.17.1/fit_details.json
700c32c9adc67eabb30089812657134839e03b96e915b2e3c430327a1dbc37d2  ./linux_py311_numpy2.4.6_scipy1.17.1/predictions.csv
fdbc2fcff0fde7638a0a6ead0caa0f26de46e1b04efe4ce48eede11b72d0d264  ./linux_py311_numpy2.4.6_scipy1.17.1/replicates.csv
c4e0f29ff611358033702ebdf22d684dc059276b4c33eade11999e4a7281dc36  ./linux_py311_numpy2.4.6_scipy1.17.1/summary.json
8405435b445ea4330336e2b97691ffecca8787ce395c5b640d92d77d922e0302  ./linux_py312_numpy2.5.3_scipy1.18.1_pinned/REPORT.md
7165559abc2afc1ad0cf65ac1efd099fd84cb2e1ab78d8c1fbc08b88ba5a9c28  ./linux_py312_numpy2.5.3_scipy1.18.1_pinned/config.json
f0ea0405636eadb592fd0f9c1116534d3d402b088afde8f3e8a98c2e7a5110b7  ./linux_py312_numpy2.5.3_scipy1.18.1_pinned/environment.json
cfc7fe08ca189e9c178bf23226808ab08f2aab8667148ad02b8c298cb6055271  ./linux_py312_numpy2.5.3_scipy1.18.1_pinned/fit_details.json
700c32c9adc67eabb30089812657134839e03b96e915b2e3c430327a1dbc37d2  ./linux_py312_numpy2.5.3_scipy1.18.1_pinned/predictions.csv
b9b3bb7bf4b4bf40f1b60400be379c8eb8a7eb5e98d96608565402a5e8a211fc  ./linux_py312_numpy2.5.3_scipy1.18.1_pinned/replicates.csv
cbe3c93a9a43cf916c5aa432699704d3a0770ff3a7596fc993f0d2f8590ebce5  ./linux_py312_numpy2.5.3_scipy1.18.1_pinned/run.log
4870eaf4b00d76953b8f1827d0d27228f33450cecf78382fee38dd8deb03fece  ./linux_py312_numpy2.5.3_scipy1.18.1_pinned/summary.json
```
