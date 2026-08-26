"""Choosing the language, and looking a phrase up in it.

Reached through the package, not directly::

    from .phrases import phrase, phrase_table

    say(phrase("resolvent_added"))
    say(phrase("step_header", number=3, title=title))

A phrase is a plain string or a ``str.format`` template; the names inside its
braces are the keyword arguments the caller passes.  A catalogue is a plain
dict of the three things a language provides -- its phrases, its tables and the
direction it is written in -- rather than the module they live in, because the
notebook build flattens the modules away and a dict survives that.
"""

from .. import config
from . import english
from . import hebrew


CATALOGUES = {
    "he": {
        "phrases": hebrew.PHRASES,
        "tables": hebrew.TABLES,
        "direction": hebrew.DIRECTION,
    },
    "en": {
        "phrases": english.PHRASES,
        "tables": english.TABLES,
        "direction": english.DIRECTION,
    },
}


def catalogue():

    """The wording for ``config.LANGUAGE``.

    An unrecognised language raises and names the ones that exist, rather than
    quietly falling back to a language the reader did not ask for -- the same
    refusal ``STRATEGY`` and ``EQUALITY_RULE`` make.
    """

    if config.LANGUAGE not in CATALOGUES:

        raise ValueError(
            f"unknown LANGUAGE {config.LANGUAGE!r}; "
            "expected one of "
            + ", ".join(
                repr(name)
                for name
                in CATALOGUES
            )
        )

    return CATALOGUES[
        config.LANGUAGE
    ]


def phrase(
    key,
    **values
):

    """One line of narration, in the language currently set.

    ``values`` fill the template's placeholders; a phrase with no braces takes
    none.  A missing key raises rather than printing the key itself, because a
    transcript with a stray identifier in it is worse than a crash.
    """

    text = catalogue()["phrases"][
        key
    ]

    if not values:
        return text

    return text.format(
        **values
    )


def phrase_table(
    name
):

    """A whole table of wording -- step titles, rule names, verdicts.

    The tables are where the narration needs a word chosen by something other
    than the call site: which step number, which rewrite rule fired, which
    verdict a candidate got.
    """

    return catalogue()["tables"][
        name
    ]


def direction():

    """``"rtl"`` or ``"ltr"``, according to the language.

    Read by output.py, which decides from it whether to emit the bidi marks at
    all.  It belongs to the language rather than sitting beside it as a setting
    of its own: choosing Hebrew and then choosing left-to-right would be
    choosing nonsense.
    """

    return catalogue()["direction"]


def check_catalogues():

    """Every language must say every phrase and fill every table.

    Run once, at import.  The alternative is finding out about a missing key
    when a reader runs the prover in the language nobody was testing in,
    halfway through a proof.
    """

    reference = CATALOGUES["he"]

    for name, entries in CATALOGUES.items():

        _same_keys(
            f"{name} phrases",
            reference["phrases"],
            entries["phrases"]
        )

        _same_keys(
            f"{name} tables",
            reference["tables"],
            entries["tables"]
        )

        for table, contents in reference["tables"].items():

            _same_keys(
                f"{name} table {table!r}",
                contents,
                entries["tables"][table]
            )


def _same_keys(
    what,
    reference,
    other
):

    """Raise unless the two mappings offer exactly the same keys."""

    missing = (
        set(reference)
        ^
        set(other)
    )

    if not missing:
        return

    raise ValueError(
        f"{what} does not match the reference catalogue; "
        "these keys are in one and not the other: "
        + ", ".join(
            repr(key)
            for key
            in sorted(missing, key=repr)
        )
    )


check_catalogues()
