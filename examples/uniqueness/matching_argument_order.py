"""לחילופין אפשר פשוט לכתוב לו את הנוסחה בצורה זהה בשני המקרים:

Eq(x,y)

במקרה הספציפי הזה זה יספיק

אבל במקרים מורכבים יותר, שהוא צריך להסיק באמצעות סימטריות, טרנזיטיביות וכו' - זה לא יעבוד
"""

from skolemization import prove

from .assumptions import ASSUMPTIONS

conclusion = (
    "exists x "
    "(P(x) and "
    "(all y (P(y) -> Eq(x,y))))"
)


if __name__ == "__main__":

    result = prove(
        ASSUMPTIONS,
        conclusion
    )
