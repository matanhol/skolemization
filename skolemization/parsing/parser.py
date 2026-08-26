"""The recursive-descent parser."""

import re

from ..formulas import (
    And,
    Atom,
    Exists,
    ForAll,
    Implies,
    Not,
    Or,
    Term,
)
from . import aliases
from .tokenizer import tokenize


# What a predicate or variable may be called.

NAME_RE = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*$"
)


class Parser:

    """Recursive descent over the token stream.

    Precedence, loosest first: ``->``, ``or``, ``and``, then unary (``not``, a
    quantifier, or a parenthesised group).  ``bound_variables`` tracks which names
    are currently quantified, and ``parse_term`` rejects any bare name that is
    not among them.
    """

    def __init__(
        self,
        text
    ):

        """Tokenize ``text``, start at the first token with nothing bound."""

        self.text = text

        self.tokens = tokenize(
            text
        )

        self.i = 0

        self.bound_variables = []

    def peek(self):

        """The current token, or None once the input is exhausted."""

        if self.i >= len(
            self.tokens
        ):
            return None

        return self.tokens[
            self.i
        ]

    def eat(
        self,
        expected=None
    ):

        """Consume the current token, checking it is ``expected`` when one is given."""

        token = self.peek()

        if token is None:

            raise SyntaxError(
                "Unexpected end of formula"
            )

        if (
            expected is not None
            and token != expected
        ):

            raise SyntaxError(
                f"Expected '{expected}', "
                f"found '{token}'"
            )

        self.i += 1

        return token

    def parse(self):

        """Parse one whole formula and insist the input is fully consumed."""

        result = (
            self.parse_implication()
        )

        if self.peek() is not None:

            raise SyntaxError(
                f"Unexpected token: "
                f"{self.peek()}"
            )

        return result

    def parse_implication(self):

        """Parse ``a -> b``, right-associative: ``a -> b -> c`` is ``a -> (b -> c)``."""

        left = self.parse_or()

        if self.peek() == aliases.IMPLIES:

            self.eat(
                aliases.IMPLIES
            )

            right = (
                self.parse_implication()
            )

            return Implies(
                left,
                right
            )

        return left

    def parse_or(self):

        """Parse a chain of ``or``, left-associative."""

        left = self.parse_and()

        while self.peek() == aliases.OR:

            self.eat(
                aliases.OR
            )

            left = Or(
                left,
                self.parse_and()
            )

        return left

    def parse_and(self):

        """Parse a chain of ``and``, which binds tighter than ``or``."""

        left = self.parse_unary()

        while self.peek() == aliases.AND:

            self.eat(
                aliases.AND
            )

            left = And(
                left,
                self.parse_unary()
            )

        return left

    def parse_quantified_variables(self):

        """Eat the variables one quantifier binds.

        A quantifier carries across a list, so ``all x, y, z`` means
        ``all x, all y, all z``.  The separators stay optional, and a different
        quantifier keyword simply ends the list and starts its own::

            all x, y, z P(x,y,z)
            all x y z P(x,y,z)
            all x, y, exists z, w B(x,y,z,w)
        """

        variables = [
            self.eat()
        ]

        while True:

            after_separator = (
                1
                if self.token_at(0) in (",", ":")
                else 0
            )

            if not self.starts_variable(
                after_separator
            ):

                # A separator sitting between the list and the body is eaten
                # here, which is what makes the comma in "all x, P(x)"
                # optional rather than meaningful.
                if after_separator:
                    self.eat()

                return variables

            if after_separator:
                self.eat()

            variables.append(
                self.eat()
            )

    def token_at(
        self,
        offset
    ):

        """The token ``offset`` places ahead, or None past the end."""

        index = self.i + offset

        if index >= len(
            self.tokens
        ):
            return None

        return self.tokens[
            index
        ]

    def starts_variable(
        self,
        offset
    ):

        """Is the token at ``offset`` another variable in a quantifier list?

        After a quantifier's variable, the body can only begin with ``not``,
        another quantifier, ``(``, a predicate *applied* to arguments, or a
        term that an ``=`` follows.  So a bare name that is none of those
        cannot be anything but one more variable -- which is what makes
        ``all x, y, z`` unambiguous.

        The equality case is why the ``=`` check is here: in ``all y x = y``
        the ``x`` is the body, not a third variable.
        """

        token = self.token_at(
            offset
        )

        if token is None:
            return False

        if token in aliases.CANONICAL_TOKENS:
            return False

        if not NAME_RE.match(
            token
        ):
            return False

        following = self.token_at(
            offset + 1
        )

        return following not in (
            "(",
            aliases.EQUALS,
            aliases.NOT_EQUALS
        )

    def quantify(
        self,
        quantifier,
        variables,
        body
    ):

        """Wrap ``body`` in one quantifier node per variable, innermost last.

        ``[x, y, z]`` becomes ``∀x ∀y ∀z body``, so the leftmost variable ends
        up outermost -- the order they were written in.
        """

        node = body

        for variable in reversed(
            variables
        ):

            if quantifier == aliases.FORALL:

                node = ForAll(
                    variable,
                    node
                )

            else:

                node = Exists(
                    variable,
                    node
                )

        return node

    def parse_unary(self):

        """Parse a negation, a quantifier, a parenthesised group, or an atom.

        A quantifier body is parsed with ``parse_implication``, so it reaches as far
        right as it can: in ``all x P(x) -> Q(x)`` the x covers the whole implication.
        """

        token = self.peek()

        if token == aliases.NOT:

            self.eat(
                aliases.NOT
            )

            return Not(
                self.parse_unary()
            )

        if token in (
            aliases.FORALL,
            aliases.EXISTS
        ):

            quantifier = (
                self.eat()
            )

            variables = (
                self.parse_quantified_variables()
            )

            old_bound = list(
                self.bound_variables
            )

            self.bound_variables.extend(
                variables
            )

            body = (
                self.parse_implication()
            )

            self.bound_variables = (
                old_bound
            )

            return self.quantify(
                quantifier,
                variables,
                body
            )

        if token == "(":

            self.eat(
                "("
            )

            result = (
                self.parse_implication()
            )

            self.eat(
                ")"
            )

            return result

        return self.parse_atom()

    def equality_ahead(self):

        """Is the thing starting here a term followed by ``=`` or ``≠``?

        Decided by scanning, not by guessing: a term is a name and, when it is
        applied, a balanced run of parentheses.  ``P(x)`` and ``f(x) = y`` start
        identically, so the only way to tell an atom from the left side of an
        equality is to look past the term.
        """

        position = self.i

        if position >= len(self.tokens):
            return False

        if not NAME_RE.match(
            self.tokens[position]
        ):

            return False

        position += 1

        if (
            position < len(self.tokens)
            and
            self.tokens[position] == "("
        ):

            depth = 0

            while position < len(self.tokens):

                if self.tokens[position] == "(":
                    depth += 1

                elif self.tokens[position] == ")":

                    depth -= 1

                    if depth == 0:

                        position += 1

                        break

                position += 1

        return (
            position < len(self.tokens)
            and
            self.tokens[position] in (
                aliases.EQUALS,
                aliases.NOT_EQUALS
            )
        )

    def parse_equality(self):

        """Parse ``term = term`` (or ``≠``) into the equality predicate.

        Sugar, and nothing more: the atom that comes out is an ordinary binary
        predicate named ``=``, so unification, resolution and the clause form
        all treat it like any other.  What makes it equality rather than an
        arbitrary relation is either the axioms the caller declares or the
        paramodulation rule -- never the parser.
        """

        left = self.parse_term()

        operator = self.eat()

        right = self.parse_term()

        atom = Atom(
            aliases.EQUALITY,
            (
                left,
                right
            )
        )

        if operator == aliases.NOT_EQUALS:

            return Not(
                atom
            )

        return atom

    def parse_atom(self):

        """Parse ``pred(term, ...)``, or ``term = term``.

        Every predicate must be applied; equality is the one infix form.
        """

        if self.equality_ahead():

            return self.parse_equality()

        predicate = self.eat()

        self.eat(
            "("
        )

        args = []

        if self.peek() != ")":

            while True:

                args.append(
                    self.parse_term()
                )

                if self.peek() == ",":

                    self.eat(
                        ","
                    )

                    continue

                break

        self.eat(
            ")"
        )

        return Atom(
            predicate,
            tuple(args)
        )

    def parse_term(self):

        """Parse a function application or a quantified variable.

        Every bare name must be bound by an enclosing quantifier.  There is no
        such thing as a constant in the input language: constants exist only as
        Skolem witnesses, invented in step 4.  So an unbound name is always a
        mistake -- a typo, or a quantifier that did not reach as far as it
        looked -- and saying so here is the difference between a clear error and
        a proof of a question you did not ask.

        A function application like ``f(x)`` is fine; it is unambiguous, and
        only the argument-less case is rejected.
        """

        name = self.eat()

        if self.peek() == "(":

            self.eat(
                "("
            )

            args = []

            if self.peek() != ")":

                while True:

                    args.append(
                        self.parse_term()
                    )

                    if self.peek() == ",":

                        self.eat(
                            ","
                        )

                        continue

                    break

            self.eat(
                ")"
            )

            return Term(
                name,
                tuple(args),
                False
            )

        if name not in self.bound_variables:

            raise SyntaxError(
                self.unbound_message(
                    name
                )
            )

        return Term(
            name,
            (),
            True
        )

    def unbound_message(
        self,
        name
    ):

        """Explain an unbound name, and say what is in scope instead."""

        if self.bound_variables:

            in_scope = (
                "in scope here: "
                + ", ".join(
                    self.bound_variables
                )
            )

        else:

            in_scope = (
                "no quantifier is in scope at that point"
            )

        return (
            f"'{name}' is not bound by any quantifier "
            f"({in_scope}).\n"
            f"    in: {self.text}\n"
            f"Every term must be introduced by a quantifier -- "
            f"constants are not part of the input language, "
            f"they only appear as Skolem witnesses in step 4.\n"
            f"If '{name}' was meant to be a variable, check that its "
            f"quantifier reaches this far: a quantifier body extends as "
            f"far right as it can, so parentheses may be needed."
        )
