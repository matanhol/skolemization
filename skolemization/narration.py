"""How everything this prover says is laid out.

The core modules do not print.  They call an *event* here -- one function per
thing that happened, not one per line of output -- and this module decides what
the reader sees::

    narration.resolvent_added(resolvent)

    ->  <the phrase for "resolvent_added">
            ¬D(x) ∨ B(x, y)

The *words* are not here: they live in phrases/, one module per language, and
are reached through ``phrase(key)`` and ``phrase_table(name)``.  So this file
is the one to open to change a layout, add a step, or decide which bindings are
worth showing -- and phrases/hebrew.py is the one to open to reword a sentence
or to add a language.

Output goes through ``say`` (output.py), which sets the direction the language
is written in and honours ``config.NARRATE``.

Sections below follow the pipeline: prover -> preprocess -> search ->
subsumption -> focus.
"""

from . import config
from . import rewrite
from .display import (
    clause_str,
    formula_str,
    show_formulas,
    show_kb,
)
from .formulas import negated_equality_str
from .inference import (
    FACTORING,
    PARAMODULATION,
)
from .output import (
    ltr,
    say,
    say_block,
)
from .phrases import (
    phrase,
    phrase_table,
)
from .resolution import meaningful_substitutions
from .unification import apply_substitution_literal


LINE = "=" * 70
RULE = "-" * 70
BANNER = "#" * 70


# ================================================================
# PROVER
# ================================================================




def relation_axioms(
    generated_axioms
):

    """Step 0: which relation properties were declared, and what they added."""

    say(
        "\n"
        + LINE
    )

    say(
        phrase("relation_axioms_1")
    )

    say(
        LINE
    )

    if not generated_axioms:

        say(
            phrase("relation_axioms_2")
        )

        return

    for (
        property_name,
        relation,
        axiom
    ) in generated_axioms:

        description = (
            phrase_table("property_names").get(
                property_name,
                phrase_table("property_names")["reflexive"]
            )
        )

        say(
            phrase("relation_axioms_3", relation=relation, description=description)
        )

        say(
            phrase("relation_axioms_4")
        )

        say(
            f"    {axiom}"
        )


EQUALITY_RULE_NAMES = {
    "paramodulation": "Paramodulation",
    "superposition": "Superposition",
}


def reflexivity_for_equality(
    axiom
):

    """The problem uses ``=`` and the rule is on, so ``x = x`` is added.

    Said out loud because it is the one axiom the rule does not replace.  A
    literal that is *written* ``c ≠ c`` needs nothing -- it is false on sight
    and dropped -- but one whose two sides only become equal after a
    substitution, like ``f(x) ≠ f(y)``, is closed by resolving against
    reflexivity.
    """

    rule = EQUALITY_RULE_NAMES[
        config.EQUALITY_RULE
    ]

    say(
        phrase("reflexivity_for_equality_1", rule=rule)
    )

    say(
        phrase("reflexivity_for_equality_2")
    )

    say(
        phrase("reflexivity_for_equality_3")
    )

    say(
        phrase("reflexivity_for_equality_4")
        + ltr(
            negated_equality_str("c", "c")
        )
        + phrase("reflexivity_for_equality_5")
    )

    say(
        phrase("reflexivity_for_equality_6")
        + ltr(
            negated_equality_str("f(x)", "f(y)")
        )
        + phrase("reflexivity_for_equality_7")
    )

    say(
        phrase("reflexivity_for_equality_8")
    )

    say(
        f"    {axiom}"
    )


def working_assumptions(
    assumptions
):

    """The assumptions the search will run on, generated axioms included."""

    say(
        phrase("working_assumptions")
    )

    for i, assumption in enumerate(
        assumptions,
        1
    ):

        say(
            f"{i}. {assumption}"
        )


def conclusion(
    text
):

    """The conclusion being tested, as written, before it is negated."""

    say(
        phrase("conclusion")
    )

    say(
        text
    )


def final_status(
    status
):

    """The verdict, framed in banners."""

    say(
        "\n"
        + LINE
    )

    say(
        "FINAL STATUS:",
        status
    )

    say(
        LINE
    )


def final_status_unframed(
    status
):

    """The FALLBACK_TO_GENERAL = False path, which prints no banners."""

    say(
        "\nFINAL STATUS:",
        status
    )


def focused_search_failed(
    witness
):

    """The focused attempt proved nothing, so the general search follows."""

    say(
        "\n"
        + LINE
    )

    say(
        phrase("focused_search_failed_1")
    )

    say(
        LINE
    )

    say(
        phrase("focused_search_failed_2", witness=witness)
    )

    say(
        phrase("focused_search_failed_3")
    )


# ================================================================
# EQUIVALENCE
# ================================================================

WIDE = "=" * 80


def equivalence_direction(
    index,
    from_name,
    to_name
):

    """Announce one of the two entailment directions being tried.

    The first direction gets one blank line above it and every later block
    gets two, which is what puts visible air between the major sections.
    """

    say(
        "\n" * index
        + WIDE
    )

    say(
        phrase("equivalence_direction", index=index)
        + ltr(
            f"{from_name} ⊨ {to_name}"
        )
    )

    say(
        WIDE
    )


def equivalence_verdict(
    result,
    first_name,
    second_name
):

    """The ruling: equivalent, one direction only, or neither."""

    say(
        "\n\n"
        + WIDE
    )

    say(
        phrase("equivalence_verdict_1")
    )

    say(
        WIDE
    )

    # These go on lines of their own, with no Hebrew beside them, so they
    # need no direction marking -- unlike the header above.

    forward = (
        f"{first_name} ⊨ {second_name}"
    )

    backward = (
        f"{second_name} ⊨ {first_name}"
    )

    if result.equivalent:

        say(
            phrase("equivalence_verdict_2")
        )

        say(
            phrase("equivalence_verdict_3")
        )

        say(
            f"    {first_name} ≡ {second_name}"
        )

        return

    if result.forward == "PROVED":

        _one_direction_only(
            forward,
            backward
        )

        return

    if result.backward == "PROVED":

        _one_direction_only(
            backward,
            forward
        )

        return

    say(
        phrase("equivalence_verdict_4")
    )

    say(
        phrase("equivalence_verdict_5")
    )


def _one_direction_only(
    proved,
    unproved
):

    """Exactly one entailment went through, so there is no equivalence yet."""

    say(
        phrase("_one_direction_only_1")
    )

    say(
        f"    {proved}"
    )

    say(
        phrase("_one_direction_only_2")
    )

    say(
        f"    {unproved}"
    )

    say(
        phrase("_one_direction_only_3")
    )


# ================================================================
# PREPROCESS
# ================================================================




def step_header(
    number
):

    """The banner announcing one numbered pipeline step."""

    say(
        "\n"
        + LINE
    )

    say(
        f"{number}. "
        f"{phrase_table("step_titles")[number]}"
    )

    say(
        LINE
    )


def implication_rule():

    """The rewrite rule for step 2, as a reminder before the work."""

    say(
        "\n"
        + ltr("P → Q")
        + phrase("implication_rule")
        + ltr("¬P ∨ Q")
    )


def cnf_rule():

    """The distribution rule for step 6."""

    say(
        "\n"
        + ltr("P ∨ (Q ∧ R)")
        + phrase("cnf_rule")
        + ltr("(P ∨ Q) ∧ (P ∨ R)")
    )





def rewrites(
    records
):

    """Every rule the step fired on this formula, in the order it fired them.

    Each record is the *local* rewrite, so the reader sees the rule itself
    rather than a subtree with several rules already applied to it.
    """

    if not config.SHOW_SUBSTEPS:
        return

    for record in records:

        say(
            f"  {phrase_table("rule_names")[record.rule]}:"
        )

        say_block(
            "      ",
            formula_str(
                record.before
            ),
            indent="      "
        )

        say_block(
            "      ⇒  ",
            formula_str(
                record.after
            ),
            indent="        "
        )


def step_kb(
    formulas
):

    """Close a step by showing the whole knowledge base."""

    if not config.SHOW_KB_AFTER_EACH_STEP:
        return

    show_formulas(
        formulas,
        phrase("step_kb")
    )


def nothing_changed():

    """The step ran but left every formula exactly as it was."""

    say(
        phrase("nothing_changed")
    )


def formula_unchanged():

    """The step ran but left *this* formula exactly as it was.

    Said rather than skipped: walking one formula through the steps, a step
    that printed nothing would look like a step that never ran.
    """

    say(
        phrase("formula_unchanged")
    )


def formula_list(
    formulas
):

    """The formulas as they now stand, numbered F1, F2, ..."""

    for i, formula in enumerate(
        formulas,
        1
    ):

        say_block(
            f"F{i}: ",
            formula_str(
                formula
            )
        )


def formula_before(
    index,
    formula
):

    """One formula's number, and its state before the step's transform."""

    say(
        f"\nF{index}:"
    )

    formula_state_before(
        formula
    )


def formula_state_before(
    formula
):

    """The "before" line on its own, for a step that already said which formula.

    Walking one formula through every step names it once, at the top; the steps
    under it only report the change.  Both orders come through here so the pair
    of them cannot drift into two different wordings.
    """

    say_block(
        phrase("formula_state_before"),
        formula_str(
            formula
        )
    )


def formula_after(
    formula
):

    """The same formula once the transform has run."""

    say_block(
        phrase("formula_after"),
        formula_str(
            formula
        )
    )


def formula_before_after(
    index,
    before,
    after
):

    """A before/after pair, which is what most steps report."""

    formula_before(
        index,
        before
    )

    formula_after(
        after
    )


# ----------------------------------------------------------------
# Walking one formula through the steps
#
# The same seven steps, told the other way round: everything below belongs to
# config.ONE_FORMULA_AT_A_TIME, where a formula is carried from its written
# form down to its clauses before the next one starts.  The step titles, the
# rule sub-steps and the witness explanations are the ones the whole-KB order
# uses -- only the framing here is new.
# ----------------------------------------------------------------

def walk_header(
    index,
    total,
    formula
):

    """Open one formula's journey through the steps."""

    say(
        "\n"
        + LINE
    )

    say(
        phrase("walk_header", index=index, total=total)
    )

    say(
        LINE
    )

    say_block(
        f"F{index}: ",
        formula_str(
            formula
        )
    )


def walk_step(
    number
):

    """One step's heading, inside a formula's journey.

    Lighter than :func:`step_header`, which announces a step for the whole KB;
    this one sits under a formula and is titled from the same table.
    """

    say(
        "\n"
        + RULE
    )

    say(
        f"{number}. "
        f"{phrase_table("step_titles")[number]}"
    )

    say(
        RULE
    )


def walk_clauses(
    index,
    clauses
):

    """Step 7 for a single formula: the clauses it turned into."""

    show_kb(
        clauses,
        phrase("walk_clauses", index=index)
    )


def skolem_explanations(
    explanations
):

    """Why each ∃ became the witness it became."""

    if not explanations:

        say(
            phrase("skolem_explanations_1")
        )

    for (
        variable,
        replacement,
        universals
    ) in explanations:

        if universals:

            say(
                ltr(f"∃{variable}")
                + phrase("skolem_explanations_2")
                +
                ltr(
                    ", ".join(
                        f"∀{u}"
                        for u
                        in universals
                    )
                )
            )

            say(
                phrase("skolem_explanations_3")
            )

            say(
                phrase("skolem_explanations_4")
            )

        else:

            say(
                ltr(f"∃{variable}")
                + phrase("skolem_explanations_5")
            )

            say(
                phrase("skolem_explanations_6")
            )

        say(
            f"    {variable} := {replacement}"
        )


def clause_kb(
    clauses
):

    """The finished clause set, on its way into the search."""

    show_kb(
        clauses,
        phrase("clause_kb")
    )


# ================================================================
# SEARCH
# ================================================================

def general_search_title():

    """The banner over the unfocused search.

    A function rather than a constant: a module-level ``phrase(...)`` would be
    looked up once, at import, and every later run would be narrated in
    whatever language happened to be set at that moment.
    """

    return phrase(
        "general_search"
    )


def focused_search_title(
    witness
):

    """What the focused pass calls itself, naming the witness it pinned."""

    return phrase("focused_search_title", witness=witness)


def search_header(
    title,
    kb
):

    """A search is starting: which one, with which rules, and on what KB."""

    say(
        "\n"
        + LINE
    )

    say(
        title
    )

    say(
        LINE
    )

    if config.EQUALITY_RULE != "none":

        say(
            phrase("search_header_1")
            + EQUALITY_RULE_NAMES[
                config.EQUALITY_RULE
            ]
            + "."
        )

    show_kb(
        kb,
        phrase("search_header_2")
    )


def set_of_support(
    seeds
):

    """The search is restricted to steps that touch the negated conclusion."""

    say(
        phrase("set_of_support_1")
    )

    say(
        phrase("set_of_support_2")
    )

    say(
        phrase("set_of_support_3")
    )

    say(
        phrase("set_of_support_4")
    )

    if not seeds:

        say(
            phrase("set_of_support_5")
        )

        return

    say(
        phrase("set_of_support_6")
    )

    for clause in seeds:

        say(
            "    "
            + ltr(
                clause_str(
                    clause
                )
            )
        )

    if config.EQUALITY_RULE == "superposition":

        say(
            phrase("set_of_support_7")
        )

        say(
            phrase("set_of_support_8")
        )

        say(
            phrase("set_of_support_9")
        )

        say(
            phrase("set_of_support_10")
        )


def set_of_support_caveat():

    """A supported search ran dry, which is weaker news than saturation.

    Only inferences touching the conclusion were tried, and that is complete
    only while the assumptions are consistent.  If they are not, the conclusion
    follows from them trivially and this search could not have found it.
    """

    say(
        phrase("set_of_support_caveat_1")
    )

    say(
        phrase("set_of_support_caveat_2")
    )

    say(
        phrase("set_of_support_caveat_3")
    )

    say(
        phrase("set_of_support_caveat_4")
    )


def saturated():

    """Nothing new is derivable and □ never appeared."""

    say(
        "\n"
        + BANNER
    )

    say(
        "SATURATED_NO_CONTRADICTION"
    )

    say(
        BANNER
    )

    say(
        phrase("saturated_1")
    )

    say(
        phrase("saturated_2")
    )


def inference_step(
    step,
    inference,
    parents
):

    """Narrate one step, whichever rule produced it."""

    if inference.kind == FACTORING:

        factoring_step(
            step,
            inference,
            parents[0]
        )

        return

    if inference.kind == PARAMODULATION:

        paramodulation_step(
            step,
            inference,
            parents
        )

        return

    resolution_step(
        step,
        inference,
        parents
    )


def step_result(
    inference
):

    """What a step produced -- and, when they were dropped, why it shrank.

    A literal like ``c ≠ c`` cannot hold, so it can never help the clause hold
    either; dropping it is free.  When that empties the clause, the step has
    reached □ on its own, which is worth showing rather than presenting the
    empty clause out of nowhere.
    """

    if inference.before_dropping is None:

        say(
            phrase("step_result_1")
        )

        say(
            f"    {clause_str(inference.result)}"
        )

        return

    say(
        phrase("step_result_2")
    )

    say(
        f"    {clause_str(inference.before_dropping)}"
    )

    say(
        phrase("step_result_3")
        + ltr(
            negated_equality_str("t", "t")
        )
        + phrase("step_result_4")
    )

    say(
        phrase("step_result_5")
    )

    say(
        f"    {clause_str(inference.result)}"
    )


def paramodulation_step(
    step,
    inference,
    parents
):

    """An equality step: one clause's equation rewrites a term in another.

    The reader is being shown the alternative to the equality axioms, so the
    line that matters is which term was replaced by which -- the rest is the
    usual bookkeeping.
    """

    say(
        "\n"
        + LINE
    )

    say(
        f"Paramodulation step {step}"
    )

    say(
        LINE
    )

    say(
        phrase("paramodulation_step_1")
    )

    say(
        f"\nC{inference.parents[0] + 1}: "
        f"{clause_str(parents[0])}"
    )

    say(
        phrase("paramodulation_step_2")
    )

    say(
        f"\nC{inference.parents[1] + 1}: "
        f"{clause_str(parents[1])}"
    )

    replacement = (
        inference.replacement
    )

    if replacement is None:

        say(
            phrase("paramodulation_step_3"),
            ltr(
                str(
                    inference.literal1
                )
            )
        )

        say(
            phrase("paramodulation_step_4"),
            ltr(
                str(
                    inference.literal2
                )
            )
        )

        substitution_used(
            meaningful_substitutions(
                inference.substitution
            )
        )

        step_result(
            inference
        )

        return

    say(
        phrase("paramodulation_step_5")
        + ltr(
            str(
                replacement.source
            )
        )
        + phrase("paramodulation_step_6")
    )

    say(
        phrase("paramodulation_step_7")
        + ltr(
            str(
                replacement.target
            )
        )
        + "."
    )

    say(
        phrase("paramodulation_step_8"),
        ltr(
            str(
                inference.literal2
            )
        )
    )

    say(
        phrase("paramodulation_step_9"),
        ltr(
            str(
                replacement.subterm
            )
        )
    )

    paramodulation_bindings(
        inference
    )

    say(
        phrase("paramodulation_step_10")
    )

    say(
        f"    {replacement.before}"
    )

    say(
        f"    ⟶  {replacement.after}"
    )

    say(
        phrase("paramodulation_step_11")
    )

    step_result(
        inference
    )


def paramodulation_bindings(
    inference
):

    """The step's bindings, split by which clause each variable came from.

    ``y := g1(c)`` says nothing until you know whether ``y`` belongs to the
    equation or to the clause being rewritten -- the two mean different things.
    The clauses were standardized apart before unifying, so their variables are
    disjoint and the split is exact.
    """

    say(
        phrase("paramodulation_bindings_1")
    )

    for label, literal in (
        (phrase("paramodulation_bindings_2"), inference.literal1),
        (phrase("paramodulation_bindings_3"), inference.literal2)
    ):

        bindings = (
            meaningful_substitutions(
                _bindings_of(
                    inference.substitution,
                    literal
                )
            )
        )

        if not bindings:

            say(
                phrase("paramodulation_bindings_4", label=label)
            )

            continue

        say(
            f"    {label}:"
        )

        for (
            variable,
            value
        ) in bindings:

            say(
                f"        {variable} := {value}"
            )


def _bindings_of(
    substitution,
    literal
):

    """The part of the substitution that binds this literal's own variables."""

    mine = _variables_of(
        literal
    )

    return {
        variable: value
        for variable, value
        in substitution.items()
        if variable in mine
    }


def _variables_of(
    literal
):

    """Every variable name occurring in a literal, internal names included."""

    found = set()

    def walk(term):
        """Collect from a term and everything below it."""

        if term.is_var:

            found.add(
                term.name
            )

            return

        for argument in term.args:

            walk(
                argument
            )

    for argument in literal.atom.args:

        walk(
            argument
        )

    return found


def factoring_step(
    step,
    inference,
    parent
):

    """A factoring step: two same-sign literals in one clause, merged.

    Worth spelling out for a reader, because it is the one rule here that
    makes a clause shorter, and shortening is what eventually reaches □.
    """

    say(
        "\n"
        + LINE
    )

    say(
        f"Factoring step {step}"
    )

    say(
        LINE
    )

    say(
        phrase("factoring_step_1")
    )

    say(
        f"\nC{inference.parents[0] + 1}: "
        f"{clause_str(parent)}"
    )

    say(
        phrase("factoring_step_2")
    )

    say(
        f"    {inference.literal1}"
    )

    say(
        f"    {inference.literal2}"
    )

    substitution_used(
        meaningful_substitutions(
            inference.substitution
        )
    )

    say(
        phrase("factoring_step_3")
    )

    step_result(
        inference
    )


def resolution_step(
    step,
    inference,
    parents
):

    """One whole resolution step: what was picked, unified, and derived.

    Deciding which bindings are worth showing, and what the literals look like
    once instantiated, is presentation work -- so it happens here rather than
    in the search loop.
    """

    literal1 = inference.literal1
    literal2 = inference.literal2
    substitution = inference.substitution
    resolvent = inference.result

    say(
        "\n"
        + LINE
    )

    say(
        f"Resolution step {step}"
    )

    say(
        LINE
    )

    say(
        phrase("resolution_step_1")
    )

    if len(parents) == 1:

        say(
            f"\nC{inference.parents[0] + 1}: "
            f"{clause_str(parents[0])}"
        )

        say(
            phrase("resolution_step_2")
        )

    else:

        say(
            f"\nC{inference.parents[0] + 1}: "
            f"{clause_str(parents[0])}"
        )

        say(
            f"C{inference.parents[1] + 1}: "
            f"{clause_str(parents[1])}"
        )

    say(
        phrase("resolution_step_3")
    )

    # Important:
    # Term.__str__ hides __vXXX_ names here.
    say(
        f"    {literal1}"
    )

    say(
        f"    {literal2}"
    )

    substitution_used(
        meaningful_substitutions(
            substitution
        )
    )

    after_substitution(
        apply_substitution_literal(
            literal1,
            substitution
        ),
        apply_substitution_literal(
            literal2,
            substitution
        ),
        inference
    )


def substitution_used(
    substitutions
):

    """The bindings this step needed, or a note that it needed none."""

    say(
        phrase("substitution_used_1")
    )

    if not substitutions:

        say(
            phrase("substitution_used_2")
        )

        return

    for (
        variable,
        value
    ) in substitutions:

        say(
            f"    {variable} := {value}"
        )


def after_substitution(
    literal1,
    literal2,
    inference
):

    """The two literals once instantiated, and the resolvent left behind."""

    say(
        phrase("after_substitution_1")
    )

    say(
        f"    {literal1}"
    )

    say(
        f"    {literal2}"
    )

    say(
        phrase("after_substitution_2")
    )

    step_result(
        inference
    )


def empty_clause(
    kb
):

    """The refutation succeeded: □ was derived."""

    show_kb(
        kb,
        phrase("empty_clause_1")
    )

    say(
        "\n"
        + BANNER
    )

    say(
        "PROVED"
    )

    say(
        BANNER
    )

    say(
        phrase("empty_clause_2")
    )

    say(
        "\n                  □"
    )

    say(
        phrase("empty_clause_3")
    )

    say(
        phrase("empty_clause_4")
    )

    say(
        phrase("empty_clause_5")
    )


# What each ranking key is called, for the block that explains a choice.  The
# order of a key tuple lives in search.STRATEGY_KEY_NAMES; these are only the
# words.




def choice_between(
    chosen,
    chosen_key,
    others,
    names
):

    """Why this step, and not the next best one.

    The ranking is the one part of the search a reader cannot reconstruct from
    the result, so a step that is not the step they would have taken looks
    arbitrary until they see what it beat.  Prints the runners-up and the first
    key on which the winner pulled ahead -- and says so plainly when nothing
    separated them and the order was arbitrary.
    """

    if not others:

        say(
            phrase("choice_between_1")
        )

        return

    say(
        phrase("choice_between_2")
    )

    for other, other_key in others:

        say(
            phrase("choice_between_3")
            + ltr(
                clause_str(
                    other.result
                )
            )
        )

    best, best_key = others[0]

    index = _first_difference(
        chosen_key,
        best_key
    )

    if index is None:

        say(
            phrase("choice_between_4")
        )

        return

    say(
        phrase("choice_between_5")
        + ltr(
            phrase_table("ranking_key_names")[
                names[index]
            ]
        )
        + ": "
        + ltr(
            f"{chosen_key[index]}"
        )
        + phrase("choice_between_6")
        + ltr(
            f"{best_key[index]}"
        )
    )


def _first_difference(
    chosen_key,
    other_key
):

    """The position of the first key the two candidates disagree on."""

    for index, (mine, theirs) in enumerate(
        zip(
            chosen_key,
            other_key
        )
    ):

        if mine != theirs:
            return index

    return None


def resolvent_added(
    resolvent
):

    """The resolvent joining the KB."""

    say(
        phrase("resolvent_added")
    )

    say(
        f"    {clause_str(resolvent)}"
    )


def kb_after_step(
    kb
):

    """The whole KB at the end of a step, when SHOW_FULL_KB_EACH_STEP is on."""

    show_kb(
        kb,
        phrase("kb_after_step")
    )


def step_limit_reached():

    """MAX_RESOLUTION_STEPS ran out with the question still open."""

    say(
        "\n"
        + BANNER
    )

    say(
        "UNKNOWN"
    )

    say(
        BANNER
    )

    say(
        phrase("step_limit_reached_1", max_resolution_steps=config.MAX_RESOLUTION_STEPS)
    )

    say(
        phrase("step_limit_reached_2")
    )


# ================================================================
# SUBSUMPTION
# ================================================================

def redundancy_check_header(
    parent_count
):

    """About to check whether the new clause made any parent redundant.

    A factoring or self-resolution step has one parent, not two, so the
    wording follows the count.
    """

    say(
        "\n"
        + RULE
    )

    if parent_count == 1:

        say(
            phrase("redundancy_check_header_1")
        )

    else:

        say(
            phrase("redundancy_check_header_2")
        )

    say(
        RULE
    )


def no_parent_redundant(
    parent_count
):

    """Every parent earns its place and stays."""

    if parent_count == 1:

        say(
            phrase("no_parent_redundant_1")
        )

    else:

        say(
            phrase("no_parent_redundant_2")
        )

    say(
        phrase("no_parent_redundant_3")
    )


def parent_is_redundant(
    resolvent,
    parent
):

    """Why a parent is being deleted: the resolvent subsumes it."""

    say(
        phrase("parent_is_redundant_1")
    )

    say(
        f"    {clause_str(resolvent)}"
    )

    say(
        phrase("parent_is_redundant_2")
    )

    say(
        f"    {clause_str(parent)}"
    )

    say(
        phrase("parent_is_redundant_3")
    )

    say(
        phrase("parent_is_redundant_4")
    )

    say(
        phrase("parent_is_redundant_5")
    )

    say(
        f"    {clause_str(parent)}"
    )


# ================================================================
# SWEEPING WITH THE UNIT CLAUSES
# ================================================================
#
# config.FULL_SUBSUMPTION_EACH_STEP.  It runs before the first step and after
# every step, so it speaks only when it has something to say.

def unit_queue_opened(
    queue
):

    """The mechanism introducing itself, with the queue it starts from."""

    say(
        "\n"
        + RULE
    )

    say(
        phrase("unit_queue_opened_1")
    )

    say(
        RULE
    )

    say(
        phrase("unit_queue_opened_2")
    )

    say(
        phrase("unit_queue_opened_3")
    )

    say(
        phrase("unit_queue_opened_4")
    )

    say(
        phrase("unit_queue_opened_5")
    )

    say(
        phrase("unit_queue_opened_6")
    )

    if not queue:

        say(
            phrase("unit_queue_opened_7")
        )

        return

    say(
        phrase("unit_queue_opened_8")
    )

    for clause in queue:

        say(
            "    "
            + ltr(
                clause_str(
                    clause
                )
            )
        )


def unit_joined_queue(
    clause
):

    """A resolvent that is a single literal, joining the back of the queue."""

    say(
        phrase("unit_joined_queue")
    )

    say(
        "    "
        + ltr(
            clause_str(
                clause
            )
        )
    )


def unit_sweep_header():

    """Said once, the first time a sweep actually does something."""

    say(
        phrase("unit_sweep_header")
    )


def unit_simplified(
    unit,
    clause,
    remainder
):

    """A unit cancelled a literal, and the clause is replaced by what is left."""

    say(
        "\n  "
        + ltr(
            clause_str(
                unit
            )
        )
        + phrase("unit_simplified_1")
    )

    say(
        "      "
        + ltr(
            clause_str(
                clause
            )
        )
    )

    say(
        phrase("unit_simplified_2")
    )

    say(
        "      "
        + ltr(
            clause_str(
                remainder
            )
        )
    )


def unit_makes_redundant(
    unit,
    clause
):

    """A clause that repeats the unit's own literal, and so says nothing new."""

    say(
        "\n  "
        + ltr(
            clause_str(
                unit
            )
        )
        + phrase("unit_makes_redundant_1")
    )

    say(
        "      "
        + ltr(
            clause_str(
                clause
            )
        )
    )

    say(
        phrase("unit_makes_redundant_2")
    )


def unit_empty_clause(
    unit,
    clause
):

    """The remainder was empty: the sweep itself reached □."""

    say(
        "\n  "
        + ltr(
            clause_str(
                unit
            )
        )
        + phrase("unit_empty_clause_1")
    )

    say(
        "      "
        + ltr(
            clause_str(
                clause
            )
        )
    )

    say(
        phrase("unit_empty_clause_2")
    )


def unit_sweep_nothing():

    """The sweep ran and found nothing -- said, so the check is visible."""

    say(
        phrase("unit_sweep_nothing")
    )


# ================================================================
# WHY A SATURATED SEARCH IS FINISHED
# ================================================================

def counterexample(
    entered,
    reduced,
    shape,
    needed
):

    """Working backwards from a saturated KB to what a counter-model must be.

    Pure epilogue: the answer is already fixed, and this only reads the
    negated conclusion's own clauses back out of it.  The reader gets the three
    stages -- as they entered, what the units left of them, and the formula
    they amount to -- and then the negation, which is what the conclusion would
    have needed to hold.
    """

    say(
        "\n"
        + LINE
    )

    say(
        phrase("counterexample_header")
    )

    say(
        LINE
    )

    say(
        phrase("counterexample_intro_1")
    )

    say(
        phrase("counterexample_intro_2")
    )

    say(
        phrase("counterexample_intro_3")
    )

    say(
        phrase("counterexample_entered")
    )

    for clause in entered:

        say(
            "    "
            + ltr(
                clause_str(clause)
            )
        )

    if not reduced:

        say(
            phrase("counterexample_nothing")
        )

        return

    say(
        phrase("counterexample_reduced")
    )

    for clause in reduced:

        say(
            "    "
            + ltr(
                clause_str(clause)
            )
        )

    say(
        phrase("counterexample_shape")
    )

    say_block(
        "    ",
        formula_str(shape),
        indent="    "
    )

    say(
        phrase("counterexample_together")
    )

    say(
        phrase("counterexample_needed")
    )

    say_block(
        "    ",
        formula_str(needed),
        indent="    "
    )


def counterexample_refused(
    focused
):

    """Why no counter-model was read off, when the flag asked for one."""

    say(
        phrase(
            "counterexample_refused_focused"
            if focused
            else "counterexample_refused_support"
        )
    )


def saturation_header():

    """Opening the account of a search that ran out of moves."""

    say(
        "\n"
        + LINE
    )

    say(
        phrase("saturation_header_1")
    )

    say(
        LINE
    )

    say(
        phrase("saturation_header_2")
    )

    say(
        phrase("saturation_header_3")
    )

    say(
        phrase("saturation_header_4")
    )


def full_redundancy_header(
    size
):

    """The whole-KB subsumption sweep is starting."""

    say(
        "\n"
        + RULE
    )

    say(
        phrase("full_redundancy_header_1", size=size)
    )

    say(
        RULE
    )

    say(
        phrase("full_redundancy_header_2")
    )

    say(
        phrase("full_redundancy_header_3")
    )


def clause_is_redundant(
    index,
    clause,
    subsumer
):

    """One clause the sweep found redundant, and what makes it so."""

    say(
        f"\nC{index}: "
        + ltr(
            clause_str(
                clause
            )
        )
    )

    say(
        phrase("clause_is_redundant_1"),
        ltr(
            clause_str(
                subsumer
            )
        )
    )

    say(
        phrase("clause_is_redundant_2")
    )


def nothing_redundant():

    """The sweep found nothing to delete."""

    say(
        phrase("nothing_redundant")
    )


def reduced_kb(
    kb
):

    """What the KB looks like once the redundant clauses are gone."""

    show_kb(
        kb,
        phrase("reduced_kb")
    )


def account_header(
    size,
    pairs
):

    """About to go over every step still available."""

    say(
        "\n"
        + RULE
    )

    say(
        phrase("account_header_1", pairs=pairs, size=size)
    )

    say(
        RULE
    )

    say(
        phrase("account_header_2")
    )


def pair_yields_nothing(
    first,
    second,
    complementary
):

    """A pair that produces no resolvent at all, and which of the two reasons.

    Either nothing in them could ever resolve, or there are literals facing
    each other that simply cannot be unified.
    """

    if complementary:

        say(
            phrase("pair_yields_nothing_1", first=first, second=second)
        )

        return

    say(
        phrase("pair_yields_nothing_2", first=first, second=second)
    )





def pair_resolvent(
    first,
    second,
    resolvent,
    verdict
):

    """A pair that does resolve, and why the result changes nothing."""

    say(
        f"\nC{first} × C{second}: "
        + ltr(
            clause_str(
                resolvent
            )
        )
    )

    say(
        "    "
        + phrase_table("account_verdicts")[
            verdict
        ]
    )


def factor_yields_nothing(
    index
):

    """No two literals of this clause can be merged."""

    say(
        phrase("factor_yields_nothing", index=index)
    )


def factor_result(
    index,
    factor,
    verdict
):

    """A factor this clause still has, and why it changes nothing."""

    say(
        phrase("factor_result", index=index)
        + ltr(
            clause_str(
                factor
            )
        )
    )

    say(
        "    "
        + phrase_table("account_verdicts")[
            verdict
        ]
    )


def factoring_is_off():

    """Factoring was not part of this search, so it is not part of the account."""

    say(
        phrase("factoring_is_off")
    )


def equality_rule_is_off():

    """No equality rule ran, so the account does not pretend otherwise."""

    say(
        phrase("equality_rule_is_off")
    )


def paramodulant_result(
    first,
    second,
    result,
    verdict
):

    """One rewriting the equality rule could still do, and why it adds nothing."""

    say(
        f"\nParamodulation C{first} → C{second}: "
        + ltr(
            clause_str(
                result
            )
        )
    )

    say(
        "    "
        + phrase_table("account_verdicts")[
            verdict
        ]
    )


def no_paramodulants():

    """The equality rule ran but has nothing left to rewrite."""

    say(
        phrase("no_paramodulants")
    )


def account_conclusion(
    new_clauses,
    focused=False
):

    """The closing statement: every possibility was tried, none of them helps.

    What that is worth depends on the KB.  A focused KB is one guess out of
    many, so its emptiness is a fact about the guess; only the general KB says
    anything about the problem.
    """

    say(
        "\n"
        + RULE
    )

    if new_clauses:

        say(
            phrase("account_conclusion_1", new_clauses=new_clauses)
        )

        say(
            RULE
        )

        return

    say(
        phrase("account_conclusion_2")
    )

    if focused:

        say(
            phrase("account_conclusion_3")
        )

        say(
            RULE
        )

        say(
            phrase("account_conclusion_4")
        )

        say(
            phrase("account_conclusion_5")
        )

        say(
            phrase("account_conclusion_6")
        )

        say(
            phrase("account_conclusion_7")
        )

        return

    say(
        phrase("account_conclusion_8")
    )

    say(
        RULE
    )

    say(
        phrase("account_conclusion_9")
    )

    say(
        phrase("account_conclusion_10")
    )


# ================================================================
# FOCUS ON c
# ================================================================

def focus_header(
    witness,
    variable
):

    """The focused attempt is starting, and the substitution it applies."""

    say(
        "\n"
        + LINE
    )

    say(
        phrase("focus_header_1", witness=witness)
    )

    say(
        LINE
    )

    say(
        phrase("focus_header_2", witness=witness)
    )

    say(
        phrase("focus_header_3")
    )

    say(
        f"\n    {variable} := {witness}"
    )


def focus_skipped_many_witnesses(
    witnesses
):

    """Why there is no focused attempt: the witness is not unique.

    ``x := c`` is a guess that only makes sense when ``c`` is *the* thing that
    exists.  With several witnesses it is a guess between them, so the prover
    does not make it.
    """

    say(
        "\n"
        + LINE
    )

    say(
        phrase("focus_skipped_many_witnesses_1")
    )

    say(
        LINE
    )

    say(
        phrase("focus_skipped_many_witnesses_2")
    )

    say(
        "    "
        + ltr(
            ", ".join(
                witnesses
            )
        )
    )

    say(
        phrase("focus_skipped_many_witnesses_3")
    )

    say(
        phrase("focus_skipped_many_witnesses_4")
    )

    say(
        phrase("focus_skipped_many_witnesses_5")
    )


def focus_keeps_axioms():

    """The relation axioms are staying general, and why."""

    say(
        phrase("focus_keeps_axioms_1")
    )

    say(
        phrase("focus_keeps_axioms_2")
        + ltr("¬Eq(x,y) ∨ Eq(y,x)")
        + phrase("focus_keeps_axioms_3")
    )

    say(
        phrase("focus_keeps_axioms_4")
        + ltr("¬Eq(c,y) ∨ Eq(y,c)")
        + phrase("focus_keeps_axioms_5")
        + ltr("c")
        + " --"
    )

    say(
        phrase("focus_keeps_axioms_6")
    )


def focus_clause_kept(
    index,
    clause
):

    """One clause the focus left exactly as it was."""

    say(
        f"\nC{index}:"
    )

    say(
        phrase("focus_clause_kept"),
        ltr(
            clause_str(
                clause
            )
        )
    )


def focus_clause(
    index,
    before,
    after
):

    """One clause, before and after being pinned to the witness."""

    say(
        f"\nC{index}:"
    )

    say(
        phrase("focus_clause_1"),
        ltr(
            clause_str(
                before
            )
        )
    )

    say(
        phrase("focus_clause_2"),
        ltr(
            clause_str(
                after
            )
        )
    )


def focused_kb(
    kb,
    witness
):

    """The KB the focused search will actually run on."""

    show_kb(
        kb,
        phrase("focused_kb", witness=witness)
    )
