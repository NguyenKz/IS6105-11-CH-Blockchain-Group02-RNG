#!/usr/bin/env python3
"""Pure checks for public-informed batch identity and output isolation."""

from pathlib import Path

from run_public_informed import ROOT, annotate_observation, protected_output, public_run_id


def main() -> None:
    assert protected_output(ROOT / "data" / "derived" / "pilot")
    assert protected_output(ROOT / "data" / "derived" / "pilot" / "nested")
    assert protected_output(ROOT / "data" / "derived" / "pre_experiment_validation")
    assert not protected_output(ROOT / "data" / "derived" / "public_informed_synthetic")

    context_id = "bsc-mainnet:0x" + "1" * 64
    fomo = public_run_id(context_id, "SC-001", "FEE_ONLY", "a" * 64, "FOMO")
    dice = public_run_id(context_id, "SC-001", "FEE_ONLY", "a" * 64, "DICE")
    assert fomo != dice

    row = {
        "context_id": context_id,
        "scenario_id": "SC-001",
        "cost_model_id": "FEE_ONLY",
        "code_commit": "a" * 64,
        "run_id": "b" * 64,
    }
    annotated = annotate_observation(row, "weak", "c" * 64)
    assert annotated["rule_family_id"] == "FOMO3D_PUBLIC_CONTEXT_HASH_MODULO"
    assert annotated["rule_provenance_status"] == "CONFIRMED"
    assert annotated["run_id"] != "b" * 64
    print("public-informed tests: PASS")


if __name__ == "__main__":
    main()
