from .Base import BaseSFPlayer, BaseSFClan, SFEmptyClan, BaseSFWeights
from .SFPlayerClan import SFPlayerClan, SFPlayerWarClan


class SFPlayer(BaseSFPlayer):
    def __init__(self, tag, **kwargs):
        super().__init__(tag, **kwargs)

    @property
    def clan(self):
        self._get_detailed()
        if isinstance(self._clan, (BaseSFClan, SFEmptyClan)):
            return self._clan
        if self._clan:
            return SFPlayerClan(self.clan_tag, **self._clan)
        return SFPlayerClan(self.clan_tag)

    @clan.setter
    def clan(self, _clan):
        if isinstance(_clan, (BaseSFClan, SFEmptyClan)):
            self._clan = _clan
        else:
            raise TypeError("clan must be a BaseSFClan or SFEmptyClan object")

    @property
    def war_clan(self):
        if isinstance(self.clan.war, type):
            return self.clan.war
        return self._clan_war(SFPlayerWarClan)

    @property
    def weight(self):
        if (
            self._weight is not None
            and isinstance(self._weight, BaseSFWeights)
            and self._weight.townhall > 0
        ):
            return self._weight
        self._get_detailed()
        return self._weight


__all__ = ("SFPlayer",)
