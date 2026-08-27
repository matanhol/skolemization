"""Every word the prover says, in Hebrew.

The layout lives in narration.py -- the banners, the indentation, which
bindings are worth printing.  This module holds only the wording, so a
second language is a second table rather than a second narrator, and the
two cannot drift apart without phrases/__init__.py noticing at import.

Keys are named after the event that says them.  A value with {braces} is a
str.format template; the names in it are the keyword arguments narration.py
passes to phrase().
"""

from .. import rewrite


DIRECTION = "rtl"


PHRASES = {
    "relation_axioms_1":
    "0. הוספת תכונות של יחסים ל-KB",

    "relation_axioms_2":
    """
לא הוגדרו תכונות מיוחדות של יחסים.""",

    "relation_axioms_3":
    """
{relation} הוגדר כיחס {description}.""",

    "relation_axioms_4":
    "מוסיפים ל-KB:",

    "reflexivity_for_equality_1":
    """
השוויון מטופל בכלל היסק ({rule}) ולא באקסיומות:""",

    "reflexivity_for_equality_2":
    "אין צורך בסימטריה, בטרנזיטיביות ובאקסיומות קונגרואנציה.",

    "reflexivity_for_equality_3":
    "האקסיומה היחידה שנשארת היא הרפלקסיביות.",

    "reflexivity_for_equality_4":
    "ליטרל שכתוב ",

    "reflexivity_for_equality_5":
    " נמחק מאליו -- הוא שקר;",

    "reflexivity_for_equality_6":
    "אבל ליטרל כמו ",

    "reflexivity_for_equality_7":
    ", ששני צדדיו משתווים רק אחרי הצבה,",

    "reflexivity_for_equality_8":
    "נסגר מול האקסיומה הזאת:",

    "working_assumptions":
    """
ההנחות שאיתן נעבוד:""",

    "conclusion":
    """
המסקנה:""",

    "focused_search_failed_1":
    "החיפוש הממוקד הסתיים ללא הוכחה",

    "focused_search_failed_2":
    """
המיקוד ב-{witness} הוא heuristic בלבד.""",

    "focused_search_failed_3":
    "לכן חוזרים ל-KB המקורי ומנסים Resolution כללי.",

    "equivalence_direction":
    "בדיקת כיוון {index}:  ",

    "equivalence_verdict_1":
    "תוצאה סופית",

    "equivalence_verdict_2":
    "✅ שתי הגרירות הוכחו.",

    "equivalence_verdict_3":
    "לכן:",

    "equivalence_verdict_4":
    "לא הוכחו שתי הגרירות.",

    "equivalence_verdict_5":
    "לכן ה-solver לא הוכיח שקילות.",

    "_one_direction_only_1":
    "הוכח:",

    "_one_direction_only_2":
    "אבל הכיוון:",

    "_one_direction_only_3":
    "לא הוכח.",

    "implication_rule":
    "   הופך ל-   ",

    "cnf_rule":
    "  הופך ל-  ",

    "step_kb":
    "ה-KB בסוף השלב",

    "nothing_changed":
    """
אף נוסחה לא השתנתה בשלב זה.""",

    "formula_unchanged":
    "הנוסחה לא השתנתה בשלב זה.",

    "formula_state_before":
    "לפני: ",

    "formula_after":
    "אחרי: ",

    "walk_header":
    "נוסחה F{index} מתוך {total}",

    "walk_clauses":
    "7. ה-clauses של F{index}",

    "skolem_explanations_1":
    "אין כמת קיומי לסלק.",

    "skolem_explanations_2":
    " נמצא תחת ",

    "skolem_explanations_3":
    "לכן הוא עשוי להיות תלוי בהם.",

    "skolem_explanations_4":
    "מציבים:",

    "skolem_explanations_5":
    " אינו תלוי במשתנה אוניברסלי.",

    "skolem_explanations_6":
    "לכן בוחרים witness קבוע:",

    "clause_kb":
    "KB לפני Resolution",

    "general_search":
    "Resolution כללי",

    "focused_search_title":
    "Resolution ממוקד ב-{witness}",

    "search_header_1":
    """
כללי ההיסק: Resolution, Factoring ו-""",

    "search_header_2":
    "KB בתחילת החיפוש",

    "set_of_support_1":
    """
חיפוש עם set of support:""",

    "set_of_support_2":
    "כל צעד חייב להשתמש לפחות ב-clause אחד מקבוצת התמיכה,",

    "set_of_support_3":
    "וכל תוצאה מצטרפת אליה. ההנחות לבדן עקביות,",

    "set_of_support_4":
    "ולכן שום סתירה לא יכולה לצאת מהן בלי המסקנה.",

    "set_of_support_5":
    """
קבוצת התמיכה ריקה -- אין הגבלה בפועל.""",

    "set_of_support_6":
    """
קבוצת התמיכה ההתחלתית -- שלילת המסקנה:""",

    "set_of_support_7":
    """
אזהרה: set of support יחד עם Superposition.""",

    "set_of_support_8":
    "שתי ההגבלות נכונות כל אחת לחוד, אבל הן לא מתחברות --",

    "set_of_support_9":
    "כל אחת מהן חוסמת צעדים שהשנייה נשענת עליהם, וההוכחה עלולה",

    "set_of_support_10":
    "לא להימצא. זה נמדד ממש על השאלה הזאת. עדיף Paramodulation.",

    "set_of_support_caveat_1":
    """
שימו לב: החיפוש הוגבל ל-set of support,""",

    "set_of_support_caveat_2":
    "כלומר נבדקו רק צעדים שנוגעים במסקנה.",

    "set_of_support_caveat_3":
    "אם ההנחות עצמן סותרות זו את זו, המסקנה נובעת מהן באופן ריק --",

    "set_of_support_caveat_4":
    "וההגבלה הזאת לא היתה מוצאת את זה. כדי לבדוק, כבו את SET_OF_SUPPORT.",

    "saturated_1":
    """
אין resolvent חדש שאפשר להוסיף.""",

    "saturated_2":
    "לא נמצאה הפסוקית הריקה □.",

    "step_result_1":
    """
מתקבל:""",

    "step_result_2":
    """
מתקבל:""",

    "step_result_3":
    """
ליטרל מהצורה """,

    "step_result_4":
    " הוא שקר, ולכן אינו יכול לתרום דבר לפסוקית.",

    "step_result_5":
    "מוחקים אותו, ונשאר:",

    "paramodulation_step_1":
    """
משתמשים בשוויון מתוך:""",

    "paramodulation_step_2":
    """
כדי להחליף שווה בשווה בתוך:""",

    "paramodulation_step_3":
    """
השוויון:""",

    "paramodulation_step_4":
    "הליטרל שנכתב מחדש:",

    "paramodulation_step_5":
    """
הכיוון: מתאימים את הצד """,

    "paramodulation_step_6":
    " של השוויון לאיבר בתוך הפסוקית,",

    "paramodulation_step_7":
    "ומציבים במקומו את הצד ",

    "paramodulation_step_8":
    """
הליטרל שנכתב מחדש:""",

    "paramodulation_step_9":
    "האיבר שהותאם, והוחלף:",

    "paramodulation_step_10":
    """
ההחלפה עצמה:""",

    "paramodulation_step_11":
    """
כך מגיעים לקונגרואנציה בלי אקסיומות: הכלל מחליף את המופע בתוך האיבר.""",

    "paramodulation_bindings_1":
    """
ההצבה שנדרשה כדי להתאים ביניהם:""",

    "paramodulation_bindings_2":
    "מתוך השוויון",

    "paramodulation_bindings_3":
    "מתוך הפסוקית שנכתבת מחדש",

    "paramodulation_bindings_4":
    "    {label}: אין צורך בהצבה",

    "factoring_step_1":
    """
בוחרים:""",

    "factoring_step_2":
    """
שני ליטרלים באותה פסוקית, עם אותו סימן:""",

    "factoring_step_3":
    """
לאחר ההצבה הם זהים, ולכן ממזגים אותם לליטרל אחד.""",

    "resolution_step_1":
    """
בוחרים:""",

    "resolution_step_2":
    "מצליבים את הפסוקית עם עותק שלה.",

    "resolution_step_3":
    """
הליטרלים שניתן להצליב:""",

    "substitution_used_1":
    """
ההצבה הדרושה:""",

    "substitution_used_2":
    "    אין צורך בהצבה ממשית.",

    "after_substitution_1":
    """
לאחר ההצבה:""",

    "after_substitution_2":
    """
הליטרלים זהים פרט לשלילה, ולכן מבטלים אותם.""",

    "empty_clause_1":
    "KB הסופי",

    "empty_clause_2":
    """
התקבלה הפסוקית הריקה:""",

    "empty_clause_3":
    """
נמצאה סתירה.""",

    "empty_clause_4":
    "ההנחות יחד עם שלילת המסקנה אינן יכולות להיות אמיתיות יחד.",

    "empty_clause_5":
    """
לכן המסקנה נובעת מן ההנחות.""",

    "choice_between_1":
    """
זה היה המועמד היחיד בצעד הזה.""",

    "choice_between_2":
    """
מדוע דווקא הצעד הזה:""",

    "choice_between_3":
    "    מולו עמד: ",

    "choice_between_4":
    "    שני המועמדים שקולים בכל המפתחות, והבחירה ביניהם שרירותית.",

    "choice_between_5":
    "    הכריע המפתח ",

    "choice_between_6":
    " מול ",

    "resolvent_added":
    """
מוסיפים את ה-resolvent ל-KB:""",

    "kb_after_step":
    "KB בסוף הצעד",

    "step_limit_reached_1":
    """
הגענו ל-{max_resolution_steps} צעדי Resolution.""",

    "step_limit_reached_2":
    "לא נמצאה סתירה, אבל החיפוש עדיין לא מוצה.",

    "redundancy_check_header_1":
    "בדיקה האם ה-parent הפך למיותר",

    "redundancy_check_header_2":
    "בדיקה האם אחד משני ה-parents הפך למיותר",

    "no_parent_redundant_1":
    """
ה-parent לא הפך למיותר.""",

    "no_parent_redundant_2":
    """
אף אחד משני ה-parents לא הפך למיותר.""",

    "no_parent_redundant_3":
    "לכן לא מוחקים דבר.",

    "parent_is_redundant_1":
    """
ה-resolvent החדש:""",

    "parent_is_redundant_2":
    """
חזק יותר מה-parent:""",

    "parent_is_redundant_3":
    """
כל מצב שמקיים את ה-resolvent ממילא מקיים גם את ה-parent.""",

    "parent_is_redundant_4":
    "לכן ה-parent אינו מוסיף מידע נוסף.",

    "parent_is_redundant_5":
    """
מוחקים מה-KB:""",

    "unit_queue_opened_1":
    "סינון לפי clauses בני ליטרל אחד",

    "unit_queue_opened_2":
    """
כל clause בן ליטרל אחד נכנס לתור.""",

    "unit_queue_opened_3":
    "בתורו, כל אחד מהם עובר על ה-KB: הוא מבטל את הליטרל",

    "unit_queue_opened_4":
    "המשלים שלו בכל clause שמכיל אותו, ומשאיר את השאר;",

    "unit_queue_opened_5":
    "ומוחק clause שכבר מכיל את הליטרל שלו עצמו.",

    "unit_queue_opened_6":
    "הכל בלי שום הצבה -- אחרת מדלגים.",

    "unit_queue_opened_7":
    """
התור ריק: אין כרגע clause בן ליטרל אחד.""",

    "unit_queue_opened_8":
    """
התור ההתחלתי:""",

    "unit_joined_queue":
    """
ה-resolvent הוא בן ליטרל אחד, ולכן נכנס לתור הסינון:""",

    "unit_sweep_header":
    """
צמצום לפי clauses בני ליטרל אחד:""",

    "unit_simplified_1":
    "  מבטל ליטרל ב:",

    "unit_simplified_2":
    "  ללא צורך בהצבה, ולכן מחליפים אותו במה שנשאר:",

    "unit_makes_redundant_1":
    "  מופיע כמות שהוא ב:",

    "unit_makes_redundant_2":
    "  ה-clause הזה כבר לא מוסיף דבר, ולכן מוחקים אותו.",

    "unit_empty_clause_1":
    "  מבטל את הליטרל היחיד ב:",

    "unit_empty_clause_2":
    "  לא נשאר כלום -- קיבלנו את הפסוקית הריקה □.",

    "unit_sweep_nothing":
    """
צמצום לפי ליטרלים בודדים: אין מה לצמצם.""",

    "saturation_header_1":
    "למה אי אפשר להמשיך?",

    "saturation_header_2":
    """
נעבור על ה-KB הסופי פעמיים:""",

    "saturation_header_3":
    "קודם נמחק ממנו כל מה שמיותר,",

    "saturation_header_4":
    "ואז נראה מה כל צמד שנשאר מסוגל לתת.",

    "full_redundancy_header_1":
    "בדיקת יתירות מלאה על {size} ה-clauses",

    "full_redundancy_header_2":
    """
במהלך החיפוש נבדקו רק ה-parents של כל צעד.""",

    "full_redundancy_header_3":
    "כאן בודקים כל clause מול כל השאר.",

    "clause_is_redundant_1":
    "נבלעת על ידי:",

    "clause_is_redundant_2":
    "כל מה שהיא אומרת כבר נאמר, ולכן מוחקים אותה.",

    "nothing_redundant":
    """
אף clause אינו מיותר -- כולם נשארים.""",

    "reduced_kb":
    "ה-KB לאחר בדיקת היתירות",

    "account_header_1":
    "כל הצמדים האפשריים: {pairs} צמדים מתוך {size} clauses",

    "account_header_2":
    """
לכל צמד -- מה הוא היה נותן, ולמה זה לא מוסיף כלום.""",

    "pair_yields_nothing_1":
    """
C{first} × C{second}: יש ליטרלים משלימים, אבל הם לא ניתנים לאיחוד.""",

    "pair_yields_nothing_2":
    """
C{first} × C{second}: אין זוג ליטרלים משלימים.""",

    "factor_yields_nothing":
    """
factoring של C{index}: אין שני ליטרלים מאותו סימן שניתן לאחד.""",

    "factor_result":
    """
factoring של C{index}: """,

    "factoring_is_off":
    """
ה-factoring כבוי (USE_FACTORING), ולכן לא נבדק כאן.""",

    "equality_rule_is_off":
    """
אין כלל היסק לשוויון (EQUALITY_RULE), ולכן לא נבדק כאן.""",

    "no_paramodulants":
    """
אין שוויון שאפשר להציב באף clause.""",

    "account_conclusion_1":
    "נמצאו {new_clauses} clauses חדשים -- החיפוש היה אמור להמשיך.",

    "account_conclusion_2":
    "אף אפשרות לא נותנת clause חדש,",

    "account_conclusion_3":
    "ולכן ה-KB הממוקד רווי: אין דרך להגיע ל-□.",

    "account_conclusion_4":
    """
שימו לב: זה נכון ל-KB הממוקד בלבד.""",

    "account_conclusion_5":
    "ההצבה היתה ניחוש, וכל מה שהתברר הוא שהניחוש לא הספיק --",

    "account_conclusion_6":
    "על השאלה עצמה אי אפשר ללמוד מכאן דבר,",

    "account_conclusion_7":
    "ולכן ממשיכים ל-Resolution הכללי.",

    "account_conclusion_8":
    "ולכן ה-KB רווי: אין דרך להגיע ל-□.",

    "account_conclusion_9":
    """
שימו לב: זה אומר שהסולבר הזה לא מצא סתירה,""",

    "account_conclusion_10":
    "לא שהמסקנה בהכרח אינה נובעת.",

    "focus_header_1":
    "שלב מיקוד ב-witness {witness}",

    "focus_header_2":
    """
נמצא witness קיומי בשם {witness}.""",

    "focus_header_3":
    "ננסה תחילה את ההצבה:",

    "focus_skipped_many_witnesses_1":
    "מדלגים על שלב המיקוד",

    "focus_skipped_many_witnesses_2":
    """
ה-Skolemization יצרה יותר מ-witness אחד:""",

    "focus_skipped_many_witnesses_3":
    """
משתנה אוניברסלי יכול להתייחס לכל אחד מהם,""",

    "focus_skipped_many_witnesses_4":
    "ולכן אין סיבה להעדיף דווקא את הראשון.",

    "focus_skipped_many_witnesses_5":
    "ממשיכים ישר ל-Resolution הכללי.",

    "focus_keeps_axioms_1":
    """
האקסיומות של היחסים נשארות כלליות, בלי ההצבה:""",

    "focus_keeps_axioms_2":
    "אקסיומה כמו ",

    "focus_keeps_axioms_3":
    " אומרת שהיחס סימטרי,",

    "focus_keeps_axioms_4":
    "ואילו ",

    "focus_keeps_axioms_5":
    " אומרת רק שהוא סימטרי ביחס ל-",

    "focus_keeps_axioms_6":
    "כלומר בדיוק מה שהוספנו אותה כדי שלא יקרה.",

    "focus_clause_kept":
    "נשארת כללית:",

    "focus_clause_1":
    "לפני:",

    "focus_clause_2":
    "אחרי:",

    "focused_kb":
    "KB לאחר המיקוד ב-{witness}",

    "countermodel_header":
    "מודל נגדי",

    "countermodel_intro_1":
    """
החיפוש רווה בלי סתירה, ולכן קבוצת ה-clauses ספיקה -- ויש בה מודל.""",

    "countermodel_intro_2":
    "הנה מודל שמקיים את כל ה-clauses שנשארו, ולכן גם את ההנחות",

    "countermodel_intro_3":
    "ואת שלילת המסקנה. זהו מודל נגדי לטענה.",

    "countermodel_check":
    """
בדיקה של המודל מול השאלה המקורית:""",

    "countermodel_assumption_true":
    "    ההנחה מתקיימת:",

    "countermodel_assumption_false":
    "    ⚠️ ההנחה אינה מתקיימת -- וזה לא אמור לקרות:",

    "countermodel_conclusion_false":
    "    המסקנה אינה מתקיימת:",

    "countermodel_conclusion_true":
    "    ⚠️ המסקנה מתקיימת -- וזה לא אמור לקרות:",

    "countermodel_verdict":
    """
ההנחות מתקיימות והמסקנה לא, ולכן המסקנה אינה נובעת מהן.""",

    "countermodel_not_found":
    """
לא נמצא מודל סופי עד גודל {largest}. ייתכן שכל מודל של ה-clauses
האלה אינסופי, וייתכן שצריך תחום גדול יותר.""",

    "countermodel_refused_focused":
    """
לא נבנה מודל נגדי: זה ה-KB הממוקד, וההצבה בו היא ניחוש.""",

    "countermodel_refused_support":
    """
לא נבנה מודל נגדי: החיפוש רץ עם set of support, ולכן הריקנות שלו
אינה מעידה על ספיקות.""",

    "reason_vacuous_universal":
    "ריקנית: אין במודל איבר שמקיים את",

    "reason_universal_holds":
    "מתקיים עבור כל איברי התחום.",

    "reason_universal_fails":
    "לא מתקיים עבור {element}.",

    "reason_witnessed":
    "העד הוא {element}.",

    "reason_no_witness":
    "אין במודל איבר שמקיים את זה.",

    "reason_vacuous_implication":
    "ריקנית: הצד השמאלי אינו מתקיים במודל --",

    "reason_implication_holds":
    "הצד הימני מתקיים במודל --",

    "reason_implication_fails":
    "הצד השמאלי מתקיים אבל הימני לא --",

    "reason_plainly":
    "כך זה יוצא במודל.",

    "countermodel_gave_up_separate_witnesses":
    """
ה-clauses מכריחים שני witnesses להיות אותו איבר -- אין ברירה.""",

    "countermodel_gave_up_no_self_application":
    """
ה-clauses מכריחים פונקציה לשלוח איבר לעצמו -- אין ברירה.""",

    "countermodel_never":
    "לא מתקיים אף פעם: {predicates}",

    "countermodel_always":
    "מתקיים תמיד: {predicates}",

    "countermodel_witnesses_header":
    """
העדים:""",

    "countermodel_added":
    """
מה שהחיפוש הוסיף:""",

    "countermodel_for_every":
    "לכל {variables}:",

    "countermodel_if_then":
    "אם {conditions} אז {consequences}",

    "countermodel_not":
    "לא מתקיים {conditions}",

    "countermodel_holds":
    "מתקיים {consequences}",

    "countermodel_fact_holds":
    "{fact}",

    "countermodel_fact_not":
    "לא {fact}",

    "countermodel_about":
    "על {witnesses}:",

}


# Wording chosen by something other than the call site: which step number,
# which rewrite rule fired, which verdict a candidate got.

TABLES = {

    "property_names":
    {
        "symmetric": "סימטרי",
        "transitive": "טרנזיטיבי",
        "reflexive": "רפלקסיבי",
    },

    "step_titles":
    {
        1: "שוללים את המסקנה ומוסיפים אותה ל-KB",
        2: "ביטול גרירות",
        3: "הכנסת השלילות פנימה",
        4: "Skolemization",
        5: "הורדת כמתי ∀",
        6: "מעבר ל-CNF",
        7: "ה-KB בצורת clauses",
    },

    "rule_names":
    {
        rewrite.IMPLICATION: "ביטול גרירה",
        rewrite.DOUBLE_NEGATION: "שלילה כפולה",
        rewrite.DE_MORGAN_AND: "דה-מורגן",
        rewrite.DE_MORGAN_OR: "דה-מורגן",
        rewrite.NOT_FORALL: "שלילת כמת ∀",
        rewrite.NOT_EXISTS: "שלילת כמת ∃",
        rewrite.DROP_FORALL: "הורדת כמת ∀",
        rewrite.DISTRIBUTE: "פילוג",
    },

    "ranking_key_names":
    {
        "depth": "עומק האיברים",
        "length": "אורך הפסוקית",
        "rule": "סוג כלל ההיסק",
        "assignment": "הצורך בהצבה",
        "weight": "משקל האיברים",
        "parents": "גודל ההורים",
    },

    "account_verdicts":
    {
        "tautology": "ה-resolvent הוא טאוטולוגיה, ולכן חסר תועלת",
        "in_kb": "ה-clause הזה כבר נמצא ב-KB",
        "seen_earlier": "ה-clause הזה כבר נגזר קודם",
        "implied": "ה-clause שממנו הוא נגזר כבר אומר את זה (subsumption)",
        "new": "ה-clause הזה חדש -- כאן זה לא אמור לקרות",
    },

}
