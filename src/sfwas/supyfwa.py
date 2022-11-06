import re, json
from .Base.exceptions import NotFound
from .Base.bases import BaseSFWAS, BaseSFWeights, SFEmptyClan
from .SFPlayer import SFPlayer
from .SFClans import SFClan

__all__ = ("SFWAS",)


class SFWAS(BaseSFWAS):
    """
    Easy and convenient way to get FWA Stats.
    """

    def __init__(self, **kwargs):
        """
        SupyFWA is a wrapper for FWA Stats API.

        @param kwargs: Keyword arguments to pass to the BaseSFWAS class.
        tries: Number of times to retry a request if it fails.
        connector: requests.Session() object to use for requests.
        """
        tries = kwargs.get("tries", 3)
        connector = kwargs.get("connector", None)
        super().__init__(connector=connector, tries=tries, **kwargs)

    def is_member_in_fwa(self, tag):
        """
        Checks if the member is in FWA Stats. If True, you can use the tag to retrieve the member's weights.
        """
        return self._member_in_fwa(tag)

    def is_clan_fwa(self, tag):
        return self._is_FWA(tag)

    def get_fwa_clans(self):
        """
        Iterates through all the clans in FWA Stats and yields a SFClan object for each clan.
        """
        clans = self._all_fwa()
        return map(lambda x: SFClan(**x), clans)

    def get_member(self, *, player_tag: str, clan_tag: str, cls_=SFPlayer):
        try:

            get_all = self._get_from_clan(clan_tag, raw=True)

            return cls_(clan=clan_tag, **self._filter_to_json(player_tag, get_all))
        except NotFound:
            raise NotFound(
                "Member %s not found in FWA Stats for given clan tag %s"
                % (player_tag, clan_tag)
            )
        except Exception as e:
            raise e

    def get_clan(self, tag: str):
        clan = self._all_fwa(raw=True)
        try:
            clan = self._filter_to_json(tag, clan)
        except Exception as e:
            raise e.with_traceback(e.__traceback__)
        return SFClan(**clan)

    def get_member_weight(self, player_tag: str):
        try:
            return self._get_member_weight(player_tag)
        except BaseException:
            raise NotFound("Member not found in FWA Stats")

    def get_member_weight_from_clan(self, *, player_tag: str, clan_tag: str):
        try:
            r = self._get_member_weights()  # if available already, then save time
            return self._filter_to_json(player_tag, r)
        except BaseException:
            ...
        c = self._get_from_clan(clan_tag, raw=True)
        try:
            player = self._filter_to_json(player_tag, c)
        except NotFound:
            raise NotFound("Member not found in clan")
        else:
            return player.get("weight", 0)

    def get_clan_weight(self, tag: str):
        clans = self._all_fwa(raw=True)
        try:
            clan = self._filter_to_json(tag, clans)
            return clan["estimatedWeight"] * 1000
        except:
            raise NotFound("Clan not found in FWA Stats")

    def get_clan_by_name(self, name):
        clans = self._all_fwa(raw=True)
        si, ei = re.search(
            r'{"tag":"#[A-Za-z0-9]+","name":\s*"' + name + r'".*?},?', clans
        ).span(0)
        try:
            return SFClan(**json.loads(clans[si:ei].strip(",")))
        except:
            raise NotFound("Clan not found in FWA Stats")
