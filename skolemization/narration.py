"""Everything this prover says, in one place.

The core modules do not print.  They call an *event* here -- one function per
thing that happened, not one per line of output -- and this module decides how
it is worded and laid out::

    narration.resolvent_added(resolvent)

    ->  מוסיפים את ה-resolvent ל-KB:
            ¬D(x) ∨ B(x, y)

So this is the file to open to reword the commentary, to add a step, or to
translate the whole thing.  No Hebrew should exist anywhere else in the
package.  Output goes through ``say`` (output.py), which handles right-to-left
direction and honours ``config.NARRATE``.

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
from .resolution import meaningful_substitutions
from .unification import apply_substitution_literal


LINE = "=" * 70
RULE = "-" * 70
BANNER = "#" * 70


# ================================================================
# PROVER
# ================================================================

PROPERTY_NAMES = {
    "symmetric": "סימטרי",
    "transitive": "טרנזיטיבי",
    "reflexive": "רפלקסיבי",
}


def relation_axioms(
    generated_axioms
):

    """Step 0: which relation properties were declared, and what they added."""

    say(
        "\n"
        + LINE
    )

    say(
        "0. הוספת תכונות של יחסים ל-KB"
    )

    say(
        LINE
    )

    if not generated_axioms:

        say(
            "\nלא הוגדרו תכונות מיוחדות של יחסים."
        )

        return

    for (
        property_name,
        relation,
        axiom
    ) in generated_axioms:

        description = (
            PROPERTY_NAMES.get(
                property_name,
                PROPERTY_NAMES["reflexive"]
            )
        )

        say(
            f"\n{relation} הוגדר כיחס "
            f"{description}."
        )

        say(
            "מוסיפים ל-KB:"
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
        f"\nהשוויון מטופל בכלל היסק ({rule}) "
        "ולא באקסיומות:"
    )

    say(
        "אין צורך בסימטריה, בטרנזיטיביות "
        "ובאקסיומות קונגרואנציה."
    )

    say(
        "האקסיומה היחידה שנשארת היא הרפלקסיביות."
    )

    say(
        "ליטרל שכתוב "
        + ltr(
            negated_equality_str("c", "c")
        )
        + " נמחק מאליו -- הוא שקר;"
    )

    say(
        "אבל ליטרל כמו "
        + ltr(
            negated_equality_str("f(x)", "f(y)")
        )
        + ", ששני צדדיו משתווים רק אחרי הצבה,"
    )

    say(
        "נסגר מול האקסיומה הזאת:"
    )

    say(
        f"    {axiom}"
    )


def working_assumptions(
    assumptions
):

    """The assumptions the search will run on, generated axioms included."""

    say(
        "\nההנחות שאיתן נעבוד:"
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
        "\nהמסקנה:"
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
        "החיפוש הממוקד הסתיים ללא הוכחה"
    )

    say(
        LINE
    )

    say(
        f"\nהמיקוד ב-{witness} הוא heuristic בלבד."
    )

    say(
        "לכן חוזרים ל-KB המקורי "
        "ומנסים Resolution כללי."
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
        f"בדיקת כיוון {index}:  "
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
        "תוצאה סופית"
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
            "✅ שתי הגרירות הוכחו."
        )

        say(
            "לכן:"
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
        "לא הוכחו שתי הגרירות."
    )

    say(
        "לכן ה-solver לא הוכיח שקילות."
    )


def _one_direction_only(
    proved,
    unproved
):

    """Exactly one entailment went through, so there is no equivalence yet."""

    say(
        "הוכח:"
    )

    say(
        f"    {proved}"
    )

    say(
        "אבל הכיוון:"
    )

    say(
        f"    {unproved}"
    )

    say(
        "לא הוכח."
    )


# ================================================================
# PREPROCESS
# ================================================================

STEP_TITLES = {
    1: "שוללים את המסקנה ומוסיפים אותה ל-KB",
    2: "ביטול גרירות",
    3: "הכנסת השלילות פנימה",
    4: "Skolemization",
    5: "הורדת כמתי ∀",
    6: "מעבר ל-CNF",
    7: "ה-KB בצורת clauses",
}


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
        f"{STEP_TITLES[number]}"
    )

    say(
        LINE
    )


def implication_rule():

    """The rewrite rule for step 2, as a reminder before the work."""

    say(
        "\n"
        + ltr("P → Q")
        + "   הופך ל-   "
        + ltr("¬P ∨ Q")
    )


def cnf_rule():

    """The distribution rule for step 6."""

    say(
        "\n"
        + ltr("P ∨ (Q ∧ R)")
        + "  הופך ל-  "
        + ltr("(P ∨ Q) ∧ (P ∨ R)")
    )


RULE_NAMES = {
    rewrite.IMPLICATION: "ביטול גרירה",
    rewrite.DOUBLE_NEGATION: "שלילה כפולה",
    rewrite.DE_MORGAN_AND: "דה-מורגן",
    rewrite.DE_MORGAN_OR: "דה-מורגן",
    rewrite.NOT_FORALL: "שלילת כמת ∀",
    rewrite.NOT_EXISTS: "שלילת כמת ∃",
    rewrite.DROP_FORALL: "הורדת כמת ∀",
    rewrite.DISTRIBUTE: "פילוג",
}


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
            f"  {RULE_NAMES[record.rule]}:"
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
        "ה-KB בסוף השלב"
    )


def nothing_changed():

    """The step ran but left every formula exactly as it was."""

    say(
        "\nאף נוסחה לא השתנתה בשלב זה."
    )


def formula_unchanged():

    """The step ran but left *this* formula exactly as it was.

    Said rather than skipped: walking one formula through the steps, a step
    that printed nothing would look like a step that never ran.
    """

    say(
        "הנוסחה לא השתנתה בשלב זה."
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
        "לפני: ",
        formula_str(
            formula
        )
    )


def formula_after(
    formula
):

    """The same formula once the transform has run."""

    say_block(
        "אחרי: ",
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
        f"נוסחה F{index} מתוך {total}"
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
        f"{STEP_TITLES[number]}"
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
        f"7. ה-clauses של F{index}"
    )


def skolem_explanations(
    explanations
):

    """Why each ∃ became the witness it became."""

    if not explanations:

        say(
            "אין כמת קיומי לסלק."
        )

    for (
        variable,
        replacement,
        universals
    ) in explanations:

        if universals:

            say(
                ltr(f"∃{variable}")
                + " נמצא תחת "
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
                "לכן הוא עשוי להיות תלוי בהם."
            )

            say(
                "מציבים:"
            )

        else:

            say(
                ltr(f"∃{variable}")
                + " אינו תלוי "
                "במשתנה אוניברסלי."
            )

            say(
                "לכן בוחרים witness קבוע:"
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
        "KB לפני Resolution"
    )


# ================================================================
# SEARCH
# ================================================================

GENERAL_SEARCH = "Resolution כללי"


def focused_search_title(
    witness
):

    """What the focused pass calls itself, naming the witness it pinned."""

    return f"Resolution ממוקד ב-{witness}"


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
            "\nכללי ההיסק: Resolution, Factoring ו-"
            + EQUALITY_RULE_NAMES[
                config.EQUALITY_RULE
            ]
            + "."
        )

    show_kb(
        kb,
        "KB בתחילת החיפוש"
    )


def set_of_support(
    seeds
):

    """The search is restricted to steps that touch the negated conclusion."""

    say(
        "\nחיפוש עם set of support:"
    )

    say(
        "כל צעד חייב להשתמש לפחות ב-clause אחד מקבוצת התמיכה,"
    )

    say(
        "וכל תוצאה מצטרפת אליה. ההנחות לבדן עקביות,"
    )

    say(
        "ולכן שום סתירה לא יכולה לצאת מהן בלי המסקנה."
    )

    if not seeds:

        say(
            "\nקבוצת התמיכה ריקה -- אין הגבלה בפועל."
        )

        return

    say(
        "\nקבוצת התמיכה ההתחלתית -- שלילת המסקנה:"
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
            "\nאזהרה: set of support יחד עם Superposition."
        )

        say(
            "שתי ההגבלות נכונות כל אחת לחוד, אבל הן לא מתחברות --"
        )

        say(
            "כל אחת מהן חוסמת צעדים שהשנייה נשענת עליהם, וההוכחה עלולה"
        )

        say(
            "לא להימצא. זה נמדד ממש על השאלה הזאת. עדיף Paramodulation."
        )


def set_of_support_caveat():

    """A supported search ran dry, which is weaker news than saturation.

    Only inferences touching the conclusion were tried, and that is complete
    only while the assumptions are consistent.  If they are not, the conclusion
    follows from them trivially and this search could not have found it.
    """

    say(
        "\nשימו לב: החיפוש הוגבל ל-set of support,"
    )

    say(
        "כלומר נבדקו רק צעדים שנוגעים במסקנה."
    )

    say(
        "אם ההנחות עצמן סותרות זו את זו, המסקנה נובעת מהן באופן ריק --"
    )

    say(
        "וההגבלה הזאת לא היתה מוצאת את זה. כדי לבדוק, כבו את SET_OF_SUPPORT."
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
        "\nאין resolvent חדש "
        "שאפשר להוסיף."
    )

    say(
        "לא נמצאה הפסוקית הריקה □."
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
            "\nמתקבל:"
        )

        say(
            f"    {clause_str(inference.result)}"
        )

        return

    say(
        "\nמתקבל:"
    )

    say(
        f"    {clause_str(inference.before_dropping)}"
    )

    say(
        "\nליטרל מהצורה "
        + ltr(
            negated_equality_str("t", "t")
        )
        + " הוא שקר, ולכן אינו יכול לתרום דבר לפסוקית."
    )

    say(
        "מוחקים אותו, ונשאר:"
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
        "\nמשתמשים בשוויון מתוך:"
    )

    say(
        f"\nC{inference.parents[0] + 1}: "
        f"{clause_str(parents[0])}"
    )

    say(
        "\nכדי להחליף שווה בשווה בתוך:"
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
            "\nהשוויון:",
            ltr(
                str(
                    inference.literal1
                )
            )
        )

        say(
            "הליטרל שנכתב מחדש:",
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
        "\nהכיוון: מתאימים את הצד "
        + ltr(
            str(
                replacement.source
            )
        )
        + " של השוויון לאיבר בתוך הפסוקית,"
    )

    say(
        "ומציבים במקומו את הצד "
        + ltr(
            str(
                replacement.target
            )
        )
        + "."
    )

    say(
        "\nהליטרל שנכתב מחדש:",
        ltr(
            str(
                inference.literal2
            )
        )
    )

    say(
        "האיבר שהותאם, והוחלף:",
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
        "\nההחלפה עצמה:"
    )

    say(
        f"    {replacement.before}"
    )

    say(
        f"    ⟶  {replacement.after}"
    )

    say(
        "\nכך מגיעים לקונגרואנציה בלי אקסיומות: "
        "הכלל מחליף את המופע בתוך האיבר."
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
        "\nההצבה שנדרשה כדי להתאים ביניהם:"
    )

    for label, literal in (
        ("מתוך השוויון", inference.literal1),
        ("מתוך הפסוקית שנכתבת מחדש", inference.literal2)
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
                f"    {label}: אין צורך בהצבה"
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
        "\nבוחרים:"
    )

    say(
        f"\nC{inference.parents[0] + 1}: "
        f"{clause_str(parent)}"
    )

    say(
        "\nשני ליטרלים באותה פסוקית, "
        "עם אותו סימן:"
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
        "\nלאחר ההצבה הם זהים, "
        "ולכן ממזגים אותם לליטרל אחד."
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
        "\nבוחרים:"
    )

    if len(parents) == 1:

        say(
            f"\nC{inference.parents[0] + 1}: "
            f"{clause_str(parents[0])}"
        )

        say(
            "מצליבים את הפסוקית "
            "עם עותק שלה."
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
        "\nהליטרלים שניתן להצליב:"
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
        "\nההצבה הדרושה:"
    )

    if not substitutions:

        say(
            "    אין צורך בהצבה ממשית."
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
        "\nלאחר ההצבה:"
    )

    say(
        f"    {literal1}"
    )

    say(
        f"    {literal2}"
    )

    say(
        "\nהליטרלים זהים פרט לשלילה, "
        "ולכן מבטלים אותם."
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
        "KB הסופי"
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
        "\nהתקבלה הפסוקית הריקה:"
    )

    say(
        "\n                  □"
    )

    say(
        "\nנמצאה סתירה."
    )

    say(
        "ההנחות יחד עם שלילת המסקנה "
        "אינן יכולות להיות אמיתיות יחד."
    )

    say(
        "\nלכן המסקנה נובעת מן ההנחות."
    )


# What each ranking key is called, for the block that explains a choice.  The
# order of a key tuple lives in search.STRATEGY_KEY_NAMES; these are only the
# words.

RANKING_KEY_NAMES = {
    "depth": "עומק האיברים",
    "length": "אורך הפסוקית",
    "rule": "סוג כלל ההיסק",
    "assignment": "הצורך בהצבה",
    "weight": "משקל האיברים",
    "parents": "גודל ההורים",
}


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
            "\nזה היה המועמד היחיד בצעד הזה."
        )

        return

    say(
        "\nמדוע דווקא הצעד הזה:"
    )

    for other, other_key in others:

        say(
            "    מולו עמד: "
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
            "    שני המועמדים שקולים בכל המפתחות, "
            "והבחירה ביניהם שרירותית."
        )

        return

    say(
        "    הכריע המפתח "
        + ltr(
            RANKING_KEY_NAMES[
                names[index]
            ]
        )
        + ": "
        + ltr(
            f"{chosen_key[index]}"
        )
        + " מול "
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
        "\nמוסיפים את ה-resolvent ל-KB:"
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
        "KB בסוף הצעד"
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
        f"\nהגענו ל-"
        f"{config.MAX_RESOLUTION_STEPS} "
        "צעדי Resolution."
    )

    say(
        "לא נמצאה סתירה, "
        "אבל החיפוש עדיין לא מוצה."
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
            "בדיקה האם ה-parent הפך למיותר"
        )

    else:

        say(
            "בדיקה האם אחד משני ה-parents הפך למיותר"
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
            "\nה-parent לא הפך למיותר."
        )

    else:

        say(
            "\nאף אחד משני ה-parents "
            "לא הפך למיותר."
        )

    say(
        "לכן לא מוחקים דבר."
    )


def parent_is_redundant(
    resolvent,
    parent
):

    """Why a parent is being deleted: the resolvent subsumes it."""

    say(
        "\nה-resolvent החדש:"
    )

    say(
        f"    {clause_str(resolvent)}"
    )

    say(
        "\nחזק יותר מה-parent:"
    )

    say(
        f"    {clause_str(parent)}"
    )

    say(
        "\nכל מצב שמקיים את ה-resolvent "
        "ממילא מקיים גם את ה-parent."
    )

    say(
        "לכן ה-parent אינו מוסיף מידע נוסף."
    )

    say(
        "\nמוחקים מה-KB:"
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
        "סינון לפי clauses בני ליטרל אחד"
    )

    say(
        RULE
    )

    say(
        "\nכל clause בן ליטרל אחד נכנס לתור."
    )

    say(
        "בתורו, כל אחד מהם עובר על ה-KB: הוא מבטל את הליטרל"
    )

    say(
        "המשלים שלו בכל clause שמכיל אותו, ומשאיר את השאר;"
    )

    say(
        "ומוחק clause שכבר מכיל את הליטרל שלו עצמו."
    )

    say(
        "הכל בלי שום הצבה -- אחרת מדלגים."
    )

    if not queue:

        say(
            "\nהתור ריק: אין כרגע clause בן ליטרל אחד."
        )

        return

    say(
        "\nהתור ההתחלתי:"
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
        "\nה-resolvent הוא בן ליטרל אחד, ולכן נכנס לתור הסינון:"
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
        "\nצמצום לפי clauses בני ליטרל אחד:"
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
        + "  מבטל ליטרל ב:"
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
        "  ללא צורך בהצבה, ולכן מחליפים אותו במה שנשאר:"
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
        + "  מופיע כמות שהוא ב:"
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
        "  ה-clause הזה כבר לא מוסיף דבר, ולכן מוחקים אותו."
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
        + "  מבטל את הליטרל היחיד ב:"
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
        "  לא נשאר כלום -- קיבלנו את הפסוקית הריקה □."
    )


def unit_sweep_nothing():

    """The sweep ran and found nothing -- said, so the check is visible."""

    say(
        "\nצמצום לפי ליטרלים בודדים: אין מה לצמצם."
    )


# ================================================================
# WHY A SATURATED SEARCH IS FINISHED
# ================================================================

def saturation_header():

    """Opening the account of a search that ran out of moves."""

    say(
        "\n"
        + LINE
    )

    say(
        "למה אי אפשר להמשיך?"
    )

    say(
        LINE
    )

    say(
        "\nנעבור על ה-KB הסופי פעמיים:"
    )

    say(
        "קודם נמחק ממנו כל מה שמיותר,"
    )

    say(
        "ואז נראה מה כל צמד שנשאר מסוגל לתת."
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
        f"בדיקת יתירות מלאה על {size} ה-clauses"
    )

    say(
        RULE
    )

    say(
        "\nבמהלך החיפוש נבדקו רק ה-parents של כל צעד."
    )

    say(
        "כאן בודקים כל clause מול כל השאר."
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
        "נבלעת על ידי:",
        ltr(
            clause_str(
                subsumer
            )
        )
    )

    say(
        "כל מה שהיא אומרת כבר נאמר, ולכן מוחקים אותה."
    )


def nothing_redundant():

    """The sweep found nothing to delete."""

    say(
        "\nאף clause אינו מיותר -- כולם נשארים."
    )


def reduced_kb(
    kb
):

    """What the KB looks like once the redundant clauses are gone."""

    show_kb(
        kb,
        "ה-KB לאחר בדיקת היתירות"
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
        f"כל הצמדים האפשריים: {pairs} צמדים "
        f"מתוך {size} clauses"
    )

    say(
        RULE
    )

    say(
        "\nלכל צמד -- מה הוא היה נותן, ולמה זה לא מוסיף כלום."
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
            f"\nC{first} × C{second}: "
            "יש ליטרלים משלימים, אבל הם לא ניתנים לאיחוד."
        )

        return

    say(
        f"\nC{first} × C{second}: "
        "אין זוג ליטרלים משלימים."
    )


ACCOUNT_VERDICTS = {
    "tautology": "ה-resolvent הוא טאוטולוגיה, ולכן חסר תועלת",
    "in_kb": "ה-clause הזה כבר נמצא ב-KB",
    "seen_earlier": "ה-clause הזה כבר נגזר קודם",
    "implied": "ה-clause שממנו הוא נגזר כבר אומר את זה (subsumption)",
    "new": "ה-clause הזה חדש -- כאן זה לא אמור לקרות",
}


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
        + ACCOUNT_VERDICTS[
            verdict
        ]
    )


def factor_yields_nothing(
    index
):

    """No two literals of this clause can be merged."""

    say(
        f"\nfactoring של C{index}: "
        "אין שני ליטרלים מאותו סימן שניתן לאחד."
    )


def factor_result(
    index,
    factor,
    verdict
):

    """A factor this clause still has, and why it changes nothing."""

    say(
        f"\nfactoring של C{index}: "
        + ltr(
            clause_str(
                factor
            )
        )
    )

    say(
        "    "
        + ACCOUNT_VERDICTS[
            verdict
        ]
    )


def factoring_is_off():

    """Factoring was not part of this search, so it is not part of the account."""

    say(
        "\nה-factoring כבוי (USE_FACTORING), ולכן לא נבדק כאן."
    )


def equality_rule_is_off():

    """No equality rule ran, so the account does not pretend otherwise."""

    say(
        "\nאין כלל היסק לשוויון (EQUALITY_RULE), ולכן לא נבדק כאן."
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
        + ACCOUNT_VERDICTS[
            verdict
        ]
    )


def no_paramodulants():

    """The equality rule ran but has nothing left to rewrite."""

    say(
        "\nאין שוויון שאפשר להציב באף clause."
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
            f"נמצאו {new_clauses} clauses חדשים -- "
            "החיפוש היה אמור להמשיך."
        )

        say(
            RULE
        )

        return

    say(
        "אף אפשרות לא נותנת clause חדש,"
    )

    if focused:

        say(
            "ולכן ה-KB הממוקד רווי: אין דרך להגיע ל-□."
        )

        say(
            RULE
        )

        say(
            "\nשימו לב: זה נכון ל-KB הממוקד בלבד."
        )

        say(
            "ההצבה היתה ניחוש, וכל מה שהתברר הוא שהניחוש לא הספיק --"
        )

        say(
            "על השאלה עצמה אי אפשר ללמוד מכאן דבר,"
        )

        say(
            "ולכן ממשיכים ל-Resolution הכללי."
        )

        return

    say(
        "ולכן ה-KB רווי: אין דרך להגיע ל-□."
    )

    say(
        RULE
    )

    say(
        "\nשימו לב: זה אומר שהסולבר הזה לא מצא סתירה,"
    )

    say(
        "לא שהמסקנה בהכרח אינה נובעת."
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
        f"שלב מיקוד ב-witness {witness}"
    )

    say(
        LINE
    )

    say(
        f"\nנמצא witness קיומי בשם {witness}."
    )

    say(
        "ננסה תחילה את ההצבה:"
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
        "מדלגים על שלב המיקוד"
    )

    say(
        LINE
    )

    say(
        "\nה-Skolemization יצרה יותר מ-witness אחד:"
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
        "\nמשתנה אוניברסלי יכול להתייחס לכל אחד מהם,"
    )

    say(
        "ולכן אין סיבה להעדיף דווקא את הראשון."
    )

    say(
        "ממשיכים ישר ל-Resolution הכללי."
    )


def focus_keeps_axioms():

    """The relation axioms are staying general, and why."""

    say(
        "\nהאקסיומות של היחסים נשארות כלליות, בלי ההצבה:"
    )

    say(
        "אקסיומה כמו "
        + ltr("¬Eq(x,y) ∨ Eq(y,x)")
        + " אומרת שהיחס סימטרי,"
    )

    say(
        "ואילו "
        + ltr("¬Eq(c,y) ∨ Eq(y,c)")
        + " אומרת רק שהוא סימטרי ביחס ל-"
        + ltr("c")
        + " --"
    )

    say(
        "כלומר בדיוק מה שהוספנו אותה כדי שלא יקרה."
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
        "נשארת כללית:",
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
        "לפני:",
        ltr(
            clause_str(
                before
            )
        )
    )

    say(
        "אחרי:",
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
        f"KB לאחר המיקוד ב-{witness}"
    )
