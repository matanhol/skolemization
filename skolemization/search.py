"""The resolution search loop.

Saturation: every step, every pair of clauses in the KB is tried, the best
resolvent by ``config.STRATEGY`` is added, and the empty clause ends it.
"""

import random

from . import config
from . import narration
from .clauses import (
    canonical_clause,
    drop_false_equalities,
)
from .counterexample import (
    as_formula,
    simplify_against_units,
    what_the_conclusion_needed,
)
from .factoring import factor_clause
from .inference import (
    FACTORING,
    Inference,
    PARAMODULATION,
    RESOLUTION,
)
from .ordering import (
    depth,
    weight,
)
from .paramodulation import paramodulants
from .resolution import (
    meaningful_substitutions,
    resolve_two_clauses,
)
from .saturation import explain_saturated_kb
from .subsumption import (
    clause_subsumes,
    remove_redundant_parents,
    sweep_with_units,
    unit_queue,
)


def run_resolution_search(
    starting_kb,
    title="Resolution",
    focused=False,
    supported=()
):

    """Resolve until □, until saturation, or until the step limit.

    Returns (status, kb).

    A saturated run closes with the account in saturation.py -- which lives
    here rather than in the caller because only here is ``ever_seen`` in scope,
    and the account has to tell a clause still in the KB from one derived
    earlier and dropped as redundant.  ``focused`` says which kind of KB this
    is, because the same emptiness means different things: a general KB running
    dry is about the problem, a witness-focused one running dry is only about
    the guess it was built on.

    ``supported`` holds the *positions* of the clauses that seed the set of
    support -- normally the ones the negated conclusion produced.  Positions
    rather than the clauses themselves, because the KB is copied on entry.
    """

    kb = [
        list(clause)
        for clause
        in starting_kb
    ]

    # Remember every clause ever produced,
    # even if later removed as redundant.
    ever_seen = {
        canonical_clause(
            clause
        )
        for clause
        in kb
    }

    # config.SET_OF_SUPPORT: every inference must touch a supported clause.
    # Held as the identity of the *unsupported* ones rather than a growing set
    # of supported ones, because then nothing has to be maintained: every
    # derived clause is a new object, so it is supported by construction, and
    # deleting clauses cannot invalidate the set.
    seeds = set(
        supported
    )

    unsupported = {
        id(clause)
        for position, clause
        in enumerate(kb)
        if position not in seeds
    }

    # The negated conclusion's own clauses, kept as they entered: what
    # config.EXPLAIN_COUNTEREXAMPLE reads backwards if the search runs dry.
    from_the_conclusion = [
        list(clause)
        for position, clause
        in enumerate(kb)
        if position in seeds
    ]

    narration.search_header(
        title,
        kb
    )

    if config.SET_OF_SUPPORT:

        narration.set_of_support(
            [
                clause
                for position, clause
                in enumerate(kb)
                if position in seeds
            ]
        )

    # The queue drives config.FULL_SUBSUMPTION_EACH_STEP: the units the KB
    # starts with, then every unit resolvent as it arrives.
    units = (
        unit_queue(
            kb
        )
        if config.FULL_SUBSUMPTION_EACH_STEP
        else []
    )

    if config.FULL_SUBSUMPTION_EACH_STEP:

        narration.unit_queue_opened(
            units
        )

        (
            kb,
            proved
        ) = sweep_with_units(
            kb,
            units,
            ever_seen
        )

        if proved:

            narration.empty_clause(
                kb
            )

            return (
                "PROVED",
                kb
            )

    for step in range(
        1,
        config.MAX_RESOLUTION_STEPS
        +
        1
    ):

        candidates = (
            _new_inferences(
                kb,
                ever_seen,
                unsupported
            )
        )

        if not candidates:

            narration.saturated()

            if config.SET_OF_SUPPORT:

                narration.set_of_support_caveat()

            if config.EXPLAIN_SATURATION:

                kb = explain_saturated_kb(
                    kb,
                    ever_seen,
                    focused
                )

            if config.EXPLAIN_COUNTEREXAMPLE:

                _read_off_counterexample(
                    from_the_conclusion,
                    kb,
                    focused
                )

            return (
                "SATURATED_NO_CONTRADICTION",
                kb
            )

        inference = (
            _choose_candidate(
                candidates,
                kb
            )
        )

        narration.inference_step(
            step,
            inference,
            [
                list(clause)
                for clause
                in inference.parent_clauses(kb)
            ]
        )

        _explain_choice(
            candidates,
            inference,
            kb
        )

        ever_seen.add(
            canonical_clause(
                inference.result
            )
        )

        if len(
            inference.result
        ) == 0:

            kb.append(
                inference.result
            )

            narration.empty_clause(
                kb
            )

            return (
                "PROVED",
                kb
            )

        # Only the parents of this step are checked, not the whole KB.
        kb = (
            remove_redundant_parents(
                kb,
                inference.parents,
                inference.result
            )
        )

        narration.resolvent_added(
            inference.result
        )

        kb.append(
            inference.result
        )

        if config.FULL_SUBSUMPTION_EACH_STEP:

            if len(
                inference.result
            ) == 1:

                narration.unit_joined_queue(
                    inference.result
                )

                units.append(
                    inference.result
                )

            # Before the KB is shown, so what is printed is what the next step
            # will actually work on.  A simplification is not a step: it costs
            # nothing from MAX_RESOLUTION_STEPS, but it can still finish the
            # proof, since cancelling the last literal of a clause leaves □.
            (
                kb,
                proved
            ) = sweep_with_units(
                kb,
                units,
                ever_seen
            )

            if proved:

                narration.empty_clause(
                    kb
                )

                return (
                    "PROVED",
                    kb
                )

        if config.SHOW_FULL_KB_EACH_STEP:

            narration.kb_after_step(
                kb
            )

    narration.step_limit_reached()

    return (
        "UNKNOWN",
        kb
    )


def _read_off_counterexample(
    from_the_conclusion,
    kb,
    focused
):

    """Work backwards from a saturated KB to the shape of a counter-model.

    Only where saturation certifies something.  A focused KB is one guess out
    of many, and a search under ``SET_OF_SUPPORT`` never tried the inferences
    among the assumptions -- neither running dry says the clauses are
    satisfiable, so neither may be read as a model.  Both refusals are said out
    loud; silence would look like an answer.
    """

    if focused or config.SET_OF_SUPPORT:

        narration.counterexample_refused(
            focused
        )

        return

    reduced = simplify_against_units(
        from_the_conclusion,
        kb
    )

    shape = as_formula(
        reduced
    )

    narration.counterexample(
        from_the_conclusion,
        reduced,
        shape,
        what_the_conclusion_needed(
            shape
        )
        if shape is not None
        else None
    )


def _new_inferences(
    kb,
    ever_seen,
    unsupported=frozenset()
):

    """Every clause derivable in one step that the search has not seen.

    Three rules feed this.  Resolution runs over pairs, and over a clause with
    a renamed copy of itself when ``ALLOW_SELF_RESOLUTION`` is on -- that is
    the only difference between ``range(i, ...)`` and ``range(i + 1, ...)``
    below.  Factoring runs over single clauses.  Paramodulation, when
    ``EQUALITY_RULE`` asks for it, runs over ordered pairs.

    "New" means not alpha-equivalent to a clause already produced at some
    point, even one since deleted as redundant -- otherwise the search would
    rederive the same clause forever.

    ``unsupported`` is the identity of the clauses outside the set of support;
    under ``config.SET_OF_SUPPORT`` a step is only offered when it touches a
    clause outside that set -- see ``_is_supported``.
    """

    candidates = []

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

            if not _worth_trying(
                unsupported,
                kb[i],
                kb[j]
            ):

                continue

            possibilities = (
                resolve_two_clauses(
                    kb[i],
                    kb[j]
                )
            )

            for (
                lit1,
                lit2,
                substitution,
                resolvent
            ) in possibilities:

                _offer(
                    candidates,
                    ever_seen,
                    kb,
                    RESOLUTION,
                    _parents(i, j),
                    lit1,
                    lit2,
                    substitution,
                    resolvent
                )

    if config.USE_FACTORING:

        for i in range(
            len(kb)
        ):

            if not _worth_trying(
                unsupported,
                kb[i]
            ):

                continue

            for (
                lit1,
                lit2,
                substitution,
                factor
            ) in factor_clause(
                kb[i]
            ):

                _offer(
                    candidates,
                    ever_seen,
                    kb,
                    FACTORING,
                    (i,),
                    lit1,
                    lit2,
                    substitution,
                    factor
                )

    if config.EQUALITY_RULE not in EQUALITY_RULES:

        raise ValueError(
            f"unknown EQUALITY_RULE {config.EQUALITY_RULE!r}; "
            "expected one of "
            + ", ".join(
                repr(name)
                for name
                in EQUALITY_RULES
            )
        )

    if config.EQUALITY_RULE != "none":

        # Ordered pairs, both ways round: rewriting A into B is a different
        # step from rewriting B into A, unlike resolving them together.

        for i in range(
            len(kb)
        ):

            for j in range(
                len(kb)
            ):

                if i == j:
                    continue

                if not _worth_trying(
                    unsupported,
                    kb[i],
                    kb[j]
                ):

                    continue

                for (
                    lit1,
                    lit2,
                    substitution,
                    result,
                    replacement
                ) in paramodulants(
                    kb[i],
                    kb[j]
                ):

                    _offer(
                        candidates,
                        ever_seen,
                        kb,
                        PARAMODULATION,
                        (i, j),
                        lit1,
                        lit2,
                        substitution,
                        result,
                        replacement
                    )

    return candidates


def _worth_trying(
    unsupported,
    *clauses
):

    """May this step be taken at all, under ``config.SET_OF_SUPPORT``?

    Only if at least one of its clauses is in the set of support.  The
    unsupported clauses are the assumptions, and a set of clauses that is
    satisfiable cannot refute anything on its own -- so every inference among
    them is provably wasted work.  Off by default, because the guarantee is
    only as good as that satisfiability: assumptions that contradict each other
    make the conclusion follow trivially, and this restriction would miss it.
    """

    if not config.SET_OF_SUPPORT:
        return True

    return any(
        id(clause) not in unsupported
        for clause
        in clauses
    )


def _offer(
    candidates,
    ever_seen,
    kb,
    kind,
    parents,
    literal1,
    literal2,
    substitution,
    raw,
    replacement=None
):

    """Record one derivable clause, unless it would add nothing.

    Every rule's output passes through here, and every rule's output gets the
    same treatment first: a literal ``t ≠ t`` is false, so it is dropped.  That
    can only make the clause stronger, it is what turns ``c ≠ c`` into □, and
    doing it here means ``ever_seen`` and the KB agree on the simplified form.

    Then two tests, in this order: the search has produced this clause before,
    or a clause it was derived from already says it -- see ``_already_implied``.
    """

    result = drop_false_equalities(
        raw
    )

    if canonical_clause(
        result
    ) in ever_seen:

        return

    if _already_implied(
        kb,
        parents,
        result
    ):

        return

    candidates.append(
        Inference(
            kind,
            parents,
            literal1,
            literal2,
            substitution,
            result,
            raw
            if result != raw
            else None,
            replacement
        )
    )


def _already_implied(
    kb,
    parents,
    result
):

    """Does a clause this step was derived from already subsume the result?

    Forward subsumption, and the mirror image of ``remove_redundant_parents``:
    that one asks whether the newcomer makes a parent redundant, this one asks
    the same question of the same two clauses the other way round.  A step whose
    result says *less* than a clause already in the KB is work the search can
    only lose by.

    Self-resolution is the reliable source of these.  A clause holding ``L`` and
    ``¬M`` where some ``τ`` has ``Mτ = L`` and ``Lτ = L`` resolves with its own
    copy to give that clause back with extra literals attached: the resolvent is
    ``(C − {L}) ∪ (Cτ − {¬L})``, which contains ``Lτ = L``, hence contains all
    of ``C``.  ``¬P(z) ∨ ¬L(y, z) ∨ L(y, c)`` with ``τ = {z := c}`` is exactly
    that, and yields itself plus ``¬P(c)``.

    Only the parents are checked, not the whole KB.  Measured on the runaway in
    examples/recursion and on the uniqueness question, the two give identical
    statuses and identical step counts, while the parents account for the large
    majority of the catches; a newcomer subsumed by some *other* clause survives
    and is cleared by the sweep in saturation.py at the end.
    """

    return any(
        clause_subsumes(
            kb[index],
            result
        )
        for index
        in parents
    )


def _parents(
    i,
    j
):

    """The distinct clauses a step used.

    A self-resolution names one clause twice; collapsing that to a single
    entry is what keeps the subsumption check from deleting it twice over.
    """

    if i == j:
        return (i,)

    return (i, j)


def _needs_assignment(
    inference
):

    """Did this step have to bind anything, or did the literals already match?

    ``meaningful_substitutions`` is the same test the narration uses to decide
    which bindings are worth printing: a variable renamed to another variable
    is bookkeeping from standardizing apart, not an instantiation.
    """

    return (
        1
        if meaningful_substitutions(
            inference.substitution
        )
        else 0
    )


def _shortest_key(
    inference,
    kb
):

    """Shortest result, ties broken by how big the parents were."""

    return (
        len(
            inference.result
        ),
        inference.parent_size(
            kb
        )
    )


def _term_weight(
    clause
):

    """How big the clause's terms are, counting every symbol in them.

    ``ordering.weight`` is the same measure superposition compares terms by, so
    "simpler" means one thing across the package.
    """

    return sum(
        weight(argument)
        for literal
        in clause
        for argument
        in literal.atom.args
    )


def _term_depth(
    clause
):

    """How deeply the clause's deepest term nests."""

    return max(
        (
            depth(argument)
            for literal
            in clause
            for argument
            in literal.atom.args
        ),
        default=0
    )


def _shallowest_general_first_key(
    inference,
    kb
):

    """Shallowest terms first, and then the shortest-general-first ordering.

    Depth leads because nothing else stops a runaway.  Resolving
    ``¬P(x) ∨ S(g2(x))`` against ``P(g1(g2(c)))`` yields ``S(g2(g1(g2(c))))``,
    which is one literal long and so looks attractive to every other key --
    and it is itself the parent of a deeper one, forever.  Measured on the
    example in examples/recursion: with the other ranking the search is
    carrying terms nested a hundred deep by step 150 and never finishes; with
    this one nothing nests past 1 and the proof takes 6 steps.
    """

    return (
        _term_depth(
            inference.result
        ),
    ) + _shortest_general_first_key(
        inference,
        kb
    )


def _is_paramodulation(
    inference
):

    """Was this step a rewrite rather than a resolution or a factor?

    Paramodulation fires at every non-variable subterm position, in both
    directions, off every positive equality -- it is far and away the most
    prolific of the three rules.  So when a rewrite and a resolution produce
    equally good clauses, the resolution is the cheaper step to spend on, and
    the one a reader is expecting: the CEO example derives ``c2 = c`` and
    ``c3 = c`` before it starts rewriting with them, which is how the argument
    reads on paper.
    """

    return (
        1
        if inference.kind == PARAMODULATION
        else 0
    )


def _shortest_general_first_key(
    inference,
    kb
):

    """Shortest result, then resolution over rewriting, then no assignment.

    Two candidates of the same length are not equally good.  Resolving
    ``P(c) ∨ B(x,y)`` against ``¬P(c)`` costs nothing and keeps ``B(x, y)``
    general, while resolving it against ``¬B(c, g1(c))`` first pins ``x`` and
    ``y`` to one object -- so prefer the one that commits to nothing.

The last key matters once paramodulation is on, because an equation can be
    used either way round: ``c = g1(c)`` turns ``P(g1(c))`` into ``P(c)`` or
    into ``P(g1(g1(c)))``, both one literal long.  Prefer the smaller term --
    the same direction ``EQUALITY_RULE = "superposition"`` enforces outright.

    Measured when the rule key was added: no example changes status or step
    count, and the CEO proof stops rewriting before it has finished deriving.
    """

    return (
        len(
            inference.result
        ),
        _is_paramodulation(
            inference
        ),
        _needs_assignment(
            inference
        ),
        _term_weight(
            inference.result
        ),
        inference.parent_size(
            kb
        )
    )


# The strategies ``config.STRATEGY`` may name.  "random" has no key -- it is
# handled separately -- but it lives here so an unknown setting can list every
# valid name.

STRATEGY_KEYS = {
    "shallowest_general_first": _shallowest_general_first_key,
    "shortest_general_first": _shortest_general_first_key,
    "shortest": _shortest_key,
    "random": None,
}


# What each position of a key tuple means, in the same order the key builds
# them.  ``narration`` turns these into Hebrew; keeping them here is what stops
# the printed reason from drifting away from the key that actually ran.

STRATEGY_KEY_NAMES = {
    "shallowest_general_first": (
        "depth",
        "length",
        "rule",
        "assignment",
        "weight",
        "parents",
    ),
    "shortest_general_first": (
        "length",
        "rule",
        "assignment",
        "weight",
        "parents",
    ),
    "shortest": (
        "length",
        "parents",
    ),
}


# What config.EQUALITY_RULE may say.  Listed here so an unrecognised setting
# can name the alternatives instead of silently handling equality as nothing.

EQUALITY_RULES = (
    "none",
    "paramodulation",
    "superposition",
)


def _explain_choice(
    candidates,
    chosen,
    kb
):

    """Say why this step and not the next best one.

    Pure narration -- it re-sorts the candidates the ranking already sorted and
    hands the top few to ``narration.choice_between``.  "random" has no key to
    explain, so it is skipped.
    """

    if not config.EXPLAIN_CHOICE:
        return

    if config.STRATEGY not in STRATEGY_KEY_NAMES:
        return

    key = STRATEGY_KEYS[
        config.STRATEGY
    ]

    ranked = sorted(
        candidates,
        key=lambda inference: key(
            inference,
            kb
        )
    )

    # Two different steps can produce the same clause -- an equation used from
    # either side, say.  Listing one of those as the rival of the other tells
    # the reader nothing, so the runners-up are the best *different* clauses.
    already = {
        canonical_clause(
            chosen.result
        )
    }

    runners_up = []

    for other in ranked:

        signature = canonical_clause(
            other.result
        )

        if signature in already:
            continue

        already.add(
            signature
        )

        runners_up.append(
            (
                other,
                key(other, kb)
            )
        )

        if len(runners_up) == 2:
            break

    narration.choice_between(
        chosen,
        key(chosen, kb),
        runners_up,
        STRATEGY_KEY_NAMES[
            config.STRATEGY
        ]
    )


def _choose_candidate(
    candidates,
    kb
):

    """Pick the next step, per ``config.STRATEGY``.

    Factors tend to win on the length key, which is what you want -- shortening
    a clause is usually the most productive thing available.

    An unrecognised strategy raises rather than quietly behaving like
    "shortest": a typo in a setting that silently answers a different question
    is exactly the failure this package refuses elsewhere.
    """

    if config.STRATEGY not in STRATEGY_KEYS:

        raise ValueError(
            f"unknown STRATEGY {config.STRATEGY!r}; "
            "expected one of "
            + ", ".join(
                repr(name)
                for name
                in STRATEGY_KEYS
            )
        )

    if config.STRATEGY == "random":

        return random.choice(
            candidates
        )

    key = STRATEGY_KEYS[
        config.STRATEGY
    ]

    return min(
        candidates,
        key=lambda inference: key(
            inference,
            kb
        )
    )
