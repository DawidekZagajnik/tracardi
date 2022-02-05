from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.configuration import Configuration


def validate(config: dict):
    return Configuration(**config)


class StartAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload):
        self.event.metadata.debug = self.config.debug

        if self.debug is True:
            self.event.metadata.debug = True
            if not self.node.has_input_node(self.flow.flowGraph.nodes, class_name='DebugPayloadAction'):
                raise ValueError("Start action can not run in debug mode without connection to Debug action.")

        allowed_event_types = self.config.get_allowed_event_types()

        if len(allowed_event_types) > 0 and self.event.type not in self.config.get_allowed_event_types():
            return None

        return Result(port="payload", value={})


def register() -> Plugin:
    return Plugin(
        start=True,
        debug=False,
        spec=Spec(
            module=__name__,
            className='StartAction',
            inputs=["payload"],
            outputs=["payload"],
            init={
                "debug": False,
                "events": []
            },
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="debug",
                            name="Collect debugging information",
                            description="Set if you want to collect debugging information. Debugging collects a lot of "
                                        "data if you no longer need to test your workflow disable it to save data and "
                                        "compute power.",
                            component=FormComponent(type="bool", props={"label": "Collect debugging information"})
                        ),
                        FormField(
                            id="events",
                            name="Trigger start on these event types",
                            description="If left empty triggers regardless the event type.",
                            component=FormComponent(type="eventTypes", props={"label": "Event types"})
                        ),
                    ]
                ),
            ]),
            version='0.6.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Start',
            desc='Starts workflow and returns empty payload.',
            keywords=['start node'],
            type="startNode",
            icon='start',
            group=["Input/Output"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON like object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns empty payload object.")
                }
            )
        )
    )
