class EnumMeta(type):
    def __new__(cls, name, bases, dct: dict):
        s = []
        l = []
        for k, v in dct.items():
            if isinstance(v, str) and v.find("{tag}") != -1:
                s.append(k)
            if not k.startswith("__") and k.isupper():
                # l.append(k)
                setattr(cls, k, v)

        dct["tagged"] = s

        return super().__new__(cls, name, bases, dct)


class Enum(metaclass=EnumMeta):
    def __init__(**kwargs):
        ...


class Route(Enum):
    ALL_CLANS = "/Clans"
    WEIGHTS = "/Weights"
    WARS = "/Wars"
    CLAN = "/Clan/{tag}"
    CLAN_WARS = CLAN + WARS
    MEMBERS = CLAN + "/Members"

    @staticmethod
    def dict_(tag=None) -> dict:
        """
        Returns a dictionary of the route with the tag replaced.
        """

        if tag and hasattr(Route, "tagged"):
            tag = tag.replace("#", "").replace("O", "0").strip().upper()
            return {
                k: v.format(tag=tag)
                for k, v in Route.__dict__.items()
                if k in Route.tagged
            }
        return {k: getattr(Route, k) for k in Route.__dict__}


class Try_Enum:
    def __init__(self, cls_: type, **inputs: dict):
        self.cls_ = cls_
        self.inputs = inputs
        self.data = cls_(**inputs)
        raise NotImplemented
