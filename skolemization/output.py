"""The single gateway for everything this package prints.

The narration mixes a right-to-left language with Latin identifiers -- ``KB``,
``resolvent``, ``Resolution``, the predicate names -- and a terminal decides a
line's base direction from its first strong character.  So a line that happens
to start with a Latin word gets laid out left-to-right and its Hebrew ends up
hanging off the wrong edge, punctuation and all.

``say`` fixes that per line, by one rule:

    any right-to-left character on the line  ->  the whole line is RTL
    none at all                              ->  the line is left untouched

The condition is the character's *direction*, never its script: ``line_is_rtl``
asks :mod:`unicodedata` for the strong classes below, so Arabic, Syriac,
Thaana, N'Ko and Adlam are covered by the same rule that covers Hebrew, and a
second right-to-left catalogue would need nothing added here.  Hebrew is what
the samples are written in because it is the right-to-left language this
package ships.

"Any" is meant literally.  It does not matter how much Latin sits next to it or
which script comes first::

    בוחרים:                          ->  RTL
    מוסיפים את ה-resolvent ל-KB:     ->  RTL
    Resolution ממוקד ב-c             ->  RTL
    C1: ¬D(x) ∨ O(x, y)              ->  LTR, untouched
    FINAL STATUS: PROVED             ->  LTR, untouched

Inside a right-to-left line the Latin runs still read left-to-right where they
stand; that is the Unicode bidi algorithm doing its job once the *paragraph*
direction is correct.  Only the line-level direction is being set here.

**The indent goes outside the isolate**, and both ways of putting it inside
lose it.  Inside and at the front, it is part of the right-to-left run: it
takes level 1, rule L2 reverses it with the text, and it lands at the visual
right where nothing shows it -- so the line comes out flush against column 0
while the formula lines beside it, holding no right-to-left character and left
alone, keep theirs.  Inside and at the *end* -- the obvious repair -- fails
too, and for a different rule: L1 resets whitespace at the end of a line to the
**paragraph** level, and a line wrapped in an isolate has paragraph level 0
whatever is inside it, since an isolate is opaque and leaves no strong
character at the top level.  The spaces are reset to left-to-right and put back
on the right.

Outside the isolate they are simply the line's own layout at paragraph level:
L2 never reverses a level-0 run and L1 only touches the end, so they stay where
they are written.  This was got wrong twice by reasoning from L2 alone; it is
now checked with an implementation that has L1 in it, and that implementation
is only believed because it first reproduces a screenshot of the failure.

**A nested block is anchored on the reader's own margin**, which is why
``say_nested`` takes the whole block instead of a line at a time.  A
right-to-left reader starts at the *right* edge of every line, so that edge is
the margin and depth steps inward from it -- and where the margin falls depends
on the longest line in the block, which is not known while the block is still
being printed.  So every line of a level ends in the same column, the innermost
level ends at the longest line's width, and each level further out ends
``INDENT`` columns further right; the arrow marking a line that opens a nested
block hangs past that anchor, forming a column of its own.  Left-to-right
output keeps the layout it always had -- indented from the left, with the arrow
leading rather than trailing.

Whether the terminal honours any of this is the terminal's business: recent
Terminal.app and iTerm2 reorder these correctly, while xterm.js-based
terminals (VS Code) ignore the marks and show the text unchanged.
"""

import re
import unicodedata

from . import config
from .phrases import (
    direction,
    phrase,
)


# U+2067 RIGHT-TO-LEFT ISOLATE ... U+2069 POP DIRECTIONAL ISOLATE.
#
# An isolate rather than an embedding, so the RTL run cannot leak into
# whatever is printed next.

RLI = "⁧"
PDI = "⁩"

# U+2066 LEFT-TO-RIGHT ISOLATE, for technical text inside an RTL line.

LRI = "⁦"

# The bidi classes that make a character *strongly* right-to-left: R is
# Hebrew, N'Ko, Adlam and the rest; AL is Arabic, Syriac and Thaana.  Asking
# unicodedata rather than matching a Hebrew block is both shorter and honest --
# it is the property the terminal itself lays the line out by, so a formula
# carrying an Arabic name would be handled instead of quietly scrambled.
#
# There is no language-to-direction table in the standard library (CLDR has
# one, but that means ICU, and this package has no dependencies), which is why
# a language states its own direction in phrases/.

STRONGLY_RTL = (
    "R",
    "AL",
)


def line_is_rtl(line):
    """True if the line holds a right-to-left character, and so must be laid out RTL."""

    return any(
        unicodedata.bidirectional(character) in STRONGLY_RTL
        for character
        in line
    )


def marks_wanted():
    """Should the bidi marks be emitted at all?

    ``config.RTL_OUTPUT`` is normally ``"auto"``, meaning "whatever the
    language needs": Hebrew is written right to left and needs them, English is
    not and would only be littered with invisible characters.  ``True`` and
    ``False`` force the question, and ``False`` is what a byte-for-byte
    comparison of the narration wants.
    """

    if config.RTL_OUTPUT == "auto":
        return direction() == "rtl"

    return bool(
        config.RTL_OUTPUT
    )


def rtl(text):
    """Wrap each right-to-left line of ``text`` in an RTL isolate.

    Lines are handled one at a time: an isolate must not span a newline, or
    the terminal is left with an unpopped isolate at the end of a paragraph.

    The indent goes **outside** the isolate, which is the whole of the trick --
    see the module docstring for the two ways of putting it inside that both
    lose it.
    """

    return "\n".join(
        _isolated(line)
        if line_is_rtl(line)
        else line
        for line
        in text.split("\n")
    )


def _isolated(line):
    """One right-to-left line, isolated, with its indent left outside.

    The indent is not right-to-left text -- it is the line's own layout -- so
    it stays at paragraph level, in front of the isolate, where it is written
    and where it renders.
    """

    body = line.lstrip(
        " "
    )

    return (
        " " * (len(line) - len(body))
        + RLI
        + body
        + PDI
    )


def ltr(text):
    """Mark technical text as one atomic left-to-right island.

    Formulas, clauses and terms must be wrapped in this before being dropped
    into a Hebrew line, because the logic symbols are not what the bidi
    algorithm calls "strong".  ``∀ ∃ ¬ ∧ ∨ →`` and the parentheses are all
    class ON (Other Neutral), so on their own they inherit the paragraph
    direction and get laid out right-to-left -- and ``(``, ``)`` and ``∃`` are
    mirrored characters, so they flip glyphs as well.  Only the Latin letters
    hold their ground, which is why an unmarked formula comes out scrambled
    rather than simply reversed::

        לפני: ∀x (D(x) → ∃y (O(x, y) ∧ F(x, y)))

    An LTR isolate covers the whole expression -- symbols, brackets and
    letters alike -- so it renders as one left-to-right unit sitting inside
    the right-to-left line.

    A no-op when the marks are not wanted -- an English transcript, or output
    being compared byte for byte -- so nothing invisible ends up in the text.
    """

    if not marks_wanted():
        return text

    return (
        LRI
        + str(text)
        + PDI
    )


def say(*values, sep=" ", end="\n"):
    """``print`` with the RTL rule applied.

    Same signature and same output as ``print``, except that Hebrew lines come
    out with an explicit right-to-left direction.  With
    ``config.RTL_OUTPUT = False`` it is a pass-through, byte for byte, and with
    ``config.NARRATE = False`` it prints nothing at all.
    """

    if not config.NARRATE:
        return

    text = sep.join(
        str(value)
        for value
        in values
    )

    if marks_wanted():
        text = rtl(text)

    print(
        text,
        end=end
    )


def say_block(
    label,
    text,
    indent="    "
):

    """Print a label and a formula that may be more than one row tall.

    A one-row formula sits on the label's line, the way the narration has
    always read.  A taller one cannot, for the reason in :func:`ltr`: an
    isolate must not span a newline, so every row is marked on its own and the
    block is indented under a label line of its own.

    ``label`` carries whatever separator it wants -- ``"לפני: "``, ``"F3: "``,
    or just spaces.  A label that is only spaces prints nothing on its own.
    """

    rows = str(text).split("\n")

    if len(rows) == 1:

        say(
            label
            + ltr(rows[0])
        )

        return

    if label.strip():

        say(
            label.rstrip()
        )

    for row in rows:

        say(
            indent
            + ltr(row)
        )


# How far one level of a nested block steps in from the level inside it, in
# columns.  Wider than the four columns the left-to-right layout uses, because
# the right-to-left anchor is a *ragged* edge -- every line of a level ends
# there, but they start wherever their own length puts them, so the levels are
# told apart by the step alone and not by a shared left edge as well.

# What kind of line an entry in a nested block is, which is all the layout
# needs to know: a line that OPENS a block earns the arrow; one ATTACHED to the
# label above it -- a formula, or a sentence about that formula -- ends where
# its label starts when the text is anchored on the right, and steps one
# further in when it is anchored on the left, because the two directions nest
# opposite ways; anything else is PLAIN.
#
# Defined here, where the emitter that reads them is, and imported by
# narration.py.  Two copies would survive the notebook's flattening only
# because narration is reached through a qualifier and so gets a namespace of
# its own -- a technicality to be relying on for three constants.

OPENS = "opens"
ATTACHED = "attached"
PLAIN = "plain"

INDENT = 8


def say_ready(line):
    """Print a line whose direction marks the caller has already placed.

    :func:`say` marks the *whole* line, which is what almost everything wants.
    The block arrow is the exception: it has to sit **outside** the isolate,
    because the isolate is what holds the line's paragraph level at 0 and that
    is what keeps a trailing neutral on the right.  Swept inside, it crosses to
    the other side and takes the line's alignment with it.

    So the one caller that needs the arrow outside marks its own text and comes
    here instead -- still through this module, still silent under
    ``config.NARRATE``.
    """

    if not config.NARRATE:
        return

    print(
        line
    )


def say_nested(entries):
    """Print a nested block: (level, kind, text) per line, or None for a blank line.

    ``level`` is the nesting depth, 0 outermost.  ``kind`` is OPENS for a line
    that a nested block hangs under, and earns it an arrow.  ``text`` is the
    finished line **without** any indent -- the caller has already wrapped its
    formulas in :func:`ltr`, and this decides only where the line sits.

    The whole block arrives at once because a right-to-left block cannot be
    laid out one line at a time: the reader's margin is the *right* edge, and
    where that edge falls is the longest line in the block.  See the module
    docstring for the anchoring rule.  The left-to-right layout has no such
    problem and is untouched by any of it.

    None of this reasons about the bidi algorithm.  Six attempts that did got
    it wrong; the layout below is the one candidate that was confirmed by
    rendering it on a real terminal, and every apparent simplification in it
    has already been tried and reverted.
    """

    rows = _nested_rows(
        entries
    )

    if direction() == "rtl":

        _say_nested_rtl(
            rows
        )

        return

    _say_nested_ltr(
        rows
    )


def _nested_rows(entries):
    """The block's entries as one entry per *printed* row.

    ``config.TALL_BRACKETS`` makes a formula several rows tall, and an isolate
    must never span a newline -- so a tall entry becomes one entry per row at
    the same level, each measured, marked and padded on its own, exactly as
    :func:`say_block` splits one.  The arrow stays on the first row: it marks
    the point the nested block opens, and the block opens where the entry
    starts.
    """

    rows = []

    for entry in entries:

        if entry is None:

            rows.append(
                None
            )

            continue

        level, kind, text = entry

        for index, row in enumerate(_rows_of(text)):

            rows.append(
                (
                    level,
                    # A tall formula's rows all sit at one level, and only the
                    # first can carry the arrow.
                    kind
                    if index == 0
                    else PLAIN,
                    row,
                )
            )

    return rows


def _rows_of(text):
    """One entry's text as rows, with no isolate left spanning a newline.

    A one-row text is passed straight through, marks and all: it is the line
    the caller wrote and there is nothing to repair.

    A text with newlines in it can only have come from a formula printed under
    ``config.TALL_BRACKETS``, and the caller will have wrapped that formula in
    :func:`ltr` as one piece -- which now opens an isolate on the first row and
    pops it on the last.  The wrap is undone and reapplied per row, since once
    the rows are separate lines that is the only marking that means anything;
    a caller that hands the rows over unmarked gets the same treatment and the
    same result.
    """

    text = str(
        text
    )

    if "\n" not in text:
        return [text]

    if text.startswith(LRI) and text.endswith(PDI):
        text = text[len(LRI):-len(PDI)]

    return [
        ltr(row)
        for row
        in text.split("\n")
    ]


def _width(text):
    """How many columns a line of the block takes up.

    ``len``, direction marks included, which is not what a Unicode-correct
    implementation would do: ``LRI`` and ``PDI`` are formatting characters and
    ought to be zero-width.  On the terminal this layout was settled against
    they each advance a column, and the anchoring was measured there rather
    than derived from the standard -- so stripping them would push every line
    holding a formula two columns off its own anchor.
    """

    return len(
        text
    )


def _say_nested_rtl(rows):
    """The right-to-left layout: every line of a level ends in the same column.

    The pad is computed from the *text* alone and the arrow appended after it,
    so an arrow hangs past the anchor instead of pushing its own line off it --
    which is what leaves the arrows standing in a column of their own beyond
    the block.

    The isolate is left entirely to ``say``: it wraps a line holding
    right-to-left text in ``RLI...PDI``, and that is what holds the line's
    paragraph level at 0, which is what keeps the trailing arrow on the right.
    Take the isolate away and every arrow crosses to the other side.
    """

    arrow = phrase(
        "countermodel_block_arrow"
    )

    printed = [
        row
        for row
        in rows
        if row is not None
    ]

    deepest = max(
        (
            level
            for level, _, _
            in printed
        ),
        default=0,
    )

    innermost = max(
        (
            _width(text)
            for _, _, text
            in printed
        ),
        default=0,
    )

    for row in rows:

        if row is None:

            say(
                ""
            )

            continue

        level, kind, text = row

        anchor = innermost + (deepest - level) * INDENT

        # The text is marked here rather than by say(), so the arrow can be
        # appended *after* the isolate closes.  Inside it, a trailing neutral
        # takes the right-to-left level and renders on the left.
        body = (
            rtl(text)
            if marks_wanted()
            else text
        )

        line = (
            " " * (anchor - _width(text))
            + body
        )

        if kind == OPENS:

            line = (
                line
                + " "
                + arrow
            )

        say_ready(
            line
        )


def _say_nested_ltr(rows):
    """The left-to-right layout, which is what it always was.

    Four columns per level from the left, and the arrow *before* the text it
    belongs to, hanging into the two columns the block is offset by -- the
    mirror image of the right-to-left case, and the reason a reader of either
    finds the arrows on the side they start each line from.

    An ATTACHED line steps one level further in here, where the right-anchored
    layout leaves it on its label's own anchor.  The two directions nest
    opposite ways: anchored on the right, a formula *ends* where its label
    begins, so they share a column; anchored on the left it has to sit under
    that label, which is one step in.
    """

    arrow = phrase(
        "countermodel_block_arrow"
    )

    for row in rows:

        if row is None:

            say(
                ""
            )

            continue

        level, kind, text = row

        pad = (
            len(arrow)
            + 1
            + (
                level
                + (1 if kind == ATTACHED else 0)
            )
            * 4
        )

        if kind == OPENS:

            say(
                " " * (pad - len(arrow) - 1)
                + arrow
                + " "
                + text
            )

            continue

        say(
            " " * pad
            + text
        )
