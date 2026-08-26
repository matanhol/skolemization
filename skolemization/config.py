"""Settings, read at call time.

These are looked up as ``config.NAME`` rather than imported by value, so a
caller can still change one before invoking :func:`skolemization.prove`::

    from skolemization import config, prove

    config.MAX_RESOLUTION_STEPS = 400
    prove(assumptions, conclusion)
"""


# ================================================================
# SEARCH
# ================================================================

# Which of the available steps to take next.
#
# "shallowest_general_first" ranks by how deeply the result's terms nest, and
# only then by the keys below it.  Depth has to come first because nothing else
# stops a runaway: resolving ¬P(x) ∨ S(g2(x)) against P(g1(g2(c))) gives
# S(g2(g1(g2(c)))), which is short, general, and the parent of a deeper one --
# see examples/recursion, where the other ranking is carrying terms nested a
# hundred deep by step 150 and never finishes.
#
# "shortest_general_first" is that ranking without the depth key: shortest
# resolvent, then a pair that matches as it stands over one that has to bind
# variables -- P(c) ∨ B(x,y) against ¬P(c) rather than against ¬B(c, g1(c)) --
# then the simpler terms.  "shortest" drops the generality preference;
# "random" picks any candidate.

STRATEGY = "shallowest_general_first"
MAX_RESOLUTION_STEPS = 30
SHOW_FULL_KB_EACH_STEP = True

# After each step, show the runners-up: the two next-best candidates and the
# key that decided between them.  The ranking is the one thing in the search a
# reader cannot see from the result, so when the prover takes a step that is
# not the one they would have taken, this is what names the preference that
# overruled theirs instead of leaving it looking arbitrary.
#
# Off, because that is a question a reader has now and then and the block is
# printed at every step: the proof itself is what the transcript is for.  Turn
# it on for the lesson where the question comes up.

EXPLAIN_CHOICE = False

# Close a saturated search by showing why nothing more can be derived: a full
# subsumption sweep over the final KB, then every remaining pair and what it
# yields.  Pure epilogue -- it cannot change the answer, only explain it.

EXPLAIN_SATURATION = True

# Set of support: seed a "supported" set with the clauses of the negated
# conclusion, and allow only inferences that touch it -- every result joining
# the set in turn.  The assumptions are left resolving against the conclusion
# instead of against each other, which is where the contradiction has to come
# from anyway: a satisfiable set of clauses cannot refute anything on its own.
#
# Off by default, and the reason is the word "satisfiable".  If the assumptions
# contradict each other, the conclusion follows trivially -- and this
# restriction can miss exactly that, turning a provable question into a
# saturated one.  The narration says so when a supported search runs dry.

SET_OF_SUPPORT = False

# Let the one-literal clauses simplify the KB, instead of only checking each
# step's own parents.  Before the first step and after every step, each unit --
# held in a queue, in the order they appeared -- goes over the KB and:
#
#     {P(x)} with {¬P(x) ∨ Q(x)}   ->  the clause is replaced by {Q(x)}
#     {P(x)} with {P(x) ∨ Q(x)}    ->  the clause is deleted, it adds nothing
#     {P(x)} with {¬P(x)}          ->  nothing is left: □, and the proof is done
#
# Only when no assignment is needed: {P(x)} does not touch {¬P(c) ∨ Q(c)}, and
# a match that would rewrite the remainder is refused too.  A remainder of one
# literal joins the queue.  None of this costs a resolution step.
#
# Off by default -- an option to watch, not a change to how the search reads.

FULL_SUBSUMPTION_EACH_STEP = False

# Try the search once with every focused variable pinned to the Skolem
# witness before running it in general.  Named for the witness, not for "c",
# because the witness is only called c when the problem leaves that name free.

FOCUS_ON_WITNESS = True
FALLBACK_TO_GENERAL = True


# ================================================================
# INFERENCE RULES
# ================================================================
#
# Binary resolution alone is not refutation-complete, so with these off the
# prover can report SATURATED_NO_CONTRADICTION on a knowledge base that is
# genuinely unsatisfiable.  They are switchable precisely so that failure can
# be demonstrated -- run it off, watch it saturate, turn it on.

# Merge two same-sign literals within one clause (factoring.py).  This is the
# one that restores completeness; without it nothing ever shortens a clause.

USE_FACTORING = True

# Resolve a clause against a renamed copy of itself, which ordinary resolution
# allows -- the two premises of the rule need only be variable-disjoint.  It is
# what composes a clause with itself: P(x) ∨ ¬P(f(x)) resolves with its own copy
# to P(x) ∨ ¬P(f(f(x))), which no other rule here produces, and which factoring
# (same-sign literals only) cannot touch.
#
# Note what it does *not* need: two literals that are complementary as written.
# L(y, c) and ¬L(y, z) merely unify, and the clause holding both is not a
# tautology -- take L(a,b) true exactly when b is not c -- so the tautology
# check leaves it alone and the rule applies to it.  Where those two literals
# match one-way (some τ with Mτ = L and Lτ = L) the result is the parent clause
# with extra literals attached, and search._already_implied throws it away.

ALLOW_SELF_RESOLUTION = True

# How equality is handled, when the problem uses x = y.
#
#   "none"            equality is an ordinary predicate.  It means nothing to
#                     the prover unless you supply the axioms yourself --
#                     reflexivity, symmetry, transitivity AND congruence for
#                     every predicate and function.
#   "paramodulation"  the rule instead of the axioms: rewrite equals for equals
#                     inside clauses, at any depth (paramodulation.py).  With
#                     resolution and factoring this is complete for equality,
#                     and the reflexivity axiom x = x is added for you.
#   "superposition"   the same rule, but an equation may only rewrite a term
#                     into a smaller one (ordering.py).  Far fewer candidates;
#                     this is the restriction real provers are built on.

EQUALITY_RULE = "paramodulation"


# ================================================================
# HOW MUCH THE PREPROCESSING STEPS EXPLAIN
# ================================================================
#
# Setting the first two False and the third True gives the terser narration
# the package shipped with originally.

# Close each of the seven steps by showing the whole knowledge base, so the
# reader sees the state and not only the individual edits.

SHOW_KB_AFTER_EACH_STEP = True

# Report every individual rule application inside a step -- each De Morgan,
# each distribution -- instead of only the finished formula.

SHOW_SUBSTEPS = True

# Narrate formulas a step left alone.  Off by default: a before/after pair
# showing identical text is noise that hides the formulas that did change.

SHOW_UNCHANGED_FORMULAS = False

# Walk one formula through steps 2-7 before starting the next one, instead of
# running each step across the whole KB.  Same clauses either way -- only the
# order of the telling changes -- but following a single formula no longer
# means finding it again under every step.
#
# Step 1 stays whole-KB in both orders, since negating the conclusion is about
# the set.  SHOW_KB_AFTER_EACH_STEP has nothing to close in this order (the KB
# is half-converted while a formula is being walked) and is ignored; each
# formula ends with its own clauses instead.

ONE_FORMULA_AT_A_TIME = False


# ================================================================
# OUTPUT
# ================================================================

# Which language the narration speaks.  The words live in phrases/, one module
# per language; "he" is Hebrew and "en" is English, and an unrecognised value
# raises rather than quietly picking one.
#
# The direction the output is laid out in follows from this and is not a
# setting of its own -- see RTL_OUTPUT below.

LANGUAGE = "he"

# The narration is the point of this package, so it is on by default.
# Set to False to run the prover silently and just take its return value.

NARRATE = True

# Whether the bidi marks are emitted: an RTL base direction on every line that
# holds right-to-left text, and an LTR isolate around every formula inside one.
#
# "auto" follows LANGUAGE -- Hebrew needs them, English would only be littered
# with invisible characters.  True and False force the question; False is what
# a byte-for-byte comparison of the narration wants, and what the original
# single-file script emitted.

RTL_OUTPUT = "auto"

# How a negated equality is printed: "≠" gives  c2 ≠ c3, and "not" gives
# ¬(c2 = c3).  Nothing but the text changes -- x != y, x ≠ y and not (x = y)
# all parse to the same tree, Not(Atom("=", ...)), so the search cannot tell
# them apart and no example's answer or step count moves with this setting.

NEGATED_EQUALITY = "≠"

# Draw every grouping bracket at its own height, stacked out of ⎛ ⎜ ⎝ pieces:
# three rows for the innermost level and two more for every level outwards, so
# the outermost bracket of a formula is the tallest.  A formula is then a block
# of rows rather than a line, with the formula itself on the middle row.
#
# The point is that the ordinary one-row ( ) belongs to P(x) and g1(x) -- an
# application, not a grouping -- so no bracket the printer adds may be that
# small, and nesting stops being something to count.
#
# Set to False to print those same brackets as ordinary ( ) on one line, which
# is what a byte-for-byte comparison wants, and what makes the output paste
# back in as input.

TALL_BRACKETS = True
