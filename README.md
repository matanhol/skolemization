# skolemization

An educational first-order-logic resolution prover. Its purpose is not speed and not completeness —
it is to **narrate**, in Hebrew, every step of the CNF conversion and of the resolution refutation,
the way they would be written out by hand in a logic course. The verbose printed output is the
product; the answer at the end is almost a side effect.

Python 3, standard library only. No dependencies, no build step.

```bash
python3 -m examples.question8.pr_and_not_l
```

## What it prints

Step 1, the assumptions and the negated conclusion. Brackets are recomputed from the structure — the
ones you typed to satisfy the parser do not come back out, the ones you left to precedence are put
in, and each is drawn at a height that shows how deep it sits:

```
======================================================================
1. שוללים את המסקנה ומוסיפים אותה ל-KB
======================================================================
F1:
       ⎛                     ⎞
       ⎜⎛            ⎞       ⎟
    ∀x ⎜⎜Pr(x) ∧ L(x)⎟ → C(x)⎟
       ⎜⎝            ⎠       ⎟
       ⎝                     ⎠
```

A resolution step: the two clauses, the literals crossed, the substitution that made them match, and
what is left once they cancel.

```
======================================================================
Resolution step 4
======================================================================

בוחרים:

C2: ¬S(y) ∨ y = c1
C9: S(c3)

הליטרלים שניתן להצליב:
    ¬S(y)
    S(c3)

ההצבה הדרושה:
    y := c3

לאחר ההצבה:
    ¬S(c3)
    S(c3)

הליטרלים זהים פרט לשלילה, ולכן מבטלים אותם.

מתקבל:
    c3 = c1
```

Set `EXPLAIN_CHOICE` and each step also names the two candidates it beat and the ranking key that
decided — for when the prover takes a step you would not have taken.

A search that ends without a contradiction explains *that* too: it sweeps the knowledge base for
redundant clauses and then walks every step still available, one line each, saying why none of them
adds anything. `SATURATED_NO_CONTRADICTION` is the one answer a reader has to take on trust, so it
is the one that gets the longest account.

## The seven steps

One module per teaching step, so a numbered step in the output maps to exactly one file:

| step | | |
| --- | --- | --- |
| 0 | properties of relations added as axioms | `axioms.py` |
| 1 | negate the conclusion, add it to the KB | `preprocessing.py` |
| 2 | remove implications | `steps/implications.py` |
| 3 | negation normal form | `steps/nnf.py` |
| 4 | Skolemization | `steps/skolemize.py` |
| 5 | drop the universal quantifiers | `steps/forall.py` |
| 6 | conjunctive normal form | `steps/cnf.py` |
| 7 | read off the clauses | `steps/clausify.py` |

Then `search.py` saturates: resolution, factoring, and — when the problem uses `=` —
paramodulation, which replaces the entire family of equality axioms with one inference rule that
rewrites equals for equals inside terms.

## As a library

```python
from skolemization import prove, config

config.MAX_RESOLUTION_STEPS = 400        # settings are read at call time

prove(["all x (P(x) -> Q(x))", "exists x P(x)"], "exists x Q(x)")
# -> "PROVED"
```

`prove` returns `"PROVED"`, `"SATURATED_NO_CONTRADICTION"` or `"UNKNOWN"` (the step limit ran out).
`Equivalence(φ1, φ2).check()` runs both entailment directions and reports the verdict.

The input language takes `and or not -> forall exists` and their symbols (`∧ ∨ ¬ → ∀ ∃`), plain
words (`all x, y P(x,y)`), and `=` / `!=` / `≠`. There is no biconditional; write it as two
implications. Every symbol the narration prints parses back in.
There are no constants: every bare name must be bound by a quantifier, because an unbound one is
always a typo or a quantifier that did not reach as far as it looked.

## The examples

Each directory is one problem; each script inside it is one conclusion, with its own commentary.

| | |
| --- | --- |
| `examples/dogs/` | the running example: dogs, owners, loyalty and betrayal — seven scripts over one set of assumptions, four of whose conclusions do not follow |
| `examples/question8/` | programmers, logic and bonuses |
| `examples/teacher/` | the lecturer's own question, run with nothing overridden |
| `examples/ceo/` | exactly one applicant succeeded, at least two applied ⇒ someone applied and failed |
| `examples/uniqueness/` | the same uniqueness question five ways: with equality axioms, without them, with the arguments written in matching order, with paramodulation, with superposition |
| `examples/equality/` | a burglary, in four formulations — the cost of doing equality by axioms versus by rule (343 steps against 9) |
| `examples/recursion/` | one question, two rankings: one runs away into nested Skolem terms, the other proves it in six steps |
| `examples/equivalence/` | two formulas, both directions, and the ≡ verdict |

They are also the regression suite: after changing solver logic, run them and check the statuses
still match what each docstring claims.

## Settings

`skolemization/config.py`, all read at call time so they can be changed before a `prove`:

| | |
| --- | --- |
| `STRATEGY` | which step to take next — the default ranks by term depth, then length, then rule, then whether an assignment is needed |
| `EQUALITY_RULE` | `"paramodulation"`, `"superposition"`, or `"none"` to go back to axioms |
| `FOCUS_ON_WITNESS` | try the search once with every variable pinned to the Skolem witness before running it in general |
| `SET_OF_SUPPORT` | allow only inferences that touch the negated conclusion |
| `TALL_BRACKETS` | draw grouping brackets at their real height, as above |
| `EXPLAIN_CHOICE` | off by default; on, it prints the runners-up after each step and the key that beat them |
| `EXPLAIN_COUNTEREXAMPLE` | experimental; on, a saturated search describes the counter-model it found — the witnesses, what holds of them, and every assumption checked in it |
| `LANGUAGE` | `"he"` or `"en"` — the narration's language; the text direction follows from it |
| `NARRATE` | off makes `prove` a silent library call |

## The notebook

`build_notebook.py` flattens the whole package into `skolemization.ipynb` — one Colab cell holding
the entire model, then a cell per example. It is generated and deliberately untracked; rebuild it
with `python3 build_notebook.py`. Set `LANGUAGE = "en"` first and it writes
`skolemization.en.ipynb` instead, with the commentary and the narration both in English. The proof that flattening changed nothing is that the narration is
byte-for-byte identical between the package and the notebook cell.

`skolemization_example.py` is the frozen single-file original the package was split out of. It still
runs, and it is expected to drift.
