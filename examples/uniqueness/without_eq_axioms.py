"""אותה מסקנה, בלי אף תכונה של היחס Eq

ההנחה נותנת Eq(x,y) והמסקנה מבקשת Eq(y,x), ובלי אקסיומת סימטריה
נראה היה שאין דרך לחבר ביניהם.

אבל זה לא נכון, וכדאי לעצור על זה: ההנחה היא

all x all y ((P(x) and P(y)) -> Eq(x,y))

והיא מכומתת על **שני** הארגומנטים. אפשר פשוט להציב x := y ו-y := c
ולקבל Eq(y,c) בלי שום סימטריה. אין כאן מודל נגדי -- המסקנה נובעת.

מה שהשתנה הוא סדר החיפוש, לא הלוגיקה:

תחת הדירוג הקודם ("shortest_general_first") הסולבר לא מצא את הדרך
הזאת ונגמרו לו הצעדים -- UNKNOWN.

תחת ברירת המחדל היום ("shallowest_general_first"), שמעדיפה קודם כל
איברים רדודים, הוא מוצא אותה ב-13 צעדים.

זו דוגמה טובה למה ש-UNKNOWN באמת אומר: לא "לא נובע", אלא "הסולבר הזה,
עם הדירוג הזה, לא הגיע לשם".
"""

COMMENTARY_EN = """The same conclusion, with no property of the relation Eq at all

The assumption supplies Eq(x,y) and the conclusion asks for Eq(y,x), and
without a symmetry axiom it looked as though there were no way to connect
the two.

But that is not so, and it is worth stopping on: the assumption is

all x all y ((P(x) and P(y)) -> Eq(x,y))

and it is quantified over **both** arguments. One can simply instantiate
x := y and y := c and obtain Eq(y,c) with no symmetry whatsoever. There is
no counter-model here -- the conclusion does follow.

What changed is the search order, not the logic:

under the previous ranking ("shortest_general_first") the solver did not
find that route and ran out of steps -- UNKNOWN.

under today's default ("shallowest_general_first"), which prefers shallow
terms before anything else, it finds it in 13 steps.

This is a good illustration of what UNKNOWN really says: not "does not
follow", but "this solver, with this ranking, did not get there".
"""


from skolemization import prove

from .assumptions import ASSUMPTIONS

conclusion = (
    "exists x "
    "(P(x) and "
    "(all y (P(y) -> Eq(y,x))))"
)


if __name__ == "__main__":

    result = prove(
        ASSUMPTIONS,
        conclusion
    )
