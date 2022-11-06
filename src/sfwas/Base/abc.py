class MetaSFWAS(type):
    def __new__(cls, name, bases, dct: dict):

        if bases:
            if not bases[0].__name__.lower().startswith("base"):
                raise TypeError("BaseSFWAS must be the base class")
            d = dct.copy()
            for k, v in d.items():
                try:
                    if k.startswith("_") and not k.startswith("__") or v.isupper():
                        dct.pop(k)
                except AttributeError:
                    ...
            del d
            # dct["__slots__"] = tuple(dct.keys())

        return super().__new__(cls, name, bases, dct)

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.__dict__})>"

    def __str__(self):
        return f"{self.__class__.__name__}"
