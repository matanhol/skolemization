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

## The counter-model

A search that runs dry rather than reaching □ has proved something after all. Refutation
completeness has a second half: a clause set saturated under a complete calculus with no empty
clause in it **is** satisfiable — so the surviving clauses are not what stands between the reader
and a counter-model, they are the description of one. `counterexample.py` reads it off and states
it: the witnesses, what is known about each of them, which predicates never or always hold, and
then every assumption and the conclusion evaluated in that model. This is `some_dog_exists` — the
conclusion "there is a dog", which does not follow.

```
======================================================================
מודל נגדי
======================================================================

החיפוש רווה בלי סתירה, ולכן קבוצת ה-clauses ספיקה -- ויש בה מודל.
הנה מודל שמקיים את כל ה-clauses שנשארו, ולכן גם את ההנחות
ואת שלילת המסקנה. זהו מודל נגדי לטענה.

לא מתקיים אף פעם:
    ∀x ¬D(x)

העדים:
    c

c:
    ∀y ¬F(c, y)
    ∀y B(c, y)

בדיקה של המודל מול השאלה המקורית:

                                        הנחה 1: ←
           ∀x (D(x) → (∃y (O(x, y) ∧ F(x, y))))
                       ✓ מתקיימת במודל.

ריקנית: אין במודל איבר שמקיים את התנאי:
                                   D(x)


                                        הנחה 2: ←
                   ∀x (∀y (F(x, y) → ¬B(x, y)))
                       ✓ מתקיימת במודל.

ריקנית: אין במודל איבר שמקיים את התנאי:
                                F(x, y)


                                        הנחה 3: ←
                              ∃x (∀y (B(x, y)))
                       ✓ מתקיימת במודל.

                             העד הוא c: ←
            מתקיים עבור כל איברי התחום.


                                         מסקנה: ←
                                      ∃x (D(x))
                  ✗ אינה מתקיימת במודל.

            אין במודל איבר שמקיים אותו.

ההנחות מתקיימות והמסקנה לא, ולכן המסקנה אינה נובעת מהן.
```

The block is anchored to the right, because that is where a Hebrew reader starts a line: depth steps
inward from that edge, and `←` marks a block opening.

The witnesses are grouped by universe and named for it. The sorts are inferred before
skolemization, so one witness in a universe gets the bare letter `c`, several get `c1, c2`, and a
second universe gets `d` — which is why the grouping needs no explaining. Everything known about
them is said as a formula rather than handed over as a clause, and the facts are ordered: by arity,
so what is known about single things comes first; then by whether a fact names a witness or carries
a `∀`, since the concrete is what a reader anchors on; then by the order the problem first writes
the predicate in, so the block reads in the vocabulary of the question.

The check is the point. The assumptions have to come out true in the model and the conclusion
false — that is what makes it a counter-example rather than a picture of one, and it is checked
rather than asserted, with a verdict that lands the wrong way round printed under a ⚠️ instead of
smoothed over, since it would mean the model, the saturation or the evaluator is broken. Every
verdict carries the reason it came out that way: true of every element, vacuously true, witnessed by
a named element, or one of the three verdicts an implication can have. The reasons nest — an
implication says which of its sides decided it, and a named element says why *that* element
qualifies, with the body shown instantiated at it (`P(c3)`, not `P(x)`).

Underneath all of it is a finite structure — a domain, a table per predicate, tables for the
constants and the Skolem functions — found by plain DPLL over the ground instances at domain sizes
1, 2, 3 up to a cap, and never printed. It is the proof that the description is satisfiable rather
than merely plausible, and what the explanations point at when they name a witness.

Under `SET_OF_SUPPORT` the pass refuses, out loud: that search never tried the inferences among the
assumptions, so its running dry certifies nothing about satisfiability.

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
| `examples/dogs/` | the running example: dogs, owners, loyalty and betrayal — seven scripts over one set of assumptions, four of whose conclusions do not follow and end in a counter-model instead |
| `examples/question8/` | programmers, logic and bonuses |
| `examples/teacher/` | the lecturer's own question, run with nothing overridden |
| `examples/ceo/` | exactly one applicant succeeded, at least two applied ⇒ someone applied and failed |
| `examples/uniqueness/` | the same uniqueness question five ways: with equality axioms, without them, with the arguments written in matching order, with paramodulation, with superposition |
| `examples/equality/` | a burglary, in four formulations — the cost of doing equality by axioms versus by rule (343 steps against 9) |
| `examples/recursion/` | one question, two rankings: one runs away into nested Skolem terms, the other proves it in six steps |
| `examples/equivalence/` | two formulas, both directions, and the ≡ verdict — φ1 ⊨ φ2 fails, with a counter-model to show for it |

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
| `EXPLAIN_COUNTEREXAMPLE` | on by default, experimental; a saturated search reads a counter-model off its own clauses — see *The counter-model* |
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
