from __future__ import annotations
# type: ignore
import toga, toga.style
from typing import Dict, Iterable
import re
import uuid
from collections import defaultdict
LINE_SYNTAX = re.compile(r'^( *)([a-zA-Z_\?]+:) *?([a-zA-Z0-9_\? \'\"]+|) *$')


class LineReader:
    def __init__(self, lines):
        self._lines = lines
        self._line_index = 0

    @property
    def current_line_number(self):
        return self._line_index + 1

    def get_current_line(self) -> str:
        if self._line_index >= len(self._lines):
            return None

        return self._lines[self._line_index]
    
    def peek_next_line(self) -> str:
        if self._line_index+1 >= len(self._lines):
            return None

        return self._lines[self._line_index+1]



    def next(self):
        self._line_index += 1

class IteratorPlusOne:
    def __init__(self, it: Iterable):
        self._it = it
        self._go_back = False
        self._line_count = 1

    def go_back(self):
        self._go_back = True

    @property
    def line_count(self):
        return self._line_count

    def __next__(self):
        if self._go_back:
            self._go_back = False
            return self._current_value

        self._line_count += 1
        self._current_value = next(self._it)
        return self._current_value

def extract_line_parts(line):
    match = LINE_SYNTAX.match(line)
    if not match:
        raise Exception(f'Invalid syntax: {line}!')

    indentation, key, value = match.groups()
    indentation_count = indentation.count(' ')
    key = key.rstrip(':')
    value = value.strip(' ').strip('"').strip("'")

    return indentation_count, key, value

def load_widget_from_string(string: str) -> toga.Widget:
    lines = LineReader([x for x in string.split('\n') if len(x) > 0])

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
                    children.append(_return_widget_instance(current_widget_name, current_widget_attributes))

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
                returned_initial_attributes, returned_children, returned_attributes, negative_jump = workie()
                
                if current_widget_attribute != None:
                    current_widget_attributes[current_widget_attribute] = returned_attributes
                    current_widget_attribute = None
                else:
                    current_widget_attributes.update(returned_attributes)

                if returned_initial_attributes != {}:
                    children.append(_return_widget_with_children(current_key, initial_attributes, returned_children))
                    current_widget_name = None
                    current_widget_attributes = {}
                    current_widget_attribute = None
                    returned_children = []
                

                for child in returned_children:
                    children.append(child)

                if negative_jump < 0:
                    if current_widget_name:
                        children.append(_return_widget_instance(current_widget_name, current_widget_attributes))
                    else:
                        raise NotImplementedError()
                    return {}, children, {}, 0
                
                next_line = lines.peek_next_line()
                next_indentation = current_indentation
                if next_line != None:
                    next_indentation, *_ = extract_line_parts(next_line)

                if not next_line or (next_indentation - current_indentation) < 0:
                    if not current_widget_name:
                        return initial_attributes, children, current_widget_attributes, next_indentation - current_indentation

                    widget = _return_widget_instance(current_widget_name, current_widget_attributes)
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
            children.append(_return_widget_instance(current_widget_name, current_widget_attributes))
            current_widget_name = None
            current_widget_attributes = {}

        return initial_attributes, children, current_widget_attributes, 0

    res = workie()
    return res[1][0] if type(res) is tuple else res


def _return_widget_instance(widget_type_name, widget_type_attributes) -> toga.Widget:
    if 'style' in widget_type_attributes:
        widget_type_attributes['style'] = toga.style.Pack(**widget_type_attributes['style'])
    widget = getattr(toga, widget_type_name)(**widget_type_attributes)
    return widget
def _return_widget_with_children(widget_type_name, widget_type_attributes, child_widgets: list[toga.Widget]):
    widget = _return_widget_instance(widget_type_name, widget_type_attributes) #getattr(toga, widget_type_name)(**widget_type_attributes)
    for child in child_widgets:
        widget.add(child)

    return widget

def _load_widget_from_string(string: str) -> toga.Widget:
    def _parse_content(content: IteratorPlusOne, parent_indentation_count, depth=0) -> toga.Widget:
        line = None

        initial_indentation_count = None
        
        current_widget_type_name = None
        current_widget_type_attributes: Dict[str, str] = {}
        current_widget_type_attribute_key = None
        children = []


        while True:
            try:
                line = next(content)
            except StopIteration:
                if current_widget_type_name:
                    if parent_indentation_count == 0:
                        return [_return_widget_with_children(
                            current_widget_type_name, 
                            current_widget_type_attributes, 
                            children)], False
                    else:
                        widget = _return_widget_instance(current_widget_type_name, current_widget_type_attributes)
                        children.append(widget)
                        return children, False
                else:
                    return current_widget_type_attributes, False, False

            match = LINE_SYNTAX.match(line)
            if not match:
                raise Exception(f'Invalid syntax: {line}!')

            indentation, key, value = match.groups()
            indentation_count = indentation.count(' ')
            key = key.rstrip(':')
            value = value.strip(' ').strip('"').strip("'")

            if not initial_indentation_count:
                initial_indentation_count = indentation_count

            is_widget = key[0].istitle()
            if is_widget:
                if indentation_count > parent_indentation_count:
                    pass # Worked content.go_back()
                    v = _parse_content(content, indentation_count, depth + 1)
                    additional_children, should_go_back = _parse_content(content, indentation_count, depth + 1)

                    for child in additional_children:
                        children.append(child)

                    if initial_indentation_count < indentation_count:
                        if current_widget_type_name != None:
                            return [_return_widget_with_children(
                                current_widget_type_name, 
                                current_widget_type_attributes, 
                                children)], True

                        return additional_children, False

                    if should_go_back:
                        content.go_back()
                elif indentation_count < parent_indentation_count:
                    if current_widget_type_name != None:
                        return [_return_widget_with_children(
                            current_widget_type_name, 
                            current_widget_type_attributes, 
                            children)], True
                    else:
                        return current_widget_type_attributes, True
                else:
                    if current_widget_type_name != None:
                        widget = _return_widget_instance(current_widget_type_name, current_widget_type_attributes)
                        children.append(widget)

                    current_widget_type_name = key
            else:
                last_parameter = False
                if indentation_count > parent_indentation_count and current_widget_type_attributes:
                    content.go_back()
                    attributes, should_go_back, last_parameter = _parse_content(content, indentation_count, depth + 1)

                    if not last_parameter:
                        current_widget_type_attributes[current_widget_type_attribute_key] = attributes
                        current_widget_type_attribute_key = None
                    else:
                        current_widget_type_attributes.update(attributes) 

                    if key in attributes and value in attributes[key]:
                        last_parameter = True
                        return current_widget_type_attributes, True, last_parameter

                #elif indentation_count < initial_indentation_count:
                #    return current_widget_type_attributes, True
                
                #TODO: How do we handle recursive 
                if not last_parameter:
                    current_widget_type_attributes[key] = value
                    current_widget_type_attribute_key = key

    line_count = count(x for x in string.split('\n') if len(x) > 0)
    lines = IteratorPlusOne(iter(x for x in string.split('\n') if len(x) > 0))
    return _parse_content(lines, 0)[0][0]

