"""An educational first-order-logic resolution prover.

The point of this package is not speed -- it is the running commentary.  Every
stage prints what it did and why, the way it would be written out by hand:

    prove()                     prover.py
      add_relation_axioms()     axioms.py              symmetry / transitivity / ...
      preprocess()              preprocessing.py       the seven numbered steps
        signature_of()          signature.py           refuse inconsistent symbols
        remove_implications()   steps/implications.py  2
        to_nnf()                steps/nnf.py           3
        skolemize()             steps/skolemize.py     4
        remove_forall()         steps/forall.py        5
        to_cnf()                steps/cnf.py           6
        extract_clauses()       steps/clausify.py      7
      focus_kb_on_witness()     focus.py               the "try x := witness" heuristic
      run_resolution_search()   search.py              saturation until the empty clause

Usage::

    from skolemization import prove

    prove(
        ["all x (D(x) -> exists y F(x,y))"],
        "exists x exists y F(x,y)",
    )

which returns "PROVED", "SATURATED_NO_CONTRADICTION" or "UNKNOWN".
"""

from . import config
from .equivalence import (
    Equivalence,
    EquivalenceResult,
)
from .output import say
from .preprocessing import preprocess
from .prover import prove
from .search import run_resolution_search

__all__ = [
    "Equivalence",
    "EquivalenceResult",
    "config",
    "preprocess",
    "prove",
    "run_resolution_search",
    "say",
]
