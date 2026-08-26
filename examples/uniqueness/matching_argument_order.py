"""לחילופין אפשר פשוט לכתוב לו את הנוסחה בצורה זהה בשני המקרים:

Eq(x,y)

במקרה הספציפי הזה זה יספיק

אבל במקרים מורכבים יותר, שהוא צריך להסיק באמצעות סימטריות, טרנזיטיביות וכו' - זה לא יעבוד
"""

COMMENTARY_EN = """Alternatively one can simply write the formula in the same shape in both places:

Eq(x,y)

in this particular case that is enough

but in more involved cases, where the solver has to reason through symmetry, transitivity and so on - that will not work
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
