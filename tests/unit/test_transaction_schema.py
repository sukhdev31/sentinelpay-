from decimal import Decimal

import pytest
from pydantic import ValidationError

from sentinelpay.schemas.transaction import (
    AuthenticationResult,
    PaymentChannel,
    TransactionRequest,
)


def valid_transaction_payload() -> dict[str, object]:
    return {
        "transaction_id": "txn_0001",
        "event_time": "2026-09-09T18:30:00Z",
        "account_id": "acct_82f91",
        "card_token": "card_tok_b72c",
        "merchant_id": "merchant_1042",
        "device_id": "device_a992",
        "ip_token": "ip_tok_d410",
        "amount": "24999.00",
        "currency": "inr",
        "country": "in",
        "channel": "WEB",
        "card_present": False,
        "authentication_result": "PASS",
    }


def test_valid_transaction_is_normalized() -> None:
    transaction = TransactionRequest.model_validate(valid_transaction_payload())

    assert transaction.amount == Decimal("24999.00")
    assert transaction.currency == "INR"
    assert transaction.country == "IN"
    assert transaction.channel is PaymentChannel.WEB
    assert transaction.authentication_result is AuthenticationResult.PASS


def test_transaction_rejects_unknown_fields() -> None:
    payload = valid_transaction_payload()
    payload["secret_risk_override"] = True

    with pytest.raises(ValidationError):
        TransactionRequest.model_validate(payload)


def test_transaction_requires_timezone() -> None:
    payload = valid_transaction_payload()
    payload["event_time"] = "2026-09-09T18:30:00"

    with pytest.raises(ValidationError, match="must include a timezone"):
        TransactionRequest.model_validate(payload)


def test_transaction_rejects_card_present_payment() -> None:
    payload = valid_transaction_payload()
    payload["card_present"] = True

    with pytest.raises(
        ValidationError,
        match="supports only card-not-present transactions",
    ):
        TransactionRequest.model_validate(payload)


@pytest.mark.parametrize("invalid_amount", ["0", "-1.00", "10000000000.00"])
def test_transaction_rejects_invalid_amounts(
    invalid_amount: str,
) -> None:
    payload = valid_transaction_payload()
    payload["amount"] = invalid_amount

    with pytest.raises(ValidationError):
        TransactionRequest.model_validate(payload)
