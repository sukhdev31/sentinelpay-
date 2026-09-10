from decimal import Decimal

from sentinelpay.schemas.features import TransactionFeatures
from sentinelpay.schemas.transaction import TransactionRequest


class FeatureService:
    """Derive safe defaults when an online feature store has no prior history."""

    def resolve(
        self,
        transaction: TransactionRequest,
        supplied: TransactionFeatures | None,
    ) -> TransactionFeatures:
        if supplied is not None:
            return supplied

        return TransactionFeatures(
            customer_average_amount_30d=Decimal(transaction.amount),
            transaction_count_10m=1,
            transaction_count_1h=1,
            failed_authentication_count_1h=(
                1 if transaction.authentication_result.value == "FAIL" else 0
            ),
            device_account_count_24h=1,
            ip_confirmed_fraud_count_30d=0,
            distance_from_last_transaction_km=0,
            minutes_since_last_transaction=None,
            merchant_fraud_rate_30d=0,
            is_new_device=True,
            feature_freshness_ms=0,
        )
