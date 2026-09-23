from types import SimpleNamespace

import pytest

from rcwe.numerical_audit import EXPOSED_SEEDS, convergence_diagnostic, runtime_provenance
from scripts.run_synthetic_recovery import summarize


@pytest.mark.parametrize("norm,expected", [
    (0.0, "CONVERGED"), (0.5e-5, "CONVERGED"),
    (1e-4 / 10, "MARGINAL"), (0.99e-4, "MARGINAL"), (1.01e-4, "MARGINAL"),
    (1e-4 * 10, "MARGINAL"), (1.01e-3, "FAILED"), (float("nan"), "FAILED"),
])
def test_diagnostic_marks_cutoff_neighborhood_without_retuning(norm, expected):
    starts = [SimpleNamespace(optimizer_reported_success=True, log_likelihood=-10.,
                              projected_gradient_inf_norm=norm) for _ in range(2)]
    assert convergence_diagnostic(starts, tolerance=1e-4, agreement_tolerance=1e-6) == expected


def test_distinct_basins_and_optimizer_failures_are_not_rescued():
    a = SimpleNamespace(optimizer_reported_success=True, log_likelihood=-10., projected_gradient_inf_norm=0.)
    b = SimpleNamespace(optimizer_reported_success=True, log_likelihood=-11., projected_gradient_inf_norm=0.)
    assert convergence_diagnostic([a, b], tolerance=1e-4, agreement_tolerance=1e-6) == "FAILED"
    b.log_likelihood = -10.
    b.optimizer_reported_success = False
    assert convergence_diagnostic([a, b], tolerance=1e-4, agreement_tolerance=1e-6) == "FAILED"


def test_benchmark_cannot_claim_acceptance_without_preregistered_criteria():
    result = summarize([], [])
    assert result["acceptance_status"] == "NOT_ASSESSED"
    assert EXPOSED_SEEDS == frozenset(range(260901, 260921))


def test_runtime_records_build_configuration_not_just_package_versions():
    runtime = runtime_provenance()
    assert runtime["reference_runtime"]["numpy"] == "2.5.3"
    assert runtime["numerical_build_configuration"]
    assert "OPENBLAS_NUM_THREADS" in runtime["thread_environment"]
