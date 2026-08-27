# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Maintaining this file

**Update this file in the same change as the code, not afterwards.** It is loaded at the start of
every session here, so it is the only description of the project that is guaranteed to be read —
and a stale line in it does more damage than no line at all, because it is trusted. This file has
already asserted things that were false (that unbound names become constants; that propositional
atoms are unsupported; that the witness-focus pass was unsound), and each one survived because the
code moved and the file didn't.

The sections that go stale fastest, in order: **Architecture** (any module added, moved or
renamed), **Things that will bite you** (any behaviour that becomes safe, or any new trap found),
the `config` settings list, and the accepted input language. A change to what the prover *answers*
always belongs here.

When you find a claim here that the code contradicts, fix the claim in that same change and say
so — do not leave it for later.

`AGENTS.md` is a **symlink to this file**, not a second copy. It was a copy once, and it fell six
commits behind without anyone noticing — the failure mode this whole section is about, made
inevitable by having two of something. Leave the symlink alone; write here.

## What this is

An **educational** first-order-logic resolution prover. Its purpose is not speed or
completeness — it is to *narrate* every step of the CNF conversion and resolution refutation in
Hebrew, the way it would be written out by hand in a logic course. Verbose printed output is
the product, not debug noise.

Stdlib only. No package metadata, tests, or lint config. `.idea/` is PyCharm.

**A git repository, one commit per change.** Work goes: plan → the author approves it → implement →
verify → *one* commit, whose subject names the change and whose body says why it was made and what
was measured. Documentation moves inside that same commit, never after it — which is what the
section above is asking for, now with something to enforce it. Nothing is committed before
approval. There is one remote, `origin`, pointing at the public repository
`github.com/matanhol/skolemization`; pushing stays a deliberate act, not something that follows a
commit automatically.

**Partition the work, then parallelise it. This is not an optimisation; it is how work is planned
here.**

**Plan by dependency first.** Before starting anything with more than one part, ask of every
subtask: does it need the output of an earlier one? Those form a cascade and run in order.
Everything else runs at the same time, one subagent per piece. Then ask the same question *inside*
each subtask, recursively — a stage of a cascade is usually partitionable itself, and a serial chain
of parallel fans is still parallel work.

**And the recursion is not yours alone to perform.** An agent may fork subagents of its own, and so
may they, all the way down: the piece handed to an agent is a task like any other, so the first
thing it does is ask the same question of *its* parts. Say so when handing the work over — an agent
that has not been told it may fan out will do its piece serially, and a fan-out one level deep is
the same bottleneck with more steps. Parallelise everything that can be parallelised.

Two examples of the shape:

- running many tests or measurements and aggregating the results into one table — every run is
  independent of the others, and the table is the reduce;
- translating many phrases that do not depend on each other — likewise, one fan-out and one merge.

**The reduce step is never delegated.** Results come back to be checked against each other and
against this repository's invariants — the examples still agree, the Hebrew transcripts are still
byte-for-byte what they were, the notebook still flattens, this file still describes what the code
does — before anything is committed.

What *not* to fan out: pieces that share state or must see each other's results, anything where one
piece's answer changes another's question, and single edits — a subagent costs more than the edit it
would make.

`skolemization_example.py` at the root is the **frozen original** — the single-file Colab export
the package was split out of. It still runs, but it is a reference copy: all changes go to
`skolemization/`, and the two will drift.

`skolemization.ipynb` is the *live* Colab export and does not drift, because it is **generated**
by `build_notebook.py` — see "The notebook" below. Never edit it by hand; regenerate it in the
same change as the code, exactly like this file. It is **not tracked** (`.gitignore`): it is
reproducible byte for byte from the package and the examples, so rebuild it, check it, and do not
commit it.

## Running

```bash
python3 -m examples.dogs.betrayer_not_dog        # from the repo root
python3 -m examples.dogs.betrayer_not_dog_per_formula   # the same, told formula by formula
python3 -m examples.uniqueness.with_eq_axioms
python3 -m examples.equivalence.equivalence      # both directions + the ≡ verdict
python3 -m examples.question8.pr_and_not_l
python3 -m examples.teacher.linked_to_every_s    # the lecturer's question, as given
python3 -m examples.ceo.some_t_is_not_s          # one applicant succeeded, two applied ⇒ one failed

python3 build_notebook.py                        # regenerate skolemization.ipynb
```

Nothing runs on import; every example is behind a `__main__` guard. Library use:

```python
from skolemization import prove, config

config.MAX_RESOLUTION_STEPS = 400          # settings are read at call time
prove(["all x (P(x) -> Q(x))", "exists x P(x)"], "exists x Q(x)")   # -> "PROVED"
```

`prove` returns `"PROVED"`, `"SATURATED_NO_CONTRADICTION"`, or `"UNKNOWN"` (hit
`MAX_RESOLUTION_STEPS`).

`Equivalence` (`equivalence.py`) is the other entry point — two formulas, both entailment
directions, then a verdict:

```python
from skolemization import Equivalence

result = Equivalence("all x P(x)", "not (exists x (not P(x)))").check()
result.forward, result.backward, result.equivalent      # "PROVED", "PROVED", True
```

`first_name`/`second_name` set the labels the narration prints (default `φ1`/`φ2`), and the
relation-property arguments pass through to `prove`. Note that `equivalent` being False means
equivalence was *not established*, not that the formulas differ — see the completeness caveat
below.

The examples are the de facto regression suite. After changing solver logic, re-run them and
check the statuses still match what each script's docstring claims — `betrayer_not_dog`,
`betrayer_not_dog_per_formula`, `owner_never_betrayed_variant`, all four `uniqueness` provables
(`with_eq_axioms` — which pins `STRATEGY` — plus `without_eq_axioms`, `matching_argument_order`,
`with_paramodulation`, `with_superposition`), the three provable `equality` examples
(`with_congruence`, `with_paramodulation`, `with_superposition`), `recursion/shallowest_first`,
`phi2_implies_phi1`, `pr_and_not_l`, `teacher/linked_to_every_s` and `ceo/some_t_is_not_s`
prove; the rest saturate,
except two that hit the step limit
on purpose — `equality/without_congruence`, and `recursion/runaway` with its limit lowered to 12 so
the runaway stays readable.

`betrayer_not_dog_per_formula` is the one example that is not about a conclusion: same
assumptions and same conclusion as `betrayer_not_dog`, run with `config.ONE_FORMULA_AT_A_TIME`
on, so the two scripts are also the check that the orders agree.

Careful with that last one: its Hebrew commentary claims the conclusion is unreachable without
the symmetry axiom, and that is **false**. `∀x∀y ((P(x) ∧ P(y)) → Eq(x,y))` is quantified over
both arguments, so instantiating `x := y, y := c` yields `Eq(y,c)` with no symmetry needed;
there is no counter-model. It demonstrates a limit of this solver, not of the logic.

## The notebook

`skolemization.ipynb` is the package as one Colab notebook: **cell 1 is the whole model**, then a
markdown cell of commentary and a code cell for each of the twenty-four examples, in the
order they appear under `examples/`. **One notebook per language**: the build reads
`config.LANGUAGE`, takes each example's commentary from its Hebrew docstring or its
`COMMENTARY_EN` constant accordingly, rewrites `LANGUAGE` inside the flattened `class config:` so
the prover in the notebook speaks the same language as the prose around it, and writes
`skolemization.ipynb` for Hebrew or `skolemization.<language>.ipynb` for anything else. A module
with no `COMMENTARY_EN` falls back to its docstring, so a half-translated package still builds. Each example cell restates its own assumptions, so the
cells can be run in any order. `build_notebook.py` writes it, stdlib `ast` and `json` only, and
nothing in it is hand-written — every formula, status and word of Hebrew is read out of
`skolemization/` and `examples/`.

How the flattening works, since a change to the package can break it:

- **Modules are ordered by their imports**, discovered from the AST — a new module lands in the
  notebook without being registered anywhere. `READING_ORDER` only decides between modules that
  are equally ready, so the cell reads settings → data model → parsing → the seven steps →
  search rather than alphabetically. An import cycle raises rather than emitting a broken cell.
- **Each module docstring becomes a `# ====` banner**, so the teaching text survives. Relative
  imports are dropped and the stdlib ones hoisted; everything else is copied verbatim, comments
  and vertical layout included. `from .x import y as z` is **refused**, because dropping that
  import leaves the body calling `z` in a file that only defines `y` — a `NameError` in the
  notebook and nowhere else. Rename the definition instead of aliasing the import.
- **An example that sets a flag has it set and put back around its cell.** `config.NAME = ...`
  assignments in an example's `__main__` block are rendered into its code cell, then restored to
  whatever `config.py` says the default is — a script can walk away with a flag set, a notebook
  namespace cannot, or every cell run afterwards inherits it. `betrayer_not_dog_per_formula` is
  the example that exercises this.
- **The module qualifiers stay**, because the code depends on them: `config.py` becomes
  `class config:`, and `narration` / `rewrite` / `aliases` each get a namespace class listing the
  attributes the package actually reaches for. This is not cosmetic — `preprocessing.py` calls
  `narration.rewrites(...)` while holding a local list named `rewrites`, so dropping the
  qualifier would silently pass the list to the call. `qualified_uses` in the generator finds
  that surface automatically.

The proof that flattening changed nothing is that the narration is **byte-for-byte identical**,
RTL marks included, between `skolemization.prove(...)` and the notebook cell's `prove(...)`.
Check that, not just the returned status, after touching the generator.

## Architecture

One module per teaching step, so a numbered step in the output maps to exactly one file:

```
prove()                     prover.py
  add_relation_axioms()     axioms.py               step 0, symmetry/transitivity/reflexivity
  preprocess()              preprocessing.py        announces and drives steps 1-7
    (parse, negate)         preprocessing.py        1
    remove_implications()   steps/implications.py   2
    to_nnf()                steps/nnf.py            3
    skolemize()             steps/skolemize.py      4
    remove_forall()         steps/forall.py         5
    to_cnf()                steps/cnf.py            6
    extract_clauses()       steps/clausify.py       7
  focus_kb_on_witness()     focus.py                the "try x := witness" heuristic
  run_resolution_search()   search.py               saturation until the empty clause
    paramodulants()         paramodulation.py       equality as a rule, not axioms
    explain_saturated_kb()  saturation.py           why a saturated KB is finished
```

`steps/` holds only transforms — they compute and print nothing; `preprocessing.py` does the
announcing. Steps 0 and 1 sit outside the folder because they are not transforms, which
`steps/__init__.py` explains so the numbering does not look like it has holes.

**`preprocess` drives those steps in either of two orders**, and they produce the same clause
list, in the same order, with the same Skolem names — only the narration differs. The default is
step-major (`_mapped_step`: each step swept across the whole KB). `config.ONE_FORMULA_AT_A_TIME`
switches to formula-major (`_walk_each_formula`: one formula carried through steps 2–7, then the
next). The equality holds because every transform is a function of one formula and the single
shared `SkolemNames` is consumed in formula order either way — so if you add a step, keep it that
way, and check the two orders still agree before checking anything else. Step 1 is whole-KB in
both.

**Transforms report their working without printing it.** Each recursive transform takes an
optional `rewrites` list and appends a `Rewrite(rule, before, after)` per rule it fires
(`rewrite.py`), the same pattern `skolemize(..., explanations=[])` already used. Records describe
the *local* rewrite with un-recursed children — what the rule did at that node, which is what a
reader would write on paper — not the fully-processed subtree. `to_nnf` carries negation in a
`negated` flag rather than rewriting `Not` nodes, so it records at the point the flag is
*consumed*: a negated `And` becoming an `Or` is the De Morgan step. Rule names get their Hebrew
in `narration.RULE_NAMES`.

Each step then closes by showing the whole KB (`display.show_formulas`, the formula-side
counterpart of `show_kb`), and says nothing at all about formulas it left unchanged.

Supporting modules: `formulas.py` (the data model), `display.py`, `substitution.py`,
`unification.py`, `clauses.py` (variable renaming, canonical keys, tautologies),
`resolution.py` (one resolution step), `paramodulation.py` and `ordering.py` (equality as a
rule), `subsumption.py` (three sweeps — see below), `saturation.py`, `config.py`, `narration.py`,
`output.py`, and the `parsing/` subpackage (`aliases.py` → `tokenizer.py` → `parser.py`).

The core does not print. It calls an *event* in `narration.py` — one function per thing that
happened, not per line of output — and that module owns the wording and layout:

```python
narration.resolvent_added(resolvent)     # search.py says what happened
                                         # narration.py decides how it reads
```

So `narration.py` is where you go to reword commentary, add a step, or translate. Presentation
work belongs there too, not in the caller: `narration.resolution_step` computes the instantiated
literals and picks which bindings are worth showing.

Representation: frozen dataclasses. `Term` (with `is_var`), `Atom`, and the connective nodes
`Not/And/Or/Implies/ForAll/Exists` for formulas; after clausification everything is
`list[list[Literal]]` — a KB is a list of clauses, a clause is a list of `Literal`.

Examples are one package per problem: `assumptions.py` holds the shared knowledge base and each
conclusion gets its own script importing it. **Every example module carries its commentary twice** —
the Hebrew as its docstring, the English as a `COMMENTARY_EN` constant right after it — and only
`build_notebook.py` reads either, so a translation cannot affect what the prover does. `examples/teacher/` is the lecturer's own question, run with nothing overridden; the same
question appears again in `examples/recursion/`, where the settings are changed to make the search
run away. `examples/dogs/` has two assumption sets —
`BASE`, and `OWNERSHIP_VARIANT` for the one case where rewording the assumptions changes the
answer.

### Things that will bite you

**Words and layout are separate** (`phrases/`, `narration.py`). `narration.py` decides what a
reader sees — the banners, the indentation, which bindings are worth printing — and holds no words
at all; `phrases/hebrew.py` holds every sentence, keyed by the event that says it, reached through
`phrase(key, **values)` and `phrase_table(name)`. Adding a language is a second catalogue, not a
second narrator, and `phrases/lookup.py` checks at import that the catalogues offer exactly the same
keys, so a language cannot quietly fall behind. `config.LANGUAGE` chooses; an unrecognised value
raises and names the ones that exist.

**All Hebrew lives in `phrases/hebrew.py`**, and everything printed goes through `say()`
(`output.py`), never bare `print`. A Hebrew string anywhere else in `skolemization/` is a bug —
`grep -rlP '[\x{0590}-\x{05FF}]' skolemization/` should name only `phrases/hebrew.py` (and
`output.py`, whose docstring illustrates the RTL rule).

**No two modules may define the same top-level name.** Flattening puts them all in one namespace,
so the second definition silently replaces the first and a call lands in the wrong function — in the
notebook only. `build_notebook.refuse_duplicate_names` raises instead, and it exists because
`sorts.py` and `signature.py` both defined `_walk_formula` with different signatures. A name may
repeat only when the modules holding it are reached through a qualifier, since each of those gets a
namespace class of its own (`hebrew.PHRASES` and `english.PHRASES` do not collide).

**Logic never goes in an `__init__.py`.** `build_notebook.py` treats those files as re-exports and
skips their bodies, so a function defined in one exists in the package and vanishes from the
notebook — which is exactly how `phrases/lookup.py` came to be a module of its own.

Direction is handled at two levels, and both are needed:

1. `say` forces RTL base direction on any line containing a Hebrew character — including lines
   mixing Hebrew with Latin identifiers, which is most of them
   (`מוסיפים את ה-resolvent ל-KB:`). Lines with no Hebrew pass through untouched, LTR.
2. **`ltr()` wraps any formula, clause or term before it goes into a Hebrew line.** Without it
   the expression scrambles, because `∀ ∃ ¬ ∧ ∨ →` and the parentheses are bidi class ON
   (Other Neutral), *not* `L` — only the Latin letters hold their direction. The neutrals
   inherit the RTL paragraph direction and move to the wrong side, and `(`, `)` and `∃` are
   mirrored characters, so they flip glyphs as well. An LTR isolate covers the whole
   expression, symbols and brackets included. A lone symbol ending a Hebrew sentence
   (`הורדת כמתי ∀`) is the exception — it should inherit RTL, so leave it unmarked. So is a
   line that is *nothing but* a formula, the counter-model's fact lines among them: with no
   strong-RTL character on it `say` leaves it LTR already, and an isolate would only add
   invisible bytes to a line that was never going to move.

**The direction follows the language, and is not a separate setting.** Each catalogue declares its
`DIRECTION`, and `config.RTL_OUTPUT` is `"auto"` by default: Hebrew gets the marks, English would
only be littered with invisible characters. `True`/`False` force it. There is no language-to-
direction table in the standard library (CLDR has one, but that means ICU and this package has no
dependencies), which is why the language states its own; `output.line_is_rtl` asks
`unicodedata.bidirectional` for the strong classes `R`/`AL` rather than matching a Hebrew block, so
Arabic, Syriac, Thaana, N'Ko and Adlam are laid out rather than scrambled.

`config.RTL_OUTPUT = False` makes both a no-op and `say` a byte-for-byte `print`;
`config.NARRATE = False` silences it entirely, so `prove` can be used as a library call. That
byte-comparison no longer matches `skolemization_example.py` on formula lines — the frozen
original brackets every binary node and prints one line per formula, and this one does neither
(below).

**Brackets say what binds to what, and nothing is left to precedence** (`display.py`). The printer
recomputes them from the tree every time, so parentheses written into an assumption to satisfy the
parser do not come back out, ones the author left implicit are put in, and ones that stop meaning
anything vanish at the step that makes them meaningless — dropping `∀x` in step 5 takes its scope
bracket with it. Four rules, in `formula_pieces` and its neighbours:

1. a quantifier brackets its **whole scope**, even a scope of one atom: `∃y (P(y, x))`;
2. a quantifier standing as an operand is closed off as well, so its reach cannot be misread:
   `all x Q(x) and exists y P(y,x)` → `∀x (Q(x) ∧ (∃y (P(y, x))))`;
3. where the connective **changes**, both sides are bracketed unless a side is a single predicate —
   `(P(x) ∨ Q(x)) ∨ (R(z) ∧ S(y))`, whatever precedence would have settled on its own. Only a run
   of one connective goes without (`P(x) ∨ Q(x) ∨ R(x)`, which is why clause lines stay flat), and
   `→` is never a run, because it does not associate;
4. `¬` brackets a connective and nothing else: `¬(A ∧ B)`, but `¬P(x)`.

The test is that **re-parsing the printed text gives the same formula**, and it is run over every
formula the examples print (572 of them; the rest hold Skolem constants, which are not input
language) and a generated corpus of 4000. "Same" means up to the associativity of `∧`/`∨`, since a
run prints flat: `A ∧ (B ∧ C)` and `(A ∧ B) ∧ C` print alike and re-parse to the left-nested one.

**A formula can be a block rather than a line** (`config.TALL_BRACKETS`, **off** by default).
`P(x)` and `g1(x)` are an *application*, so the ordinary one-row `( )` belongs to them and no
grouping bracket may be that small: grouping brackets are stacked out of `⎛ ⎜ ⎝` / `⎞ ⎟ ⎠`, three
rows for the innermost level and two more for every level outwards, formula on the middle row.

```
   ⎛                     ⎞
   ⎜⎛            ⎞       ⎟
∀x ⎜⎜Pr(x) ∧ L(x)⎟ → C(x)⎟
   ⎜⎝            ⎠       ⎟
   ⎝                     ⎠
```

So `formula_str` returns text that may contain newlines, and **nothing may interpolate it into a
sentence**. Callers go through `output.say_block(label, text, indent)`, which keeps a one-row
formula on the label's line and otherwise prints the label alone and indents the rows under it —
each row in its own `ltr()` isolate, because an isolate must not span a newline. The rule holds
whatever the flag says, because `display` reads it where it renders, not at import: a caller that
formats a formula into a line of its own looks fine until someone turns the flag on. Left off, which
is the default, those same brackets print as ordinary `( )` on one line — which is what the
round-trip test needs and what makes the output paste back in as input.

**How much the steps explain** is three more flags: `SHOW_KB_AFTER_EACH_STEP`, `SHOW_SUBSTEPS`
and `SHOW_UNCHANGED_FORMULAS` (that last one off — a before/after pair of identical text buries
the formulas that did change). Setting the first two False and the third True gives the terser
narration the package shipped with, which is how a change to the *narration* is proved not to be
a change to the *transforms*. The similarly named `SHOW_FULL_KB_EACH_STEP` is a different flag
for a different phase: it dumps the KB after each *resolution* step (`search.py`), not after each
preprocessing step.

**`ONE_FORMULA_AT_A_TIME`** changes the *order* the steps are told in rather than how much they
say — see Architecture above. Two consequences for the narration: `SHOW_KB_AFTER_EACH_STEP` is
ignored (there is no whole-KB moment to close on while one formula is mid-conversion; each
formula ends with its own clauses instead, and `clause_kb` still prints the combined KB at the
end), and a step that changes nothing prints `narration.formula_unchanged()` rather than printing
nothing, because in a chain a silent step reads as a step that never ran.

**The narration speaks whichever language `config.LANGUAGE` names** — `"he"` or `"en"`, and an
unrecognised value raises. The words live in `phrases/`, the layout in `narration.py`, and the
direction follows the language (see above). Measured when English was added: every example gives the
same status and the same step count in both, and the Hebrew output is byte-for-byte what it was.

**Import config as a module**, not by value: `from . import config` then `config.STRATEGY`.
`from .config import STRATEGY` freezes the value at import time and breaks the documented
ability to override a setting before calling `prove`.

**`atom_str` and `visible_variable_name` live in `formulas.py`, not `display.py`.**
`Literal.__str__` and `Term.__str__` call them, so moving them into `display.py` creates a
circular import.

**There are no constants in the input language.** Every bare name must be bound by an enclosing
quantifier; `Parser.parse_term` raises `SyntaxError` on anything else, naming the variable, the
source text, and what *is* in scope. Constants exist only as Skolem witnesses invented in step 4.
This is deliberate: an unbound name is always a typo or a quantifier that did not reach as far
as it looked, and the old behaviour — silently making it a constant — meant the prover answered
a different question without complaint. A ground fact like `Man(socrates)` cannot be expressed;
if that is ever needed, add an explicit declared-constants argument rather than restoring the
silent fallback. Function applications (`f(x)`) are unaffected — only the argument-less case is
rejected.

**Accepted spellings live in `parsing/aliases.py` and nowhere else.** Both the tokenizer's regex
and its lookup are derived from those tables, so adding a spelling is a one-line edit there.
Keywords are case-insensitive and multi-word forms tolerate any spacing (`FoR   aLL` → `forall`),
because phrases are matched after tokenizing, not against raw text. **`!` is negation**, the
programming-language reading — it used to mean `forall`, which was a bug. Predicate and variable
names keep their case (`P` and `p` stay distinct); only keywords are folded, so a predicate named
`All` would be swallowed. Every symbol the narration prints (`∀ ∃ ¬ ∧ ∨ →`) parses as input too,
so output can be pasted back in.

**A quantifier carries across a variable list.** `all x, y, z P(x,y,z)` means
`all x, all y, all z P(x,y,z)`; separators are optional (`all x y z` works), and a different
quantifier keyword starts its own list (`there exist x, y, all z B(x,y,z)`). The disambiguation
is exact, not heuristic: after a quantifier's variable the body can only begin with `not`,
another quantifier, `(`, or a predicate *applied* to arguments, so a bare name that is neither a
keyword nor followed by `(` can only be another variable (`Parser.starts_variable`).

**Propositional logic works, through zero-argument predicates.** `P()` parses, and
`prove(["P()", "P() -> Q()"], "Q()")` is `PROVED`, the invalid converse saturates, and
`prove([], "P() or not P()")` is `PROVED`. Predicates must still be *applied* — bare `P` is a
syntax error — so the empty parentheses are required.

**Other parsing rules** (`parsing/parser.py`). An optional `,` or `:` may follow the quantified
variable.
Precedence is implication (loosest) → or → and → unary, and a quantifier body is parsed with
`parse_implication`, so it extends as far right as possible — parenthesize when that is not what
you mean. `(all x P(x)) and Q(x)` now fails loudly on that trailing `x`, which is the point.

**Equality is not built in, and there are two ways to supply it.**

*By axioms.* Model it as an ordinary predicate (`Eq` in the older examples) and declare its
properties through `prove`'s `symmetric_relations` / `transitive_relations` / `reflexive_relations`
arguments, which `axioms.py` turns into extra assumption *text*. Without those axioms the prover
cannot connect `Eq(x,y)` and `Eq(y,x)`; `examples/uniqueness/without_eq_axioms.py` exists to
demonstrate that failure. The clauses those axioms produce are the ones the witness-focus pass
leaves alone — see the focus paragraph below. **Note what those three axioms do *not* give you:**
they make `Eq` an equivalence relation, not equality. Equality also needs congruence — `x = y ∧
P(x) → P(y)` for every predicate, `x = y → f(x) = f(y)` for every function, Skolem functions
included. Measured: `P(c) ∧ ∀y (c = y)` does **not** yield `∀y P(y)` under the three axioms; it
saturates.

*By rule.* `config.EQUALITY_RULE` — see the paramodulation paragraph below — replaces the whole
axiom family with one inference rule, and is the honest answer to that gap.

**`=` is input syntax** (`parsing/aliases.py`, `Parser.parse_equality`). `x = y`, `x != y` and
`x ≠ y` parse into an atom over the reserved predicate `"="`, which no user name can collide with
because names must match `NAME_RE`. **`x != y`, `x ≠ y` and `not (x = y)` are one and the same
tree** — `Not(Atom("=", …))` for all three — so nothing downstream can tell them apart; `≠` is a
printing convention and `config.NEGATED_EQUALITY` (`"≠"` by default, `"not"` for `¬(c2 = c3)`)
chooses it. Everything that prints one goes through `formulas.negated_equality_str`, the narration's
own examples included, so a transcript never mixes the two. Measured over the five examples that use
`=`, with the witness focus on and off: identical statuses, identical step counts, and the identical
sequence of inferences. It is pure sugar: unification, resolution and clausification
treat it as an ordinary binary predicate, and what makes it *equality* is the axioms or the rule,
never the parser. `formulas.atom_str` prints it infix (`x = y`, and `x ≠ y` for the negated
literal). One interaction to remember: `Parser.starts_variable` had to learn about `=`, or
`all y x = y` would read `x` as a third quantified variable.

**Skolem names say which universe a witness belongs to** (`steps/skolemize.py`, `sorts.py`).
The sorts are inferred before step 4, and a witness takes the letter of its universe: **one witness
in a universe gets the bare letter** (`c`), **several get numbers** (`c1, c2, c3`), a second
universe gets the next free letter (`d`), and functions follow the same rule in the universe of what
they *return* (`g`, or `g1, g2`). So `F(x, y)` relating two kinds of thing produces `c` and `d`
rather than `c` and `c2`, and a reader can see at a glance that they are not comparable.

"One or several" cannot be decided while inventing the first name, so `SkolemNames.plan` counts the
existentials per universe first, over the NNF formulas. **Both step orders plan from the whole KB**:
`ONE_FORMULA_AT_A_TIME` computes every formula's NNF up front, before walking the first one, or the
two orders would name witnesses differently — which is the one thing that ordering is not allowed to
change.

The letter families are still chosen against the problem's own vocabulary. A letter is available
only if no input name matches `^<letter>\d*$`, so writing `g` rules out `g1`, and writing `g1`
rules out `g2` — the whole family is contaminated either way. Constants then walk `c → d → e`,
functions `g → h → i`, each universe taking the next letter still free. This exists because the collision was silent and produced *false positives*:
`all x exists y R(x,y)` plus `all x (R(x, g1(x)) -> Q(x))` used to prove `exists x Q(x)` purely
because the user's `g1` and the invented `g1` were the same string.

Consequently **the witness name is never hardcoded**. `preprocess` returns a `Preprocessed`
record (the clauses, the chosen `SkolemNames`, the parsed assumptions and conclusion, which clauses
came from the generated axioms and which from the conclusion, and the order the predicates are
written in), `prove`
reads `.witness` and `.witnesses` off it, and `focus.py` / `narration.py` take them as parameters.
`config.FOCUS_ON_WITNESS` (formerly `FOCUS_ON_C`) gates that pass — and it only runs when
skolemization invented exactly one witness; `config.FALLBACK_TO_GENERAL` re-runs the search on the
original KB when it fails.

**Every symbol must be used one way** (`signature.py`). Before anything is printed, `preprocess`
walks the parsed formulas and refuses a name used with two arities, or as two kinds of thing
(predicate/function/variable). Nothing downstream would report it: atoms of different arity
simply never unify, so the search saturates and looks like a reasoned negative answer. The error
quotes both uses and the formulas they came from.

**Two-layer variable naming** (`clauses.py`). `standardize_clause` renames variables apart to
`__v<N>_<orig>` before every resolution attempt; `clean_clause_variables` renames survivors back
to `x, y, z, u, v, w, …` for storage; `Term.__str__` runs `visible_variable_name` so internal
names are never printed. Never surface a raw `__v…` name in output, and never compare clauses by
string — use `canonical_clause`, the alpha-invariant key the search uses for its `ever_seen`
dedup set.

**Search loop** (`search.py`): naive saturation each step over three sources of new clauses —
resolution across clause pairs, resolution of a clause with a renamed copy of itself
(`config.ALLOW_SELF_RESOLUTION`), and factoring (`config.USE_FACTORING`). Results that are
tautologies, already in `ever_seen`, or subsumed by one of their own parents (`_already_implied`)
are discarded; `config.STRATEGY` picks the next step. After each step only that step's parents are
checked for subsumption by the result (`remove_redundant_parents`), not the whole KB. Empty
clause ⇒ `PROVED`.

**Four strategies**, as a table of key functions (`search.STRATEGY_KEYS`); an unrecognised name
raises rather than quietly behaving like `"shortest"`. The default
`"shallowest_general_first"` is `"shortest_general_first"` with one key in front of it,
`term_depth(result)` — how deeply the result's deepest term nests. Depth has to lead because
nothing else stops a runaway: resolving `¬P(x) ∨ S(h(x))` against `P(g(h(c)))` gives
`S(h(g(h(c))))`, which is short, general, assignment-free and therefore attractive to every
other key — and it is the parent of a deeper one, forever. Measured in `examples/recursion`:
without the depth key the search is carrying terms nested a hundred deep by step 150 and never
finishes, with it the proof takes 6 steps and nothing nests past 1. It is not free — the equality
axioms build deep terms on purpose, so `uniqueness/with_eq_axioms` does not finish in 150 steps
under the default and pins `"shortest_general_first"` itself, which proves it in 7.

`"shortest_general_first"` ranks by
`(len(result), is_paramodulation, needs_assignment, term_weight(result), parent_size)` — among
equally short resolvents it prefers a resolution or a factor over a rewrite, and then the pair that
matches as it stands over one that has to bind variables, so `P(c) ∨ B(x,y)` resolves against
`¬P(c)` rather than `¬B(c, g(c))` and the derived clause stays general instead of being about one
object. The rule key is there because paramodulation fires at every non-variable subterm in both
directions and is by far the most prolific of the three: on a tie the cheaper rule is the one to
spend the step on, and it is the one a reader expects — the CEO example now derives `c2 = c` and
`c3 = c` before it starts rewriting with them. Measured when it was added: no example changes
status or step count. The third key is there for equality: an
equation can be used either way round, so `c = g(c)` turns `P(g(c))` into `P(c)` *or* into
`P(g(g(c)))`, both one literal long — `ordering.weight` picks the smaller term, the same
direction `"superposition"` enforces outright. Measured when it was added: no example changes
status or step count; only which of several tied candidates wins. "Needs assignment" is
`resolution.meaningful_substitutions` being non-empty — the same test the narration uses, so a
variable renamed to a variable (bookkeeping from standardizing apart) does not count. `"shortest"`
drops that middle key; `"random"` picks any candidate. Measured when the default changed: no
example changes status, and `with_eq_axioms` and `matching_argument_order` each prove a step
sooner. Putting generality *before* length instead loses `with_eq_axioms` entirely (`PROVED` →
`UNKNOWN`), which is why it is a tie-break.

**The ranking can explain itself** (`config.EXPLAIN_CHOICE`, **off** by default). With it on, after
each step the
narration prints the two next-best *different* candidates and the first key on which the winner
pulled ahead — or says the candidates were level and the order arbitrary. The ranking is the one
part of the search a reader cannot reconstruct from the result, so a step that is not the step they
would have taken looks arbitrary until this names the key that overruled it — which is worth a block
per step only while that is the question being asked, hence the default. The key *names* live in
`search.STRATEGY_KEY_NAMES`, beside the functions, so the printed reason cannot drift from the key
that ran; `narration.RANKING_KEY_NAMES` holds their Hebrew.

Do not reach for a lookahead key to make the search "think ahead": measured, ranking a candidate by
whether □ is one step away afterwards takes the CEO example from 7 steps to **23**, because a large
share of candidates score as "could close next" and the key stops discriminating.

**Subsumption is asked in both directions, and in four places** (`subsumption.py` and
`search._already_implied`). Forward, before a candidate is recorded: `_offer` drops a result one of
its own *parents* already subsumes, which is the mirror image of `remove_redundant_parents` asking,
after the step, whether the result made a parent redundant. `remove_all_redundant` checks
everything against everything in the saturation epilogue, *with* assignments — strictly the
strongest of them: on `phi1_implies_phi2` it removes `¬Q(c,y)` under `¬Q(x,y)`, which the unit
sweep below correctly refuses.

Forward subsumption stops a runaway that is not about depth at all. Measured: the uniqueness
question with `FOCUS_ON_WITNESS` off went `UNKNOWN` at 150 steps and 312 seconds → `PROVED` in 6
(the variable-source restriction below rescues that one too, independently),
`recursion/shallowest_first` 7 steps → 6, `equality/with_congruence` 359 steps → 343, and no
example changes status. Only the
parents are checked, not the whole KB: measured against the whole-KB alternative on both problems,
identical statuses and identical step counts, while the parents account for the large majority of
the catches (46 against 25, and 15 against 4). A newcomer subsumed by some *other* clause survives
and is cleared by the epilogue sweep — if that ever bites, `remove_all_redundant` is already
written and can be run on a schedule.

**`sweep_with_units`** (`config.FULL_SUBSUMPTION_EACH_STEP`, **off** by default) is the only one
that *shortens* clauses. It runs before the first step and after every step, over
a queue holding the KB's one-literal clauses. Each unit in turn does two things to every other
clause, and neither may need an assignment:

```
{P(x)} with {¬P(x) ∨ Q(x)}   →  the clause is replaced by {Q(x)}
{P(x)} with {P(x) ∨ Q(x)}    →  the clause is deleted; the unit says it already
{P(x)} with {¬P(x)}          →  nothing is left: □, and the search returns PROVED
{P(x)} with {¬P(c) ∨ Q(c)}   →  untouched, it would have to decide x is c
```

A remainder of one literal joins the back of the queue, and lands in `ever_seen` so the main loop
does not re-derive it. **None of this costs a resolution step** — the sweep is not counted against
`MAX_RESOLUTION_STEPS` — but it can finish the proof, which is why it returns `(kb, found_empty)`
and `search.py` checks the flag.

Two guards make replacing a clause by its remainder safe, and `resolve_with_unit` enforces both:
the unifier must bind nothing meaningful, **and** the remainder must come through unchanged
(`canonical_clause` before vs after). Without the second, `{Eq(x,x)}` "simplifies"
`¬Eq(x,y) ∨ Eq(y,x)` to `Eq(x,x)` by merging the axiom's two variables — the symmetry axiom
silently becomes reflexivity again, and `with_eq_axioms` stops proving. With both guards the
remainder is a literal subset of the clause it replaces, so nothing is lost. Measured with the
sweep on: no example changes status, and four of them (`owner_variant`, `with_eq_axioms`,
`matching_argument_order`, `question8`) reach □ inside the sweep itself.

"Needs no assignment" is one definition shared by three places — this sweep, the
`shortest_general_first` strategy, and the bindings the narration bothers to print: it is
`resolution.meaningful_substitutions` coming back empty, so a variable renamed to a variable
(bookkeeping from standardizing apart) never counts as an assignment. In `clause_subsumes` the
requirement is checked where the match *succeeds*, so a pairing needing an assignment cannot mask a
different pairing of the same literals that needs none.

**Set of support** (`config.SET_OF_SUPPORT`, **off** by default) restricts *which pairs* may be
tried at all: the clauses of the negated conclusion seed a supported set, every inference must
touch it, and every result joins it (`search._worth_trying`, one predicate covering resolution,
factoring and paramodulation alike). The argument is not a heuristic — the assumptions alone are
satisfiable, so no refutation lives among them, and every step that avoids the conclusion is
provably wasted. `preprocess` supplies the seed as `Preprocessed.conclusion_clauses`, and
`run_resolution_search` turns those *positions* into the identity of the **unsupported** clauses
right after it copies the KB, so nothing has to be maintained: derived clauses are new objects and
therefore supported, and deletions cannot invalidate the set.

Measured with it on: no example changes status except the one noted below, and the search gets much
shorter — `equality/with_congruence` 343 → 52 steps, `equality/with_paramodulation` 16 → 10,
`owner_never_betrayed_variant` 6 → 3, and the saturating dogs examples now run dry in 0–2 steps
instead of 3–5, which is itself the clearest possible statement that the conclusion has nothing to
attack.

Two caveats, both narrated rather than hidden:

- **It is complete only while the unsupported clauses are satisfiable.** Assumptions that
  contradict *each other* make the conclusion follow trivially, and this restriction would never
  look there. A supported search that runs dry says so (`narration.set_of_support_caveat`).
- **It does not compose with `"superposition"`.** Both restrict which inferences exist, each is
  complete on its own, and their union is not: measured, `equality/with_superposition` goes
  `PROVED` (9 steps) → `SATURATED` with both on. The header warns when it sees the combination and
  points at `"paramodulation"`.

**A saturated search explains itself** (`saturation.py`, `config.EXPLAIN_SATURATION`). Pure
epilogue — it runs after the answer is decided and cannot change it. First a full subsumption
sweep (`subsumption.remove_all_redundant`), then every step still available, one line each: no
complementary literals, complementary literals that will not unify, a tautological resolvent, a
clause already known, or a clause its own parents already subsume. That last verdict exists because
the search refuses such a candidate *without* recording it in `ever_seen` — so `_verdict` has to
run the same test `search._already_implied` does, or the account would meet the clause again and
report it as new. It **replays the search's own rules under the same flags** — self-pairs only
when `ALLOW_SELF_RESOLUTION`, factoring only when `USE_FACTORING` — or it would be explaining a
different search; if it ever finds a genuinely new clause it says so rather than hiding it, since
that would mean a bug. It lives inside `run_resolution_search` (only there is `ever_seen` in
scope, which is what distinguishes "already in the KB" from "derived earlier and dropped").

**A saturated KB is a counter-model, and can be described as one**
(`counterexample.py`, `config.EXPLAIN_COUNTEREXAMPLE`, **on**, experimental). Refutation
completeness has a second half: a clause set saturated under a complete calculus with no □ in it
*is* satisfiable. The surviving clauses are not an obstacle to reading that model — they are the
description of it, and the pass says so in the vocabulary of the problem.

**The universes are inferred, not assumed.** A union-find over argument positions — `(P, 1)`,
`(g, result)` — merged whenever the same variable or the same term is written in two of them. So
`D(x)` with `F(x, y)` puts `D·1` and `F·1` in one universe, `F(x, y)` keeps its two places apart
unless something links them, and a Skolem term written into `F`'s second place belongs *there*, not
with the constant it was built from. Inference runs over the clauses **as they entered**, since a
link made by a clause later subsumed is still a fact about the vocabulary.

**The universes are never explained, only used.** Nothing prints a list of argument places: the
*names* carry the sorts, because skolemization already chose them that way — `c` against `d`. The
witnesses get one line per universe, and what is known about them follows under a bare heading of
the names the facts are about (`c1, c2:` — there is no word to wrap around a list of names, and none
is invented), and a fact mentioning several witnesses is stated once under all of them rather than
repeated under each.

**What gets said is what the question does not already say.** Two kinds of thing, because those are
the two a reader cannot get from the assumptions as they stand: a predicate that **never** or
**always** holds (a one-literal clause over distinct variables), and everything known about each
**witness**, gathered onto its own line instead of scattered across a clause list — and a witness is
found however deeply it is buried, so a clause mentioning only `g(c)` is a fact about `c`. A
surviving clause that is neither — no witness in it, and nothing universal to say — is not reported
at all: it is a *general* fact, so it is a consequence of assumptions the reader is already holding,
and it reads as news only because it is written as a clause. In the dogs example the two such
clauses were the same fact twice — a dog does not betray its owner — printed differently only
because the two clauses store their literals in opposite orders, which is as clear a statement as
there is of what a list of derived clauses is: the search's history, not a description of the model.
Saying the question back to the reader is what made the first version unreadable, and this is that
argument carried as far as it goes.

**Every fact is said as a formula, in every language** (`display.clause_as_formula`). A clause is a
disjunction, but that is not how anyone states the fact it stands for: the negative literals are the
conditions and the positive ones the consequences, so the reading is an implication where there are
both, a denial where there are only conditions, and a plain disjunction where there are only
consequences. One literal is `¬D(c1)`, all-negative is `∀x ¬(D(x) ∧ B(x, g(x)))`, mixed is
`∀x (D(x) → ¬B(x, g(x)))`, all-positive is `∀x (P(x) ∨ Q(x))`. The **never** and **always** sections
are formulas under a plain header the same way (`∀x ¬D(x)`), not a comma-list of predicate names
folded into a sentence. The body is a real formula tree handed to the ordinary printer, so the four
bracket rules above hold inside it and equality still comes out `x ≠ y`; only the `∀` prefix is
written **flat** — `∀x ∀y `, not the `∀x (∀y (…))` `formula_str` would give — because the block is a
list of terse facts, and burying each one a bracket deeper than the last is what a reader cannot
follow.

**The facts are ordered, not left in clause order** (`counterexample._line_order`), and every list
in the block by the same three keys: **arity**, so one-argument predicates come first; **specificity**,
so a fact about named witnesses comes before one carrying a `∀`; and then **the order the predicate
is first written in the problem**, which is the order the reader is already holding. A clause of
several literals is led by its smallest such key, and a predicate the problem never wrote — `=`, or
anything the search invented — sorts after every one it did. That third key costs nothing:
`signature_of` already walks the assumptions left to right and `Signature.uses` is insertion-ordered,
so `Signature.predicates` only reads it back out and `Preprocessed.predicate_order` carries it to
the pass; recovering it anywhere else would mean walking every formula a second time.

**A finite model is built and never printed.** `finite_model` searches domain sizes with DPLL over
the ground instances; it is the proof that the description is satisfiable rather than merely
plausible, and it is what the explanations point at when they name a witness. It prefers separate
witnesses and `f(a) ≠ a` over a smaller domain, because a function sending an element to itself
reads as "the owner of x is x".

**Every assumption is explained, and a `∀` never by example.** `why` returns a structured reason:
vacuous (naming the condition nothing satisfies — checked over *all* the ∀-bound variables, not just
the outermost), true of every element, witnessed by a named element for an `∃`, or an implication
whose left-hand side fails. The assumptions must come out true and the conclusion false; a wrong
verdict is printed with a ⚠️ rather than smoothed over, since it would mean the model, the
saturation or the evaluator is broken.

Two refusals, said out loud: a **focused** KB (its substitution is a guess) and a run under
**`SET_OF_SUPPORT`** (which never tried the inferences among the assumptions, so its running dry
certifies nothing).

**Every saturating search explains itself, the focused pass included** — that is where the reader
most needs it, since the focused KB is a guess. What differs is the closing sentence, and it must:
a general KB with nothing left says something about the problem, while a focused KB with nothing
left says only that `x := c` did not pay off. `run_resolution_search(..., focused=True)` (passed by
`prove` for the focused attempt) carries that through to `narration.account_conclusion`. Never let
the general wording run over a focused KB.

**Paramodulation is how equality is really done** (`paramodulation.py`, `ordering.py`,
`config.EQUALITY_RULE`, `"paramodulation"` by default; `"none"` turns it off and hands equality
back to the axioms). One rule replaces the entire congruence axiom family:

```
C1: s = t ∨ rest1            s not a variable either
C2: … u …                    u a non-variable subterm, σ = mgu(s, u)
────────────────────────────────────────────────────────────
    (C2 with that u replaced by t  ∨  rest1) σ
```

**An equation is never used from a variable side** (`paramodulation.equations`). `c = y` read as
`y ⟶ c` matches the first subterm it meets, binds `y` to it, and puts `c` back — under that same
binding the equation itself has become `c = c`, so what comes out is the clause that was rewritten
plus the leftovers: weaker than a clause already in the KB, by construction. The standard calculus
excludes it too (a variable is never the maximal side), and the ordering *cannot*: `greater` leaves
`c` and `y` incomparable, so even `"superposition"` used to let it through. Measured: it is what
made the uniqueness question run away with the focus pass off.

Because it rewrites *inside terms*, below the predicates, it covers every predicate and function
at once — including the Skolem functions invented in step 4, which no axiom generator could know
about. Resolution + factoring + this rule + the axiom `x = x` is refutation-complete for
first-order logic with equality; `prover._add_reflexivity` adds that one axiom itself when the
rule is on and the problem mentions `=`, and narrates why.

A paramodulation step has three things a resolution step does not, and the rule hands them to the
narration in a `Replacement` record (`paramodulation.py`) carried on `Inference.replacement`:
**which way round the equation was used** (`source ⟶ target` — `s = t` can rewrite either side),
**which subterm matched**, and the bindings **split by which clause each variable came from**
(`narration.paramodulation_bindings`; the clauses are standardized apart, so the split is exact).
Without those, `y := g1(c)` under an equation printed whole tells the reader nothing.

`"superposition"` is the same rule with the ordering in `ordering.py` (KBO, all weights 1)
forbidding a rewrite that goes uphill — the restriction real provers are built on. Measured on the
burglary in `examples/equality/`: `"paramodulation"` proves it in 16 steps, 12 of them rewrites;
`"superposition"` in 9 steps, 5 rewrites. On the smaller question 3א the two are level (5 steps,
one rewrite each) — the ordering pays where there are equations to choose between. **It is a simplified ordered variant**, not the full calculus with literal
selection, so treat `"paramodulation"` as the complete one and `"superposition"` as the fast one.
`examples/uniqueness/with_paramodulation.py` and `with_superposition.py` are the same question
solved with no equality axioms at all. An unrecognised value raises, like `STRATEGY`, and
`saturation.py` replays the rule so a saturated account is about the calculus that actually ran.

**Trivial equalities are settled where clauses are built** (`clauses.py`). `t = t` is true and
`t ≠ t` is false, both on sight, so `clause_is_tautology` now also rejects a clause holding a
positive `t = t` (it is an instance of reflexivity and says nothing), and `drop_false_equalities`
strips every `t ≠ t` — a disjunct that cannot hold cannot help. Every rule's output goes through
`search._offer`, which does the dropping once for all three rules, keys `ever_seen` on the
simplified clause, and keeps the pre-drop form so `narration.step_result` can show the reader the
step's own output *before* explaining why it shrank. When the drop empties the clause the step has
reached □ by itself, which is what shortened the equality proofs from 7 steps to 5. One consequence
for the wording: the reflexivity axiom is no longer what closes a literal written `c ≠ c` — that is
free now — it is what closes one whose sides only match after a substitution, like `f(x) ≠ f(y)`.

**`examples/equality/` is one problem in four formulations** — a burglary: whoever left the
fingerprints sent the letter, that person is the gardener, and the gardener holds a key; conclude
that the letter-sender *is* the gardener and holds a key. The conclusion demands the equality atom
itself, which is what forces transitivity — a congruence axiom moves a predicate along an equality,
it cannot manufacture one — while the two links are both stated with the fingerprint-leaver first,
which forces symmetry, and the key must cross the identity, which forces congruence:

| | result | steps |
| --- | --- | --- |
| `without_congruence.py` — the three properties, no congruence | **UNKNOWN** | the step limit, whatever it is |
| `with_congruence.py` — symmetry + transitivity + congruence for `K` | PROVED | 343 |
| `with_paramodulation.py` — `=`, no axioms | PROVED | 16 |
| `with_superposition.py` — `=`, no axioms, ordered | PROVED | 9 |

Two measurements worth keeping: adding **reflexivity** to `with_congruence` stops it proving even
at 400 steps — `Eq(x,x)` unifies with almost every equality and floods the search — and the
congruence axiom there is written for `K` alone, so the reader has to know in advance which
predicate the proof will need to move. One more argument for the rule, visible in any transcript:
`c = g(c)` and `g(c) ≠ c` are a contradiction that plain resolution cannot close, because the
atoms `=(c, g(c))` and `=(g(c), c)` do not unify — it takes a symmetry axiom, or one rewrite.

**Factoring is what makes the calculus complete** (`factoring.py`). Binary resolution yields
`|C1| + |C2| - 2` literals, so two 2-literal parents produce 2-literal resolvents forever and
nothing ever shrinks toward □. Factoring unifies two *same-sign* literals inside one clause and
merges them (`P(x) ∨ P(y)` → `P(x)`), which is the only rule here that shortens a clause.
Resolution alone is not refutation-complete: with `USE_FACTORING = False` the prover reports
`SATURATED_NO_CONTRADICTION` on `{∀x∀y (P(x)∨P(y)), ∀x∀y (¬P(x)∨¬P(y))}`, which is
unsatisfiable. Both rules are switchable so that failure can be demonstrated. A step's parents
arrive as a *tuple* of distinct indices (`inference.py`) — a factoring or self-resolution step
names one clause, and listing it twice would delete it twice.

**Self-resolution is a third rule, and most of what it produces is junk**
(`config.ALLOW_SELF_RESOLUTION`). Resolving a clause with a renamed copy of itself composes it with
itself: `P(x) ∨ ¬P(f(x))` gives `P(x) ∨ ¬P(f(f(x)))`, which neither resolution across a pair nor
factoring produces. What it needs is not two literals that are complementary *as written* — that
is a tautology, and `clause_is_tautology` has already dropped it — but two that merely unify, and
such a clause is perfectly satisfiable: `L(y,c) ∨ ¬L(y,z)` is false when `L(a,b)` holds exactly for
`b ≠ c`. So nothing may be deleted from it, and the rule genuinely applies.

When it is a waste is exactly characterisable, which is why `_already_implied` catches so much:
*if `L, ¬M ∈ C` and some `τ` has `Mτ = L` and `Lτ = L`, the self-resolvent is
`(C − {L}) ∪ (Cτ − {¬L})`, which contains `Lτ = L` and therefore all of `C`* — the parent with
literals bolted on. `¬P(z) ∨ ¬L(y,z) ∨ L(y,c)` with `τ = {z := c}` is that case, and it returns
itself plus `¬P(c)`. When the unifier has to move `C`'s own variables instead, as in
`P(x) ∨ ¬P(f(x))`, the result is genuinely new. Do not conclude from the first case that the rule
can be dropped: the completeness proof lifts a ground refutation, and a ground refutation may
resolve two distinct *instances* of one clause — which is precisely a self-resolution.

**The witness-focus pass is sound but incomplete** — not unsound, as an earlier version of this
file claimed. Substituting `x := witness` is universal instantiation, so a `PROVED` from the
focused pass is a real proof; only a negative from it is meaningless. It guesses, so it declines
to guess in the two places where the guess is baseless:

- **More than one witness ⇒ no focused pass at all** (`prover._try_focusing`). With `c1`, `c2`,
  `c3` all standing for "something that exists", `x := c1` is a coin toss between them, so the
  prover narrates the skip and goes to the general search. `SkolemNames.witnesses` reports what
  was invented; `Preprocessed.witnesses` passes it on. `owner_never_betrayed(_variant)` (3
  witnesses) and both equivalence directions (2 and 5) take this path, and still return what they
  did before, faster.
- **The relation axioms stay general** (`focus_kb_on_witness(..., protected=...)`). Pinning
  `¬Eq(x,y) ∨ Eq(y,x)` to `c` leaves an axiom that says the relation is symmetric *about `c`* —
  which is exactly what declaring it symmetric was meant to avoid. The clauses know where they
  came from: `prove` hands `preprocess` the positions of the assumptions `axioms.py` generated
  (they are appended, so they are the tail), and `Preprocessed.axiom_clauses` comes back with the
  clause indices they produced. Both step orders record it, since either can be the one running.

What is still open: `focus_kb_on_witness` substitutes only the variable named by
`focus.FOCUSED_VARIABLE` (`"x"`), and `clean_clause_variables` keeps a variable's original name
when it is free — so formulas written with `u`/`v` produce a "focused" KB identical to the
original, and the prover then runs the entire search twice for nothing.

## Conventions

Match the existing style: an extremely vertical layout (one argument, operand, or list element
per line, blank lines between logical groups), plain functions over classes, no type annotations
outside the dataclass fields. User-facing narration is Hebrew; module docstrings, identifiers,
and comments are English except where they carry preserved course commentary. New solver stages
should print their reasoning in the same numbered-step format as `preprocess`.
