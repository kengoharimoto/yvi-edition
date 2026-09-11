# Pātañjalayogaśāstravivaraṇa: critical edition and translation

Working files for Kengo Harimoto's critical edition and annotated English
translation of the **Pātañjalayogaśāstravivaraṇa** (YVi), the commentary on
Patañjali's Yogaśāstra (sūtras and bhāṣya) attributed to Śaṅkara.

The edition is based on a fresh collation of the surviving manuscripts against
the only printed text, the 1952 Madras edition (Madras Government Oriental
Series 94, cited throughout as *E* by page and line). The current focus is the
commentary on the first pāda (Samādhipāda); the section under active work is
the long discussion of the means of knowledge (pramāṇa) under sūtras 1.6–7.

This is not a software project. The repository holds XeLaTeX sources, the
style files that implement the apparatus, and the philological working notes
that record how the manuscripts were read.

## Witnesses

| Siglum | Witness |
|--------|---------|
| T (Tm) | Trivandrum, Malayalam-script palm-leaf manuscript |
| Td | Trivandrum, Devanagari transcript (not yet collated) |
| L | Lahore manuscript |
| *E* | Madras edition, 1952 |

A further manuscript in Thrissur (B-0667) has been examined but not yet
collated. Manuscript images are not part of the repository.

## Contents

- `roman_edition.tex` — the edition of YVi on 1.6–7 in IAST; inputs `text07.tex`. This is the primary build.
- `deva_edition.tex` — the same text in Devanagari; inputs `text07dn.tex`, which is generated from `text07.tex` by `iast2deva_tex.py` and never edited by hand.
- `yvibook2a4.tex` — the full book layout (memoir class). Chapters are the `text0N.tex` files, translations the `trl0N.tex` files, switched on and off by commenting the `\input` lines.
- `crited.sty`, `yvied.sty` — apparatus and lacuna markup on top of the `ednotes` package. `crited.sty` is used by the two current editions, `yvied.sty` by the book.
- `00MS correspondences YVi 1.7 (E25,21-33,9).md` — the map from stretches of *E* to manuscript leaves and images, with verified line anchors and warnings about foliation.
- `00MSS to look at.txt`, `00edn classification.md` — working to-do list and classification of editorial notes.
- `CLAUDE.md` — a compact description of the markup conventions and build steps.

Built PDFs are committed alongside the sources.

## Building

All documents compile with XeLaTeX:

```
xelatex -output-driver="xdvipdfmx -q -E" roman_edition.tex
```

After editing `text07.tex`, regenerate the Devanagari source before building
`deva_edition.tex`:

```
python3 iast2deva_tex.py text07.tex text07dn.tex
```

The transliteration is delegated to the `sanscript` command-line tool.

## Markup in brief

The text carries three registers of notes: the apparatus of variants, margin
pratīkas keyed to the bhāṣya, and editorial notes. An apparatus entry has the
form `\vrt{lemma}{agreeing witnesses}{\rdg{reading}{witness}}`; a `°` on the
lemma marks a trimmed side. Stretches missing in a witness are marked in the
running text by zero-width hooks below the baseline: `\mms` … `\mme` for the
Malayalam manuscript, `\mds` … `\mde` for the Devanagari transcript. Comments
of the form `%[25,21]` give the page and line of *E*.

Commit messages record philological findings and decisions about the
manuscripts, not only file changes, so the git history is part of the
working notes.
