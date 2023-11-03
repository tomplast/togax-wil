from togawil import load_widget_from_string
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
    PasswordInput:
    Label:
        text: 'Password is "password"'
    Button:
        text: 'Authenticate'
"""

    widget = load_widget_from_string(widget_string)
    assert type(widget) is toga.Box

    assert type(widget.children[0]) is toga.PasswordInput
    assert (
        type(widget.children[1]) is toga.Label
        and widget.children[1].text == 'Password is "password"'
    )
    assert (
        type(widget.children[2]) is toga.Button
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
                    padding: '50

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
        text: 'Am I living in a box?'
        style:
            padding: 50

    Box:
        PasswordInput:
        style:
            padding: 50"""

    widget = load_widget_from_string(widget_string)
    assert type(widget) is toga.Box

    assert type(widget.children[0]) is toga.Label
    assert widget.children[0].text == "Am I living in a box?"
    assert widget.children[0].style.padding == (50, 50, 50, 50)


def test_box_ception():
    widget_string = '''
Box:
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
