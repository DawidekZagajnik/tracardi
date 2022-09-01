from tracardi.service.tracardi_http_client import HttpClient


class StripeClientException(Exception):
    pass


class StripeClient:

    def __init__(self, api_key: str):
        self._key = api_key
        self._retries = 1

    def set_retries(self, retries: int) -> None:
        self._retries = retries if retries >= 1 else 1

    async def create_charge(self, amount: int, currency_code: str, customer_id: str, payment_source: str,
                            email: str) -> dict:
        async with HttpClient(
                self._retries,
                [200, 201, 202, 203],
                headers={"Authorization": f"Bearer {self._key}"}
        ) as client:
            async with client.post(
                url="https://api.stripe.com/v1/charges",
                data={
                    "amount": amount,
                    "currency": currency_code,
                    "customer": customer_id,
                    "source": payment_source,
                    "receipt_email": email
                }
            ) as response:

                if response.status not in [200, 201, 202, 203] or "error" in await response.json():
                    raise StripeClientException(await response.text())

                return await response.json()
