"""Reproducible checklist progress and an explicitly heuristic N2 pass estimate."""

import argparse
import json
import math
import random
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SECTIONS = ("knowledge", "reading", "listening")


def checklist_progress(text, expected_total):
    rows = re.findall(r"^- \[([ x])\] R(\d+)\b", text, re.MULTILINE)
    ids = [int(number) for _, number in rows]
    if sorted(ids) != list(range(1, expected_total + 1)):
        raise ValueError("Checklist IDs must preserve the fixed denominator without duplicates.")
    done = sum(mark == "x" for mark, _ in rows)
    return {
        "completed": done,
        "total": expected_total,
        "remaining": expected_total - done,
        "percent": round(100 * done / expected_total, 1),
        "stage": "past_papers" if done == expected_total else "core_learning",
    }


def posteriors(observations, config, as_of):
    prior = config["prior_beta"]
    if len(prior) != 2 or min(prior) <= 0:
        raise ValueError("Beta prior parameters must be positive.")
    result = {section: list(map(float, prior)) for section in SECTIONS}
    support = {section: 0.0 for section in SECTIONS}
    seen = set()
    for row in observations:
        if row["id"] in seen:
            raise ValueError("Duplicate observation: " + row["id"])
        seen.add(row["id"])
        target_original = (row["level"] == "original" and row.get("target_level") == "N2"
                           and row["kind"] in ("original_check", "correction_check"))
        if row.get("repeated", False) or (row["level"] != "N2" and not target_original):
            continue
        when = date.fromisoformat(row["date"])
        if when > as_of:
            raise ValueError("An observation cannot come from the future.")
        correct, total = row["correct"], row["total"]
        if not 0 <= correct <= total or total <= 0:
            raise ValueError("Invalid correct/total values.")
        weight = config["evidence_weights"][row["kind"]]
        if not 0 < weight <= 1:
            raise ValueError("Evidence weights must be in (0, 1].")
        weight *= 2 ** (-(as_of - when).days / config["half_life_days"])
        section = row["section"]
        result[section][0] += weight * correct
        result[section][1] += weight * (total - correct)
        support[section] += weight * total
    return result, support


def estimate_pass(posterior, config):
    """Simulate a subjective normalized-score model, not an official raw-score map."""
    draws = config["simulation_draws"]
    if draws <= 0:
        raise ValueError("simulation_draws must be positive.")
    rng = random.Random(config["random_seed"])
    passed = 0
    for _ in range(draws):
        scores = [60 * rng.betavariate(*posterior[section]) for section in SECTIONS]
        passed += min(scores) >= config["section_pass_mark"] and sum(scores) >= config["overall_pass_mark"]
    probability = passed / draws
    # Coarse display avoids presenting simulation precision as predictive accuracy.
    shown = max(5, min(95, 5 * math.floor(probability * 20 + 0.5)))
    return probability, shown


def calculate(root=ROOT):
    config = json.loads((root / "progress/assessment_config.json").read_text(encoding="utf-8"))
    observations = json.loads((root / "progress/assessment_observations.json").read_text(encoding="utf-8"))
    checklist = (root / config["checklist_path"]).read_text(encoding="utf-8")
    progress = checklist_progress(checklist, config["fixed_total"])
    posterior, support = posteriors(observations, config, date.fromisoformat(config["as_of"]))
    probability, shown = estimate_pass(posterior, config)
    return {
        "as_of": config["as_of"],
        "model_version": config["model_version"],
        "learning_progress": progress,
        "pass_estimate": {
            "percent_display": shown,
            "model_probability": round(probability, 6),
            "meaning": "Current-level heuristic, not an exam-day forecast or calibrated probability",
            "confidence": "low",
            "effective_observations": {key: round(value, 4) for key, value in support.items()},
            "posterior_beta": posterior,
            "official_scaled_score_conversion": False,
            "future_learning_gain_assumed": False,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Save the computed dashboard JSON.")
    args = parser.parse_args()
    result = calculate()
    if args.write:
        target = ROOT / "progress/latest_metrics.json"
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
