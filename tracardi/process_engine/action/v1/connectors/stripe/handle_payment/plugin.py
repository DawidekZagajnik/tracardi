from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config, ApiKey
from tracardi.service.storage.driver import storage
from ..client import StripeClient, StripeClientException


def validate(config: dict) -> Config:
    return Config(**config)


class StripeChargeAction(ActionRunner):

    config: Config
    client: StripeClient

    async def set_up(self, init):
        self.config = validate(init)
        resource = storage.driver.resource.load(self.config.source.id)
        self.client = StripeClient(resource.credentials.get_credentials(self, ApiKey).api_key)
        self.client.set_retries(self.node.on_connection_error_repeat)

    async def run(self, payload: dict, in_edge=None):
        dot = self._get_dot_accessor(payload=payload)
        try:
            result = await self.client.create_charge(
                amount=int(dot[self.config.charge]),
                currency_code=self.config.iso_currency_code.id,
                customer_id=dot[self.config.customer_id],
                payment_source=dot[self.config.payment_source],
                email=dot[self.config.receipt_email]
            )
            return Result(port="success", value={"result": result})

        except StripeClientException as e:
            return Result(port="error", value={"message": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='StripeChargeAction',
            inputs=["payload"],
            outputs=["success", "error"],
            version='0.7.2',
            license="MIT",
            author="Dawid Kruk",
            manual="stripe_charge_action",
            init={
                "source": {
                    "id": "",
                    "name": ""
                },
                "charge": None,
                "iso_currency_code": {
                    "id": "",
                    "name": ""
                },
                "customer_id": None,
                "payment_source": None,
                "receipt_email": None
            },
            form=Form(
                title="Stripe charge plugin configuration",
                groups=[
                    FormGroup(
                        fields=[
                            FormField(
                                id="source",
                                name="Stripe resource",
                                description="Select your Stripe resource, containing Stripe authorization key.",
                                component=FormComponent(type="resource", props={"tag": "stripe"})
                            ),
                            FormField(
                                id="charge",
                                name="Charge amount",
                                description="Type in the path to the amount that you want to charge. It has to be an "
                                            "integer and be expressed in the smallest monetary units of selected "
                                            "currency (so cents for USD and yens for japanese yens, etc.). That means "
                                            "value 100 will result in charging $1 if USD is selected.",
                                component=FormComponent(type="dotPath", props={"label": "Amount"})
                            ),
                            FormField(
                                id="iso_currency_code",
                                name="ISO currency code",
                                description="Select the currency that your amount is expressed in.",
                                component=FormComponent(type="select", props={"label": "Currency", "items": {
                                    "aed": "AED",
                                    "afn": "AFN",
                                    "all": "ALL",
                                    "amd": "AMD",
                                    "ang": "ANG",
                                    "aoa": "AOA",
                                    "ars": "ARS",
                                    "aud": "AUD",
                                    "awg": "AWG",
                                    "azn": "AZN",
                                    "bam": "BAM",
                                    "bbd": "BBD",
                                    "bdt": "BDT",
                                    "bgn": "BGN",
                                    "bif": "BIF",
                                    "bmd": "BMD",
                                    "bnd": "BND",
                                    "bob": "BOB",
                                    "brl": "BRL",
                                    "bsd": "BSD",
                                    "bwp": "BWP",
                                    "byn": "BYN",
                                    "bzd": "BZD",
                                    "cad": "CAD",
                                    "cdf": "CDF",
                                    "chf": "CHF",
                                    "clp": "CLP",
                                    "cny": "CNY",
                                    "cop": "COP",
                                    "crc": "CRC",
                                    "cve": "CVE",
                                    "czk": "CZK",
                                    "djf": "DJF",
                                    "dkk": "DKK",
                                    "dop": "DOP",
                                    "dzd": "DZD",
                                    "egp": "EGP",
                                    "etb": "ETB",
                                    "eur": "EUR",
                                    "fjd": "FJD",
                                    "fkp": "FKP",
                                    "gbp": "GBP",
                                    "gel": "GEL",
                                    "gip": "GIP",
                                    "gmd": "GMD",
                                    "gnf": "GNF",
                                    "gtq": "GTQ",
                                    "gyd": "GYD",
                                    "hkd": "HKD",
                                    "hnl": "HNL",
                                    "hrk": "HRK",
                                    "htg": "HTG",
                                    "huf": "HUF",
                                    "idr": "IDR",
                                    "ils": "ILS",
                                    "inr": "INR",
                                    "isk": "ISK",
                                    "jmd": "JMD",
                                    "jpy": "JPY",
                                    "kes": "KES",
                                    "kgs": "KGS",
                                    "khr": "KHR",
                                    "kmf": "KMF",
                                    "krw": "KRW",
                                    "kyd": "KYD",
                                    "kzt": "KZT",
                                    "lak": "LAK",
                                    "lbp": "LBP",
                                    "lkr": "LKR",
                                    "lrd": "LRD",
                                    "lsl": "LSL",
                                    "mad": "MAD",
                                    "mdl": "MDL",
                                    "mga": "MGA",
                                    "mkd": "MKD",
                                    "mmk": "MMK",
                                    "mnt": "MNT",
                                    "mop": "MOP",
                                    "mro": "MRO",
                                    "mur": "MUR",
                                    "mvr": "MVR",
                                    "mwk": "MWK",
                                    "mxn": "MXN",
                                    "myr": "MYR",
                                    "mzn": "MZN",
                                    "nad": "NAD",
                                    "ngn": "NGN",
                                    "nio": "NIO",
                                    "nok": "NOK",
                                    "npr": "NPR",
                                    "nzd": "NZD",
                                    "pab": "PAB",
                                    "pen": "PEN",
                                    "pgk": "PGK",
                                    "php": "PHP",
                                    "pkr": "PKR",
                                    "pln": "PLN",
                                    "pyg": "PYG",
                                    "qar": "QAR",
                                    "ron": "RON",
                                    "rsd": "RSD",
                                    "rub": "RUB",
                                    "rwf": "RWF",
                                    "sar": "SAR",
                                    "sbd": "SBD",
                                    "scr": "SCR",
                                    "sek": "SEK",
                                    "sgd": "SGD",
                                    "shp": "SHP",
                                    "sll": "SLL",
                                    "sos": "SOS",
                                    "srd": "SRD",
                                    "std": "STD",
                                    "szl": "SZL",
                                    "thb": "THB",
                                    "tjs": "TJS",
                                    "top": "TOP",
                                    "try": "TRY",
                                    "ttd": "TTD",
                                    "twd": "TWD",
                                    "tzs": "TZS",
                                    "uah": "UAH",
                                    "ugx": "UGX",
                                    "usd": "USD",
                                    "uyu": "UYU",
                                    "uzs": "UZS",
                                    "vnd": "VND",
                                    "vuv": "VUV",
                                    "wst": "WST",
                                    "xaf": "XAF",
                                    "xcd": "XCD",
                                    "xof": "XOF",
                                    "xpf": "XPF",
                                    "yer": "YER",
                                    "zar": "ZAR",
                                    "zmw": "ZMW"
                                }})
                            ),
                            FormField(
                                id="customer_id",
                                name="Customer ID",
                                description="Provide a path to the ID of the customer that you want to charge.",
                                component=FormComponent(type="dotPath", props={"label": "Customer ID"})
                            ),
                            FormField(
                                id="payment_source",
                                name="Payment source",
                                description="Provide the payment source to be charged, e.g. ID of a card, bank account,"
                                            " etc.",
                                component=FormComponent(type="dotPath", props={"label": "Source"})
                            ),
                            FormField(
                                id="receipt_email",
                                name="Receipt email",
                                description="Provide a path to the email that the receipt will be sent to.",
                                component=FormComponent(type="dotPath", props={"label": "Email"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Create charge with Stripe',
            desc='Creates new charge using Stripe, according to given configuration.',
            icon='plugin',
            group=["Connectors"],
            brand="Stripe",
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "success": PortDoc(
                        desc="This port returns Stripe API response if the charge was created successfully."
                    ),
                    "error": PortDoc(
                        desc="This port returns Stripe API response if the charge was not created successfully."
                    )
                }
            )
        )
    )
