"""דוגמה:

הנחות:

1. כל כלב יש בעלים והוא נאמן לו

2. מי שנאמן למישהו לא בוגד בו

3. קיים מישהו שבוגד בכולם


הצרנה:

הגדרות:

D(x): x is a dog

O(x,y): y is owner of x

F(x,y): x is loyal to y

B(x,y): x betrays on y



Assumptions:

1. all x, (D(x) -> exists y (O(x,y) and F(x,y))

2. all x all y (F(x,y) -> not B(x,y))

3. exists x, all y B(x,y)
"""

BASE = [
    "all x, D(x) -> (exists y (O(x,y) and F(x,y)))",
    "all x all y (F(x,y) -> not B(x,y))",
    "exists x, all y B(x,y)"
]


# ------------------------------------------------
# ניסוח שונה של אותן הנחות
#
# לכל כלב יש בעלים
# אם y בעלים של x אז x נאמן ל y
# כל יתר ההנחות כמו קודם
# ------------------------------------------------

OWNERSHIP_VARIANT = [
    "all x, D(x) -> (exists y O(x,y))",
    "all x all y (O(x,y) -> F(x,y))",
    "all x all y (F(x,y) -> not B(x,y))",
    "exists x, all y B(x,y)"
]
