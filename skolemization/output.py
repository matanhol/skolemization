"""The single gateway for everything this package prints.

The narration mixes Hebrew with Latin identifiers -- ``KB``, ``resolvent``,
``Resolution``, the predicate names -- and a terminal decides a line's base
direction from its first strong character.  So a line that happens to start
with a Latin word gets laid out left-to-right and its Hebrew ends up hanging
off the wrong edge, punctuation and all.

``say`` fixes that per line, by one rule:

    any Hebrew character on the line  ->  the whole line is RTL
    no Hebrew at all                  ->  the line is left untouched

"Any" is meant literally.  It does not matter how much Latin sits next to the
Hebrew or which script comes first::

    בוחרים:                          ->  RTL
    מוסיפים את ה-resolvent ל-KB:     ->  RTL
    Resolution ממוקד ב-c             ->  RTL
    C1: ¬D(x) ∨ O(x, y)              ->  LTR, untouched
    FINAL STATUS: PROVED             ->  LTR, untouched

Inside a right-to-left line the Latin runs still read left-to-right where they
stand; that is the Unicode bidi algorithm doing its job once the *paragraph*
direction is correct.  Only the line-level direction is being set here.

Whether the terminal honours any of this is the terminal's business: recent
Terminal.app and iTerm2 reorder these correctly, while xterm.js-based
terminals (VS Code) ignore the marks and show the text unchanged.
"""

import re

from . import config


# U+2067 RIGHT-TO-LEFT ISOLATE ... U+2069 POP DIRECTIONAL ISOLATE.
#
# An isolate rather than an embedding, so the RTL run cannot leak into
# whatever is printed next.

RLI = "⁧"
PDI = "⁩"

# U+2066 LEFT-TO-RIGHT ISOLATE, for technical text inside an RTL line.

LRI = "⁦"

HEBREW_RE = re.compile(
    r"[֐-׿]"
)


def line_is_rtl(line):
    """True if the line holds any Hebrew, and so should be laid out RTL."""

    return bool(
        HEBREW_RE.search(
            line
        )
    )


def rtl(text):
    """Wrap each Hebrew-bearing line of ``text`` in an RTL isolate.

    Lines are handled one at a time: an isolate must not span a newline, or
    the terminal is left with an unpopped isolate at the end of a paragraph.
    """

    return "\n".join(
        RLI + line + PDI
        if line_is_rtl(line)
        else line
        for line
        in text.split("\n")
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

    A no-op when ``config.RTL_OUTPUT`` is off, so output stays byte-identical.
    """

    if not config.RTL_OUTPUT:
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

    if config.RTL_OUTPUT:
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
