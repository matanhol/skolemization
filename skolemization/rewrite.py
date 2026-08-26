"""A record of one rule application, so a step can show its working.

The clausification transforms recurse over the whole formula and hand back the
finished result, which leaves the interesting part -- every De Morgan, every
distribution -- invisible.  Each transform therefore takes an optional list and
appends one of these per rule it fires, the same way ``skolemize`` already
collects its ``explanations``.

Records describe the **local** rewrite, with children as they stood before the
recursion reached them.  That is what the rule actually did at that node, and
it is what a reader would write on paper::

    ¬(a ∧ b)   ⇒   ¬a ∨ ¬b

rather than the fully-processed subtree, which would show several rules at
once and none of them clearly.
"""

from dataclasses import dataclass


# The rules a reader might see.  narration.py holds their Hebrew names.

IMPLICATION = "implication"
DOUBLE_NEGATION = "double_negation"
DE_MORGAN_AND = "de_morgan_and"
DE_MORGAN_OR = "de_morgan_or"
NOT_FORALL = "not_forall"
NOT_EXISTS = "not_exists"
DROP_FORALL = "drop_forall"
DISTRIBUTE = "distribute"


@dataclass(frozen=True)
class Rewrite:

    """One rule application: which rule, and the subformula either side of it."""

    rule: str
    before: object
    after: object


def record(
    rewrites,
    rule,
    before,
    after
):

    """Append a rewrite, tolerating the no-tracing case.

    Every transform takes ``rewrites=None`` when nobody is watching, so this
    keeps the ``if rewrites is not None`` check out of the transforms.
    """

    if rewrites is None:
        return

    rewrites.append(
        Rewrite(
            rule,
            before,
            after
        )
    )
