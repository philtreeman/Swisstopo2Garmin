#!/usr/bin/env python3
"""Kleiner Interpreter fuer die mkgmap-Stildateien von SwissTOPO Vector (nur die hier benutzte Teilmenge der Syntax), fuer die Vorschau:
Bedingungen mit = != & | und Klammern, Aktionen «set k=v», if/else/end mit Stil-Optionen (mkgmap:option:variant, :routing), include,
Typ-Angabe [0x.. resolution N[-M] continue [with_actions]]. Kein Ersatz fuer mkgmap: die Vorschau zeigt, was die Regeln ergeben sollten."""
import os, re

STYLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mkgmap", "vector", "style")
LEVELS = (24, 22, 21, 20, 18)


def tokenize(s):
    return re.findall(r"'[^']*'|\"[^\"]*\"|!=|[()&|=\[\]{};]|[^\s()&|=!\[\]{};]+", s)


class _P:
    def __init__(self, toks): self.t, self.i = toks, 0
    def peek(self): return self.t[self.i] if self.i < len(self.t) else None
    def nxt(self): v = self.t[self.i]; self.i += 1; return v


def _unq(v): return v[1:-1] if v[0] in "'\"" else v


def _or(p):
    a = _and(p)
    while p.peek() == "|":
        p.nxt(); a = ("or", a, _and(p))
    return a


def _and(p):
    a = _atom(p)
    while p.peek() == "&":
        p.nxt(); a = ("and", a, _atom(p))
    return a


def _atom(p):
    if p.peek() == "(":
        p.nxt()
        if p.peek() == ")":
            p.nxt(); return ("true",)
        a = _or(p); assert p.nxt() == ")"; return a
    k = _unq(p.nxt()); op = p.nxt(); v = _unq(p.nxt())
    return ("cmp", k, op, v)


def ev(c, tags):
    if c[0] == "true": return True
    if c[0] == "or": return ev(c[1], tags) or ev(c[2], tags)
    if c[0] == "and": return ev(c[1], tags) and ev(c[2], tags)
    _, k, op, v = c
    if v == "*": return (k in tags) if op == "=" else (k not in tags)
    return (tags.get(k) == v) if op == "=" else (tags.get(k) != v)


def _logical(path):
    out = []
    for ln in open(path, encoding="utf-8").read().splitlines():
        if ln.startswith((" ", "\t")) and out and not ln.strip().startswith("#") and ln.strip():
            out[-1] += " " + ln.strip()
        else:
            out.append(ln.rstrip())
    return out


def load(kind, options, style=STYLE):
    """Regeln einer Datei (lines, polygons, points): Liste (Bedingung, Aktionen, Typ-Angabe oder None)"""
    rules = []
    def read(path, active=True):
        stack = []   # (aktiv_aussen, bedingung_wahr)
        on = lambda: all(a for a, _ in stack) if stack else True
        for ln in _logical(path):
            ln = ln.strip()
            if not ln or ln.startswith("#"): continue
            m = re.match(r"^if\s*\((.*)\)\s*then\s*$", ln)
            if m:
                stack.append((ev(_or(_P(tokenize(m.group(1)))), options), True)); continue
            if ln == "else":
                a, _ = stack.pop(); stack.append((not a, True)); continue
            if ln.rstrip(";") == "end":
                stack.pop(); continue
            if not on(): continue
            if ln.startswith("include"):
                read(os.path.join(style, ln.split('"')[1])); continue
            if ln.startswith("name=*"): continue
            m = re.match(r"^(.*?)\s*(\{.*\})?\s*(\[.*\])?\s*$", ln)
            cond, act, typ = m.group(1), m.group(2), m.group(3)
            if not cond: continue
            c = _or(_P(tokenize(cond)))
            acts = []
            if act:
                for a in act.strip("{} ").split(";"):
                    a = a.strip()
                    if a.startswith("set "):
                        k, v = a[4:].split("=", 1); acts.append((k.strip(), v.strip().strip("'")))
            spec = None
            if typ:
                tk = typ.strip("[] ").split()
                spec = {"type": tk[0].lower(), "lo": 0, "hi": 24, "cont": "continue" in tk, "wa": "with_actions" in tk}
                if "resolution" in tk:
                    r = tk[tk.index("resolution") + 1]
                    lo, _, hi = r.partition("-")
                    spec["lo"] = int(lo); spec["hi"] = int(hi) if hi else 24
            rules.append((c, acts, spec))
    read(os.path.join(style, kind))
    return rules


def classify(rules, tags, res):
    """Typen eines Objekts bei der Aufloesung res (mehrere bei «continue»)"""
    t = dict(tags); orig = dict(tags); out = []
    for c, acts, spec in rules:
        if not ev(c, t): continue
        for k, v in acts: t[k] = v
        if spec is None: continue
        if spec["lo"] <= res <= spec["hi"]:
            out.append(spec["type"])
        if spec["cont"]:
            if not spec["wa"]: t = dict(orig)
            continue
        break
    return out
