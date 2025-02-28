import bpy


def iter_lines(text):
    for i, line in enumerate(text.splitlines(), start=1):
        yield line, i


def line_to_rows(line, row_length):
    font_points = bpy.context.preferences.ui_styles[0].widget.points
    row_length /= font_points / 11  # font size

    rows = []
    row = ""
    words = line.split(" ")
    for word in words:
        if len(word) > row_length:
            for char in word:
                if len(row) + len(char) + 1 > row_length:
                    rows.append(row)
                    row = char
                else:
                    row += char if row else char
        if len(row) + len(word) + 1 > row_length:
            rows.append(row)
            row = word
        else:
            row += f" {word}" if row else word

    rows.append(row)
    return rows


def draw_line(layout, line, row_length, alignment="LEFT"):
    text_rows = line_to_rows(line, row_length)
    for text_row in text_rows:
        row = layout.row()
        row.alignment = alignment
        row.label(text=text_row)


def draw_text(layout, text, row_length, alignment="LEFT"):
    for line, _ in iter_lines(text):
        draw_line(layout, line, row_length, alignment)
