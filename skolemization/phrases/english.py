"""Every word the prover says, in English.

The same keys as phrases/hebrew.py, in the same order -- phrases/lookup.py
refuses to import if the two ever disagree about which keys exist.

Written to teach rather than to translate: where the Hebrew explains why a step
is allowed, or what a saturated knowledge base does and does not tell you, the
English carries the same argument rather than the same word order.  Leading
newlines and trailing spaces are part of the phrase, because narration.py
concatenates several of these around a formula.
"""

from .. import rewrite


DIRECTION = "ltr"


PHRASES = {
    "relation_axioms_1":
    "0. Adding the declared properties of relations to the KB",

    "relation_axioms_2":
    """
No special properties of relations were declared.""",

    "relation_axioms_3":
    """
{relation} was declared {description}.""",

    "relation_axioms_4":
    "Adding to the KB:",

    "reflexivity_for_equality_1":
    """
Equality is handled by an inference rule ({rule}), not by axioms:""",

    "reflexivity_for_equality_2":
    "symmetry, transitivity and the congruence axioms are not needed.",

    "reflexivity_for_equality_3":
    "The one axiom that remains is reflexivity.",

    "reflexivity_for_equality_4":
    "A literal written ",

    "reflexivity_for_equality_5":
    " drops of its own accord -- it is false;",

    "reflexivity_for_equality_6":
    "but a literal like ",

    "reflexivity_for_equality_7":
    ", whose two sides become equal only after a substitution,",

    "reflexivity_for_equality_8":
    "is closed against this axiom:",

    "working_assumptions":
    """
The assumptions we start from:""",

    "conclusion":
    """
The conclusion:""",

    "focused_search_failed_1":
    "The focused search ended without a proof",

    "focused_search_failed_2":
    """
Focusing on {witness} is only a heuristic.""",

    "focused_search_failed_3":
    "So we go back to the original KB and try a general Resolution.",

    "equivalence_direction":
    "Checking direction {index}:  ",

    "equivalence_verdict_1":
    "Final result",

    "equivalence_verdict_2":
    "✅ Both implications were proved.",

    "equivalence_verdict_3":
    "Therefore:",

    "equivalence_verdict_4":
    "The two implications were not both proved.",

    "equivalence_verdict_5":
    "So the solver did not establish equivalence.",

    "_one_direction_only_1":
    "Proved:",

    "_one_direction_only_2":
    "but the direction:",

    "_one_direction_only_3":
    "was not proved.",

    "implication_rule":
    "   becomes   ",

    "cnf_rule":
    "  becomes  ",

    "step_kb":
    "The KB at the end of the step",

    "nothing_changed":
    """
No formula changed in this step.""",

    "formula_unchanged":
    "This formula did not change in this step.",

    "formula_state_before":
    "before: ",

    "formula_after":
    "after:  ",

    "walk_header":
    "Formula F{index} of {total}",

    "walk_clauses":
    "7. The clauses of F{index}",

    "skolem_explanations_1":
    "No existential quantifier to eliminate.",

    "skolem_explanations_2":
    " stands under ",

    "skolem_explanations_3":
    "so it may depend on them.",

    "skolem_explanations_4":
    "Substituting:",

    "skolem_explanations_5":
    " does not depend on any universal variable.",

    "skolem_explanations_6":
    "so a constant witness is chosen:",

    "clause_kb":
    "The KB before Resolution",

    "general_search":
    "General Resolution",

    "focused_search_title":
    "Resolution focused on {witness}",

    "search_header_1":
    """
Inference rules: Resolution, Factoring and """,

    "search_header_2":
    "The KB the search starts from",

    "set_of_support_1":
    """
Searching with a set of support:""",

    "set_of_support_2":
    "every step must use at least one clause from the supported set,",

    "set_of_support_3":
    "and every result joins it. The assumptions alone are consistent,",

    "set_of_support_4":
    "so no contradiction can come out of them without the conclusion.",

    "set_of_support_5":
    """
The supported set is empty -- no restriction in practice.""",

    "set_of_support_6":
    """
The supported set to begin with -- the negated conclusion:""",

    "set_of_support_7":
    """
Warning: a set of support together with Superposition.""",

    "set_of_support_8":
    "Each restriction is sound on its own, but they do not compose --",

    "set_of_support_9":
    "each blocks steps the other relies on, and the proof may simply",

    "set_of_support_10":
    "not be found. Measured on this very question. Prefer Paramodulation.",

    "set_of_support_caveat_1":
    """
Note: the search was restricted to the set of support,""",

    "set_of_support_caveat_2":
    "so only steps touching the conclusion were tried.",

    "set_of_support_caveat_3":
    "If the assumptions contradict each other, the conclusion follows vacuously --",

    "set_of_support_caveat_4":
    "and this restriction would not have found that. To check, turn SET_OF_SUPPORT off.",

    "saturated_1":
    """
There is no new resolvent left to add.""",

    "saturated_2":
    "The empty clause □ was not reached.",

    "step_result_1":
    """
Result:""",

    "step_result_2":
    """
Result:""",

    "step_result_3":
    """
A literal of the form """,

    "step_result_4":
    " is false, so it can contribute nothing to the clause.",

    "step_result_5":
    "Dropping it leaves:",

    "paramodulation_step_1":
    """
Using the equation from:""",

    "paramodulation_step_2":
    """
to substitute equals for equals inside:""",

    "paramodulation_step_3":
    """
The equation:""",

    "paramodulation_step_4":
    "The literal rewritten:",

    "paramodulation_step_5":
    """
Direction: matching the """,

    "paramodulation_step_6":
    " side of the equation to a term inside the clause,",

    "paramodulation_step_7":
    "and putting in its place the side ",

    "paramodulation_step_8":
    """
The literal rewritten:""",

    "paramodulation_step_9":
    "The term matched, and replaced:",

    "paramodulation_step_10":
    """
The replacement itself:""",

    "paramodulation_step_11":
    """
This is congruence without axioms: the rule replaces the occurrence inside the term.""",

    "paramodulation_bindings_1":
    """
The substitution needed to match them:""",

    "paramodulation_bindings_2":
    "from the equation",

    "paramodulation_bindings_3":
    "from the clause being rewritten",

    "paramodulation_bindings_4":
    "    {label}: no substitution needed",

    "factoring_step_1":
    """
Chosen:""",

    "factoring_step_2":
    """
Two literals in the same clause, with the same sign:""",

    "factoring_step_3":
    """
After the substitution they are identical, so they merge into one literal.""",

    "resolution_step_1":
    """
Chosen:""",

    "resolution_step_2":
    "Resolving the clause against a copy of itself.",

    "resolution_step_3":
    """
The literals that can be crossed:""",

    "substitution_used_1":
    """
The substitution needed:""",

    "substitution_used_2":
    "    No real substitution is needed.",

    "after_substitution_1":
    """
After the substitution:""",

    "after_substitution_2":
    """
The literals are identical except for the negation, so they cancel.""",

    "empty_clause_1":
    "The final KB",

    "empty_clause_2":
    """
The empty clause was derived:""",

    "empty_clause_3":
    """
A contradiction was found.""",

    "empty_clause_4":
    "The assumptions together with the negated conclusion cannot all hold.",

    "empty_clause_5":
    """
Therefore the conclusion follows from the assumptions.""",

    "choice_between_1":
    """
This was the only candidate at this step.""",

    "choice_between_2":
    """
Why this step and not another:""",

    "choice_between_3":
    "    it beat: ",

    "choice_between_4":
    "    the two candidates are level on every key, and the order between them is arbitrary.",

    "choice_between_5":
    "    decided by the key ",

    "choice_between_6":
    " against ",

    "resolvent_added":
    """
Adding the resolvent to the KB:""",

    "kb_after_step":
    "The KB at the end of the step",

    "step_limit_reached_1":
    """
Reached {max_resolution_steps} Resolution steps.""",

    "step_limit_reached_2":
    "No contradiction was found, but the search is not exhausted either.",

    "redundancy_check_header_1":
    "Checking whether the parent has become redundant",

    "redundancy_check_header_2":
    "Checking whether either of the two parents has become redundant",

    "no_parent_redundant_1":
    """
The parent has not become redundant.""",

    "no_parent_redundant_2":
    """
Neither of the two parents has become redundant.""",

    "no_parent_redundant_3":
    "So nothing is deleted.",

    "parent_is_redundant_1":
    """
The new resolvent:""",

    "parent_is_redundant_2":
    """
is stronger than the parent:""",

    "parent_is_redundant_3":
    """
Every state satisfying the resolvent satisfies the parent as well.""",

    "parent_is_redundant_4":
    "So the parent adds no further information.",

    "parent_is_redundant_5":
    """
Deleting from the KB:""",

    "unit_queue_opened_1":
    "Simplifying by one-literal clauses",

    "unit_queue_opened_2":
    """
Every one-literal clause joins a queue.""",

    "unit_queue_opened_3":
    "Each of them in turn goes over the KB: it cancels its complementary",

    "unit_queue_opened_4":
    "literal in every clause holding it, leaving the rest;",

    "unit_queue_opened_5":
    "and it deletes a clause that already holds its own literal.",

    "unit_queue_opened_6":
    "All of it without any substitution -- otherwise it is skipped.",

    "unit_queue_opened_7":
    """
The queue is empty: there is no one-literal clause at the moment.""",

    "unit_queue_opened_8":
    """
The queue to begin with:""",

    "unit_joined_queue":
    """
The resolvent has one literal, so it joins the simplification queue:""",

    "unit_sweep_header":
    """
Simplification by one-literal clauses:""",

    "unit_simplified_1":
    "  cancels a literal in:",

    "unit_simplified_2":
    "  No substitution is needed, so it is replaced by what is left:",

    "unit_makes_redundant_1":
    "  appears as it stands in:",

    "unit_makes_redundant_2":
    "  That clause no longer adds anything, so it is deleted.",

    "unit_empty_clause_1":
    "  cancels the only literal in:",

    "unit_empty_clause_2":
    "  Nothing is left -- we have the empty clause □.",

    "unit_sweep_nothing":
    """
Simplification by single literals: there is nothing to simplify.""",

    "saturation_header_1":
    "Why can it not go on?",

    "saturation_header_2":
    """
We go over the final KB twice:""",

    "saturation_header_3":
    "first deleting everything redundant in it,",

    "saturation_header_4":
    "then seeing what every remaining pair is capable of.",

    "full_redundancy_header_1":
    "A full redundancy check over the {size} clauses",

    "full_redundancy_header_2":
    """
During the search only the parents of each step were checked.""",

    "full_redundancy_header_3":
    "Here every clause is checked against all the others.",

    "clause_is_redundant_1":
    "is subsumed by:",

    "clause_is_redundant_2":
    "Everything it says has been said already, so it is deleted.",

    "nothing_redundant":
    """
No clause is redundant -- they all stay.""",

    "reduced_kb":
    "The KB after the redundancy check",

    "account_header_1":
    "Every possible pair: {pairs} pairs out of {size} clauses",

    "account_header_2":
    """
For each pair -- what it would give, and why that adds nothing.""",

    "pair_yields_nothing_1":
    """
C{first} × C{second}: there are complementary literals, but they cannot be unified.""",

    "pair_yields_nothing_2":
    """
C{first} × C{second}: there is no complementary pair of literals.""",

    "factor_yields_nothing":
    """
factoring C{index}: there are no two literals of the same sign that can be merged.""",

    "factor_result":
    """
factoring C{index}: """,

    "factoring_is_off":
    """
Factoring is off (USE_FACTORING), so it is not checked here.""",

    "equality_rule_is_off":
    """
There is no inference rule for equality (EQUALITY_RULE), so it is not checked here.""",

    "no_paramodulants":
    """
There is no equation that can be substituted into any clause.""",

    "account_conclusion_1":
    "{new_clauses} new clauses were found -- the search should have gone on.",

    "account_conclusion_2":
    "No possibility yields a new clause,",

    "account_conclusion_3":
    "so the focused KB is saturated: there is no way to reach □.",

    "account_conclusion_4":
    """
Note: this holds for the focused KB only.""",

    "account_conclusion_5":
    "The substitution was a guess, and all that has emerged is that the guess was not enough --",

    "account_conclusion_6":
    "nothing can be learned here about the question itself,",

    "account_conclusion_7":
    "so we go on to the general Resolution.",

    "account_conclusion_8":
    "so the KB is saturated: there is no way to reach □.",

    "account_conclusion_9":
    """
Note: this says that this solver found no contradiction,""",

    "account_conclusion_10":
    "not that the conclusion necessarily does not follow.",

    "focus_header_1":
    "Focusing on the witness {witness}",

    "focus_header_2":
    """
An existential witness named {witness} was found.""",

    "focus_header_3":
    "We try this substitution first:",

    "focus_skipped_many_witnesses_1":
    "Skipping the focusing stage",

    "focus_skipped_many_witnesses_2":
    """
Skolemization invented more than one witness:""",

    "focus_skipped_many_witnesses_3":
    """
A universal variable may refer to any of them,""",

    "focus_skipped_many_witnesses_4":
    "so there is no reason to prefer the first.",

    "focus_skipped_many_witnesses_5":
    "Going straight on to the general Resolution.",

    "focus_keeps_axioms_1":
    """
The relation axioms stay general, without the substitution:""",

    "focus_keeps_axioms_2":
    "an axiom like ",

    "focus_keeps_axioms_3":
    " says the relation is symmetric,",

    "focus_keeps_axioms_4":
    "while ",

    "focus_keeps_axioms_5":
    " says only that it is symmetric about ",

    "focus_keeps_axioms_6":
    "which is precisely what declaring it symmetric was meant to prevent.",

    "focus_clause_kept":
    "stays general:",

    "focus_clause_1":
    "before:",

    "focus_clause_2":
    "after:",

    "focused_kb":
    "The KB after focusing on {witness}",

    "countermodel_header":
    "A counter-model",

    "countermodel_intro_1":
    """
The search saturated without a contradiction, so the clause set is""",

    "countermodel_intro_2":
    "satisfiable -- and here is a model of it. It satisfies every surviving",

    "countermodel_intro_3":
    "clause, and so the assumptions and the negated conclusion: a counter-model.",

    "countermodel_check":
    """
Checking the model against the original question:""",

    "countermodel_assumption_true":
    "    the assumption holds:",

    "countermodel_assumption_false":
    "    ⚠️ the assumption fails -- which should not happen:",

    "countermodel_conclusion_false":
    "    the conclusion fails:",

    "countermodel_conclusion_true":
    "    ⚠️ the conclusion holds -- which should not happen:",

    "countermodel_verdict":
    """
The assumptions hold and the conclusion does not, so it does not follow from them.""",

    "countermodel_not_found":
    """
No finite model was found up to size {largest}. Every model of these
clauses may be infinite, or a larger domain may be needed.""",

    "countermodel_refused_focused":
    """
No counter-model was built: this is the focused KB, and the substitution
in it is a guess.""",

    "countermodel_refused_support":
    """
No counter-model was built: the search ran with a set of support, so its
running dry certifies nothing.""",

    "reason_vacuous_universal":
    "vacuously: no element of the model satisfies",

    "reason_universal_holds":
    "it holds of every element of the domain.",

    "reason_universal_fails":
    "it fails for {element}.",

    "reason_witnessed":
    "witnessed by {element}.",

    "reason_no_witness":
    "no element of the model satisfies it.",

    "reason_vacuous_implication":
    "vacuously: the left-hand side does not hold here --",

    "reason_implication_holds":
    "the right-hand side holds here --",

    "reason_implication_fails":
    "the left-hand side holds but the right-hand side does not --",

    "reason_plainly":
    "that is how it comes out in the model.",

    "countermodel_gave_up_separate_witnesses":
    """
The clauses force two witnesses onto the same element -- there was no choice.""",

    "countermodel_gave_up_no_self_application":
    """
The clauses force a function to send an element to itself -- there was no choice.""",

    "countermodel_never":
    "never holds: {predicates}",

    "countermodel_always":
    "always holds: {predicates}",

    "countermodel_witnesses_header":
    """
The witnesses:""",

    "countermodel_added":
    """
What the search added:""",

    "countermodel_for_every":
    "for every {variables}:",

    "countermodel_if_then":
    "if {conditions} then {consequences}",

    "countermodel_not":
    "never {conditions}",

    "countermodel_holds":
    "always {consequences}",

    "countermodel_fact_holds":
    "{fact}",

    "countermodel_fact_not":
    "not {fact}",

    "countermodel_about":
    "about {witnesses}:",

}


# Wording chosen by something other than the call site: which step number,
# which rewrite rule fired, which verdict a candidate got.

TABLES = {

    "property_names":
    {
        "symmetric": "symmetric",
        "transitive": "transitive",
        "reflexive": "reflexive",
    },

    "step_titles":
    {
        1: "Negating the conclusion and adding it to the KB",
        2: "Removing implications",
        3: "Pushing the negations inwards",
        4: "Skolemization",
        5: "Dropping the ∀ quantifiers",
        6: "Into CNF",
        7: "The KB as clauses",
    },

    "rule_names":
    {
        rewrite.IMPLICATION: "removing an implication",
        rewrite.DOUBLE_NEGATION: "double negation",
        rewrite.DE_MORGAN_AND: "De Morgan",
        rewrite.DE_MORGAN_OR: "De Morgan",
        rewrite.NOT_FORALL: "negating a ∀",
        rewrite.NOT_EXISTS: "negating an ∃",
        rewrite.DROP_FORALL: "dropping a ∀",
        rewrite.DISTRIBUTE: "distribution",
    },

    "ranking_key_names":
    {
        "depth": "how deeply the terms nest",
        "length": "the length of the clause",
        "rule": "which inference rule",
        "assignment": "whether a substitution is needed",
        "weight": "the weight of the terms",
        "parents": "the size of the parents",
    },

    "account_verdicts":
    {
        "tautology": "the resolvent is a tautology, and so of no use",
        "in_kb": "this clause is already in the KB",
        "seen_earlier": "this clause was derived earlier",
        "implied": "a clause it came from already says this (subsumption)",
        "new": "this clause is new -- which is not supposed to happen here",
    },

}
