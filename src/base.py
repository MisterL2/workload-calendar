class Base():
    def __ge__(self,other) -> bool:
        return self > other or self == other
    def __le__(self,other) -> bool:
        return self < other or self == other