"""Building the counter-model that a saturated knowledge base is hiding.

A refutation is not the only thing a resolution search can produce.  When it
runs dry, the other half of the completeness theorem applies: a clause set
saturated under a complete calculus with no □ in it *is* satisfiable.  And the
KB it saturated to is not an obstacle to reading that model off -- it is the
description of it::

    ¬Q(x, y)     P(c)     ¬P(c4)

says: Q holds of nothing, P holds of c and not of c4.  Two elements, because
one clause wants something with P and another wants something without.

So this module builds a **finite structure** -- a domain, a table per
predicate, and tables for the constants and Skolem functions -- that satisfies
every surviving clause, and then evaluates the original assumptions and
conclusion in it.  The assumptions must come out true and the conclusion false;
that is what makes it a counter-example rather than a picture of one, and it is
checked rather than asserted.

Why it must be *this* KB and not just the negated conclusion's clauses: the
conclusion's half alone says what the model must avoid, not what it must
contain.  Drop ``P(c)`` from the example above and nothing explains why one
element will not do.

The search is deliberately small: domain sizes 1, 2, 3 ... up to a cap, all
interpretations of the constants and functions, and a plain DPLL over the
ground instances of the clauses.  Teaching scale, not competition scale -- and
when nothing is found it says so rather than implying there is no model.

That is the mechanism.  What is *said* about the model is a separate question
with its own answer, and it is under the ``WHAT TO SAY ABOUT THE MODEL`` banner
further down: which facts are worth printing at all, why they are printed as
formulas rather than as prose, and the order they are put in.  The model built
here is never printed -- it is the proof that the description is satisfiable
rather than merely plausible, and what an explanation points at when it names a
witness.
"""

from itertools import product

from .display import clause_as_formula
from .sorts import (
    RESULT,
    is_ground,
    position_label,
    sorts_of_clauses,
    term_key,
)
from .formulas import (
    And,
    Atom,
    Exists,
    ForAll,
    Implies,
    Not,
    Or,
    Term,
)
from .substitution import substitute_formula


# How far the search goes before giving up.  Three elements is enough for every
# saturating example in this package, and the work grows fast: every function
# symbol multiplies the interpretations to try by size ** (size ** arity).

LARGEST_DOMAIN = 3


def signature(kb):

    """The predicates, constants and functions the clauses actually mention.

    Returns ``(predicates, constants, functions)``, each a dict from name to
    arity -- the shape any model of these clauses has to have.
    """

    predicates = {}

    constants = {}

    functions = {}

    def walk_term(term):

        if term.is_var:
            return

        if term.args:

            functions[term.name] = len(
                term.args
            )

        else:

            constants[term.name] = 0

        for argument in term.args:

            walk_term(
                argument
            )

    for clause in kb:

        for literal in clause:

            predicates[literal.atom.pred] = len(
                literal.atom.args
            )

            for argument in literal.atom.args:

                walk_term(
                    argument
                )

    return (
        predicates,
        constants,
        functions
    )


def variables_of(clause):

    """Every variable in a clause, in the order it first appears."""

    found = []

    def walk(term):

        if term.is_var:

            if term.name not in found:

                found.append(
                    term.name
                )

            return

        for argument in term.args:

            walk(
                argument
            )

    for literal in clause:

        for argument in literal.atom.args:

            walk(
                argument
            )

    return found


class Model:

    """A finite structure: a domain, and a table for every symbol.

    ``constants`` and ``functions`` map a name to an element or to a tuple of
    elements indexed by the arguments; ``predicates`` maps a name to the set of
    tuples it holds of.  Everything is an integer in ``range(size)``, and the
    narration is what turns those into something a reader wants to look at.
    """

    def __init__(
        self,
        size,
        constants,
        functions,
        predicates
    ):

        self.size = size

        self.constants = constants

        self.functions = functions

        self.predicates = predicates

    def domain(self):

        """The elements, as a range."""

        return range(
            self.size
        )

    def value_of(
        self,
        term,
        binding
    ):

        """What a term denotes, under an assignment to its variables."""

        if term.is_var:

            return binding[
                term.name
            ]

        if not term.args:

            return self.constants[
                term.name
            ]

        return self.functions[
            term.name
        ][
            tuple(
                self.value_of(
                    argument,
                    binding
                )
                for argument
                in term.args
            )
        ]

    def holds(
        self,
        atom,
        binding
    ):

        """Is this atom true here, under that assignment?"""

        return tuple(
            self.value_of(
                argument,
                binding
            )
            for argument
            in atom.args
        ) in self.predicates[
            atom.pred
        ]


# What the search asks of a model before it settles for one.  Smallest is not
# clearest: a one-element universe where g1(e1) = e1 says "the owner of x is x",
# which reads like a trick rather than a counter-example.  So the preferences
# are tried in this order and given up one at a time, and whichever had to go is
# reported -- that a clause *forces* two witnesses together is itself something
# the reader should know.

SEPARATE_WITNESSES = "separate_witnesses"

NO_SELF_APPLICATION = "no_self_application"

PREFERENCES = (
    (SEPARATE_WITNESSES, NO_SELF_APPLICATION),
    (SEPARATE_WITNESSES,),
    (NO_SELF_APPLICATION,),
    (),
)


def finite_model(
    kb,
    largest=LARGEST_DOMAIN
):

    """A model of these clauses that reads naturally, or None.

    Returns ``(model, given_up)`` -- the structure, and which preferences the
    clauses would not allow.  The search starts at as many elements as there
    are constants rather than at one, because witnesses the problem named
    separately should stay separate unless something forces them together.
    """

    predicates, constants, functions = signature(
        kb
    )

    smallest = max(
        1,
        len(constants)
    )

    for wanted in PREFERENCES:

        for size in range(
            smallest,
            largest + 1
        ):

            model = _model_of_size(
                kb,
                size,
                predicates,
                constants,
                functions,
                wanted
            )

            if model is not None:

                return (
                    model,
                    [
                        preference
                        for preference
                        in PREFERENCES[0]
                        if preference not in wanted
                    ]
                )

        # Nothing at any size under these preferences: drop one and try again,
        # rather than reporting that no model exists when only a tidy one does
        # not.

    return (None, [])


def _model_of_size(
    kb,
    size,
    predicates,
    constants,
    functions,
    wanted
):

    """Try every interpretation of the constants and functions at this size.

    ``wanted`` filters those interpretations: distinct constants on distinct
    elements, and no function sending an element to itself.  The predicates are
    not enumerated -- once the terms are fixed each clause becomes a
    propositional clause over ground atoms, and DPLL settles those far faster
    than brute force would.
    """

    elements = list(
        range(size)
    )

    for constant_values in product(
        elements,
        repeat=len(constants)
    ):

        if (
            SEPARATE_WITNESSES in wanted
            and
            len(set(constant_values)) != len(constant_values)
        ):

            continue

        constant_table = dict(
            zip(
                constants,
                constant_values
            )
        )

        for function_table in _function_tables(
            functions,
            elements
        ):

            if (
                NO_SELF_APPLICATION in wanted
                and
                _sends_something_to_itself(
                    function_table
                )
            ):

                continue

            candidate = Model(
                size,
                constant_table,
                function_table,
                {}
            )

            assignment = _solve(
                _ground_clauses(
                    kb,
                    candidate,
                    elements
                )
            )

            if assignment is None:
                continue

            candidate.predicates = _predicate_tables(
                predicates,
                assignment
            )

            return candidate

    return None


def _sends_something_to_itself(
    function_table
):

    """Does any function map an element to itself?

    ``g1(e1) = e1`` reads as "the owner of x is x", which is the kind of model a
    reader stops believing.  Where the clauses allow it, one more element buys a
    structure that says what it means.
    """

    for table in function_table.values():

        for arguments, value in table.items():

            if value in arguments:
                return True

    return False


def _function_tables(
    functions,
    elements
):

    """Every way of interpreting the function symbols over the domain."""

    names = sorted(
        functions
    )

    argument_tuples = [
        list(
            product(
                elements,
                repeat=functions[name]
            )
        )
        for name
        in names
    ]

    choices = [
        product(
            elements,
            repeat=len(arguments)
        )
        for arguments
        in argument_tuples
    ]

    for values in product(*choices):

        yield {
            name: dict(
                zip(
                    arguments,
                    row
                )
            )
            for name, arguments, row
            in zip(names, argument_tuples, values)
        }


def _ground_clauses(
    kb,
    model,
    elements
):

    """Every clause, over every assignment of its variables to the domain.

    A literal becomes ``(predicate, argument tuple, sign)`` -- a propositional
    atom, since the terms are already resolved by the model's constant and
    function tables.
    """

    grounded = []

    for clause in kb:

        variables = variables_of(
            clause
        )

        for values in product(
            elements,
            repeat=len(variables)
        ):

            binding = dict(
                zip(
                    variables,
                    values
                )
            )

            grounded.append(
                [
                    (
                        (
                            literal.atom.pred,
                            tuple(
                                model.value_of(
                                    argument,
                                    binding
                                )
                                for argument
                                in literal.atom.args
                            )
                        ),
                        not literal.negated
                    )
                    for literal
                    in clause
                ]
            )

    return grounded


def _solve(
    clauses,
    assignment=None
):

    """DPLL, with unit propagation and nothing clever.

    Returns a dict from ground atom to True/False satisfying every clause, or
    None.  The clause sets here are tiny -- a handful of predicates over three
    elements -- so the plain algorithm is the readable choice.
    """

    if assignment is None:
        assignment = {}

    clauses, assignment = _propagate(
        clauses,
        dict(assignment)
    )

    if clauses is None:
        return None

    if not clauses:
        return assignment

    atom = clauses[0][0][0]

    for value in (True, False):

        decided = dict(
            assignment
        )

        decided[atom] = value

        result = _solve(
            clauses,
            decided
        )

        if result is not None:
            return result

    return None


def _propagate(
    clauses,
    assignment
):

    """Simplify under the assignment, forcing every unit clause it produces.

    Returns ``(clauses, assignment)``, or ``(None, assignment)`` when a clause
    has come out empty and this branch is dead.
    """

    changed = True

    while changed:

        changed = False

        simplified = []

        for clause in clauses:

            literals = []

            satisfied = False

            for atom, sign in clause:

                if atom not in assignment:

                    literals.append(
                        (atom, sign)
                    )

                    continue

                if assignment[atom] == sign:

                    satisfied = True

                    break

            if satisfied:
                continue

            if not literals:
                return (None, assignment)

            if len(literals) == 1:

                atom, sign = literals[0]

                assignment[atom] = sign

                changed = True

                continue

            simplified.append(
                literals
            )

        clauses = simplified

    return (clauses, assignment)


def _predicate_tables(
    predicates,
    assignment
):

    """The satisfying assignment, turned back into one table per predicate.

    Atoms the solver never had to decide are false: nothing in the clauses
    asked for them, and the smallest relation is the clearest to read.
    """

    tables = {
        name: set()
        for name
        in predicates
    }

    for (name, arguments), value in assignment.items():

        if value:

            tables.setdefault(
                name,
                set()
            ).add(
                arguments
            )

    return tables


def evaluate(
    formula,
    model,
    binding=None
):

    """Is this formula true in that model?

    The whole point of the pass: the assumptions must evaluate to True here and
    the conclusion to False, or what was built is not a counter-example.
    """

    if binding is None:
        binding = {}

    if isinstance(formula, Atom):

        return model.holds(
            formula,
            binding
        )

    if isinstance(formula, Not):

        return not evaluate(
            formula.x,
            model,
            binding
        )

    if isinstance(formula, And):

        return (
            evaluate(formula.a, model, binding)
            and
            evaluate(formula.b, model, binding)
        )

    if isinstance(formula, Or):

        return (
            evaluate(formula.a, model, binding)
            or
            evaluate(formula.b, model, binding)
        )

    if isinstance(formula, Implies):

        return (
            not evaluate(formula.a, model, binding)
            or
            evaluate(formula.b, model, binding)
        )

    if isinstance(
        formula,
        (ForAll, Exists)
    ):

        results = []

        for element in model.domain():

            extended = dict(
                binding
            )

            extended[formula.var] = element

            results.append(
                evaluate(
                    formula.body,
                    model,
                    extended
                )
            )

        if isinstance(formula, ForAll):
            return all(results)

        return any(results)

    raise TypeError(formula)


# Why a formula came out the way it did.  A reason is (key, values): the key
# picks the sentence, the values are the elements or subformulas it names.
#
# A reason may carry another reason.  "The left side holds" is exactly the
# point at which a reader wants to ask *why*, so an implication's reason
# carries the reason for whichever side decided it, keyed beside the formula it
# explains: ``condition`` with ``condition_reason``, ``consequent`` with
# ``consequent_reason``.  The nested one is computed under that side's own
# verdict, which the branch it came from already settled.  This nests
# recursively by construction -- a side that is itself an implication brings
# its own sides with it -- and it terminates, because every nested reason is
# about a strictly smaller formula.
#
# A reason that *names* an element carries one too, keyed ``body_reason``.
# WITNESSED and UNIVERSAL_FAILS both answer "which element", and the reader's
# next question is always "why that one" -- so the quantifier's body is
# instantiated at that element and asked the same question, under the verdict
# the branch has already settled.  The body comes out **instantiated**
# (``P(c3)``, not ``P(x)``), because a line naming an element has to stand on
# its own.
#
# An element with no name brings no body reason.  The sentence still points at
# it (as "?"), but there is nothing to substitute -- and it is being *named*
# that makes an element a constant of the model, which is what makes the
# substituted body safe to evaluate at all.
#
# A nested PLAINLY reason is left off entirely rather than attached: "that is
# how it comes out in the model" tells the reader nothing they did not just
# read, and an absent key is a case nothing downstream has to recognise -- the
# notebook flattens every module into one namespace, so a narration that had to
# import this one to spot it would be paying for the privilege.
#
# The one rule worth stating: a **universal** is never explained by pointing at
# an element -- "it holds of every element", or "vacuously, because nothing
# satisfies the condition".  Only an **existential** names a witness, because
# there naming one *is* the explanation.  Naming the element that *breaks* a ∀
# (UNIVERSAL_FAILS) is a different thing: a counter-example is not an example,
# and it is the whole content of the failure -- which is why explaining the
# body *there* deepens the counter-example rather than softening the rule.

VACUOUS_UNIVERSAL = "vacuous_universal"
UNIVERSAL_HOLDS = "universal_holds"
UNIVERSAL_FAILS = "universal_fails"
WITNESSED = "witnessed"
NO_WITNESS = "no_witness"
VACUOUS_IMPLICATION = "vacuous_implication"
IMPLICATION_HOLDS = "implication_holds"
IMPLICATION_FAILS = "implication_fails"
PLAINLY = "plainly"


def why(
    formula,
    model,
    names=()
):

    """``(verdict, reason)`` -- is it true here, and what makes it so.

    ``names`` maps a domain element to the witness name the reader was given
    (``{0: "c1", 1: "c3"}``).  The model's elements are integers and the model
    is never printed, so a name is the only handle a reader has on an element --
    which is why the naming happens here, where the reason is built, rather than
    over a finished reason afterwards: a named element is also the only one
    whose body can be instantiated and explained.
    """

    verdict = evaluate(
        formula,
        model
    )

    return (
        verdict,
        _reason(
            formula,
            model,
            {},
            verdict,
            dict(names)
        )
    )


def _reason(
    formula,
    model,
    binding,
    verdict,
    names
):

    """The one sentence worth saying about why this formula came out so."""

    if isinstance(formula, ForAll):

        return _universal_reason(
            formula,
            model,
            binding,
            verdict,
            names
        )

    if isinstance(formula, Exists):

        if verdict:

            for element in model.domain():

                if evaluate(
                    formula.body,
                    model,
                    _with(binding, formula.var, element)
                ):

                    return (
                        WITNESSED,
                        _at_element(
                            formula,
                            model,
                            binding,
                            element,
                            True,
                            names
                        )
                    )

        return (
            NO_WITNESS,
            {}
        )

    if isinstance(formula, Implies):

        def because(
            name,
            side,
            side_verdict
        ):

            """That side, and why it came out that way -- when there is a why.

            The verdict is passed in rather than evaluated: each branch below
            has already established what its sides come to, and re-asking the
            model would only recompute an answer we are standing inside.
            """

            values = {
                name: side
            }

            reason = _reason(
                side,
                model,
                binding,
                side_verdict,
                names
            )

            if reason[0] != PLAINLY:

                values[name + "_reason"] = reason

            return values

        if verdict:

            if not evaluate(
                formula.a,
                model,
                binding
            ):

                # True because the condition is not -- so the condition is
                # false, and that is the verdict its own reason answers.
                return (
                    VACUOUS_IMPLICATION,
                    because(
                        "condition",
                        formula.a,
                        False
                    )
                )

            # True with a true condition leaves only one way for it to be
            # true: the consequent is.
            return (
                IMPLICATION_HOLDS,
                because(
                    "consequent",
                    formula.b,
                    True
                )
            )

        # An implication fails in exactly one way, so both verdicts are known
        # without asking: the condition holds and the consequent does not.
        values = because(
            "condition",
            formula.a,
            True
        )

        values.update(
            because(
                "consequent",
                formula.b,
                False
            )
        )

        return (
            IMPLICATION_FAILS,
            values
        )

    return (
        PLAINLY,
        {}
    )


def _at_element(
    formula,
    model,
    binding,
    element,
    verdict,
    names
):

    """The values of a reason that names an element: the name, and the body.

    Shared by the two reasons that answer "which element" -- an ∃ that holds
    and a ∀ that fails.  Both leave the reader with the same next question, and
    both know the verdict of the body there without re-asking the model, so the
    body is instantiated at the element and explained under that verdict.

    Instantiating is what makes the nested reason worth reading: ``P(c3)``
    stands on its own where ``P(x)`` would send the reader back up the block to
    find out what ``x`` was.
    """

    values = {
        "element": names.get(
            element,
            "?"
        )
    }

    if element not in names:

        # Nothing to substitute, and nothing safe to evaluate: an element the
        # clauses never named is not a constant of the model.
        return values

    reason = _reason(
        substitute_formula(
            formula.body,
            {
                formula.var: Term(
                    names[element]
                )
            }
        ),
        model,
        binding,
        verdict,
        names
    )

    if reason[0] != PLAINLY:

        values["body_reason"] = reason

    return values


def _universal_reason(
    formula,
    model,
    binding,
    verdict,
    names
):

    """Why a ∀ holds -- in general terms, or vacuously; never by example."""

    if not verdict:

        for element in model.domain():

            if not evaluate(
                formula.body,
                model,
                _with(binding, formula.var, element)
            ):

                return (
                    UNIVERSAL_FAILS,
                    _at_element(
                        formula,
                        model,
                        binding,
                        element,
                        False,
                        names
                    )
                )

    # "Vacuously" has to be checked over *all* the universally quantified
    # variables, not just the outermost one: in ∀x ∀y (F(x, y) → ¬B(x, y)) the
    # condition is F(x, y), and it is the pair that has to be unsatisfiable.
    variables, condition = _guarded_condition(
        formula
    )

    if condition is not None:

        satisfied = any(
            evaluate(
                condition,
                model,
                dict(
                    binding,
                    **dict(
                        zip(
                            variables,
                            values
                        )
                    )
                )
            )
            for values
            in product(
                model.domain(),
                repeat=len(variables)
            )
        )

        if not satisfied:

            return (
                VACUOUS_UNIVERSAL,
                {"condition": condition}
            )

    return (
        UNIVERSAL_HOLDS,
        {}
    )


def _guarded_condition(
    formula
):

    """The ∀-bound variables, and the condition their body is guarding.

    ``(["x", "y"], F(x, y))`` for ``∀x ∀y (F(x, y) → ¬B(x, y))``; the variables
    come back with the condition because a condition mentioning ``y`` cannot be
    evaluated without binding ``y`` too.
    """

    variables = []

    while isinstance(formula, ForAll):

        variables.append(
            formula.var
        )

        formula = formula.body

    if isinstance(formula, Implies):

        return (
            variables,
            formula.a
        )

    if (
        isinstance(formula, Or)
        and
        isinstance(formula.a, Not)
    ):

        return (
            variables,
            formula.a.x
        )

    return (
        variables,
        None
    )


def _with(
    binding,
    variable,
    element
):

    """``binding`` extended with one more variable."""

    extended = dict(
        binding
    )

    extended[variable] = element

    return extended


# ================================================================
# WHAT TO SAY ABOUT THE MODEL
# ================================================================
#
# Not everything: the reader has the question.  What they cannot get from it is
# which predicates never hold and what is known about each witness.  The
# witnesses are named already -- skolemization named them after their universes
# (steps/skolemize.py) -- so nothing here renames anything.
#
# There used to be a third kind, "what the search added": every surviving clause
# naming no witness and saying nothing universal.  Those are general facts, so
# they are consequences of assumptions the reader already has, and they read as
# news only because they are written in clause form.  In the dogs example the
# two of them were the same fact twice -- a dog does not betray its owner --
# printed differently only because the two clauses store their literals in
# opposite orders.  A list of derived clauses is the search's history, not a
# description of the model, so such a clause is now simply not mentioned.
#
# Everything said is said as a **formula**.  Prose around a clause ("for every
# y: B(c1, y) holds") is a second notation for something the reader has been
# reading in the first one since step 1, and it was the prose that made the
# block unreadable.  So every fact is rendered by display.clause_as_formula and
# comes out of here as a finished line; the narration only indents and prints.
#
# The lines are ordered rather than left in clause order, because clause order
# is the search's history and says nothing about the model.  Three keys, in
# _line_order: arity first, so what is known about single things comes before
# what is known about pairs; then a fact about named witnesses before one
# carrying a ∀, since the concrete is what a reader anchors on; then the order
# the predicates were first written in the problem, so a block reads in the
# vocabulary of the question rather than alphabetically or by accident.


def witnesses_by_universe(
    clauses,
    sorts
):

    """The Skolem constants of these clauses, grouped by universe.

    One line per universe is all the reader needs: the names carry the sorting,
    since ``c`` and ``d`` were chosen to say exactly that.
    """

    grouped = {}

    order = []

    for clause in clauses:

        for literal in clause:

            for index, argument in enumerate(
                literal.atom.args
            ):

                if argument.is_var or argument.args:
                    continue

                universe = sorts.find(
                    (literal.atom.pred, index)
                )

                if universe not in grouped:

                    grouped[universe] = []

                    order.append(
                        universe
                    )

                if argument.name not in grouped[universe]:

                    grouped[universe].append(
                        argument.name
                    )

    return [
        grouped[universe]
        for universe
        in order
    ]


def describe(
    clauses,
    predicate_order=()
):

    """What is worth saying about the model, as lines ready to print.

    Every value in the returned dict -- ``never``, ``always``, and each group's
    facts -- is a list of rendered formula lines, already in the order they are
    to be read (see ``_line_order``).  A line may contain newlines under
    ``config.TALL_BRACKETS``, exactly like ``formula_str``, so the narration
    prints it with ``output.say_block``.

    Facts mentioning witnesses are grouped by *which* witnesses they mention,
    so a fact about two of them is stated once under both rather than repeated
    under each; the groups keep the order the witnesses were first met in.
    A clause that names no witness and is not universal is not reported at all:
    it is a general consequence of assumptions the reader already has, which
    makes it the search's history rather than a description of the model.
    ``predicate_order`` is the order the predicates are first written in the
    problem, and is the last of the sort keys.
    """

    never = []

    always = []

    groups = {}

    order = []

    for clause in clauses:

        # Key and line together, so the sorting can be done on the way out
        # without asking the clause anything twice.
        entry = (
            _line_order(
                clause,
                predicate_order
            ),
            clause_as_formula(
                clause
            )
        )

        universal = _universal_unit(
            clause
        )

        if universal is not None:

            (
                never
                if universal.negated
                else always
            ).append(
                entry
            )

            continue

        mentioned = tuple(
            _constants_in(
                clause
            )
        )

        if mentioned:

            if mentioned not in groups:

                groups[mentioned] = []

                order.append(
                    mentioned
                )

            groups[mentioned].append(
                entry
            )

    return {
        "never": _ordered_lines(never),
        "always": _ordered_lines(always),
        "groups": [
            (
                list(names),
                _ordered_lines(
                    groups[names]
                )
            )
            for names
            in order
        ],
    }


def _ordered_lines(
    entries
):

    """The lines of these ``(key, line)`` pairs, in the order they read best.

    The sort is stable, so two facts the keys cannot separate stay in clause
    order -- there is nothing better to say about them than the order they were
    derived in.
    """

    return [
        line
        for _, line
        in sorted(
            entries,
            key=lambda entry: entry[0]
        )
    ]


def _line_order(
    clause,
    predicate_order
):

    """The sort key of one fact: arity, then specificity, then appearance.

    A clause of several literals is led by its smallest ``(arity,
    appearance)``: the predicate a reader will read first is the one the line
    is about.  A predicate the problem never wrote -- ``=``, or anything the
    search invented -- has no place in ``predicate_order`` and sorts after
    everything that does, rather than raising.
    """

    arity, appearance = min(
        (
            (
                len(literal.atom.args),
                _appearance(
                    literal.atom.pred,
                    predicate_order
                )
            )
            for literal
            in clause
        ),
        default=(
            0,
            len(predicate_order)
        )
    )

    return (
        arity,
        # A fact about named witnesses before one carrying a ∀: the concrete
        # is what the reader anchors the general statements to.
        1 if variables_of(clause) else 0,
        appearance
    )


def _appearance(
    predicate,
    predicate_order
):

    """Where the problem first wrote this predicate, or after all of them."""

    if predicate in predicate_order:

        return predicate_order.index(
            predicate
        )

    return len(
        predicate_order
    )


def _universal_unit(
    clause
):

    """The literal, when the clause says a predicate never or always holds.

    One literal, every argument a distinct variable: ``¬D(x)`` is "nothing is a
    D", ``P(x, y)`` is "P holds of every pair".  Anything mentioning a witness
    is about particular elements and belongs with them instead.  The literal
    comes back rather than a verdict because the caller needs its sign to know
    which of the two lists the line belongs in.
    """

    if len(clause) != 1:
        return None

    literal = clause[0]

    arguments = literal.atom.args

    if not all(
        argument.is_var
        for argument
        in arguments
    ):

        return None

    if len(
        {
            argument.name
            for argument
            in arguments
        }
    ) != len(arguments):

        return None

    return literal


def _constants_in(
    clause
):

    """Every Skolem constant the clause mentions, in order of appearance."""

    found = []

    def walk(term):

        if term.is_var:
            return

        if not term.args:

            if term.name not in found:

                found.append(
                    term.name
                )

            return

        for argument in term.args:

            walk(
                argument
            )

    for literal in clause:

        for argument in literal.atom.args:

            walk(
                argument
            )

    return found
