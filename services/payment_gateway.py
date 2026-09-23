import uuid


class MockPaymentGateway:
    """
    Development-only mock payment gateway.
    Never use this implementation for real payments.
    """

    @staticmethod
    def process_payment():
        transaction_id = (
            f"MOCK-{uuid.uuid4().hex[:12].upper()}"
        )

        return {
            "transaction_id": transaction_id,
            "status": "SUCCESS",
        }