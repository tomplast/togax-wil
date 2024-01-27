import pytest
from togawil import BreadcrumbAccessor, load_widget_from_string
import toga


def test_load_one_level_widget_tree_from_string():
    widget_string = """
Box:"""

    widget = load_widget_from_string(widget_string)
    assert type(widget) is toga.Box


def test_load_one_level_widget_with_attributes_from_string():
    widget_string = """
Box:
    id: 'box1'
"""

    widget = load_widget_from_string(widget_string)
    assert type(widget) is toga.Box
    assert widget.id == "box1"


def test_load_two_level_widget_tree_from_string():
    widget_string = """
Box:
    id: 'box1'
    PasswordInput:
    Label:
        id: 'label1'
        text: 'Password is "password"'
    Button:
        id: 'button1'
        text: 'Authenticate'
"""

    widget = load_widget_from_string(widget_string)
    assert type(widget) is toga.Box

    assert type(widget.children[0]) is toga.PasswordInput
    assert (
        type(widget.children[1]) is toga.Label
        and widget.children[1].id == 'label1'
        and widget.children[1].text == 'Password is "password"'
    )
    assert (
        type(widget.children[2]) is toga.Button
        and widget.children[2].id == "button1"
        and widget.children[2].text == "Authenticate"
    )


def test_load_three_level_widget_tree_from_string():
    widget_string = """
Box:
    id: box1
    Box:
        id: box2
        Label:
            text: 'Am I living in a box?'
    Label:
        text: 'Am I living in a cardboard box?'
"""

    widget = load_widget_from_string(widget_string)
    assert type(widget) is toga.Box

    assert widget.id == "box1"
    assert widget.children[0].id == "box2"

    assert type(widget.children[0]) is toga.Box
    assert (
        type(widget.children[0].children[0]) is toga.Label
        and widget.children[0].children[0].text == "Am I living in a box?"
    )

    assert (
        type(widget.children[1]) is toga.Label
        and widget.children[1].text == "Am I living in a cardboard box?"
    )


def test_load_four_level_widget_tree_from_string():
    widget_string = """
Box:
    Box:
        id: 'box5'
        Box:
            Label:
                text: 'Am I living in a box?'
                style:
                    padding: '50'
    Label:
        text: 'Am I living in a cardboard box?'
"""
    widget = load_widget_from_string(widget_string)

    assert type(widget.children[0]) is toga.Box
    assert type(widget.children[0].children[0]) is toga.Box
    assert (
        type(widget.children[0].children[0].children[0]) is toga.Label
        and widget.children[0].children[0].children[0].text == "Am I living in a box?"
    )

    assert (
        type(widget.children[1]) is toga.Label
        and widget.children[1].text == "Am I living in a cardboard box?"
    )


def test_widget_tree_with_attributes():
    widget_string = """
Box:
    Label:
        text: "Am I living in a box?"
        style:
            padding: 50
    Box:
        PasswordInput:
            style:
                padding: 50
    TextInput:  
"""

    widget = load_widget_from_string(widget_string)
    assert type(widget) is toga.Box

    assert type(widget.children[0]) is toga.Label
    assert widget.children[0].text == "Am I living in a box?"
    assert widget.children[0].style.padding == (50, 50, 50, 50)

    assert type(widget.children[2]) is toga.TextInput

def test_box_ception():
    widget_string = '''
Box:
    id: "box1"
    Box:
        Box:
            Box:
                Box:
                    Box:
                        Label:
                            text: "Label"'''
    widget = load_widget_from_string(widget_string)
    assert type(widget) is toga.Box

    child = None
    for i in range(0, 5):
        child = child.children[0] if child != None else widget.children[0]
        assert type(child) is toga.Box

def test_another_thing():
    widget_string = """
Box:
    style:
        direction: row

    Box:
        style:
            direction: column
        TextInput:
            id: 'text_1'

        TextInput:

    Box:
        style:
            direction: column
        Button:
            text: 'Hello World'
"""
    widget_string = """
Box:
    style:
        direction: row

    Box:
        style:
            direction: column
        TextInput:
            id: 'text_1'

        TextInput:
"""
    widget = load_widget_from_string(widget_string)
    assert type(widget) is toga.Box
    assert widget.style.direction == 'row'
    assert len(widget.children[0].children) == 2
    assert widget.children[0].style.direction == 'column'
    assert type(widget.children[0].children[0]) is toga.TextInput 
    assert widget.children[0].children[0].id == 'text_1'

def test_yet_another_thing():
    widget_string = """
Box:
    style:
        direction: column
    Box:
        style:
            direction: row
        id: "box1"

        TextInput:
            style:
                flex: 1
        Button:
            id: "button1"
            text: 'Press me'
            style:
                width: 50
                padding_left: 5

    WebView:
        style:
            flex: 1


"""
    widget = load_widget_from_string(widget_string)
    assert type(widget) is toga.Box

def test_breadcrumb_accessor():
    widget_string = """
Box:
    style:
        direction: column
    Box:
        style:
            direction: row
        id: "box1"

        TextInput:
            style:
                flex: 1
        Button:
            id: "button1"
            text: 'Press me'
            style:
                width: 50
                padding_left: 5

    WebView:
        style:
            flex: 1


"""
    widget = load_widget_from_string(widget_string)

    accessor = BreadcrumbAccessor(widget)
    button1 = accessor['box1.button1']
    assert type(button1) is toga.Button 


def test_invalid_accessor_use():
    widget = load_widget_from_string("""
Box:
    Button:
        id: 'mybutton'
        text: "My button"
""")

    with pytest.raises(KeyError):
        BreadcrumbAccessor(widget)['button1']

def test_webview_view_url():
    widget = load_widget_from_string("""
WebView:
    url: 'http://www.example.com?q=1&x=5'
""")