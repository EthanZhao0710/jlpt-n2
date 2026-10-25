import unittest
from datetime import date

from calculate_progress import checklist_progress, estimate_pass, posteriors


class ProgressCalculationTests(unittest.TestCase):
    def test_progress_and_switch_use_only_the_fixed_checklist(self):
        partial = checklist_progress("- [x] R01 one\n- [ ] R02 two", 2)
        self.assertEqual(partial["percent"], 50)
        self.assertEqual(partial["stage"], "core_learning")
        complete = checklist_progress("- [x] R01 one\n- [x] R02 two", 2)
        self.assertEqual(complete["stage"], "past_papers")

    def test_duplicate_or_missing_ids_are_rejected(self):
        for text in ("- [x] R01\n- [x] R01", "- [x] R02"):
            with self.assertRaises(ValueError):
                checklist_progress(text, 2)

    def setUp(self):
        self.config = {
            "prior_beta": [2, 2], "half_life_days": 30,
            "evidence_weights": {"independent": 1, "aided": 0.25},
            "simulation_draws": 3000, "random_seed": 7,
            "section_pass_mark": 19, "overall_pass_mark": 90,
        }
        self.row = {"id": "one", "level": "N2", "section": "knowledge",
                    "date": "2026-10-25", "kind": "aided", "correct": 1, "total": 1}

    def test_aided_success_is_not_counted_as_full_independent_success(self):
        posterior, _ = posteriors([self.row], self.config, date(2026, 10, 25))
        self.assertEqual(posterior["knowledge"], [2.25, 2])

    def test_old_evidence_decays_but_is_not_relabelled(self):
        row = dict(self.row, date="2026-09-25", correct=0)
        posterior, _ = posteriors([row], self.config, date(2026, 10, 25))
        self.assertEqual(posterior["knowledge"], [2, 2.125])

    def test_repeats_and_other_levels_do_not_inflate_results(self):
        rows = [dict(self.row, repeated=True), dict(self.row, id="n3", level="N3")]
        posterior, support = posteriors(rows, self.config, date(2026, 10, 25))
        self.assertEqual(posterior["knowledge"], [2, 2])
        self.assertEqual(support["knowledge"], 0)

    def test_duplicate_and_future_observations_are_rejected(self):
        with self.assertRaises(ValueError):
            posteriors([self.row, self.row], self.config, date(2026, 10, 25))
        with self.assertRaises(ValueError):
            posteriors([dict(self.row, date="2026-10-26")], self.config, date(2026, 10, 25))

    def test_target_original_is_not_mislabelled_as_an_n2_past_paper(self):
        self.config["evidence_weights"]["original_check"] = 0.1
        row = dict(self.row, level="original", target_level="N2", kind="original_check")
        posterior, _ = posteriors([row], self.config, date(2026, 10, 25))
        self.assertEqual(posterior["knowledge"], [2.1, 2])

    def test_simulation_is_reproducible(self):
        posterior, _ = posteriors([self.row], self.config, date(2026, 10, 25))
        self.assertEqual(estimate_pass(posterior, self.config), estimate_pass(posterior, self.config))


if __name__ == "__main__":
    unittest.main()
