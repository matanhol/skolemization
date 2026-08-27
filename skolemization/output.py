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

The second half of that rule is about the indent, and it is not optional.  A
terminal writes every line from column 0, so a right-to-left line whose spaces
are written first has them reversed to the far end and its text pushed flush
against the margin -- the indent spent where nobody can see it, while the
formula lines beside it, holding no right-to-left character and so left to
themselves, keep theirs on the left.  So an RTL line is emitted with its
indent at the logical end, which is where the same reversal puts it on the
visual left.  See :func:`rtl`.

Whether the terminal honours any of this is the terminal's business: recent
Terminal.app and iTerm2 reorder these correctly, while xterm.js-based
terminals (VS Code) ignore the marks and show the text unchanged.
"""

import re
import unicodedata

from . import config
from .phrases import direction


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
    """Wrap each right-to-left line of ``text`` in an RTL isolate, indent last.

    Lines are handled one at a time: an isolate must not span a newline, or
    the terminal is left with an unpopped isolate at the end of a paragraph.

    The indent has to move.  Written where a caller puts it -- at the front --
    it is a run of neutrals at the *start* of a right-to-left line, so it takes
    the base direction and rule L2 reverses it along with everything else: the
    spaces come out at the far end and the text sits flush against column 0,
    because a terminal writes from column 0 whatever the direction is.  The
    indent is spent off the edge of the line and the nesting it was expressing
    disappears -- while a line holding only a formula, having no strongly
    right-to-left character in it, keeps its indent on the left.  A block of
    the two together is indented from both sides at once.

    Which lines those are is :func:`line_is_rtl`'s answer and nothing else's,
    so this holds for every right-to-left script rather than for Hebrew: the
    same reordering happens to an Arabic or an Adlam line, and the same repair
    fixes it.

    So a right-to-left line carries its indent at the logical *end*, where the
    same reversal puts it on the visual left, next to where the formula lines
    put theirs.  Measured with rule L2 over the classes ``unicodedata`` gives:
    four leading spaces render as four trailing ones, and four trailing spaces
    render as four leading ones.
    """

    return "\n".join(
        _indent_last(line)
        if line_is_rtl(line)
        else line
        for line
        in text.split("\n")
    )


def _indent_last(line):
    """One right-to-left line, isolated, with its indent moved to the end."""

    body = line.lstrip(
        " "
    )

    return (
        RLI
        + body
        + " " * (len(line) - len(body))
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
