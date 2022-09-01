from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.domain.named_entity import NamedEntity
from pydantic import validator


class Config(PluginConfig):
    source: NamedEntity
    charge: int
    iso_currency_code: NamedEntity
    customer_id: str
    payment_source: str
    receipt_email: str

    @validator("iso_currency_code", always=True)
    def validate_currency(cls, value: str):
        if len(value) != 3 or not value.isalpha():
            raise ValueError("Currency code has to consist of 3 letters.")
        return value.lower()


class ApiKey(PluginConfig):
    api_key: str
