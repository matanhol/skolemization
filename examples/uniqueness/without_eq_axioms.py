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
