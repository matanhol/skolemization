"""Making the knowledge base smaller without losing anything.

Three sweeps live here, each answering a different question:

* ``remove_redundant_parents`` -- did the step's own parents just become
  redundant?  Cheap, and where redundancy usually shows up.
* ``sweep_with_units`` -- what can the one-literal clauses do to the rest of
  the KB for free?  Optional, and runs every step.
* ``remove_all_redundant`` -- everything against everything, once the search
  has stopped.
"""

from . import narration
from .clauses import (
    canonical_clause,
    clean_clause_variables,
    standardize_clause,
)
from .resolution import meaningful_substitutions
from .unification import (
    apply_substitution_literal,
    unify_atoms,
)


def match_term(
    pattern,
    target,
    substitution
):

    """One-way match: can ``pattern`` be instantiated to ``target``?

    Asymmetric, unlike unification -- variables in ``target`` are never bound,
    only variables in ``pattern``.  Returns the extended substitution, or None.
    """

    if pattern.is_var:

        if pattern.name in substitution:

            if (
                substitution[
                    pattern.name
                ]
                ==
                target
            ):

                return substitution

            return None

        result = dict(
            substitution
        )

        result[
            pattern.name
        ] = target

        return result

    if target.is_var:
        return None

    if (
        pattern.name
        !=
        target.name
    ):

        return None

    if (
        len(pattern.args)
        !=
        len(target.args)
    ):

        return None

    current = dict(
        substitution
    )

    for p, t in zip(
        pattern.args,
        target.args
    ):

        current = match_term(
            p,
            t,
            current
        )

        if current is None:
            return None

    return current


def match_literal(
    pattern,
    target,
    substitution
):

    """Match two literals, which must agree on sign, predicate and arity."""

    if (
        pattern.negated
        !=
        target.negated
    ):

        return None

    if (
        pattern.atom.pred
        !=
        target.atom.pred
    ):

        return None

    if (
        len(pattern.atom.args)
        !=
        len(target.atom.args)
    ):

        return None

    current = dict(
        substitution
    )

    for p, t in zip(
        pattern.atom.args,
        target.atom.args
    ):

        current = match_term(
            p,
            t,
            current
        )

        if current is None:
            return None

    return current


def clause_subsumes(
    smaller,
    larger,
    require_no_assignment=False
):

    """Is ``smaller`` at least as strong as ``larger``?

    True when every literal of ``smaller`` matches, under one substitution, a
    *distinct* literal of ``larger``.  A subsumed clause adds nothing to the KB,
    so it can be deleted.

    ``require_no_assignment`` accepts only a match that binds nothing -- where
    the literals are already there as written, up to renaming.  ``¬D(x)`` then
    still subsumes ``¬D(y) ∨ O(y, g1(y))`` but no longer subsumes ``¬D(c)``,
    which would need ``x := c``.  "Binds nothing" is
    ``meaningful_substitutions`` being empty, the same test the search uses to
    prefer a general resolution, so the two agree on what an assignment is.

    The requirement is checked where the match *succeeds*, not on the way out,
    so a pairing that would need an assignment cannot hide a different pairing
    of the same literals that would not.
    """

    if (
        len(smaller)
        >
        len(larger)
    ):

        return False

    smaller = (
        standardize_clause(
            smaller
        )
    )

    larger = (
        standardize_clause(
            larger
        )
    )

    def backtrack(
        index,
        substitution,
        used
    ):

        """Match pattern literals from ``index`` on, each to a distinct unused target."""

        if index == len(
            smaller
        ):

            return (
                not require_no_assignment
                or
                not meaningful_substitutions(
                    substitution
                )
            )

        pattern = (
            smaller[
                index
            ]
        )

        for j, target in enumerate(
            larger
        ):

            if j in used:
                continue

            new_sub = (
                match_literal(
                    pattern,
                    target,
                    substitution
                )
            )

            if new_sub is None:
                continue

            if backtrack(
                index + 1,
                new_sub,
                used | {j}
            ):

                return True

        return False

    return backtrack(
        0,
        {},
        set()
    )


def unit_queue(
    kb
):

    """The one-literal clauses of a KB, in order -- the queue's first contents.

    The queue holds the clause objects the KB holds, not positions, so clauses
    being deleted around it cannot leave it pointing at the wrong thing.
    """

    return [
        clause
        for clause
        in kb
        if len(clause) == 1
    ]


def resolve_with_unit(
    unit,
    clause
):

    """What is left of ``clause`` once the unit cancels a literal of it.

    Returns that remainder -- possibly the empty clause -- or None when this
    unit cannot act on this clause for free.  "For free" is two conditions:

    * the two literals must unify **without an assignment**, so ``{P(x)}`` acts
      on ``{¬P(x) ∨ Q(x)}`` but not on ``{¬P(c) ∨ Q(c)}``, which would first
      have to decide that ``x`` is ``c``;
    * the remainder must come through untouched.  ``{Eq(x,x)}`` against
      ``{¬Eq(x,y) ∨ Eq(y,x)}`` unifies by merging two variables of the clause,
      which turns the remainder into ``Eq(x,x)`` -- a different, weaker clause
      than the ``Eq(y,x)`` that was there.  Adding that in place of the
      original would lose the symmetry axiom, so it is refused.

    Both conditions together are what makes the swap safe: the remainder is a
    subset of the clause it replaces, so it says everything that clause said.
    """

    literal = standardize_clause(
        unit
    )[0]

    target = standardize_clause(
        clause
    )

    for i, other in enumerate(
        target
    ):

        if other.negated == literal.negated:
            continue

        substitution = (
            unify_atoms(
                literal.atom,
                other.atom
            )
        )

        if substitution is None:
            continue

        if meaningful_substitutions(
            substitution
        ):

            continue

        remainder = [
            rest
            for j, rest
            in enumerate(target)
            if j != i
        ]

        substituted = [
            apply_substitution_literal(
                rest,
                substitution
            )
            for rest
            in remainder
        ]

        if (
            canonical_clause(
                substituted
            )
            !=
            canonical_clause(
                remainder
            )
        ):

            continue

        if not substituted:
            return []

        return clean_clause_variables(
            substituted
        )

    return None


def sweep_with_units(
    kb,
    queue,
    ever_seen
):

    """Let each one-literal clause simplify the rest of the KB.

    One literal at a time, in queue order.  Against every other clause the unit
    does one of two things, and neither needs an assignment:

    * cancels a complementary literal -- the clause is replaced by what is left
      of it, which is shorter and says the same;
    * deletes a clause that already contains the unit's own literal, which the
      unit says by itself.

    A remainder of one literal joins the back of the queue, so the sweep keeps
    going as long as it keeps producing units.  A remainder of *no* literals is
    the empty clause: the KB is refuted, and ``(kb, True)`` says so rather than
    the sweep quietly continuing.

    Returns (kb, found_empty_clause).  A unit never acts on itself, and a queue
    entry no longer in the KB is skipped.
    """

    clauses = list(
        kb
    )

    acted = False

    def announce():

        """The header, emitted once, the first time there is something to say."""

        nonlocal acted

        if not acted:

            narration.unit_sweep_header()

            acted = True

    for unit in queue:

        if not any(
            clause is unit
            for clause
            in clauses
        ):

            continue

        index = 0

        while index < len(
            clauses
        ):

            clause = clauses[index]

            if clause is unit:

                index += 1

                continue

            remainder = (
                resolve_with_unit(
                    unit,
                    clause
                )
            )

            if remainder is not None:

                announce()

                if not remainder:

                    narration.unit_empty_clause(
                        unit,
                        clause
                    )

                    clauses[index] = remainder

                    return (
                        clauses,
                        True
                    )

                narration.unit_simplified(
                    unit,
                    clause,
                    remainder
                )

                clauses[index] = remainder

                ever_seen.add(
                    canonical_clause(
                        remainder
                    )
                )

                if len(remainder) == 1:

                    narration.unit_joined_queue(
                        remainder
                    )

                    queue.append(
                        remainder
                    )

                index += 1

                continue

            if clause_subsumes(
                unit,
                clause,
                require_no_assignment=True
            ):

                announce()

                narration.unit_makes_redundant(
                    unit,
                    clause
                )

                del clauses[index]

                continue

            index += 1

    if not acted:

        narration.unit_sweep_nothing()

    return (
        clauses,
        False
    )


def remove_all_redundant(
    kb
):

    """Sweep the whole KB, not just one step's parents.

    The search only ever asks whether the clauses a step consumed became
    redundant, because that is cheap and it is where redundancy usually
    appears.  Redundancy can also arrive from a clause derived much earlier, so
    once the search is over and the KB is final, this checks every clause
    against every other.

    A clause is dropped only when a *survivor* subsumes it, so two clauses that
    subsume each other -- variants of the same clause -- leave one behind
    instead of both disappearing.
    """

    narration.full_redundancy_header(
        len(kb)
    )

    survivors = []

    removed = 0

    for index, clause in enumerate(
        kb
    ):

        subsumer = _first_subsumer(
            clause,
            survivors,
            kb[index + 1:]
        )

        if subsumer is None:

            survivors.append(
                clause
            )

            continue

        removed += 1

        narration.clause_is_redundant(
            index + 1,
            clause,
            subsumer
        )

    if not removed:

        narration.nothing_redundant()

    narration.reduced_kb(
        survivors
    )

    return survivors


def _first_subsumer(
    clause,
    survivors,
    later
):

    """A clause that makes this one redundant, or None.

    Survivors are checked first, then the clauses still to come; a clause that
    was already dropped cannot justify dropping another.
    """

    for other in survivors:

        if clause_subsumes(
            other,
            clause
        ):

            return other

    for other in later:

        if (
            clause_subsumes(
                other,
                clause
            )
            and
            not clause_subsumes(
                clause,
                other
            )
        ):

            return other

    return None


def remove_redundant_parents(
    kb,
    parent_indices,
    resolvent
):

    """Delete whichever parents the new clause has made redundant.

    Checks ONLY the clauses this step consumed, not the whole KB.
    ``parent_indices`` holds one or two *distinct* indices -- a step that used
    a single clause, by factoring or self-resolution, must not list it twice or
    it would be deleted twice.
    """

    redundant = []

    for index in parent_indices:

        if clause_subsumes(
            resolvent,
            kb[index]
        ):

            redundant.append(
                index
            )

    narration.redundancy_check_header(
        len(parent_indices)
    )

    if not redundant:

        narration.no_parent_redundant(
            len(parent_indices)
        )

        return kb

    for index in redundant:

        narration.parent_is_redundant(
            resolvent,
            kb[index]
        )

    for index in sorted(
        redundant,
        reverse=True
    ):

        del kb[
            index
        ]

    return kb
