from __future__ import annotations
import toga  # type: ignore
import toga.style  # type: ignore
from typing import Any, Optional
import re
import sys
import inspect

LINE_SYNTAX = re.compile(
    r"^( *)([a-zA-Z_\?]+:) *?([\=\.\:\/\&a-zA-Z0-9_\-\? \'\"]+|) *$"
)

TOGA_WIDGETS_CONSTRUCTOR_TYPE_HINTS: dict[str, dict[str, str]] = {}

for c in dir(toga):
    try:
        if c.startswith("_") or c[0].islower():
            continue

        annotations = next(
            x
            for x in inspect.getmembers(getattr(toga, c).__init__)
            if x[0] == "__annotations__"
        )[1]
        TOGA_WIDGETS_CONSTRUCTOR_TYPE_HINTS[c] = annotations
    except StopIteration:
        pass
    except Exception as e:
        raise Exception(
            f"An unexpected error occured while looking for constructor type hints for widget {c}!"
        ) from e


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


class BreadcrumbAccessor:
    """Access widget tree through ['child_id.child_id.child_id...']"""

    def __init__(self, widget: toga.Widget):
        self._widget = widget

    def __getitem__(self, key) -> Optional[toga.Widget]:
        current_widget = None
        current_path = ""

        for k in key.split("."):
            current_path = current_path + f"{k}."
            try:
                current_widget = next(
                    x for x in (current_widget or self._widget).children if x.id == k
                )
            except StopIteration:
                raise KeyError(
                    f"Could not find widget with id {k} in {current_widget} ({current_path.rstrip('.')})"
                )

        return current_widget


def load_widget_from_string(string: str) -> toga.Widget:
    scope: dict[str, dict[str, object]] = {"local": {}, "module": {}}
    current_frame = inspect.currentframe()
    if current_frame and current_frame.f_back:
        scope["local"] = current_frame.f_back.f_locals

    caller_filename = inspect.getframeinfo(sys._getframe(1)).filename

    try:
        for i in range(0, 100):
            frame = sys._getframe(i)
            frame_info = inspect.getframeinfo(frame)
            if (
                frame_info.filename == caller_filename
                and frame_info.function == "<module>"
            ):
                scope["module"] = frame.f_locals
                break
    except ValueError:
        pass

    lines = LineReader(
        [x for x in string.split("\n") if len(x) > 0 and len(x) != x.count(" ")]
    )

    def process_level(initial_indentation):
        current_widget_name = None
        current_widget_attributes = {}
        parent_widget_attributes = {}
        children = []

        while line := lines.get_current_line():
            _, key, value = extract_line_parts(line)

            is_widget = key[0].istitle()

            if is_widget:
                if current_widget_name != None:
                    children.append(
                        _return_widget_instance(
                            current_widget_name, current_widget_attributes, scope
                        )
                    )
                    current_widget_attributes = {}

                current_widget_name = key
            else:
                parent_widget_attributes[key] = value

            next_line = lines.peek_next_line()
            if next_line:
                lines.next()
                next_indentation, *_ = extract_line_parts(next_line)
                if next_indentation > initial_indentation:
                    (
                        returned_children,
                        returned_attributes,
                        negative_jump,
                    ) = process_level(next_indentation)

                    if len(returned_children) > 0:
                        children.extend(
                            [
                                _return_widget_with_children(
                                    current_widget_name,
                                    returned_attributes,
                                    returned_children,
                                    scope,
                                )
                            ]
                        )
                        returned_attributes = {}
                        current_widget_name = None

                    if returned_attributes != {}:
                        if is_widget:
                            current_widget_attributes |= returned_attributes
                        else:
                            parent_widget_attributes[key] = returned_attributes

                    if int(negative_jump) > 1:
                        if current_widget_name != None:
                            if parent_widget_attributes != {}:
                                children.append(
                                    _return_widget_instance(
                                        current_widget_name,
                                        current_widget_attributes,
                                        scope,
                                    )
                                )
                            else:
                                children = [
                                    _return_widget_with_children(
                                        current_widget_name,
                                        current_widget_attributes,
                                        children,
                                        scope,
                                    )
                                ]
                            current_widget_attributes = {}

                        return (
                            children,
                            parent_widget_attributes,
                            int(negative_jump) - 1,
                        )

                elif next_indentation < initial_indentation:
                    return (
                        children,
                        parent_widget_attributes,
                        (initial_indentation - next_indentation) / 4,
                    )
            else:
                lines.next()

        # We ran out of lines
        if current_widget_name != None:
            if initial_indentation > 0 and len(children) > 0:
                children.append(
                    _return_widget_instance(
                        current_widget_name, current_widget_attributes, scope
                    )
                )
                return children, parent_widget_attributes, 1

            if len(children) > 0 and initial_indentation == 0:
                raise Exception("Error! Only one root element is allowed!")

            return (
                [
                    _return_widget_instance(
                        current_widget_name, current_widget_attributes, scope
                    )
                ],
                parent_widget_attributes,
                1,
            )
        else:
            return children, parent_widget_attributes, 1

    return process_level(0)[0][0]


def _return_widget_instance(
    widget_type_name, widget_type_attributes, scope: dict[str, dict[str, object]]
) -> toga.Widget:

    for on_attribute in (x for x in widget_type_attributes if x.startswith("on_")):
        target_method = widget_type_attributes[on_attribute]
        
        if target_method in scope["local"]:
            widget_type_attributes[on_attribute] = scope["local"][target_method]
        elif target_method in scope["module"]:
            widget_type_attributes[on_attribute] = scope["module"][target_method]
        else:
            raise Exception(
                f"No handler with the name {target_method} for event {on_attribute}. Must be defined within calling method or inside current file at the top level!"
            )

    if widget_annotations := TOGA_WIDGETS_CONSTRUCTOR_TYPE_HINTS.get(widget_type_name):
        for k in widget_type_attributes:
            if not k in widget_annotations:
                continue

            if widget_annotations[k].startswith("float"):
                widget_type_attributes[k] = float(widget_type_attributes[k])
            elif widget_annotations[k].startswith("int"):
                widget_type_attributes[k] = int(widget_type_attributes[k])

    if "style" in widget_type_attributes and widget_type_attributes["style"] != "":
        widget_type_attributes["style"] = toga.style.Pack(
            **widget_type_attributes["style"]
        )
    widget = getattr(toga, widget_type_name)(**widget_type_attributes)
    return widget


def _return_widget_with_children(
    widget_type_name,
    widget_type_attributes,
    child_widgets: list[toga.Widget],
    scope: dict[str, dict[str, object]],
):
    widget = _return_widget_instance(widget_type_name, widget_type_attributes, scope)
    for child in child_widgets:
        widget.add(child)

    return widget
