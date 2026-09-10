from typing import Final

import numpy as np

from sentinelpay.schemas.features import TransactionFeatures
from sentinelpay.schemas.transaction import TransactionRequest

FEATURE_NAMES: Final[tuple[str, ...]] = (
    "amount",
    "amount_ratio",
    "transaction_count_10m",
    "transaction_count_1h",
    "failed_authentication_count_1h",
    "device_account_count_24h",
    "ip_confirmed_fraud_count_30d",
    "distance_from_last_transaction_km",
    "merchant_fraud_rate_30d",
    "is_new_device",
)


def vectorize(
    transaction: TransactionRequest,
    features: TransactionFeatures,
) -> np.ndarray:
    average = float(features.customer_average_amount_30d)
    amount = float(transaction.amount)
    amount_ratio = amount / average if average else 1.0
    return np.asarray(
        [
            amount,
            amount_ratio,
            features.transaction_count_10m,
            features.transaction_count_1h,
            features.failed_authentication_count_1h,
            features.device_account_count_24h,
            features.ip_confirmed_fraud_count_30d,
            features.distance_from_last_transaction_km,
            features.merchant_fraud_rate_30d,
            int(features.is_new_device),
        ],
        dtype=float,
    ).reshape(1, -1)
