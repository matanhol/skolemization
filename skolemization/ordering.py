"""A term ordering, so an equation can be used in one direction only.

Paramodulation may rewrite ``s`` into ``t`` and ``t`` into ``s``.  Half of that
work undoes the other half: the search rewrites ``a`` to ``b``, then ``b`` back
to ``a``, forever.  Superposition fixes this by ordering terms and only ever
rewriting the bigger one into the smaller -- downhill, never up.

The ordering here is the Knuth-Bendix ordering with every symbol weighing 1,
which for this package means:

    s ≻ t   iff   every variable occurs in s at least as often as in t,
                  and s has more symbols than t
                  (ties broken by how the two print, so the order is total)

The variable condition is not decoration.  Without it the ordering would not
survive substitution -- ``f(x) ≻ y`` by size, but ``x := y`` makes both sides
``f(y)`` and ``y``... still fine, whereas ``g(x) ≻ f(y)`` would flip once
``y := g(g(x))``.  Requiring t's variables to be covered by s's is what makes
the comparison stable under every substitution, which is what a rewrite rule
needs.
"""

from collections import Counter


def weight(term):

    """How many symbols the term is built from; variables count as one."""

    return 1 + sum(
        weight(argument)
        for argument
        in term.args
    )


def depth(term):

    """How deeply the term nests: 0 for a variable or a constant.

    The measure the search ranks by first.  Weight counts every symbol, so a
    clause of many shallow literals can outweigh one carrying ``g2(g1(g2(c)))``;
    depth is what actually runs away when a Skolem function feeds itself.
    """

    if not term.args:
        return 0

    return 1 + max(
        depth(argument)
        for argument
        in term.args
    )


def variable_counts(term):

    """How many times each variable occurs, as a multiset."""

    if term.is_var:

        return Counter(
            [term.name]
        )

    total = Counter()

    for argument in term.args:

        total += variable_counts(
            argument
        )

    return total


def greater(first, second):

    """Is ``first`` strictly bigger, in a way substitution cannot overturn?"""

    if not (
        variable_counts(second)
        <=
        variable_counts(first)
    ):

        return False

    if (
        weight(first)
        !=
        weight(second)
    ):

        return (
            weight(first)
            >
            weight(second)
        )

    return (
        str(first)
        >
        str(second)
    )
