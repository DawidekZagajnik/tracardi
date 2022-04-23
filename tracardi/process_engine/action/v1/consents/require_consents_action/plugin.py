from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.plugin.domain.result import Result
from tracardi.service.storage.driver import storage
from tracardi.domain.consent_type import ConsentType
from pytimeparse import parse


def validate(config: dict) -> Config:
    return Config(**config)


class RequireConsentsAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = Config(**kwargs)

    async def run(self, payload):
        if self.event.metadata.profile_less is True:
            self.console.warning("Cannot perform consent check on profile less event.")
            return Result(port="false", value=payload)

        self.config.consent_ids = [consent["id"] for consent in self.config.consent_ids]

        for consent_id in self.config.consent_ids:
            consent_type = await storage.driver.consent_type.get_by_id(consent_id)

            if consent_type is None:
                raise ValueError(f"There is no consent type with ID {consent_id}")
            consent_type = ConsentType(**consent_type)

            if self.config.require_all is True:
                if consent_id not in self.profile.consents:
                    return Result(port="false", value=payload)

                if consent_type.revokable is True:
                    try:
                        revoke_timestamp = self.profile.consents[consent_id].revoke.timestamp() + \
                            parse(consent_type.auto_revoke)
                    except AttributeError:
                        raise ValueError(f"Corrupted data - no revoke date provided for revokable consent "
                                         f"type {consent_id}")

                    if revoke_timestamp <= self.event.metadata.time.insert.timestamp():
                        return Result(port="false", value=payload)

            else:
                if consent_id in self.profile.consents:
                    if consent_type.revokable is False:
                        return Result(port="true", value=payload)

                    try:
                        revoke_timestamp = self.profile.consents[consent_id].revoke.timestamp() + \
                            parse(consent_type.auto_revoke)
                    except AttributeError:
                        raise ValueError(f"Corrupted data - no revoke date provided for revokable consent "
                                         f"type {consent_id}")

                    if revoke_timestamp > self.event.metadata.time.insert.timestamp():
                        return Result(port="true", value=payload)

        return Result(port="true" if self.config.require_all is True else "false", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='RequireConsentsAction',
            inputs=["payload"],
            outputs=["true", "false"],
            version='0.6.2',
            license="MIT",
            author="Dawid Kruk",
            manual="require_consents_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Consent requirements",
                        fields=[
                            FormField(
                                id="consent_ids",
                                name="IDs of required consents",
                                description="Provide a list of IDs of consents that are required.",
                                component=FormComponent(type="consentTypes")
                            ),
                            FormField(
                                id="require_all",
                                name="Require all",
                                description="If set to ON, plugin will require all consents to be present and not "
                                            "revoked. If set to OFF, plugin will require only on of provided consents.",
                                component=FormComponent(type="bool", props={"label": "Require all"})
                            )
                        ]
                    )
                ]
            ),
            init={
                "consent_ids": [],
                "require_all": False
            }
        ),
        metadata=MetaData(
            name='Require consents',
            desc='Checks if defined consents are granted by current profile.',
            icon='plugin',
            group=["Consents"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "true": PortDoc(desc="This port returns given payload if defined consents are granted."),
                    "false": PortDoc(desc="This port returns given payload if defined consents are not granted.")
                }
            )
        )
    )
