"""Runtime provenance and non-acceptance diagnostics for optimizer v0.1."""

from contextlib import redirect_stdout
from io import StringIO
import os
import platform

import numpy as np
import scipy

REFERENCE_RUNTIME = {"python": "3.12.14", "numpy": "2.5.3", "scipy": "1.18.1",
                     "system": "Windows", "machine": "AMD64"}
EXPOSED_SEEDS = frozenset(range(260901, 260921))


def runtime_provenance() -> dict[str, object]:
    actual = {"python": platform.python_version(), "numpy": np.__version__,
              "scipy": scipy.__version__, "system": platform.system(), "machine": platform.machine()}
    config = StringIO()
    with redirect_stdout(config):
        np.show_config()
        scipy.show_config()
    return {**actual, "reference_runtime": REFERENCE_RUNTIME,
            "reference_family_matches": actual == REFERENCE_RUNTIME,
            "numerical_build_configuration": config.getvalue(),
            "thread_environment": {key: os.environ.get(key) for key in (
                "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")}}


def convergence_diagnostic(starts, *, tolerance: float, agreement_tolerance: float) -> str:
    """Three-state sensitivity annotation, NOT a replacement acceptance gate.

    Examine the two highest-likelihood raw successful starts. A full decade
    around the existing cutoff is marginal; endpoints are marginal too.
    No change to the v0.1 selection, numerical trajectory, or converged boolean.
    """
    successful = sorted((s for s in starts if s.optimizer_reported_success),
                        key=lambda s: s.log_likelihood, reverse=True)
    if len(successful) < 2:
        return "FAILED"
    best, second = successful[:2]
    if not np.isfinite([best.log_likelihood, second.log_likelihood]).all():
        return "FAILED"
    if best.log_likelihood - second.log_likelihood > agreement_tolerance:
        return "FAILED"
    norms = [s.projected_gradient_inf_norm for s in (best, second)]
    if not np.isfinite(norms).all() or min(norms) < 0 or max(norms) > tolerance * 10:
        return "FAILED"
    return "CONVERGED" if max(norms) < tolerance / 10 else "MARGINAL"
