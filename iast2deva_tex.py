#!/usr/bin/env python3
"""Convert the IAST Sanskrit content of text07.tex to Devanagari,
leaving all LaTeX markup, labels, sigla, and comments untouched.
Transliteration itself is delegated to the `sanscript` CLI.
"""
import re, subprocess, sys

SANSCRIPT = "/Users/kengo_1/.local/bin/sanscript"
SRC, DST = sys.argv[1], sys.argv[2]

IAST = "a-zāīūṛṝḷḹṅñṭḍṇśṣḥṃ"
RUN_RE = re.compile(f"[{IAST}']+")
# lines to leave completely untouched (English headings, layout commands)
SKIP_LINE = re.compile(r"\s*\\(section|subsection|subsubsection|paragraph|subparagraph|chapter|setlength|settowidth|pagewiselinenumbers)")
# macros whose (first) argument is a label/length, never Sanskrit
PROTECT_ARG = re.compile(
    r"\\(mll|donote|llbl|linelabel|label|pageref|lineref|ref|pause|resume|"
    r"[A-E]notelabel|lost|wmhl|ittspc|begin|end)\{[^{}]*\}")
CTRL = re.compile(r"\\[a-zA-Z@]+\*?|\\-|\\\\")
DIM = re.compile(r"\d+(?:\.\d+)?(?:pt|em|ex|in|mm|cm)\b")
LATINISM = re.compile(
    r"\b(?:conj|em)\."
    r"|\(\\emph\{kṣya\} appearing[^)]*\)")  # English remark in the app. at l.289

VOWEL2MATRA = {"अ": "", "आ": "ा", "इ": "ि", "ई": "ी", "उ": "ु", "ऊ": "ू",
               "ऋ": "ृ", "ॠ": "ॄ", "ए": "े", "ऐ": "ै", "ओ": "ो", "औ": "ौ"}
DEVA_DIGIT = str.maketrans("0123456789", "०१२३४५६७८९")

lines = open(SRC, encoding="utf-8").read().split("\n")

# ---------- pass 1: protect, collect runs ----------
protected = []   # per line: (code_with_placeholders, comment, stash) or None if skipped
runs = set()

def stash_repl(stash):
    def repl(m):
        stash.append(m.group(0))
        return f"\x01{len(stash)-1}\x02"
    return repl

def mark_avagraha(code):
    """U+2019 followed by a letter is an avagraha unless it closes a `...' insertion."""
    out, open_tick = [], False
    for i, ch in enumerate(code):
        if ch == "`":
            open_tick = True
        elif ch in "'’":
            if open_tick:
                open_tick = False
                ch = "’"                   # insertion closer: keep out of runs
            elif i + 1 < len(code) and re.match(f"[{IAST}]", code[i+1]):
                ch = "'"                   # avagraha: normalize for sanscript
        out.append(ch)
    return "".join(out)

for line in lines:
    m = re.search(r"(?<!\\)%", line)
    code, comment = (line[:m.start()], line[m.start():]) if m else (line, "")
    if SKIP_LINE.match(line) or not code.strip():
        protected.append(None)
        continue
    stash = []
    code = PROTECT_ARG.sub(stash_repl(stash), code)
    code = LATINISM.sub(stash_repl(stash), code)
    code = CTRL.sub(stash_repl(stash), code)
    code = DIM.sub(stash_repl(stash), code)
    code = mark_avagraha(code)
    for r in RUN_RE.findall(code):
        runs.add(r)
    protected.append((code, comment, stash))

# ---------- pass 2: batch transliterate unique runs ----------
runs = sorted(r for r in runs if r)
proc = subprocess.run(
    [SANSCRIPT, "--from", "iast", "--to", "devanagari", "\n".join(runs)],
    capture_output=True, text=True, check=True)
out_lines = proc.stdout.rstrip("\n").split("\n")
assert len(out_lines) == len(runs), f"line count mismatch {len(out_lines)} vs {len(runs)}"
trans = dict(zip(runs, out_lines))

# ---------- pass 3: substitute, post-process, restore ----------
MARKER = re.compile(r"\\(?:mds|mde|mms|mme)(?: |(?=[^a-zA-Z]))|\\-|[{}]")

def fix_joins(code):
    """virama + word-splitting marker + independent vowel  ->  matra join"""
    out, i = [], 0
    while i < len(code):
        ch = code[i]
        if ch == "्":
            j, saw_marker = i + 1, False
            while True:
                m = MARKER.match(code, j)
                if not m:
                    break
                saw_marker = True
                j = m.end()
            if saw_marker and j < len(code) and code[j] in VOWEL2MATRA:
                out.append(code[i+1:j] + VOWEL2MATRA[code[j]])
                i = j + 1
                continue
        out.append(ch)
        i += 1
    return "".join(out)

CONS = "\\u0915-\\u0939\\u0958-\\u095F"
CONS_RE = re.compile(f"[{CONS}]")
TOK = re.compile(r"\\[a-zA-Z@]+\*?|\\-|[{} ]")

def skip_group(code, j):
    """j is at '{'; return position after the matching '}' (or None)."""
    d, k = 1, j + 1
    while k < len(code) and d:
        if code[k] == "{": d += 1
        elif code[k] == "}": d -= 1
        k += 1
    return k if d == 0 else None

def skip_tokens(code, j):
    """Advance from j to the next character that is typeset in the body:
    spaces are counted, macro names and braces stepped over.  An opening
    brace is ENTERED (its first argument is body text, e.g. the lemma of
    \\vrt or the content of \\bht); after a bare closing brace any
    directly following groups are argument groups (sigla, readings) and
    are skipped OPAQUELY.  Returns (end, kept_tokens, space_count)."""
    kept, spaces = [], 0
    while j < len(code):
        ch = code[j]
        if ch == "{":
            kept.append("{")
            j += 1
            continue
        if ch == "}":
            kept.append("}")
            j += 1
            while j < len(code) and code[j] == "{":
                k = skip_group(code, j)
                if k is None: break
                kept.append(code[j:k])
                j = k
            continue
        m = TOK.match(code, j)
        if not m:
            break
        if m.group(0) == " ":
            spaces += 1
        else:
            kept.append(m.group(0))
            if m.group(0).startswith("\\") and m.group(0)[1:2].isalpha():
                kept.append(" ")   # terminate the macro name (TeX eats it)
        j = m.end()
    return j, kept, spaces

def drop_spaces(code):
    """Devanagari convention: a space may stand only after an akshara-final
    sound (vowel, anusvara, visarga, avagraha).  After a bare (virama)
    consonant the words run on.  At the virama, macros and braces are
    stepped over; only the spaces are removed, and only when the next
    Devanagari letter is a consonant (an independent vowel would have to
    be rewritten as a matra, which must not happen across a macro
    boundary -- it would alter an apparatus lemma)."""
    out, i = [], 0
    while i < len(code):
        ch = code[i]
        out.append(ch)
        i += 1
        if ch != "\u094d":            # virama
            continue
        j, kept, spaces = skip_tokens(code, i)
        if spaces == 0 or j >= len(code):
            continue
        nxt = code[j]
        if CONS_RE.match(nxt):
            out.append("".join(kept))          # drop the spaces only
            i = j
        elif nxt in VOWEL2MATRA and not kept:  # plain text: matra join
            out.pop()                          # remove the virama
            out.append(VOWEL2MATRA[nxt])
            i = j + 1
    code = "".join(out)
    # space before avagraha
    code = re.sub("(?<=[\u0900-\u097f]) +\u093d", "\u093d", code)
    return code

result = []
for line, prot in zip(lines, protected):
    if prot is None:
        result.append(line)
        continue
    code, comment, stash = prot
    code = RUN_RE.sub(lambda m: trans.get(m.group(0), m.group(0)), code)
    code = code.replace("°", "॰")
    code = code.replace("||", "॥").replace("|", "।")
    code = re.sub(r"॥(\d+)॥", lambda m: "॥" + m.group(1).translate(DEVA_DIGIT) + "॥", code)
    code = re.sub("\x01(\\d+)\x02", lambda m: stash[int(m.group(1))], code)
    code = fix_joins(code)
    code = drop_spaces(code)
    # scribal insertion marks: combining accents don't exist in Devanagari MT,
    # so use crited's \il/\ir (which switch to the Latin font themselves)
    code = code.replace("`", "\\il{}").replace("’", "\\ir{}")
    code = code.replace("•", "{\\cm\\textbullet}")
    # Devanagari readings quoted inside sigla qualifications, e.g. \Me(°paḥ):
    # the sigla group is Latin, so re-enter the Sanskrit font there.
    code = re.sub(r"(\\(?:Me|Tm(?:ac|pc)?|L(?:ac|pc))|(?<![\\a-zA-Z])[LTE])"
                  r"\(([ऀ-ॿ॰।॥][^()]*)\)",
                  r"\1({\\sanskritfont \2})", code)
    result.append(code + comment)

# ---------- pass 4: joins across source line breaks ----------
# A newline is a space to TeX, so a virama-final line followed by a
# Devanagari-initial line needs joining too.  Commenting out the rest of
# the line makes TeX resume directly at the next line's first token
# (comment-only lines in between are transparent).
def split_line(ln):
    m = re.search(r"(?<!\\)%", ln)
    return (ln[:m.start()], ln[m.start():]) if m else (ln, "")

for i in range(len(result) - 1):
    code, comment = split_line(result[i])
    tail = code.rstrip()
    if not tail:
        continue
    # find the next line with code on it; blank lines end the paragraph
    k = i + 1
    while k < len(result):
        ncode, _ = split_line(result[k])
        if not result[k].strip():
            k = None
            break
        if ncode.strip():
            break
        k += 1
    if k is None or k >= len(result):
        continue
    ncode, ncomment = split_line(result[k])
    nxt = ncode.lstrip()
    q2, _, _ = skip_tokens(nxt, 0)
    eff = nxt[q2:q2+1] if q2 < len(nxt) else ""
    v = tail.rfind("\u094d")
    bare_virama = False
    if v != -1:
        e, _, _ = skip_tokens(tail, v + 1)
        bare_virama = (e >= len(tail))
    if bare_virama:
        if CONS_RE.match(eff):
            result[i] = tail + (comment or "%")
        elif tail.endswith("\u094d") and nxt and nxt[0] in VOWEL2MATRA:
            result[i] = tail[:-1] + VOWEL2MATRA[nxt[0]] + (comment or "%")
            result[k] = ncode.replace(nxt, nxt[1:], 1) + ncomment
    elif re.match("[\u0900-\u097f]", tail[-1:]) and nxt.startswith("\u093d"):
        result[i] = tail + (comment or "%")

open(DST, "w", encoding="utf-8").write("\n".join(result))
leftover = sum(1 for ln in result
               if re.search(r"् |(?<=[ऀ-ॿ]) ऽ", re.sub(r"(?<!\\)%.*", "", ln)))
print(f"lines with remaining post-consonant spaces: {leftover}")
print(f"wrote {DST}: {len(runs)} unique runs transliterated")
