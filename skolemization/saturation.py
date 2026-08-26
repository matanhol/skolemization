"""Why a saturated search is really finished.

``SATURATED_NO_CONTRADICTION`` is the one answer the reader has to take on
trust: the empty clause never appeared, and the search stopped because nothing
new could be built.  This closes that gap by doing the accounting out loud --
first a full subsumption sweep, so what is left is only the clauses that carry
their weight, then every remaining pair with what it would produce.

Nothing here can change the answer.  It runs after the search has decided, and
what it reports is the search's own arithmetic, replayed: the same rules under
the same ``config`` flags, so an account that says "nothing is left" is a claim
about the search that actually ran, not about a similar one.
"""

from . import config
from . import narration
from .clauses import (
    canonical_clause,
    clause_is_tautology,
)
from .factoring import factor_clause
from .paramodulation import paramodulants
from .resolution import resolve_two_clauses
from .subsumption import (
    clause_subsumes,
    remove_all_redundant,
)


# What one candidate clause turned out to be.  Every possible step lands in
# exactly one of these, and none of them is a reason to keep searching.

TAUTOLOGY = "tautology"
IN_KB = "in_kb"
SEEN_EARLIER = "seen_earlier"
IMPLIED = "implied"
NEW = "new"


def explain_saturated_kb(
    kb,
    ever_seen,
    focused=False
):

    """Narrate why nothing more is derivable.  Returns the reduced KB.

    ``focused`` marks a KB that was pinned to the witness first.  The account
    is the same either way -- the arithmetic does not care -- but what it means
    is not: a general KB with nothing left says something about the problem, a
    focused one says only that ``x := c`` was the wrong guess.
    """

    narration.saturation_header()

    reduced = (
        remove_all_redundant(
            kb
        )
    )

    _account_for_everything(
        reduced,
        ever_seen,
        focused
    )

    return reduced


def _account_for_everything(
    kb,
    ever_seen,
    focused
):

    """Every step the search could still try, and what each one yields."""

    in_kb = {
        canonical_clause(
            clause
        )
        for clause
        in kb
    }

    narration.account_header(
        len(kb),
        _pair_count(
            len(kb)
        )
    )

    verdicts = []

    for i in range(
        len(kb)
    ):

        first = (
            i
            if config.ALLOW_SELF_RESOLUTION
            else i + 1
        )

        for j in range(
            first,
            len(kb)
        ):

            verdicts += (
                _account_for_pair(
                    kb,
                    i,
                    j,
                    in_kb,
                    ever_seen
                )
            )

    verdicts += (
        _account_for_factoring(
            kb,
            in_kb,
            ever_seen
        )
    )

    verdicts += (
        _account_for_paramodulation(
            kb,
            in_kb,
            ever_seen
        )
    )

    narration.account_conclusion(
        verdicts.count(NEW),
        focused
    )


def _pair_count(
    size
):

    """How many pairs the account will report, self-pairs included or not."""

    if config.ALLOW_SELF_RESOLUTION:

        return size * (size + 1) // 2

    return size * (size - 1) // 2


def _account_for_pair(
    kb,
    i,
    j,
    in_kb,
    ever_seen
):

    """One pair of clauses: what resolution can still do with it."""

    results = (
        resolve_two_clauses(
            kb[i],
            kb[j],
            keep_tautologies=True
        )
    )

    if not results:

        narration.pair_yields_nothing(
            i + 1,
            j + 1,
            _has_complementary_literals(
                kb[i],
                kb[j]
            )
        )

        return []

    verdicts = []

    for (
        literal1,
        literal2,
        substitution,
        resolvent
    ) in results:

        verdict = (
            _verdict(
                resolvent,
                in_kb,
                ever_seen,
                (
                    kb[i],
                    kb[j]
                )
            )
        )

        narration.pair_resolvent(
            i + 1,
            j + 1,
            resolvent,
            verdict
        )

        verdicts.append(
            verdict
        )

    return verdicts


def _account_for_factoring(
    kb,
    in_kb,
    ever_seen
):

    """The other rule: what factoring can still do, clause by clause."""

    if not config.USE_FACTORING:

        narration.factoring_is_off()

        return []

    verdicts = []

    for i, clause in enumerate(
        kb,
        1
    ):

        factors = (
            factor_clause(
                clause
            )
        )

        if not factors:

            narration.factor_yields_nothing(
                i
            )

            continue

        for (
            literal1,
            literal2,
            substitution,
            factor
        ) in factors:

            verdict = (
                _verdict(
                    factor,
                    in_kb,
                    ever_seen,
                    (
                        clause,
                    )
                )
            )

            narration.factor_result(
                i,
                factor,
                verdict
            )

            verdicts.append(
                verdict
            )

    return verdicts


def _account_for_paramodulation(
    kb,
    in_kb,
    ever_seen
):

    """The equality rule, when the search was using one.

    Replayed under the same ``EQUALITY_RULE``, or the account would be about a
    calculus that never ran.
    """

    if config.EQUALITY_RULE == "none":

        narration.equality_rule_is_off()

        return []

    verdicts = []

    steps = 0

    for i, first in enumerate(
        kb,
        1
    ):

        for j, second in enumerate(
            kb,
            1
        ):

            if i == j:
                continue

            for (
                literal1,
                literal2,
                substitution,
                result,
                replacement
            ) in paramodulants(
                first,
                second
            ):

                steps += 1

                verdict = (
                    _verdict(
                        result,
                        in_kb,
                        ever_seen,
                        (
                            first,
                            second
                        )
                    )
                )

                narration.paramodulant_result(
                    i,
                    j,
                    result,
                    verdict
                )

                verdicts.append(
                    verdict
                )

    if not steps:

        narration.no_paramodulants()

    return verdicts


def _verdict(
    clause,
    in_kb,
    ever_seen,
    parents
):

    """Why this candidate adds nothing -- or, if it would, say so.

    The order of the tests is the search's own order (``search._offer``), and
    ``parents`` is here for the last of them: a candidate its own parents
    already subsume is one the search refuses without recording it, so without
    this test the account would meet it again here and call it new.

    ``NEW`` cannot happen after saturation, since the search stops precisely
    when no unseen clause is derivable.  It is reported rather than hidden, so
    that a bug in the search or in this account shows up as a line a reader can
    see instead of a reassuring lie.
    """

    if clause_is_tautology(
        clause
    ):

        return TAUTOLOGY

    key = canonical_clause(
        clause
    )

    if key in in_kb:
        return IN_KB

    if key in ever_seen:
        return SEEN_EARLIER

    for parent in parents:

        if clause_subsumes(
            parent,
            clause
        ):

            return IMPLIED

    return NEW


def _has_complementary_literals(
    clause1,
    clause2
):

    """Is there an opposite-sign pair here at all, unifiable or not?

    Distinguishes the two ways a pair can be barren: nothing that could ever
    resolve, or literals that face each other but cannot be made equal --
    ``P(c)`` against ``¬P(g1(x))``, which is the interesting case.
    """

    for literal1 in clause1:

        for literal2 in clause2:

            if (
                literal1.negated
                !=
                literal2.negated
                and
                literal1.atom.pred
                ==
                literal2.atom.pred
                and
                len(literal1.atom.args)
                ==
                len(literal2.atom.args)
            ):

                return True

    return False
