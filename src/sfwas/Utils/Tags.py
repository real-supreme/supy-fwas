import coc


class BaseTag:
    __slots__ = ("tag",)


class sfwasTag:
    def __init__(self, client, tag=None, **kwargs):
        self.tag = tag
        self._type = None
        if isinstance(client, coc.Client):
            self.client = client
        else:
            raise TypeError("Client must be a coc.Client object")

    def __repr__(self):
        return (
            f"<sfwasTag {self.tag}>"
            if self.tag
            else f"<sfwasTag {self.__class__.__name__}>"
        )

    def verify_tag(self, tag):
        raise NotImplemented
