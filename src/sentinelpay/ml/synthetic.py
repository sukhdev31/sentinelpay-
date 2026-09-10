import argparse
import csv
from pathlib import Path

import numpy as np

from sentinelpay.ml.features import FEATURE_NAMES


def generate(rows: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Generate reproducible, intentionally synthetic fraud signals."""

    rng = np.random.default_rng(seed)
    amount = rng.lognormal(6.4, 1.0, rows)
    amount_ratio = rng.lognormal(0.05, 0.7, rows)
    velocity_10m = rng.poisson(1.2, rows)
    velocity_1h = velocity_10m + rng.poisson(2.5, rows)
    auth_failures = rng.poisson(0.25, rows)
    device_accounts = 1 + rng.poisson(0.35, rows)
    bad_ip = rng.binomial(2, 0.015, rows)
    distance = rng.exponential(70, rows)
    merchant_rate = rng.beta(1.2, 35, rows)
    new_device = rng.binomial(1, 0.18, rows)
    matrix = np.column_stack(
        [
            amount,
            amount_ratio,
            velocity_10m,
            velocity_1h,
            auth_failures,
            device_accounts,
            bad_ip,
            distance,
            merchant_rate,
            new_device,
        ]
    )
    logits = (
        -5.4
        + 0.55 * np.log1p(amount_ratio)
        + 0.38 * velocity_10m
        + 0.45 * auth_failures
        + 0.42 * device_accounts
        + 2.2 * bad_ip
        + 0.003 * distance
        + 9.0 * merchant_rate
        + 0.55 * new_device
    )
    probability = 1 / (1 + np.exp(-logits))
    labels = rng.binomial(1, np.clip(probability, 0, 0.98))
    return matrix, labels


def write_csv(path: Path, matrix: np.ndarray, labels: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([*FEATURE_NAMES, "is_fraud"])
        writer.writerows([*row, int(label)] for row, label in zip(matrix, labels, strict=True))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SentinelPay synthetic training data")
    parser.add_argument("--rows", type=int, default=25_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("data/synthetic_transactions.csv"))
    args = parser.parse_args()
    matrix, labels = generate(args.rows, args.seed)
    write_csv(args.output, matrix, labels)
    print(f"wrote {len(labels)} rows to {args.output} (fraud rate={labels.mean():.3%})")


if __name__ == "__main__":
    main()
