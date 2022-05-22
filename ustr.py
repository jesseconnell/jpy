class UStr(str):
    def __new__(cls, *args):
        if args and type(args[0]) is int:
            n = args[0]
            args = tuple(r for r in args[1:])
        elif len(args) == 2 and type(args[1]) is int:
            n = args[1]
            args = tuple(args[0])
        else:
            n = -1

        o = str.__new__(cls, *args)
        o.n = n
        return o

    def full(self):
        srepr = super().__repr__()
        return f"UStr[{self.n}/{srepr}]"

    def __repr__(self):
        return super().__repr__()

    def _cmp(self, other):
        n2 = other.n if type(other) is UStr else -1
        a = (self.n, str(self),)
        b = (n2, str(other),)
        if a < b: return -1
        if a > b: return 1
        return 0

    def __lt__(self, other):
        return self._cmp(other) == -1

    def __gt__(self, other):
        return self._cmp(other) == 1

    def __eq__(self, other):
        return self._cmp(other) == 0

    def __hash__(self):
        return self.full().__hash__()

    # return (self.n, str(self),) < (n2, str(other),)

def _test():
    u = UStr("hi")
    print(u)

    l = [UStr(i, "test") for i in [1111, 62, 3, 4]]
    print(l)
    print([s.full() for s in sorted(l)])
    print(sorted(s.full() for s in l))

    print(f"Compare {l[0].full()} == {l[1].full()} (_cmp={l[0]._cmp(l[1])}): {l[0] == l[1]}")
    print(f"Compare {l[0].full()} <  {l[1].full()} (_cmp={l[0]._cmp(l[1])}): {l[0] < l[1]}")
    print(f"Compare {l[0].full()} >  {l[1].full()} (_cmp={l[0]._cmp(l[1])}): {l[0] > l[1]}")
    print(l[0].full())
    print(l[1].full())

    import json
    d = dict()
    for i in range(10):
        d[UStr(i, "key")] = i*i

    print(json.dumps(d))

if __name__ == '__main__':
    _test()