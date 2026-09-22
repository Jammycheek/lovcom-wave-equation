"""Frozen discriminant-validity pilot for Tension Bridge T/D ratings."""

from __future__ import annotations

import hashlib
from typing import Iterable, Mapping

import numpy as np

from .tension_bridge import AggregatedWindow, ReliabilityResult

MIN_WORKS = 4
MIN_WINDOWS = 30
MIN_WINDOWS_PER_WORK = 5
BOOTSTRAP_REPEATS = 5000
DISCRIMINANT_LIMIT = 0.85


def _seed(master_seed: str | int, repeat: int) -> int:
    material = f"{master_seed}|T-D|{repeat}".encode()
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def evaluate_discriminant_pilot(
    windows: Iterable[AggregatedWindow],
    reliability: Mapping[str, ReliabilityResult],
    *,
    master_seed: str | int,
    repeats: int = BOOTSTRAP_REPEATS,
    limit: float = DISCRIMINANT_LIMIT,
) -> dict[str, object]:
    data = list(windows)
    works = sorted({item.work_id for item in data})
    counts = {work: sum(item.work_id == work for item in data) for work in works}
    sufficient = (
        len(data) >= MIN_WINDOWS
        and len(works) >= MIN_WORKS
        and bool(counts)
        and all(count >= MIN_WINDOWS_PER_WORK for count in counts.values())
    )
    base = {
        "eligible_windows": len(data),
        "independent_works": len(works),
        "work_window_counts": counts,
        "repeats_requested": repeats,
        "discriminant_limit": limit,
    }
    if not sufficient:
        return {**base, "status": "INSUFFICIENT_PILOT_DATA", "abs_r_td": None, "upper_95_abs_r_td": None, "repeats_valid": 0}
    reliability_passed = all(key in reliability and reliability[key].passed for key in ("T", "D"))
    if not reliability_passed:
        return {**base, "status": "PILOT_MEASUREMENT_FAILURE", "abs_r_td": None, "upper_95_abs_r_td": None, "repeats_valid": 0}

    by_work: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    centered_t, centered_d = [], []
    for work in works:
        subset = [item for item in data if item.work_id == work]
        t = np.asarray([item.t_obs for item in subset], dtype=float)
        d = np.asarray([item.d_obs for item in subset], dtype=float)
        t = t - t.mean()
        d = d - d.mean()
        by_work[work] = (t, d)
        centered_t.extend(t)
        centered_d.extend(d)
    if np.std(centered_t) == 0 or np.std(centered_d) == 0:
        return {**base, "status": "PILOT_MEASUREMENT_FAILURE", "abs_r_td": None, "upper_95_abs_r_td": None, "repeats_valid": 0}
    point = abs(float(np.corrcoef(centered_t, centered_d)[0, 1]))
    bootstrap = []
    for repeat in range(repeats):
        rng = np.random.default_rng(_seed(master_seed, repeat))
        sampled = rng.choice(works, size=len(works), replace=True)
        t = np.concatenate([by_work[str(work)][0] for work in sampled])
        d = np.concatenate([by_work[str(work)][1] for work in sampled])
        if np.std(t) == 0 or np.std(d) == 0:
            continue
        correlation = float(np.corrcoef(t, d)[0, 1])
        if np.isfinite(correlation):
            bootstrap.append(abs(correlation))
    if not bootstrap:
        return {**base, "status": "PILOT_MEASUREMENT_FAILURE", "abs_r_td": point, "upper_95_abs_r_td": None, "repeats_valid": 0}
    upper = float(np.percentile(np.asarray(bootstrap), 95.0))
    status = "PILOT_PASS" if point < limit and upper < limit else "PILOT_DISCRIMINANT_FAILURE"
    return {**base, "status": status, "abs_r_td": point, "upper_95_abs_r_td": upper, "repeats_valid": len(bootstrap)}
