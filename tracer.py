import sys
import pprint
import json
import xml.etree.ElementTree as ET
from collections import *
import ustr


HACKTAGNAME = ""
def HACK_tagname(t):
    return t.replace(HACKTAGNAME, "")

Frame = namedtuple("Frame", ["depth", "fn", "args", "kwargs"])


class _colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BLUE = "\033[0;33m"
    YELLOW = "\033[0;34m"
    CYAN = "\033[0;35m"
    MAGENTA = "\033[0;36m"
    WHITE = "\033[0;37m"
    HIRED = "\033[1;31m"
    HIGREEN = "\033[1;32m"
    HIBLUE = "\033[1;33m"
    HIYELLOW = "\033[1;34m"
    HICYAN = "\033[1;35m"
    HIMAGENTA = "\033[1;36m"
    HIWHITE = "\033[1;37m"
    NORM = "\033[0m"


def _framestr(f: Frame):
    return "{}({})".format(f.fn, ','.join(str(a) for a in f.args))


class Tracer(object):
    def __init__(self, name: str, out=sys.stdout):
        self._name = name
        self._header = f"[{name.upper()}]"
        self._out = out
        self._indent = "    "
        self._stack = []

    def name(self):
        return self._name

    def header(self):
        return self._header

    def depth(self):
        return len(self._stack)

    def indent(self):
        return self._indent * self.depth()

    def format(self, s, *args):
        f = s.format(*args) if args else s
        return "{} {} {} {}".format(
            self.header(),
            self.depth(),
            self.indent(),
            f)

    def print(self, s, *args, out=None):
        out = out if out else self._out
        text = self.format(s, *args)

        if True:
            text = text \
                .replace("HIRED", _colors.HIRED) \
                .replace("HIGREEN", _colors.HIGREEN) \
                .replace("HIBLUE", _colors.HIBLUE) \
                .replace("HIYELLOW", _colors.HIYELLOW) \
                .replace("HICYAN", _colors.HICYAN) \
                .replace("HIMAGENTA", _colors.HIMAGENTA) \
                .replace("HIWHITE", _colors.HIWHITE) \
                .replace("RED", _colors.RED) \
                .replace("GREEN", _colors.GREEN) \
                .replace("BLUE", _colors.BLUE) \
                .replace("YELLOW", _colors.YELLOW) \
                .replace("CYAN", _colors.CYAN) \
                .replace("MAGENTA", _colors.MAGENTA) \
                .replace("WHITE", _colors.WHITE) \
                .replace("NORM", _colors.NORM)
        out.write(text)
        out.write("\n")

    def __pprint(self, name, object, printer, out):
        text = printer.pformat(object)
        name = name + ": " if name else ""
        altname = " " * len(name)

        for l in text.split("\n"):
            self.print("{} {}".format(name, l), out=out)
            name = altname

    def pprint(self, *args, width=80, depth=None, compact=False, out=None, **kwargs):
        printer = pprint.PrettyPrinter(width=width, depth=depth, compact=compact)
        name = ""
        if len(args) >= 1:
            if len(args) > 1:
                if type(args[0]) is str:
                    name, args = args[0], args[1:]
            for obj in args:
                self.__pprint(name, obj, printer, out)

        for k, v in kwargs.items():
            self.__pprint(f"{name} {k}", v, printer=printer, out=out)

    def enter(self, fn, *args, **kwargs):
        if not args:
            args = kwargs.get("args", ())
        frame = Frame(depth=self.depth(), fn=fn, args=args, kwargs=kwargs)
        self.print(f"{_framestr(frame)} HIGREEN{{NORM")
        self._stack.append(frame)
        return frame

    def gen_callstack(self):
        for depth, info in enumerate(self._stack):
            fn, args, kwargs = info
            yield Frame(depth=depth, fn=fn, args=args, kwargs=kwargs)

    def gen_keystack(self):
        for f in self.callstack():
            yield f.kwargs.get("key", "")

    def calls(self):
        return list(self.gen_callstack())

    def keys(self):
        return list(self.gen_keystack())

    def str(self):
        return str(self.calls())

    def exit(self):
        if self._stack:
            frame = self._stack.pop()
            self.print(f"HIWHITE}}NORM /// returning from {_framestr(frame)}")
        self._out.flush()


def _test():
    def f(n):
        if n < 1: return ""
        s = ["abcdefghij"[i] * i for i in range(1, n)]
        d = {i: f(i - 2) for i in range(1, n)}
        return {"arr": s, "dict": d}

    trace = Tracer("check")

    trace.enter("hi")
    trace.enter("f2", 3)
    trace.enter("f4", key="fun")
    trace.print("here I am! {}", ["so", "much", "fun"])
    trace.exit()
    trace.print("AGAIN... {}", ["so", "much", "fun"])
    d = f(10)
    trace.pprint(d)
    trace.exit()
    trace.exit()
    trace.exit()


def show_xml(*args, **kwargs):
    print("show_xml...")
    for n, a in enumerate(args):
        kwargs[f'elem{n}'] = a

    for k, v in kwargs.items():
        print(f"type: {type(v)}, repr: {v}")
        print(f"tojson({k}):")
        print(tojson(v))
        print(f"pxml({k}):")
        print(pxml(v))
        print(f"dense({k}):")
        print(dense(v))
    print("show_xml...done")


DEBUG_NAME = False
DictType = dict


def element_as_kv(elem: ET.Element):
    tag = HACK_tagname(elem.tag)
    d = DictType(elem.attrib.copy())
    del j["tag"]
    name = d.get("name", None)
    if name:
        del d["name"]
        tag = f"{tag}.{name}"

    subs = DictType()
    for n, sub_elem in enumerate(elem):
        k, v = element_as_kv(sub_elem)
        subs[UStr(k)] = v

    # all_named = all("tag" in s and "name" in s for s in subs)
    #
    # if all_named:
    #     for nz, s in enumerate(subs):
    #         tag, name = s["tag"], s["name"]
    #         del s["tag"]
    #         del s["name"]
    #         j["subs"] = DictType()
    #
    # else:
    #     if subs:
    #         j["subs"] = subs

    # Check name/thename
    if DEBUG_NAME:
        b1 = "name" in j
        b2 = "thename" in j;
        if b1 != b2 or (b1 and b2 and j['name'] != j['thename']):
            sys.stderr.write("UUUUGH, name isn't in json correctly?")
            pprint.pprint(j)
            sys.exit(34)

    d["subs"] = subs
    return (tag, d,)


def dense(elem):
    return ' '.join([l.strip() for l in ET.tostringlist(elem, 'unicode')])


def pxml(elem):
    if not elem:
        return 'None'
    s = ET.tostring(elem, 'unicode')
    s = s.rstrip()
    lines = s.split("\n")

    if len(lines) <= 1:
        return lines
    l = lines[-1]
    adj = l.lstrip(' ')
    trim = len(l) - len(adj)

    if trim > 0:
        def trimfn(l, n):
            n = min(n, len(l))
            for i in range(n):
                if l[i] != ' ':
                    return l[i:]
            return l[n:]

        lines = [trimfn(l, trim if i else 0) for i, l in enumerate(lines)]
    return '\n'.join(lines)


if __name__ == "__main__":
    _test()

