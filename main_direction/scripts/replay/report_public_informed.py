#!/usr/bin/env python3
"""Add the locked VERY_SIMPLE_RULES comparison to the Step 10 report."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def delta(rows: list[dict[str, Any]]) -> float:
    decided = [
        row for row in rows
        if row["replay_success"]
        and row["canonical_win"] is not None
        and row["manipulated_win"] is not None
    ]
    if not decided:
        return 0.0
    return (
        sum(bool(row["manipulated_win"]) for row in decided)
        - sum(bool(row["canonical_win"]) for row in decided)
    ) / len(decided)


def main() -> None:
    report = ROOT / "reports" / "public_informed_synthetic_report.md"
    public_rows = [
        row for row in read_jsonl(
            ROOT / "data" / "derived" / "public_informed_synthetic" / "observations.jsonl"
        ) if row["cost_model_id"] == "FEE_ONLY"
    ]
    baseline_rows = [
        row for row in read_jsonl(ROOT / "data" / "derived" / "pilot" / "observations.jsonl")
        if row["cost_model_id"] == "FEE_ONLY"
    ]
    public_groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    baseline_groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in public_rows:
        public_groups.setdefault((row["rule_family_id"], row["capability"]), []).append(row)
    for row in baseline_rows:
        baseline_groups.setdefault((row["rng_pattern"], row["capability"]), []).append(row)

    mapping = {
        "FOMO3D_PUBLIC_CONTEXT_HASH_MODULO": "WEAK_PUBLIC_CONTEXT",
        "DICE2WIN_COMMIT_BLOCKHASH": "COMMIT_BEFORE_ENTROPY",
    }
    section = [
        "## Comparison with VERY_SIMPLE_RULES",
        "",
        "| Public-informed family | Capability | Baseline delta_p_win | Public-informed delta_p_win | Difference |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for family, capability in sorted(public_groups):
        public_delta = delta(public_groups[(family, capability)])
        baseline_delta = delta(baseline_groups[(mapping[family], capability)])
        section.append(
            f"| {family} | {capability} | {baseline_delta:+.3f} | "
            f"{public_delta:+.3f} | {public_delta - baseline_delta:+.3f} |"
        )

    text = report.read_text(encoding="utf-8")
    marker = "## Evidence status"
    if "## Comparison with VERY_SIMPLE_RULES" in text:
        text = text.split("## Comparison with VERY_SIMPLE_RULES", 1)[0].rstrip() + "\n\n" + marker + text.split(marker, 1)[1]
    text = text.replace(marker, "\n".join(section) + "\n\n" + marker)
    report.write_text(text, encoding="utf-8")
    print("public-informed baseline comparison: PASS")


if __name__ == "__main__":
    main()
