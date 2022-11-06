from .Base.bases import BaseSFClan, BaseSFWar
from .SFPlayer import SFPlayer


class SFClan(BaseSFClan):
    def __init__(self, tag, **kwargs):
        super().__init__(tag, **kwargs)

    @property
    def members(self):
        if len(self._members) == 0:
            self._members = [f for f in self._get_members(cls_=SFPlayer)]
        return self._members

    @property
    def members_iter(self):
        for i in self._get_members(cls_=SFPlayer):
            yield i

    @property
    def clan_weight(self):
        return sum([f.weight for f in self.members])

    @property
    def clan_estimated_weight(self):
        return self.EstWeight * 1000

    @property
    def war(self):
        if hasattr(self, "_war") and isinstance(self._war, type):
            return self._war
        self._war = self._get_war(cls_=SFWarClan)
        return self._war

    @property
    def composition(self):
        return self._composition

    @property
    def composition_iter(self):
        yield self._composition.items()


class SFWarClan(BaseSFWar):
    def __init__(self, tag, **kwargs):
        self.__data = kwargs
        super().__init__(tag, **kwargs)

    @property
    def clan(self):
        return SFClan(tag=self.clan_tag, **self.__data)

    @property
    def opponent(self):
        return SFClan(tag=self.opp_tag, **self.__data)

    @property
    def war_members(self):
        return [f for f in self.__iter__()]

    @property
    def war_members_iter(self):
        for i in self.__iter__():
            yield i


__all__ = ("SFClan", "SFWarClan")
