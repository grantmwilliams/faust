"""Leader assignor."""
from typing import Any
from mode import Service
from ..types import AppT, TP, TopicT
from ..types.assignor import LeaderAssignorT
from ..utils.objects import cached_property


class LeaderAssignor(Service, LeaderAssignorT):
    """Leader assignor, ensures election of a leader."""

    def __init__(self, app: AppT, **kwargs: Any) -> None:
        Service.__init__(self, **kwargs)
        self.app = app

    async def on_start(self) -> None:
        await self._leader_topic.maybe_declare()
        self.app.topics.add(self._leader_topic)

    @cached_property
    def _leader_topic(self) -> TopicT:
        return self.app.topic(
            self._leader_topic_name,
            partitions=1,
            acks=False,
            internal=True,
        )

    @cached_property
    def _leader_topic_name(self) -> str:
        return f'{self.app.conf.id}-__assignor-__leader'

    @cached_property
    def _leader_tp(self) -> TP:
        return TP(self._leader_topic_name, 0)

    def is_leader(self) -> bool:
        return self._leader_tp in self.app.consumer.assignment()
