from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.domain.named_entity import NamedEntity


class Config(PluginConfig):
    source: NamedEntity
    charge: int
    iso_currency_code: NamedEntity
    customer_id: str
    payment_source: str
    receipt_email: str


class ApiKey(PluginConfig):
    api_key: str
