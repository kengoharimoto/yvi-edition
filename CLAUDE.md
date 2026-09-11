# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Not a software project: this is the working directory for Kengo Harimoto's critical edition and translation of the **Pātañjalayogaśāstravivaraṇa (YVi)**, attributed to Śaṅkara. It holds XeLaTeX sources, style files, manuscript images, and philological notes. The current active work is the edition of YVi on sūtras 1.6–7 in `text07.tex` (git shows it modified most sessions).

## Building the PDFs

All documents compile with XeLaTeX:

```
xelatex -output-driver="xdvipdfmx -q -E" roman_edition.tex
```

Main documents:
- `roman_edition.tex` — IAST edition of YVi 1.7; inputs `text07.tex`. The primary build.
- `deva_edition.tex` — Devanagari counterpart; inputs `text07dn.tex`.
- `yvibook2a4.tex` — the full book (memoir class, ednotes, yvied.sty); chapters `text0N.tex` / translations `trl0N.tex` are enabled by (un)commenting `\input` lines.

`text07dn.tex` is **generated, never hand-edited**. After changing `text07.tex`, regenerate with:

```
python3 iast2deva_tex.py text07.tex text07dn.tex
```

(The script delegates transliteration to the `sanscript` CLI at `~/.local/bin/sanscript` and leaves LaTeX markup, labels, sigla, and comments untouched. Devanagari-specific macro overrides live in the preamble of `deva_edition.tex`, not in the generated file.)

## Edition markup (ednotes + crited.sty / yvied.sty)

`crited.sty` is used by the roman/deva editions; `yvied.sty` is the older book counterpart. Key macros in `text07.tex`:

- `\vrt{lemma}{agreeing witnesses}{\rdg{reading}{witness}}` — apparatus entry (Anote). Variants `\vrtms`, `\vrtmm`, `\vrtsm` differ in whether a `°` (kundala) marks a trimmed lemma on either side and whether Tm-lacuna rules apply.
- `\mms` / `\mme` — start/end of text missing in Tm (zero-width sub-baseline half hooks); `\mds` / `\mde` — missing in Td (same hooks with a doubled foot). The `\vrt` family no longer marks the lemma extent in the text.
- `\mll{LABEL}` + `\donote{LABEL}{pratīka}` — margin pratīka notes (Bnotes).
- `\str{...}` — sūtra text; `\bht{...}` — bhāṣya words being glossed (bold); `\lost{n}` — n lost akṣaras; `\om` — omitted; `\il`/`\ir` — scribal insertions.
- Comments like `%[18,25]` mark page,line of **E** (the 1952 Madras edition); apparatus and notes cite the text as E page,line.

Sigla: `\Tm` (Trivandrum Malayalam MS — prints as "T"; `\Tmac`/`\Tmpc` = ante/post correctionem), `L` (Lahore MS), `\Me` = *E* (Madras ed.), `\eme` = editor's emendation. The Thrissur MS (B-0667) is **not yet collated**; when it is brought in, a new siglum must be added in `crited.sty`.

## Manuscript images and philological notes

- `Lahore MS/`, `Trivandrum MS/`, `Thrissur MS/` hold working copies of leaf images; masters live under `~/Documents/MSS/YVi MSS/`.
- `00MS correspondences YVi 1.7 (E25,21-33,9).md` is the authoritative, actively maintained map of which MS leaf/image corresponds to which stretch of E — including verified line-anchors, foliation quirks (Tm's written foliation runs one behind the textual foliation; Thrissur leaves lie reversed in the bundle), and warnings (numbers on the backs of the Trivandrum photo prints are untrustworthy — identify leaves by the annotations on the photos and by textual continuity). **Read it before locating text in the manuscripts, and update it when new anchors are verified.**
- `00MSS to look at.txt` is a short to-do list of leaves to examine.
- Git commit messages record philological findings and provenance decisions, not just file changes — continue that practice.

## Conventions

- All Sanskrit in `.tex` sources is Unicode IAST; comments in the sources carry substantive editorial reasoning — preserve them when editing.
- LaTeX byproducts (`.aux`, `.log`, `.out`, `.synctex.gz`, built PDFs) are committed in this repo; there is no .gitignore or Makefile.
