#!/usr/bin/env python3
"""Reproducible Step 11 analysis for the completed replay batches."""

from __future__ import annotations

import hashlib
import json
import math
import platform
from decimal import Decimal
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


TOPIC_ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP_SEED = 6105
BOOTSTRAP_RESAMPLES = 10_000
WEI_PER_BNB = Decimal(10**18)

PUBLIC_FAMILIES = {
    "FOMO3D_PUBLIC_CONTEXT_HASH_MODULO": "Fomo3D-inspired",
    "DICE2WIN_COMMIT_BLOCKHASH": "Dice2Win-inspired safe reference",
}
BASELINE_FAMILIES = {
    "WEAK_PUBLIC_CONTEXT": "Very simple weak rule",
    "COMMIT_BEFORE_ENTROPY": "Very simple safe reference",
}
CAPABILITIES = [
    "SEARCHER_ONLY",
    "BUILDER_REORDER",
    "BUILDER_SELECTIVE_INCLUSION",
]


def read_jsonl(path: Path) -> pd.DataFrame:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return pd.DataFrame(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_inputs(topic_root: Path = TOPIC_ROOT) -> dict[str, Any]:
    public_dir = topic_root / "data" / "derived" / "public_informed_synthetic"
    baseline_dir = topic_root / "data" / "derived" / "pilot"
    paths = {
        "public_observations": public_dir / "observations.jsonl",
        "public_invariants": public_dir / "invariants.jsonl",
        "public_manifest": topic_root / "data" / "manifests" / "public_informed_synthetic_manifest.json",
        "baseline_observations": baseline_dir / "observations.jsonl",
        "baseline_manifest": topic_root / "data" / "manifests" / "pilot_manifest.json",
    }
    return {
        "paths": paths,
        "public_observations": read_jsonl(paths["public_observations"]),
        "public_invariants": read_jsonl(paths["public_invariants"]),
        "baseline_observations": read_jsonl(paths["baseline_observations"]),
        "public_manifest": json.loads(paths["public_manifest"].read_text(encoding="utf-8")),
        "baseline_manifest": json.loads(paths["baseline_manifest"].read_text(encoding="utf-8")),
    }


def validate_inputs(inputs: dict[str, Any]) -> pd.DataFrame:
    public = inputs["public_observations"]
    baseline = inputs["baseline_observations"]
    invariants = inputs["public_invariants"]
    public_fee = public[public["cost_model_id"] == "FEE_ONLY"]
    baseline_fee = baseline[baseline["cost_model_id"] == "FEE_ONLY"]

    checks = {
        "public_observation_rows": len(public) == 2400,
        "baseline_observation_rows": len(baseline) == 2400,
        "public_fee_only_rows": len(public_fee) == 600,
        "baseline_fee_only_rows": len(baseline_fee) == 600,
        "public_contexts": public["context_id"].nunique() == 100,
        "baseline_contexts": baseline["context_id"].nunique() == 100,
        "public_invariant_rows": len(invariants) == 600,
        "public_no_replay_failures": bool(public["replay_success"].all()),
        "baseline_no_replay_failures": bool(baseline["replay_success"].all()),
        "public_unique_pairs": not public_fee.duplicated(
            ["context_id", "scenario_id", "rule_family_id"]
        ).any(),
        "baseline_unique_pairs": not baseline_fee.duplicated(
            ["context_id", "scenario_id", "rng_pattern"]
        ).any(),
        "canonical_execution_valid": bool(invariants["canonical_valid"].all()),
        "manipulated_execution_valid": bool(invariants["manipulated_valid"].all()),
        "canonical_snapshot_restored": bool(invariants["canonical_snapshot_restored"].all()),
        "manipulated_snapshot_restored": bool(invariants["manipulated_snapshot_restored"].all()),
        "builder_input_unchanged": bool(invariants["builder_input_unchanged"].all()),
        "safe_reorder_preserves_winner": bool(invariants["safe_reorder_preserves_winner"].all()),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"Step 11 input validation failed: {', '.join(failed)}")
    return pd.DataFrame(
        {"check": list(checks), "status": ["PASS" if value else "FAIL" for value in checks.values()]}
    )


def prepare_outcome_rows(inputs: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame]:
    public = inputs["public_observations"]
    public = public[public["cost_model_id"] == "FEE_ONLY"].copy()
    invariants = inputs["public_invariants"]
    keys = ["context_id", "scenario_id", "rule_family_id"]
    public = public.merge(invariants, on=keys, how="left", validate="one_to_one")
    public["family_id"] = public["rule_family_id"]
    public["family_label"] = public["family_id"].map(PUBLIC_FAMILIES)
    public["execution_valid"] = (
        public["replay_success"] & public["canonical_valid"] & public["manipulated_valid"]
    )
    public["liveness_checked"] = public["validity_checks"].map(
        lambda checks: checks.get("liveness_checked") if isinstance(checks, dict) else None
    )

    baseline = inputs["baseline_observations"]
    baseline = baseline[baseline["cost_model_id"] == "FEE_ONLY"].copy()
    baseline["family_id"] = baseline["rng_pattern"]
    baseline["family_label"] = baseline["family_id"].map(BASELINE_FAMILIES)
    baseline["execution_valid"] = baseline["replay_success"]
    baseline["liveness_checked"] = baseline["validity_checks"].map(
        lambda checks: checks.get("liveness_checked") if isinstance(checks, dict) else None
    )

    for frame in (public, baseline):
        decided = frame["canonical_win"].notna() & frame["manipulated_win"].notna()
        frame["valid_pair"] = frame["execution_valid"] & decided
        frame["outcome_difference"] = np.where(
            frame["valid_pair"],
            frame["manipulated_win"].astype(int) - frame["canonical_win"].astype(int),
            np.nan,
        )
    return public, baseline


def bootstrap_interval(
    values: np.ndarray,
    *,
    seed: int = BOOTSTRAP_SEED,
    resamples: int = BOOTSTRAP_RESAMPLES,
) -> tuple[float, float]:
    values = np.sort(np.asarray(values, dtype=float))
    if values.size == 0:
        return math.nan, math.nan
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, values.size, size=(resamples, values.size))
    means = values[indices].mean(axis=1)
    return tuple(np.percentile(means, [2.5, 97.5]).tolist())


def transition_counts(group: pd.DataFrame) -> dict[str, int]:
    valid = group[group["valid_pair"]]
    canonical = valid["canonical_win"].astype(bool)
    manipulated = valid["manipulated_win"].astype(bool)
    return {
        "loss_to_win": int((~canonical & manipulated).sum()),
        "win_to_loss": int((canonical & ~manipulated).sum()),
        "unchanged_win": int((canonical & manipulated).sum()),
        "unchanged_loss": int((~canonical & ~manipulated).sum()),
    }


def summarize_outcomes(rows: pd.DataFrame, dataset: str) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for (family_id, family_label, capability), group in rows.groupby(
        ["family_id", "family_label", "capability"], sort=True
    ):
        valid = group[group["valid_pair"]]
        differences = valid["outcome_difference"].to_numpy(dtype=float)
        low, high = bootstrap_interval(differences)
        transitions = transition_counts(group)
        records.append({
            "dataset": dataset,
            "family_id": family_id,
            "family_label": family_label,
            "capability": capability,
            "total_pairs": len(group),
            "valid_pairs": len(valid),
            "failed_pairs": len(group) - len(valid),
            "validity_rate": float(group["execution_valid"].mean()),
            "canonical_wins": int(valid["canonical_win"].sum()),
            "manipulated_wins": int(valid["manipulated_win"].sum()),
            "canonical_win_rate": float(valid["canonical_win"].mean()),
            "manipulated_win_rate": float(valid["manipulated_win"].mean()),
            "delta_p_win": float(differences.mean()),
            "ci_95_low": low,
            "ci_95_high": high,
            "winner_change_rate": float((differences != 0).mean()),
            "liveness_status": (
                "NOT_CHECKED"
                if capability == "BUILDER_SELECTIVE_INCLUSION"
                and not bool(group["liveness_checked"].map(lambda value: value is True).all())
                else "NOT_APPLICABLE"
            ),
            **transitions,
        })
    return pd.DataFrame(records)


def paired_uplift(rows: pd.DataFrame) -> pd.DataFrame:
    pivot = rows[rows["valid_pair"]].pivot(
        index=["context_id", "family_id", "family_label"],
        columns="capability",
        values="outcome_difference",
    )
    records = []
    for (family_id, family_label), family in pivot.groupby(level=["family_id", "family_label"]):
        for capability in ("BUILDER_REORDER", "BUILDER_SELECTIVE_INCLUSION"):
            differences = (
                family[capability] - family["SEARCHER_ONLY"]
            ).dropna().to_numpy(dtype=float)
            low, high = bootstrap_interval(differences)
            records.append({
                "family_id": family_id,
                "family_label": family_label,
                "builder_capability": capability,
                "paired_contexts": len(differences),
                "capability_uplift": float(differences.mean()),
                "ci_95_low": low,
                "ci_95_high": high,
            })
    return pd.DataFrame(records)


def economic_summary(public_rows: pd.DataFrame) -> pd.DataFrame:
    records = []
    valid = public_rows[
        public_rows["replay_success"]
        & public_rows["canonical_win"].notna()
        & public_rows["manipulated_win"].notna()
    ]
    for (family_id, capability, cost_model), group in valid.groupby(
        ["rule_family_id", "capability", "cost_model_id"], sort=True
    ):
        n = len(group)
        difference_sum = sum(
            int(manipulated) - int(canonical)
            for canonical, manipulated in zip(group["canonical_win"], group["manipulated_win"])
        )
        delta = Decimal(difference_sum) / Decimal(n)
        prize = Decimal(str(group["prize_wei"].iloc[0]))
        tx_cost = sum(Decimal(str(value)) for value in group["attacker_tx_cost_wei"]) / Decimal(n)
        bid = sum(Decimal(str(value)) for value in group["explicit_bid_or_bribe_wei"]) / Decimal(n)
        opportunity = sum(Decimal(str(value)) for value in group["opportunity_cost_wei"]) / Decimal(n)
        total_cost = tx_cost + bid + opportunity
        incremental_payout = delta * prize
        net_profit = incremental_payout - total_cost
        break_even = None
        if delta > 0:
            break_even = int((total_cost / delta).to_integral_value(rounding="ROUND_CEILING"))
        records.append({
            "family_id": family_id,
            "family_label": PUBLIC_FAMILIES[family_id],
            "capability": capability,
            "cost_model_id": cost_model,
            "valid_pairs": n,
            "delta_p_win": float(delta),
            "declared_prize_wei": str(int(prize)),
            "mean_tx_cost_wei": str(int(tx_cost)),
            "mean_bid_wei": str(int(bid)),
            "mean_opportunity_cost_wei": str(int(opportunity)),
            "mean_total_cost_wei": str(int(total_cost)),
            "incremental_expected_payout_wei": str(int(incremental_payout)),
            "net_profit_at_declared_prize_wei": str(int(net_profit)),
            "break_even_prize_wei": None if break_even is None else str(break_even),
            "break_even_prize_bnb": math.nan if break_even is None else break_even / 1e18,
            "cost_evidence": "REPLAYED_FEE_PLUS_MODELED_BID_AND_OPPORTUNITY",
        })
    return pd.DataFrame(records)


def safe_reference_comparison(public: pd.DataFrame) -> pd.DataFrame:
    valid = public[public["valid_pair"]]
    pivot = valid.pivot(
        index=["context_id", "capability"],
        columns="family_id",
        values="outcome_difference",
    )
    records = []
    weak = "FOMO3D_PUBLIC_CONTEXT_HASH_MODULO"
    safe = "DICE2WIN_COMMIT_BLOCKHASH"
    for capability, group in pivot.groupby(level="capability"):
        paired = group[[weak, safe]].dropna()
        reduction = (paired[weak] - paired[safe]).to_numpy(dtype=float)
        low, high = bootstrap_interval(reduction)
        records.append({
            "capability": capability,
            "paired_contexts": len(paired),
            "weak_delta_p_win": float(paired[weak].mean()),
            "safe_delta_p_win": float(paired[safe].mean()),
            "delta_reduction": float(reduction.mean()),
            "ci_95_low": low,
            "ci_95_high": high,
            "safe_provenance_status": "RULE_UNCONFIRMED",
        })
    return pd.DataFrame(records)


def baseline_comparison(public: pd.DataFrame, baseline: pd.DataFrame) -> pd.DataFrame:
    family_mapping = {
        "FOMO3D_PUBLIC_CONTEXT_HASH_MODULO": "WEAK_PUBLIC_CONTEXT",
        "DICE2WIN_COMMIT_BLOCKHASH": "COMMIT_BEFORE_ENTROPY",
    }
    left = public[public["valid_pair"]][
        ["context_id", "capability", "family_id", "outcome_difference"]
    ].rename(columns={"outcome_difference": "public_difference"})
    left["baseline_family_id"] = left["family_id"].map(family_mapping)
    right = baseline[baseline["valid_pair"]][
        ["context_id", "capability", "family_id", "outcome_difference"]
    ].rename(columns={
        "family_id": "baseline_family_id",
        "outcome_difference": "baseline_difference",
    })
    paired = left.merge(
        right,
        on=["context_id", "capability", "baseline_family_id"],
        how="inner",
        validate="one_to_one",
    )
    records = []
    for (family_id, baseline_family_id, capability), group in paired.groupby(
        ["family_id", "baseline_family_id", "capability"], sort=True
    ):
        difference = (group["public_difference"] - group["baseline_difference"]).to_numpy(float)
        low, high = bootstrap_interval(difference)
        records.append({
            "public_family_id": family_id,
            "baseline_family_id": baseline_family_id,
            "capability": capability,
            "paired_contexts": len(group),
            "baseline_delta_p_win": float(group["baseline_difference"].mean()),
            "public_delta_p_win": float(group["public_difference"].mean()),
            "difference": float(difference.mean()),
            "ci_95_low": low,
            "ci_95_high": high,
        })
    return pd.DataFrame(records)


def coverage_table(inputs: dict[str, Any]) -> pd.DataFrame:
    public = inputs["public_observations"]
    baseline = inputs["baseline_observations"]
    invariants = inputs["public_invariants"]
    return pd.DataFrame([
        {
            "dataset": "VERY_SIMPLE_RULES baseline",
            "observation_rows": len(baseline),
            "scenario_executions": len(baseline[baseline["cost_model_id"] == "FEE_ONLY"]),
            "contexts": baseline["context_id"].nunique(),
            "failed_contexts": int((~baseline["replay_success"]).sum() / 24),
            "invariant_rows": 0,
        },
        {
            "dataset": "Public-informed synthetic",
            "observation_rows": len(public),
            "scenario_executions": len(public[public["cost_model_id"] == "FEE_ONLY"]),
            "contexts": public["context_id"].nunique(),
            "failed_contexts": int(inputs["public_manifest"]["failed_contexts"]),
            "invariant_rows": len(invariants),
        },
    ])


def build_results(inputs: dict[str, Any]) -> dict[str, pd.DataFrame]:
    audit = validate_inputs(inputs)
    public, baseline = prepare_outcome_rows(inputs)
    public_summary = summarize_outcomes(public, "PUBLIC_INFORMED_SYNTHETIC")
    baseline_summary = summarize_outcomes(baseline, "VERY_SIMPLE_RULES")
    return {
        "audit": audit,
        "coverage": coverage_table(inputs),
        "public_rows": public,
        "baseline_rows": baseline,
        "public_summary": public_summary,
        "baseline_summary": baseline_summary,
        "capability_uplift": paired_uplift(public),
        "economic_sensitivity": economic_summary(inputs["public_observations"]),
        "safe_reference": safe_reference_comparison(public),
        "baseline_comparison": baseline_comparison(public, baseline),
    }


def _save_figure(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160, bbox_inches="tight", metadata={"Software": "Step 11 analysis"})
    plt.close(fig)


def create_figures(results: dict[str, pd.DataFrame], figures_dir: Path) -> list[Path]:
    plt.rcParams.update({
        "figure.figsize": (10, 5.5),
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.22,
        "font.size": 10,
    })
    paths: list[Path] = []

    coverage = results["coverage"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    x = np.arange(len(coverage))
    axes[0].bar(x - 0.18, coverage["contexts"], 0.36, label="Contexts", color="#486581")
    axes[0].bar(x + 0.18, coverage["failed_contexts"], 0.36, label="Failed", color="#d64545")
    axes[0].set_xticks(x, ["Baseline", "Public-informed"])
    axes[0].set_ylabel("Count")
    axes[0].set_title("Context coverage")
    axes[0].legend()
    axes[1].bar(x, coverage["scenario_executions"], color="#2a9d8f")
    axes[1].set_xticks(x, ["Baseline", "Public-informed"])
    axes[1].set_ylabel("Scenario executions")
    axes[1].set_title("Execution coverage")
    fig.suptitle("Dataset coverage and replay failures")
    path = figures_dir / "01_dataset_coverage.png"
    _save_figure(fig, path)
    paths.append(path)

    summary = results["public_summary"]
    matrix = summary.pivot(index="family_label", columns="capability", values="delta_p_win")
    matrix = matrix.reindex(columns=CAPABILITIES)
    fig, ax = plt.subplots(figsize=(10, 4.5))
    image = ax.imshow(matrix.to_numpy(), cmap="RdBu_r", vmin=-0.1, vmax=0.1, aspect="auto")
    ax.set_xticks(range(len(matrix.columns)), [name.replace("_", "\n") for name in matrix.columns])
    ax.set_yticks(range(len(matrix.index)), matrix.index)
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            ax.text(column, row, f"Δp={matrix.iloc[row, column]:+.3f}", ha="center", va="center")
    ax.set_title("Capability matrix: change in attacker win rate")
    fig.colorbar(image, ax=ax, label="delta_p_win")
    path = figures_dir / "02_capability_matrix.png"
    _save_figure(fig, path)
    paths.append(path)

    ordered = summary.sort_values(["family_id", "capability"]).reset_index(drop=True)
    labels = [f"{PUBLIC_FAMILIES[row.family_id]}\n{row.capability}" for row in ordered.itertuples()]
    values = ordered["delta_p_win"].to_numpy()
    lower = values - ordered["ci_95_low"].to_numpy()
    upper = ordered["ci_95_high"].to_numpy() - values
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.errorbar(values, np.arange(len(values)), xerr=[lower, upper], fmt="o", color="#264653", capsize=4)
    ax.axvline(0, color="#555555", linewidth=1)
    ax.set_yticks(np.arange(len(labels)), labels)
    ax.set_xlabel("delta_p_win with paired bootstrap 95% interval")
    ax.set_title("Paired capability effects")
    path = figures_dir / "03_paired_delta_ci.png"
    _save_figure(fig, path)
    paths.append(path)

    economics = results["economic_sensitivity"]
    positive = economics[
        (economics["family_id"] == "FOMO3D_PUBLIC_CONTEXT_HASH_MODULO")
        & (economics["capability"] == "BUILDER_REORDER")
    ]
    prizes = np.geomspace(1e-5, 1e-2, 300)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    colors = ["#264653", "#e76f51", "#6a4c93", "#2a9d8f"]
    for row, color in zip(positive.itertuples(), colors):
        costs_bnb = float(Decimal(row.mean_total_cost_wei) / WEI_PER_BNB)
        net = row.delta_p_win * prizes - costs_bnb
        ax.plot(prizes, net, label=row.cost_model_id, color=color)
        ax.axvline(row.break_even_prize_bnb, color=color, linestyle=":", alpha=0.75)
    ax.axhline(0, color="#555555", linewidth=1)
    ax.set_xscale("log")
    ax.set_xlabel("Prize assumption (BNB, log scale)")
    ax.set_ylabel("Derived expected net profit (BNB)")
    ax.set_title("Modeled break-even region for Fomo3D-inspired builder reorder")
    ax.legend()
    path = figures_dir / "04_net_profit_sensitivity.png"
    _save_figure(fig, path)
    paths.append(path)

    safe = results["safe_reference"].set_index("capability").reindex(CAPABILITIES).reset_index()
    x = np.arange(len(safe))
    fig, ax = plt.subplots(figsize=(10, 5.5))
    weak_values = safe["weak_delta_p_win"].to_numpy()
    weak_errors = np.vstack([
        weak_values - safe["ci_95_low"].to_numpy(),
        safe["ci_95_high"].to_numpy() - weak_values,
    ])
    ax.bar(
        x - 0.18,
        weak_values,
        0.36,
        yerr=weak_errors,
        capsize=4,
        label="Weak public-context rule",
        color="#e76f51",
    )
    ax.bar(x + 0.18, safe["safe_delta_p_win"], 0.36, label="Commit-before-entropy", color="#2a9d8f")
    ax.axhline(0, color="#555555", linewidth=1)
    ax.set_xticks(x, [name.replace("_", "\n") for name in safe["capability"]])
    ax.set_ylabel("delta_p_win")
    ax.set_title("Weak rule and safe-reference comparison")
    ax.legend()
    path = figures_dir / "05_weak_vs_safe.png"
    _save_figure(fig, path)
    paths.append(path)
    return paths


def _markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    display = frame[columns].copy()
    for column in display.select_dtypes(include=["float"]).columns:
        digits = 6 if column.endswith("_bnb") else 3
        display[column] = display[column].map(
            lambda value: "" if pd.isna(value) else f"{value:.{digits}f}"
        )
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    rows = [
        "| " + " | ".join(str(value) for value in row) + " |"
        for row in display.itertuples(index=False, name=None)
    ]
    return "\n".join([header, separator, *rows])


def write_reports(results: dict[str, pd.DataFrame], reports_dir: Path) -> None:
    public = results["public_summary"]
    economics = results["economic_sensitivity"]
    safe = results["safe_reference"]
    positive = economics[economics["delta_p_win"] > 0]
    rq_columns = [
        "family_id", "capability", "valid_pairs", "validity_rate",
        "canonical_win_rate", "manipulated_win_rate", "delta_p_win",
        "ci_95_low", "ci_95_high", "winner_change_rate", "liveness_status",
    ]
    economic_columns = [
        "family_id", "capability", "cost_model_id", "delta_p_win",
        "mean_total_cost_wei", "break_even_prize_bnb", "cost_evidence",
    ]
    safe_columns = [
        "capability", "paired_contexts", "weak_delta_p_win", "safe_delta_p_win",
        "delta_reduction", "ci_95_low", "ci_95_high", "safe_provenance_status",
    ]
    results_text = f"""# Step 11 results by research question

All numbers below are derived from controlled local replay. They do not show that a historical BSC actor performed an attack.

## RQ-C1: Capability boundary

{_markdown_table(public, rq_columns)}

Searcher-only did not change the decoded winner in either public-informed rule. Builder reorder and declared selective inclusion changed the winner in every Fomo3D-inspired pair, but the changes were not always favorable to the attacker. Selective inclusion remains a capability test because liveness was not measured.

## RQ-C2: Paired effect

The Fomo3D-inspired point estimate is `delta_p_win = +0.080` for builder reorder and selective inclusion. Its paired bootstrap 95% interval includes zero, so this batch does not establish a stable positive advantage. The Dice2Win-inspired abstraction has `delta_p_win = 0.000` for all capabilities.

## RQ-C3: Economic sensitivity

{_markdown_table(positive, economic_columns)}

These break-even values use a point estimate and named cost assumptions. Transaction fees are replayed; bid and opportunity-cost fields are modeled. Because the probability interval includes zero, the table is sensitivity analysis rather than evidence of historical profitability. Capabilities with non-positive `delta_p_win` have no finite positive break-even prize under the declared formula.

## RQ-C4: Safe reference

{_markdown_table(safe, safe_columns)}

The commit-before-entropy abstraction preserved the winner under reorder. Its deployed Dice2Win bytecode linkage remains `RULE_UNCONFIRMED`, and the weak-versus-safe effect interval for builder capabilities includes zero.

## Claim boundary

- C-002 is supported only as a controlled synthetic capability result.
- C-003, C-004 and C-005 are partially supported because uncertainty, modeled costs and provenance limits remain.
- The two-transaction workload does not estimate realistic competition, prevalence or all-block behavior.
"""
    (reports_dir / "results_by_rq.md").write_text(results_text, encoding="utf-8")

    fomo_builder = public[
        (public["family_id"] == "FOMO3D_PUBLIC_CONTEXT_HASH_MODULO")
        & (public["capability"] == "BUILDER_REORDER")
    ].iloc[0]
    robustness_text = f"""# Step 11 robustness checks

## Completed checks

- Paired bootstrap: 10,000 context-level resamples with seed `{BOOTSTRAP_SEED}`.
- Input integrity: 2,400 public-informed observations, 600 invariant rows and no replay failure.
- Cost-model duplication: outcome rates use only `FEE_ONLY`; economic sensitivity uses all four named models.
- Execution validity: canonical and manipulated runtime invariants pass for all 600 scenario executions.
- Safe lifecycle: commit-before-entropy checks and reorder winner preservation pass.

## Uncertainty

Fomo3D-inspired builder reorder has point estimate `{fomo_builder.delta_p_win:+.3f}` with 95% interval `[{fomo_builder.ci_95_low:+.3f}, {fomo_builder.ci_95_high:+.3f}]`. The interval includes zero. The report therefore does not claim a stable positive probability advantage.

## Known limitations

- The workload has one honest and one attacker transaction. It demonstrates a minimal capability, not realistic competition magnitude.
- The optional participant-count batch for 2, 5 and 10 participants was not run.
- Selective inclusion records a declared omission but does not measure liveness or historical censorship.
- Dice2Win-inspired replay abstracts the public mechanism; deployed-bytecode linkage remains `RULE_UNCONFIRMED`.
- Bid and opportunity cost are modeled. Break-even values are conditional sensitivity results.
"""
    (reports_dir / "robustness_checks.md").write_text(robustness_text, encoding="utf-8")


def export_results(
    inputs: dict[str, Any],
    results: dict[str, pd.DataFrame],
    topic_root: Path = TOPIC_ROOT,
) -> dict[str, Any]:
    tables_dir = topic_root / "reports" / "tables"
    figures_dir = topic_root / "reports" / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    table_names = [
        "coverage", "public_summary", "baseline_summary", "capability_uplift",
        "economic_sensitivity", "safe_reference", "baseline_comparison",
    ]
    for name in table_names:
        results[name].to_csv(tables_dir / f"{name}.csv", index=False)
    figure_paths = create_figures(results, figures_dir)
    write_reports(results, topic_root / "reports")

    manifest = {
        "analysis": "STEP_11_PAIRED_REPLAY",
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
        "python_version": platform.python_version(),
        "dependency_versions": {
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "input_hashes": {
            name: sha256(path) for name, path in inputs["paths"].items()
        },
        "row_counts": {
            "public_observations": len(inputs["public_observations"]),
            "baseline_observations": len(inputs["baseline_observations"]),
            "public_invariants": len(inputs["public_invariants"]),
        },
        "outputs": {
            "tables": [f"reports/tables/{name}.csv" for name in table_names],
            "figures": [str(path.relative_to(topic_root)) for path in figure_paths],
            "reports": ["reports/results_by_rq.md", "reports/robustness_checks.md"],
        },
    }
    manifest_path = topic_root / "analysis" / "analysis_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def run_analysis(topic_root: Path = TOPIC_ROOT, *, export: bool = True) -> tuple[dict[str, Any], dict[str, pd.DataFrame], dict[str, Any] | None]:
    inputs = load_inputs(topic_root)
    results = build_results(inputs)
    manifest = export_results(inputs, results, topic_root) if export else None
    return inputs, results, manifest


if __name__ == "__main__":
    _, result_tables, _ = run_analysis()
    print(result_tables["audit"].to_string(index=False))
    print("Step 11 analysis: PASS")
