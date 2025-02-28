from functools import cache
import bpy

from .text import iter_lines, line_to_rows, draw_text

def get_panel_width(area):
    for r in area.regions:
        if r.type == "UI":
            return r.width

def draw_markdown(layout, text, row_length=40, line_spacing=0.9, alignment="LEFT"):
    def handle_paragraph(node):
        paragraph_text = ""
        for child in node.children:
            node_type = child.get_type()
            if node_type == "Paragraph":
                paragraph_text += handle_paragraph(child)
            elif node_type == "LineBreak":
                paragraph_text += "\n"
            elif node_type == "RawText":
                paragraph_text += child.children
            elif node_type == "CodeSpan":
                paragraph_text += f"'{child.children}'"
            elif node_type == "Emphasis":
                paragraph_text += handle_paragraph(child)
            elif node_type == "StrongEmphasis":
                paragraph_text += handle_paragraph(child)
        return paragraph_text

    def handle_element(
        node, layout, indent=0, ordered=False, list_index=0, list_depth=1
    ):
        node_type = node.get_type()
        if node_type == "Heading":
            draw_text(
                layout.column(),
                handle_paragraph(node),
                row_length - indent * 3,
                alignment,
            )
        elif node_type == "Paragraph":
            draw_text(
                layout.column(),
                handle_paragraph(node),
                row_length - indent * 3,
                alignment,
            )
        elif node_type == "List":
            for i, li in enumerate(node.children):
                handle_element(li, layout, indent, node.ordered, i + 1, list_depth)
        elif node_type == "ListItem":
            if indent > 0:
                factor = 0.075 * indent * (40 / row_length)
            else:
                factor = 0.01

            split = layout.split(factor=factor)
            _ = split.column()
            col = split.column()
            row = col.row(align=True)

            if ordered:
                item_text = f"{list_index}.  {handle_paragraph(node)}"
            else:
                item_text = handle_paragraph(node)
                level = list_depth % 4
                if level == 1:
                    icon = "DOT"
                elif level == 2:
                    icon = "dot_inverted.png"
                elif level == 3:
                    icon = "square.png"
                else:
                    icon = "square_inverted.png"

                # icon_value = get_icon_value(icon)
                # row.label(icon_value=icon_value)

            draw_text(row.column(), item_text, row_length - ((indent * 2) + 5))
            for list in (c for c in node.children if c.get_type() == "List"):
                handle_element(
                    list,
                    layout,
                    indent + 1,
                    list.ordered,
                    0,
                    list_depth if ordered else list_depth + 1,
                )
        elif node_type == "FencedCode":
            box = layout.box()
            split_factor = 0.085
            if node.lang == "python":
                text = "Python"
                icon = "SCRIPT"
            elif node.lang == "diff":
                text = "Changes"
                icon = "FORCE_CHARGE"
                split_factor = 0.07
            else:
                text = node.lang
                icon = "TEXT"

            box.label(text=text, icon=icon)

            code = handle_paragraph(node)
            if not code:
                return

            split = box.split(factor=split_factor * (40 / row_length))
            line_number_col = split.column()
            line_number_col.enabled = False
            code_col = split.column()
            for i, line in enumerate(code.splitlines()):
                if not line:
                    continue

                line_number_col.label(text=f"{i + 1}")
                code_row = code_col.row(align=True)
                if node.lang == "diff":
                    if (prefix := line[0]) in {"-", "+"}:
                        line = line[1:]
                        code_row.label(
                            icon=(
                                "SEQUENCE_COLOR_01"
                                if prefix == "-"
                                else "SEQUENCE_COLOR_04"
                            )
                        )
                    else:
                        code_row.label(icon="BLANK1")

                code_row.label(text=line)

    layout.scale_y = line_spacing
    document = parse_markdown(text)
    if document is None:
        return

    for i, node in enumerate(document.children):
        handle_element(node, layout)
        if i < len(document.children) - 1:
            layout.separator(factor=0.01)


@cache
def parse_markdown(text):
    try:
        import marko

        return marko.parse(text)
    except:
        return None
