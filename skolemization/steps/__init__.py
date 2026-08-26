"""The clausification pipeline, one module per step.

Each module holds exactly the transform its step performs, in the order they
run::

    2   implications.py   remove_implications   P → Q  becomes  ¬P ∨ Q
    3   nnf.py            to_nnf                negations pushed in to the atoms
    4   skolemize.py      skolemize             ∃ replaced by witnesses
    5   forall.py         remove_forall         ∀ prefixes dropped
    6   cnf.py            to_cnf                distributed into a conjunction
    7   clausify.py       extract_clauses       clauses read off the CNF

The numbering starts at 2 because the first two steps are not transforms and
live elsewhere:

    0   ../axioms.py      add_relation_axioms   -- called from prover.py, not
                                                   from the pipeline
    1   ../preprocessing.py                     -- parse, and negate the
                                                   conclusion

``preprocessing.py`` is what announces each step and drives it; these modules
only compute, and print nothing.
"""
