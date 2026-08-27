
nesting_level = 4
opening_lines = []
closing_lines = []
texts_starts = []
texts_ends = []
NUM_SPACES_PER_INDENT = 4
constant_indentation = " " * 40 # calculate this number by the length of the longest line so it will not be clipped
for i in range(nesting_level):
    depth = nesting_level - i - 1
    line_start = len(constant_indentation) + i * NUM_SPACES_PER_INDENT
    arrow = "←"

    opening_line_text = "שורה פותחת טווח עומק"
    opening_line = " ".join([f"{arrow}", opening_line_text, f"{depth}"])
    len_arrow_space = len(arrow) + len(" ")
    indentation = " " * (line_start - len(opening_line) + len_arrow_space)
    indented_opening_line = indentation + opening_line
    opening_lines.append(indented_opening_line)
    texts_starts_i = []
    num_rows_start = 2
    for rownum in range(num_rows_start):
        text1 = "בלהבלה התחלה עומק"
        text2 = "שורה"
        text = text1 + " " + f"{depth}" + " " + text2 + " " + f"{rownum}"
        indentation = " " * (line_start - len(text))
        indented_text_start = indentation + text
        texts_starts_i.append(indented_text_start)
    texts_starts.append(texts_starts_i)

    texts_ends_i = []
    num_rows_end = 2
    for rownum in range(num_rows_end):
        text1 = "בלהבלה סוף עומק"
        text2 = "שורה"
        text = text1 + " " + f"{depth}" + " " + text2 + " " + f"{rownum + num_rows_start}"
        indentation = " " * (line_start - len(text))
        indented_text_end = indentation + text
        texts_ends_i.append(indented_text_end)
    texts_ends.append(texts_ends_i)
    closing_line = f"שורה סוגרת טווח עומק {depth}"
    indentation = " " * (line_start - len(closing_line))
    indented_closing_line = indentation + closing_line
    closing_lines.append(indented_closing_line)

# prints the starting of the blocks
for i in range(nesting_level):
    print(opening_lines[-(i+1)])
    for line in texts_starts[-(i+1)]:
        print(line)
    print()


# prints the endings of the blocks
for i in range(nesting_level):
    for line in texts_ends[i]:
        print(line)
    print(closing_lines[i])
    print()


