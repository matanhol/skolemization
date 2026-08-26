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
"""

from itertools import product

from .clauses import canonical_clause
from .formulas import (
    And,
    Atom,
    Exists,
    ForAll,
    Implies,
    Not,
    Or,
)


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
# The one rule worth stating: a **universal** is never explained by pointing at
# an element -- "it holds of every element", or "vacuously, because nothing
# satisfies the condition".  Only an **existential** names a witness, because
# there naming one *is* the explanation.

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
    model
):

    """``(verdict, reason)`` -- is it true here, and what makes it so."""

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
            verdict
        )
    )


def _reason(
    formula,
    model,
    binding,
    verdict
):

    """The one sentence worth saying about why this formula came out so."""

    if isinstance(formula, ForAll):

        return _universal_reason(
            formula,
            model,
            binding,
            verdict
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
                        {"element": element}
                    )

        return (
            NO_WITNESS,
            {}
        )

    if isinstance(formula, Implies):

        if verdict:

            if not evaluate(
                formula.a,
                model,
                binding
            ):

                return (
                    VACUOUS_IMPLICATION,
                    {"condition": formula.a}
                )

            return (
                IMPLICATION_HOLDS,
                {"consequent": formula.b}
            )

        return (
            IMPLICATION_FAILS,
            {
                "condition": formula.a,
                "consequent": formula.b
            }
        )

    return (
        PLAINLY,
        {}
    )


def _universal_reason(
    formula,
    model,
    binding,
    verdict
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
                    {"element": element}
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
# SORTS
# ================================================================
#
# A counter-model reads badly when everything is thrown into one universe:
# F(x, y) relates two different kinds of thing, and g1(c) -- sitting in F's
# second place -- is not the same kind of thing as c.  So the argument
# positions are sorted first, and everything after that is said per universe.
#
# The rule is the only one there is: two positions are the same sort when
# something occurs in both.  A variable shared between D(x) and F(x, y) merges
# D·1 with F·1; a term occurring in two places merges those; a function's
# result belongs to whatever position it is written into.  Positions never
# linked stay apart, which is what keeps F(x, y) two universes by default.


RESULT = "result"


class Sorts:

    """Argument positions, merged into universes -- a union-find."""

    def __init__(self):

        self.parent = {}

    def find(self, node):

        """The universe a position belongs to."""

        self.parent.setdefault(
            node,
            node
        )

        while self.parent[node] != node:

            self.parent[node] = self.parent[
                self.parent[node]
            ]

            node = self.parent[node]

        return node

    def merge(self, one, other):

        """Say that these two positions hold the same kind of thing."""

        one = self.find(one)

        other = self.find(other)

        if one != other:

            self.parent[other] = one

    def universes(self):

        """Every universe, as a map from its representative to its positions."""

        grouped = {}

        for node in self.parent:

            grouped.setdefault(
                self.find(node),
                []
            ).append(
                node
            )

        return {
            root: sorted(members)
            for root, members
            in grouped.items()
        }


def sorts_of(clauses):

    """Infer the universes from where each variable and term is written.

    Runs over the clauses *as they entered the search*, not only the survivors:
    a link made by a clause that was later subsumed is still a fact about the
    vocabulary.
    """

    sorts = Sorts()

    for clause in clauses:

        occurrences = {}

        for literal in clause:

            for index, argument in enumerate(
                literal.atom.args
            ):

                _place_term(
                    argument,
                    (literal.atom.pred, index),
                    sorts,
                    occurrences
                )

        for places in occurrences.values():

            for other in places[1:]:

                sorts.merge(
                    places[0],
                    other
                )

    return sorts


def _place_term(
    term,
    position,
    sorts,
    occurrences
):

    """Record that ``term`` is written at ``position``, and recurse into it."""

    sorts.find(
        position
    )

    key = (
        term.name
        if term.is_var
        else _term_key(term)
    )

    occurrences.setdefault(
        key,
        []
    ).append(
        position
    )

    if term.is_var:
        return

    if term.args:

        # The function's result is whatever this position holds; its arguments
        # are sorted by their own places in it.
        sorts.merge(
            position,
            (term.name, RESULT)
        )

        for index, argument in enumerate(
            term.args
        ):

            _place_term(
                argument,
                (term.name, index),
                sorts,
                occurrences
            )


def _term_key(term):

    """A term as a hashable key -- ``g1(c)`` and ``g1(c)`` are the same thing."""

    if not term.args:
        return term.name

    return (
        term.name,
        tuple(
            _term_key(argument)
            for argument
            in term.args
        )
    )


# ================================================================
# NAMING AND DESCRIBING
# ================================================================

LETTERS = "ABCDEFGH"


class Naming:

    """Which universe each position belongs to, and what the witnesses are called.

    A universe gets a letter in order of first appearance; a witness gets that
    letter in lower case and a number, in its **own** universe.  So the Skolem
    term ``g1(c)``, written into ``F``'s second place, is ``b1`` -- not another
    ``a``, which is the whole point of sorting the positions first.
    """

    def __init__(
        self,
        sorts,
        clauses
    ):

        self.sorts = sorts

        self.letters = {}

        self.witnesses = []

        self._names = {}

        self._collect(
            clauses
        )

    def letter_for(
        self,
        position
    ):

        """The universe a position belongs to, as a letter."""

        root = self.sorts.find(
            position
        )

        if root not in self.letters:

            self.letters[root] = LETTERS[
                len(self.letters)
                %
                len(LETTERS)
            ]

        return self.letters[
            root
        ]

    def name_of(
        self,
        term
    ):

        """What this ground term is called, or None if it is not a witness."""

        return self._names.get(
            _term_key(term)
        )

    def _collect(
        self,
        clauses
    ):

        """Name every ground term, in the universe it is written into."""

        counts = {}

        # Letters first, in the order the positions are written, so universe A
        # is the one the reader meets first rather than whichever happened to
        # hold the first ground term.
        for clause in clauses:

            for literal in clause:

                for index, argument in enumerate(
                    literal.atom.args
                ):

                    self._walk_positions(
                        argument,
                        (literal.atom.pred, index)
                    )

        for clause in clauses:

            for literal in clause:

                for index, argument in enumerate(
                    literal.atom.args
                ):

                    self._name_term(
                        argument,
                        (literal.atom.pred, index),
                        counts
                    )

    def _walk_positions(
        self,
        term,
        position
    ):

        """Give every position a letter, in the order it appears."""

        self.letter_for(
            position
        )

        if term.is_var:
            return

        for index, argument in enumerate(
            term.args
        ):

            self._walk_positions(
                argument,
                (term.name, index)
            )

    def _name_term(
        self,
        term,
        position,
        counts
    ):

        """Give a ground term a name in its universe, once."""

        if term.is_var:
            return

        for index, argument in enumerate(
            term.args
        ):

            self._name_term(
                argument,
                (term.name, index),
                counts
            )

        if not _is_ground(term):

            # g1(x) is not a witness -- it is a function of whatever x is.  Only
            # closed terms name an element of a universe.
            return

        key = _term_key(
            term
        )

        if key in self._names:
            return

        letter = self.letter_for(
            position
        )

        counts[letter] = counts.get(
            letter,
            0
        ) + 1

        name = f"{letter.lower()}{counts[letter]}"

        self._names[key] = name

        self.witnesses.append(
            (
                name,
                letter,
                self._render_term(
                    term
                )
            )
        )

    def _render_term(
        self,
        term
    ):

        """A term with its inner witnesses already named: ``g1(a1)``."""

        if not term.args:
            return term.name

        return (
            term.name
            + "("
            + ", ".join(
                self.name_of(argument)
                or
                self._render_term(argument)
                for argument
                in term.args
            )
            + ")"
        )

    def universes(self):

        """Each universe: its letter, the positions in it, and its witnesses."""

        listed = []

        for root, members in self.sorts.universes().items():

            letter = self.letter_for(
                members[0]
            )

            listed.append(
                (
                    letter,
                    [
                        _position_label(position)
                        for position
                        in members
                    ],
                    [
                        (name, term)
                        for name, where, term
                        in self.witnesses
                        if where == letter
                    ]
                )
            )

        return sorted(
            listed
        )


def _is_ground(term):

    """Does this term mention no variable at all?"""

    if term.is_var:
        return False

    return all(
        _is_ground(argument)
        for argument
        in term.args
    )


def _position_label(position):

    """``P·1`` for an argument place, ``g1·→`` for a function's result."""

    symbol, index = position

    if index == RESULT:
        return f"{symbol}·→"

    return f"{symbol}·{index + 1}"


# Variable letters, one per universe: a variable's name is what says which
# universe it runs over, so nothing has to be annotated with "∈ A".

VARIABLE_LETTERS = "xyzuvw"


def describe(
    clauses,
    naming,
    already_said=()
):

    """What is worth saying about the model, and nothing else.

    Three kinds of thing come out, because those are the three a reader cannot
    get from the question itself:

    * a predicate that **never** holds, or **always** does -- a one-literal
      clause over distinct variables;
    * everything known about each **witness**, gathered onto its own line
      rather than scattered over the clause list;
    * whatever the **search added** that is neither of those.

    ``already_said`` is the assumptions' own clauses as they entered.  A
    surviving clause that is one of them is the question restated, and saying
    it back to the reader is what made the earlier version unreadable.
    """

    said = {
        canonical_clause(clause)
        for clause
        in already_said
    }

    never = []

    always = []

    facts = {}

    added = []

    for clause in clauses:

        universal = _universal_unit(
            clause
        )

        if universal is not None:

            predicate, negated = universal

            (
                never
                if negated
                else always
            ).append(
                predicate
            )

            continue

        statement = _statement(
            clause,
            naming
        )

        mentioned = _witnesses_in(
            clause,
            naming
        )

        if mentioned:

            for name in mentioned:

                facts.setdefault(
                    name,
                    []
                ).append(
                    statement
                )

            continue

        if canonical_clause(clause) in said:
            continue

        added.append(
            statement
        )

    return {
        "never": never,
        "always": always,
        "witnesses": [
            (
                name,
                term,
                facts.get(name, [])
            )
            for name, _, term
            in naming.witnesses
        ],
        "added": added,
    }


def _universal_unit(
    clause
):

    """``(predicate, negated)`` when the clause says a predicate never or always holds.

    One literal, every argument a distinct variable: ``¬D(x)`` is "nothing is a
    D", ``P(x, y)`` is "P holds of every pair".  Anything mentioning a term is
    about particular elements and belongs to a witness instead.
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

    return (
        literal.atom.pred,
        literal.negated
    )


def _witnesses_in(
    clause,
    naming
):

    """Every named witness the clause mentions, in order."""

    found = []

    def walk(term):

        name = naming.name_of(
            term
        )

        if name is not None and name not in found:

            found.append(
                name
            )

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


def _statement(
    clause,
    naming
):

    """One clause as ``(variables, conditions, consequences)`` for the narration."""

    renaming = _variable_names(
        clause,
        naming
    )

    return {
        "variables": sorted(
            set(
                renaming.values()
            )
        ),
        "conditions": [
            _render_literal(literal, naming, renaming)
            for literal
            in clause
            if literal.negated
        ],
        "consequences": [
            _render_literal(literal, naming, renaming)
            for literal
            in clause
            if not literal.negated
        ],
    }


def _variable_names(
    clause,
    naming
):

    """Rename the clause's variables so the letter says which universe.

    ``x`` for the first universe, ``y`` for the second, and a number when one
    clause needs two variables from the same one.
    """

    renaming = {}

    counts = {}

    for literal in clause:

        for index, argument in enumerate(
            literal.atom.args
        ):

            _name_variables(
                argument,
                (literal.atom.pred, index),
                naming,
                renaming,
                counts
            )

    return renaming


def _name_variables(
    term,
    position,
    naming,
    renaming,
    counts
):

    """Give every variable a letter belonging to its universe."""

    if term.is_var:

        if term.name in renaming:
            return

        letter = naming.letter_for(
            position
        )

        index = LETTERS.index(
            letter
        ) % len(VARIABLE_LETTERS)

        counts[letter] = counts.get(
            letter,
            0
        ) + 1

        renaming[term.name] = (
            VARIABLE_LETTERS[index]
            if counts[letter] == 1
            else f"{VARIABLE_LETTERS[index]}{counts[letter]}"
        )

        return

    for index, argument in enumerate(
        term.args
    ):

        _name_variables(
            argument,
            (term.name, index),
            naming,
            renaming,
            counts
        )


def _render_literal(
    literal,
    naming,
    renaming
):

    """``B(a1, y)`` -- witnesses by name, variables by their universe's letter."""

    return (
        literal.atom.pred
        + "("
        + ", ".join(
            _render_argument(argument, naming, renaming)
            for argument
            in literal.atom.args
        )
        + ")"
    )


def _render_argument(
    term,
    naming,
    renaming
):

    """One argument: a witness name, a renamed variable, or a term of those."""

    if term.is_var:

        return renaming.get(
            term.name,
            term.name
        )

    name = naming.name_of(
        term
    )

    if name is not None:
        return name

    return (
        term.name
        + "("
        + ", ".join(
            _render_argument(argument, naming, renaming)
            for argument
            in term.args
        )
        + ")"
    )


def witness_elements(
    model,
    naming,
    clauses
):

    """Which domain element each named witness denotes, for the explanations.

    The finite model is not printed -- it is the proof that the description is
    satisfiable -- but when an explanation wants to point at a witness, this is
    what turns the model's element back into the name the reader has been given.
    """

    names = {}

    for clause in clauses:

        for literal in clause:

            for argument in literal.atom.args:

                _element_of(
                    argument,
                    model,
                    naming,
                    names
                )

    return names


def _element_of(
    term,
    model,
    naming,
    names
):

    """Record the element a ground term denotes, and recurse into it."""

    if term.is_var:
        return

    for argument in term.args:

        _element_of(
            argument,
            model,
            naming,
            names
        )

    name = naming.name_of(
        term
    )

    if name is None:
        return

    try:

        element = model.value_of(
            term,
            {}
        )

    except KeyError:
        return

    names.setdefault(
        element,
        name
    )
