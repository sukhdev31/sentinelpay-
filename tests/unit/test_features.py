from datetime import UTC, datetime
from decimal import Decimal

from sentinelpay.schemas.transaction import TransactionRequest
from sentinelpay.services.features import FeatureService


def test_feature_service_creates_cold_start_defaults() -> None:
    transaction = TransactionRequest(
        transaction_id="txn_001",
        event_time=datetime.now(UTC),
        account_id="acct_001",
        card_token="card_001",
        merchant_id="merchant_001",
        device_id="device_001",
        ip_token="ip_001",
        amount=Decimal("100.00"),
        currency="usd",
        country="us",
        channel="WEB",
        card_present=False,
        authentication_result="PASS",
    )
    result = FeatureService().resolve(transaction, None)
    assert result.customer_average_amount_30d == Decimal("100.00")
    assert result.transaction_count_10m == 1
    assert result.is_new_device is True
