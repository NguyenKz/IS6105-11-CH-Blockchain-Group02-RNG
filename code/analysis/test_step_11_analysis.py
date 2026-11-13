from __future__ import annotations

import unittest
from decimal import Decimal
from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from step_11_analysis import (
    bootstrap_interval,
    build_results,
    load_inputs,
    transition_counts,
)


class Step11AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = build_results(load_inputs())

    def test_bootstrap_is_deterministic(self) -> None:
        values = np.array([1, 1, -1, 0, 0], dtype=float)
        self.assertEqual(bootstrap_interval(values), bootstrap_interval(values))

    def test_transition_counts(self) -> None:
        frame = pd.DataFrame({
            "valid_pair": [True, True, True, True],
            "canonical_win": [False, True, True, False],
            "manipulated_win": [True, False, True, False],
        })
        self.assertEqual(
            transition_counts(frame),
            {"loss_to_win": 1, "win_to_loss": 1, "unchanged_win": 1, "unchanged_loss": 1},
        )

    def test_expected_effects(self) -> None:
        summary = self.results["public_summary"].set_index(["family_id", "capability"])
        fomo = "FOMO3D_PUBLIC_CONTEXT_HASH_MODULO"
        dice = "DICE2WIN_COMMIT_BLOCKHASH"
        self.assertEqual(summary.loc[(fomo, "SEARCHER_ONLY"), "delta_p_win"], 0.0)
        for capability in ("BUILDER_REORDER", "BUILDER_SELECTIVE_INCLUSION"):
            row = summary.loc[(fomo, capability)]
            self.assertAlmostEqual(row["delta_p_win"], 0.08)
            self.assertLessEqual(row["ci_95_low"], 0.0)
            self.assertGreaterEqual(row["ci_95_high"], 0.0)
        for capability in ("SEARCHER_ONLY", "BUILDER_REORDER", "BUILDER_SELECTIVE_INCLUSION"):
            self.assertEqual(summary.loc[(dice, capability), "delta_p_win"], 0.0)

    def test_break_even_only_for_positive_delta(self) -> None:
        economics = self.results["economic_sensitivity"]
        positive = economics[economics["delta_p_win"] > 0]
        non_positive = economics[economics["delta_p_win"] <= 0]
        self.assertTrue(positive["break_even_prize_wei"].notna().all())
        self.assertTrue(non_positive["break_even_prize_wei"].isna().all())
        for row in positive.itertuples():
            self.assertGreater(Decimal(row.break_even_prize_wei), 0)

    def test_batch_acceptance(self) -> None:
        coverage = self.results["coverage"].set_index("dataset")
        public = coverage.loc["Public-informed synthetic"]
        self.assertEqual(public["observation_rows"], 2400)
        self.assertEqual(public["scenario_executions"], 600)
        self.assertEqual(public["contexts"], 100)
        self.assertEqual(public["failed_contexts"], 0)
        self.assertTrue((self.results["audit"]["status"] == "PASS").all())


if __name__ == "__main__":
    unittest.main()
