#!/usr/bin/env python3
"""Repair transcription errors in the vocalised text.

Three faults in the Wikisource transcription, each verified against correct
spellings that appear elsewhere in the very same files. Run with --check to
report without writing.

Deliberately NOT touched: the order of dagesh and shin/sin dots relative to
their vowels. The files put the dot first, which is the normal typing order
and what HarfBuzz expects; Unicode canonical order would put it after the
vowel, and normalising to that renders worse in several browsers.
"""

import json, re, sys, collections

HOLAM   = "ֹ"   # ֹ  sits top-left
SIN_DOT = "ׂ"   # ׂ  also sits top-left — hence the confusion
SHIN_DOT= "ׁ"   # ׁ  sits top-right
HIRIQ   = "ִ"
VOWELS  = set("ְֱֲֳִֵֶַָׇֻ")
MARKS   = "֑-ׇ"

stats = collections.Counter()
samples = collections.defaultdict(list)


def note(kind, before, after):
    stats[kind] += 1
    if len(samples[kind]) < 4 and before != after:
        samples[kind].append((before, after))


def fix_sin_dot(s):
    """A shin carrying holam AND another vowel is impossible: one letter takes
    one vowel. In every such case the holam is standing in for the sin dot —
    both are top-left dots. יִשְֹרָאֵל appears 33 times, יִשְׂרָאֵל 35 times,
    in the same corpus. Only clusters with no dot of their own are touched."""
    def repl(m):
        marks = m.group(1)
        if HOLAM not in marks or SHIN_DOT in marks or SIN_DOT in marks:
            return m.group(0)
        if not any(c in VOWELS for c in marks):
            return m.group(0)          # bare holam: genuinely ambiguous, leave it
        rest = marks.replace(HOLAM, "", 1)
        out = "ש" + SIN_DOT + rest
        note("sin dot written as holam", m.group(0), out)
        return out
    return re.sub("ש([" + MARKS + "]*)", repl, s)


def fix_yerushalayim(s):
    """The hiriq of יְרוּשָׁלִַם marks an elided yod and belongs on the lamed.
    The transcription hangs it on the final mem instead, which is why it reads
    as a vowel on a sofit that cannot take one."""
    pat = re.compile("ל([" + MARKS + "]*)ם" + HIRIQ)
    def repl(m):
        lamed_marks = m.group(1)
        if HIRIQ in lamed_marks:
            return m.group(0)
        out = "ל" + HIRIQ + lamed_marks + "ם"
        note("hiriq moved off final mem", m.group(0), out)
        return out
    return pat.sub(repl, s)


def fix_doubles(s):
    """Two identical points stacked on one letter, e.g. a doubled patah."""
    def repl(m):
        note("duplicated point removed", m.group(0), m.group(1))
        return m.group(1)
    return re.sub("([" + MARKS + "])\\1+", repl, s)


def fix_shaping_hacks(s):
    """Typesetting hacks that break the shaping run, so the browser gives up on
    the font mid-word and swaps in another one — a letter or two suddenly a
    different size. Each has a plain, well-supported equivalent that the same
    files already use for the same words."""
    out = []
    for ch in s:
        if ch in ("‍", "‏"):
            # ZWJ wedged between vav and holam in עָוֹן, RLM before a maqaf.
            # עֲוֹנוֹת is written plainly 62 times and with the joiner 165.
            note("zero-width joiner removed", "◌" + ch, "")
            continue
        if ch == "֒":
            # The only cantillation mark in 1.3M characters, on חַסְדְּךָ. Spurious.
            note("stray cantillation mark removed", "חַסְדְּ" + ch + "ךָ", "חַסְדְּךָ")
            continue
        if ch == "ֺ":
            # HOLAM HASER FOR VAV, used here on ה ל כ ב ד ר as well as vav.
            # It is defined for vav alone and most fonts have no anchor for it,
            # so it drops out of the font. יְהֹוָה appears 3723 times, יְהֺוָה 118.
            note("holam haser for vav -> holam", "◌" + ch, "◌ֹ")
            out.append("ֹ")
            continue
        if ch == " ":
            out.append(" ")
            continue
        out.append(ch)
    return "".join(out)


def walk(node):
    if isinstance(node, str):
        return fix_doubles(fix_yerushalayim(fix_sin_dot(fix_shaping_hacks(node))))
    if isinstance(node, list):
        return [walk(x) for x in node]
    if isinstance(node, dict):
        return {k: walk(v) for k, v in node.items()}
    return node


check = "--check" in sys.argv
for path in ["data/polin.json", "data/lita.json", "data/mizrach.json"]:
    doc = json.load(open(path, encoding="utf-8"))
    fixed = walk(doc)
    if not check:
        json.dump(fixed, open(path, "w", encoding="utf-8"),
                  ensure_ascii=False, separators=(",", ":"))

print("check only, nothing written\n" if check else "written\n")
for kind, n in stats.most_common():
    print(f"{n:5d}  {kind}")
    for before, after in samples[kind]:
        print(f"         {before}   ->   {after}")
