"""Turning declared relation properties into extra assumptions.

The axioms are produced as *source text* and appended to the assumption
list, so they go through the ordinary parser like everything else.

Equality is not built into the prover.  Model it as an ordinary predicate and
declare its properties here, or the search will never connect Eq(x,y) with
Eq(y,x).
"""


# Property name -> how to state it about a relation R.
#
# Order matters only in that it fixes the order the axioms appear in the KB.

AXIOM_TEMPLATES = [
    (
        "symmetric",
        "all x all y "
        "({relation}(x,y) -> "
        "{relation}(y,x))"
    ),
    (
        "transitive",
        "all x all y all z "
        "(({relation}(x,y) and "
        "{relation}(y,z)) -> "
        "{relation}(x,z))"
    ),
    (
        "reflexive",
        "all x "
        "{relation}(x,x)"
    ),
]


def add_relation_axioms(
    assumptions,
    symmetric_relations=None,
    transitive_relations=None,
    reflexive_relations=None
):

    """Return (assumptions + generated axioms, [(property, relation, axiom)]).

    The second value is what the narration reports; the first is what actually
    gets parsed.
    """

    declared = {
        "symmetric": set(
            symmetric_relations
            or
            []
        ),
        "transitive": set(
            transitive_relations
            or
            []
        ),
        "reflexive": set(
            reflexive_relations
            or
            []
        ),
    }

    result = list(
        assumptions
    )

    generated = []

    for (
        property_name,
        template
    ) in AXIOM_TEMPLATES:

        for relation in sorted(
            declared[property_name]
        ):

            axiom = (
                template.format(
                    relation=relation
                )
            )

            result.append(
                axiom
            )

            generated.append(
                (
                    property_name,
                    relation,
                    axiom
                )
            )

    return (
        result,
        generated
    )
