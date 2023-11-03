from __future__ import annotations
import toga  # type: ignore
import toga.style  # type: ignore
from typing import Optional
import re


LINE_SYNTAX = re.compile(r"^( *)([a-zA-Z_\?]+:) *?([a-zA-Z0-9_\? \'\"]+|) *$")


class LineReader:
    def __init__(self, lines):
        self._lines = lines
        self._line_index = 0

    @property
    def current_line_number(self):
        return self._line_index + 1

    def get_current_line(self) -> Optional[str]:
        if self._line_index >= len(self._lines):
            return None

        return self._lines[self._line_index]

    def peek_next_line(self) -> Optional[str]:
        if self._line_index + 1 >= len(self._lines):
            return None

        return self._lines[self._line_index + 1]

    def next(self):
        self._line_index += 1


def extract_line_parts(line):
    match = LINE_SYNTAX.match(line)
    if not match:
        raise Exception(f"Invalid syntax: {line}!")

    indentation, key, value = match.groups()
    indentation_count = indentation.count(" ")
    key = key.rstrip(":")
    value = value.strip(" ").strip('"').strip("'")

    return indentation_count, key, value


def load_widget_from_string(string: str) -> toga.Widget:
    lines = LineReader([x for x in string.split("\n") if len(x) > 0])

    def workie():
        initial_attributes = {}
        current_widget_name = None
        current_widget_attributes = {}
        current_widget_attribute = None
        children = []

        while line := lines.get_current_line():
            current_indentation, current_key, current_value = extract_line_parts(line)
            is_widget = current_key[0].istitle()

            if is_widget:
                if current_widget_name:
                    children.append(
                        _return_widget_instance(
                            current_widget_name, current_widget_attributes
                        )
                    )

                if initial_attributes == {}:
                    initial_attributes = current_widget_attributes

                current_widget_name = current_key
                current_widget_attributes = {}
                current_widget_attribute = None
            else:
                current_widget_attributes[current_key] = current_value
                current_widget_attribute = current_key

            next_line = lines.peek_next_line()
            if not next_line:
                break

            next_indentation, *_ = extract_line_parts(next_line)

            if next_indentation > current_indentation:
                lines.next()
                (
                    returned_initial_attributes,
                    returned_children,
                    returned_attributes,
                    negative_jump,
                ) = workie()

                if current_widget_attribute != None:
                    current_widget_attributes[
                        current_widget_attribute
                    ] = returned_attributes
                    current_widget_attribute = None
                else:
                    current_widget_attributes.update(returned_attributes)

                if returned_initial_attributes != {}:
                    children.append(
                        _return_widget_with_children(
                            current_key, initial_attributes, returned_children
                        )
                    )
                    current_widget_name = None
                    current_widget_attributes = {}
                    current_widget_attribute = None
                    returned_children = []

                for child in returned_children:
                    children.append(child)

                if negative_jump < 0:
                    if current_widget_name:
                        children.append(
                            _return_widget_instance(
                                current_widget_name, current_widget_attributes
                            )
                        )
                    return {}, children, {}, 0

                next_line = lines.peek_next_line()
                next_indentation = current_indentation
                if next_line != None:
                    next_indentation, *_ = extract_line_parts(next_line)

                if not next_line or (next_indentation - current_indentation) < 0:
                    if not current_widget_name:
                        return (
                            initial_attributes,
                            children,
                            current_widget_attributes,
                            next_indentation - current_indentation,
                        )

                    widget = _return_widget_instance(
                        current_widget_name, current_widget_attributes
                    )
                    if not widget.can_have_children:
                        children.append(widget)
                        return initial_attributes, children, {}, 0

                    for child in children:
                        widget.add(child)

                    return initial_attributes, [widget], {}, 0

            elif next_indentation < current_indentation:
                return initial_attributes, children, current_widget_attributes, 0

            lines.next()

        if current_widget_name:
            children.append(
                _return_widget_instance(current_widget_name, current_widget_attributes)
            )
            current_widget_name = None
            current_widget_attributes = {}

        return initial_attributes, children, current_widget_attributes, 0

    res = workie()
    return res[1][0] if type(res) is tuple else res


def _return_widget_instance(widget_type_name, widget_type_attributes) -> toga.Widget:
    if "style" in widget_type_attributes:
        widget_type_attributes["style"] = toga.style.Pack(
            **widget_type_attributes["style"]
        )
    widget = getattr(toga, widget_type_name)(**widget_type_attributes)
    return widget


def _return_widget_with_children(
    widget_type_name, widget_type_attributes, child_widgets: list[toga.Widget]
):
    # getattr(toga, widget_type_name)(**widget_type_attributes)
    widget = _return_widget_instance(widget_type_name, widget_type_attributes)
    for child in child_widgets:
        widget.add(child)

    return widget
