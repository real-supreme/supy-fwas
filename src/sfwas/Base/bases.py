import json

from .abc import MetaSFWAS
from functools import lru_cache
from requests import Session
from .exceptions import *
from Utils.enums import Route
from coc.utils import is_valid_tag, correct_tag
from coc import BaseClan, BasePlayer
import re

BASE_URL = "https://www.fwastats.com"

__all__ = ("BaseSFWAS", "SFEmptyClan", "BaseSFPlayer", "BaseSFClan")


class BaseConnector(Session):
    def __init__(self, prep=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers.update({"User-Agent": "SupyFWA/1.0.0"})
        if prep is not None:
            self.prep = prep  # method to prep url
        else:
            self.prep = (
                lambda url: url + ".json" if not url.endswith(".json") else url
            )  # will miss out other validators

    def get(self, url, **kwargs):
        try:
            url = self.prep(url)
        except:
            ...

        return super().get(url, **kwargs)


class BaseSFWAS(metaclass=MetaSFWAS):
    def __init__(self, *, connector=None, tries=3, **kwargs):
        if connector:
            if not isinstance(connector, Session):
                raise TypeError("Connector must be a Connector object")
            self.connector = connector
        else:
            self.connector = BaseConnector(self._prep_url)
        self.tries = tries
        self.BASE_URL = kwargs.get("base_url") or BASE_URL
        super().__init__()

    def PATH(self, tag=None):
        if tag:
            return Route.dict_(tag)
        return Route.dict_()

    @lru_cache(maxsize=100)
    def _get(
        self, url, *, raw: bool = False, connector: Session = None, tries: int = 0
    ):
        try:

            if connector is not None:
                self.connector = connector
            res = self.connector.get(url)

            if res.status_code == 200:
                if raw:
                    return res.text
                return res.json()
            else:
                if res.status_code == 404:
                    raise NotFound("Clan not found!")
                raise SFConnectionError(res.status_code)
        except SFConnectionError as e:
            if tries < self.tries:
                return self._get(url, raw=raw, tries=tries + 1)
            else:
                raise e

    @staticmethod
    @lru_cache(maxsize=100)
    def _get_static(
        url: str,
        *,
        raw: bool = False,
        connector: Session = BaseConnector(),
        tries: int = 3,
    ):
        try:

            res = connector.get(url)
            if res.status_code == 200:
                if raw:
                    return res.text
                return res.json()
            else:
                if res.status_code == 404:

                    raise NotFound("Clan not found!")
                raise SFConnectionError(res.status_code)
        except SFConnectionError as e:
            if tries > 0:
                return BaseSFWAS._get_static(
                    url, raw=raw, connector=connector, tries=tries - 1
                )
            else:
                raise e

    @lru_cache(maxsize=100)
    def _filter_to_json(self, tag: str, content: str):
        si = re.search(r'{\s*"tag":\s*"' + tag + r'".*?}', content)

        if si is None and content.find(tag) == -1:
            raise NotFound("Tag not found in FWA Stats")
        elif si is None:
            si = content.find(tag) - 8
        else:
            si = si.span()[0]

        ei = re.search(r"}(,|])", content[si:]).span()[0]
        try:
            return json.loads(content[si : si + ei + 1])
        except (json.JSONDecodeError, IndexError):
            raise NotFound("Tag not found in FWA Stats")

    @lru_cache(maxsize=128)
    def _all_fwa(self, *, raw=False):
        url = f"{self.BASE_URL}{self.PATH()['ALL_CLANS']}"
        url = self._prep_url(url)
        return self._get(url, raw=raw)

    @lru_cache(maxsize=128)
    def _get_member_weights(self, *, raw=False):
        """
        Uses general weights info to retrieve weights of all members
        """
        url = f"{self.BASE_URL}{self.PATH()['WEIGHTS']}"
        url = self._prep_url(url)
        return self._get(url, raw=raw)

    def validate_tag(self, tag):
        tag = correct_tag(tag)
        if not is_valid_tag(tag):
            raise ValueError("Invalid clan tag")
        return tag

    def _prep_url(self, url):
        if self._is_url_valid(url):
            url = url.replace(" ", "%20").replace("#", "%23")
            url = url + ".json" if not url.endswith(".json") else url
            return url
        else:

            raise SFInvalidURL()

    @lru_cache(maxsize=128)
    def _is_FWA(self, clan_tag):
        """Check if a clan is in FWA."""
        try:
            clan_tag = self.validate_tag(clan_tag)
        except ValueError:
            return False
        _all = self._all_fwa(raw=True)
        if _all.find(clan_tag) != -1:
            return True
        return False

    def _get_member_weight(self, tag):
        all_member = self._get_member_all(tag, raw=True)
        try:
            return self._filter_to_json(tag, all_member).get("weight", 0)
        except NotFound:
            raise NotFound("Member not found in clan")

    def _get_member_all(self, clan_tag, *, raw=False):
        """
        Get all members from a clan
        """
        url = f"{self.BASE_URL}{self.PATH(clan_tag)['MEMBERS']}"
        url = self._prep_url(url)
        return self._get(url, raw=raw)

    def _is_url_valid(self, url: str):
        m = re.match(r"^https?://(www\.)?fwastats\.com/[a-zA-Z0-9#\%/]+", url)
        return m is not None

    def fwa_clans(self, function):  # Decorator
        """Decorator to allow only tags related to FWA."""

        def wrapper(*args, **kwargs):
            import time

            t = time.time()

            tag = kwargs.get("tag", None)
            if not args and tag is None:
                if function.__defaults__:  # If there are default arguments
                    tag = function.__defaults__[0]
            elif args:
                tag = args[0]
            if self._is_FWA(tag):
                t2 = time.time() - t

                return function(*args, **kwargs)

        return wrapper

    @lru_cache(maxsize=128)
    def _member_in_fwa(self, tag):
        try:
            tag = self.validate_tag(tag)
        except ValueError:
            return False
        _all = self._get_member_weights(raw=True)
        if _all.find(tag):
            return True
        return False

    @lru_cache(maxsize=128)
    def _get_from_clan(self, tag, *, raw=False):
        """Get members from clan"""
        tag = self.validate_tag(tag)
        url = f"{BASE_URL}{self.PATH(tag)['MEMBERS']}"
        url = self._prep_url(url)
        return self._get(url, raw=raw)


class BaseSFClan(metaclass=MetaSFWAS):
    def __init__(self, tag, **data):
        self.tag = tag
        self._from_data(**data)

    def _from_data(self, **kwargs):
        self._clan = kwargs.pop("clan", BaseClan)
        self._members = kwargs.pop("members", [])
        self.name = kwargs.pop("name", "")
        self.level = kwargs.pop("level", 0)
        self.location = kwargs.pop("location", "")
        self.required_trophies = kwargs.pop("requiredTrophies", 0)
        self.war_frequency = kwargs.pop("warFrequency", "")
        self.win_streak = kwargs.pop("winStreak", 0)
        self.wins, self.ties, self.losses = (
            kwargs.pop("warWins", 0),
            kwargs.pop("warTies", 0),
            kwargs.pop("warLosses", 0),
        )
        self.warlog = kwargs.pop("isWarLogPublic", False)
        if self.warlog is not False and not isinstance(self.warlog, bool):
            self.warlog = bool(
                self.warlog.replace("True", "true").replace("False", "false")
            )
        self.description = kwargs.pop("description", "")
        self.badge_url = kwargs.pop("image", "")
        self._composition = {
            "14": kwargs.pop("th14Count", 0),
            "13": kwargs.pop("th13Count", 0),
            "12": kwargs.pop("th12Count", 0),
            "11": kwargs.pop("th11Count", 0),
            "10": kwargs.pop("th10Count", 0),
            "9": kwargs.pop("th9Count", 0),
            "8": kwargs.pop("th8Count", 0),
            "7&below": kwargs.pop("thLowCount", 0),
        }
        self.EstWeight = kwargs.pop("estimatedWeight", 0)
        self.data = kwargs
        if not self.data:
            del self.data
        self.bs = BaseSFWAS()

    def _get_members(self, cls_):
        if self.tag:
            url = f"{BASE_URL}{self.bs.PATH(self.tag)['MEMBERS']}"
        else:
            url = f"{BASE_URL}{self.bs.PATH()['MEMBERS']}"
        try:
            data = BaseSFWAS._get_static(url=url)
        except SFConnectionError:
            return []  # offline
        for member in data:
            yield cls_(**member)

    def _get_war(self, cls_):
        if self.tag:
            url = f"{BASE_URL}{self.bs.PATH(self.tag)['CLAN_WARS']}"
        else:
            url = f"{BASE_URL}{self.bs.PATH()['CLAN_WARS']}"
        try:
            data = BaseSFWAS._get_static(url=url)
        except SFConnectionError:
            return []
        return cls_(**data)

    def __str__(self):
        return f"Clan {self.name} ({self.tag})"

    def __repr__(self):
        return f"SFClan({self.name}, {self.tag})"


class SFEmptyClan:

    __slots__ = ("description", "player_tag")

    def __init__(self, player_tag):
        self.player_tag = player_tag
        self.description = "Not in clan"

    def __str__(self):
        return self.description

    def __dict__(self):
        return {"description": self.description, "player_tag": self.player_tag}

    def get_player(self):
        return BaseSFPlayer(self.player_tag)


class BaseSFPlayer(metaclass=MetaSFWAS):
    # """{
    #     "tag": "#8VJVQYUUQ",
    #     "name": "⚡KONSTANTINOS⚡",
    #     "role": "Elder",
    #     "level": 220,
    #     "donated": 2887,
    #     "received": 3273,
    #     "rank": 1,
    #     "trophies": 5445,
    #     "league": "Legend League",
    #     "townHall": 14,
    #     "weight": 139000,
    #     "inWar": true,
    # }"""

    def __init__(self, tag, **data):
        self.tag = tag
        self._from_data(**data)

    def _from_data(self, **kwargs):

        self.name = kwargs.pop("name", "")
        self.level = kwargs.pop("level", 0)
        self._clan = kwargs.pop("clan", BaseClan)
        if not isinstance(self._clan, (BaseClan, BaseSFClan, str)):
            self.clan = SFEmptyClan(self.tag)
        else:
            self.role = kwargs.pop("role", "")
        if isinstance(self._clan, (str, BaseSFClan)):
            try:
                self.clan_tag = self._clan.tag
            except AttributeError:
                self.clan_tag = self._clan
        else:
            self.clan_tag = None
        self.exp_level = kwargs.pop("level", 0)
        self.donated = kwargs.pop("donated", 0)
        self.received = kwargs.pop("received", 0)
        self.position_in_clan = kwargs.pop("rank", 0)
        self.trophies = kwargs.pop("trophies", 0)
        self.league = kwargs.pop("league", "")
        self.townhall = kwargs.pop("townhall", 0)
        self.in_war = bool(str(kwargs.pop("inWar", False)).capitalize())
        weight = kwargs.pop("weight", 0)
        last_modified = kwargs.pop("lastModified", 0)
        self._weight = BaseSFWeights(
            self.tag, weight=weight, lastModified=last_modified, townhall=self.townhall
        )
        self.bs = BaseSFWAS()
        try:
            self._war = kwargs.pop("war")
        except KeyError:
            self._war = None
        if not isinstance(self._war, (BaseSFWar, dict)):
            self.war = {}
        elif isinstance(self._war, dict):
            self.war = BaseSFWar(**self._war)
        else:
            self.war = self._war

    def _clan_war(self, cls_):

        if not hasattr(self, "_clan"):
            self._get_detailed()
        try:
            data = self.bs._get_clanwars(self.clan_tag)
        except SFConnectionError:
            return None
        return cls_(**data)

    def _get_detailed(self):
        """
        Fill in the rest of the data (clan, weights) by making a second call.
        """
        # IF clan.player ->:
        # """{
        #     "tag": "#QJ2C8C98C",
        #     "name": "TouchMe",
        #     "role": "Member",
        #     "level": 52,
        #     "donated": 33,
        #     "received": 51,
        #     "rank": 41,
        #     "trophies": 1303,
        #     "league": "Unranked",
        #     "townHall": 13,
        #     "weight": 103000,
        #     "inWar": false,
        # }"""
        # IF weights..player ->:
        # {"tag":"#9U0G8RUL","weight":143000,"townhall":15,"lastModified":"2022-10-30T17:44:42Z"}

        self.bs._get_clanwars(self.clan_tag)
        data = self.bs._filter_to_json(self.tag, data)
        self._from_data(**data)

        if (hasattr(self, "weight") and not self.weight) or not hasattr(self, "weight"):
            try:
                stripped = self.bs._get_member_weight(self.tag)
            except NotFound:  # Unregistered player
                stripped = {}
            except Exception as e:
                raise e
            if isinstance(stripped, BaseSFWeights):
                self._weight = stripped
            else:
                self._weight = BaseSFWeights(self.tag, **stripped)

    def __str__(self):
        return f"Player {self.name} ({self.tag})"

    def __repr__(self):
        return f"SFPlayer({self.name}, {self.tag})"


class BaseSFWar(metaclass=MetaSFWAS):
    # """{
    #     "endTime": "2022-09-01T00:00:00Z",
    #     "result": "lose",
    #     "teamSize": 50,
    #     "clanTag": "#LGQJYLPY",
    #     "clanName": "War Farmers 18",
    #     "clanLevel": 29,
    #     "clanStars": 95,
    #     "clanDestructionPercentage": 53.8,
    #     "clanAttacks": 84,
    #     "clanExpEarned": 480,
    #     "opponentTag": "#99YQ89QJ",
    #     "opponentName": "Holder Origins",
    #     "opponentLevel": 25,
    #     "opponentStars": 112,
    #     "opponentDestructionPercentage": 73.52,
    #     "synced": true,
    #     "matched": true,
    # }"""

    def __init__(self, **data):
        self._from_data(**data)

    def _from_data(self, **data):
        self._clan = data.pop("clan", BaseClan)
        try:
            if isinstance(self.clan, dict):
                self._clan = BaseSFClan(**self.clan)
            elif isinstance(self.clan, BaseClan):
                self._clan = BaseSFClan(**data)
        except (NotFound, AttributeError):
            raise NotFound("Clan not found")
        self.clan_tag = data.pop("clanTag", "")
        self.opp_tag = data.pop("opponentTag", "")
        self.opp_name = data.pop("opponentName", "")
        self.end_time = data.pop("endTime", 0)
        self.result = data.pop("result", "")
        self.team_size = data.pop("teamSize", 0)
        self.stars = data.pop("clanStars", 0)
        self.clan_attacks = data.pop("clanAttacks", 0)
        self.exp_earned = data.pop("expEarned", 0)
        self.opp_stars = data.pop("opponentStars", 0)
        self.opp_desctruction = data.pop("opponentDestructionPercentage", 0)
        self.is_synced = bool(str(data.pop("synced", False)).capitalize())
        self.matched_fwar = bool(str(data.pop("matched", False)).capitalize())

    @property
    def clan(self):
        if isinstance(self._clan, (BaseClan, BaseSFClan)):
            return self._clan
        raise NotFound()

    def __iter__(self):
        try:
            for member in self.clan.members:
                yield member
        except (NotFound, AttributeError):
            raise StopIteration


class BaseSFWeights(metaclass=MetaSFWAS):
    # """{
    #     "tag": "#8J2Q8UCQ",
    #     "weight": 140000,
    #     "townhall": 14,
    #     "lastModified": "2022-03-21T15:30:33Z",
    # }"""

    def __init__(self, tag, **data):
        self.tag = tag
        self._from_data(**data)

    def _from_data(self, **data):
        self.amount = data.pop("weight", 0)
        self.townhall = data.pop("townhall", 0)
        self.last_modified = data.pop("lastModified", 0)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.tag} {self.weight}>"
