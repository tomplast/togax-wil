import toga
from togax_wil import load_widget_from_string, BreadcrumbAccessor


def build(app):
    accessor: BreadcrumbAccessor
    def calculate(widget):
        try:
            accessor['c_box.c_input'].value = (float(accessor['f_box.f_input'].value) - 32.0) * 5.0 / 9.0
        except ValueError:
            accessor['c_box.c_input'].value = "???"

    widget = '''Box:
        id: main_box
        style:
            direction: column
            padding: 10
        Box:
            id: f_box
            style:
                direction: row
                padding: 5

            TextInput:
                id: f_input
                style:
                    flex: 1
                    padding_left: 210
            Label:
                text: 'Fahrenheit'
                style:
                    width: 100
                    padding_left: 10
                    text_align: left
        Box:
            id: c_box
            style:
                direction: row
                padding: 5

            Label:
                text: 'is equivalent to'
                style:
                    width: 200
                    padding_right: 10
                    text_align: right

            TextInput:
                id: c_input
                readonly: True

                style:
                    flex: 1


            Label:
                text: 'Celsius
                style:
                    width: 100
                    padding_left: 10
                    text_align: left

        Button:
            text: 'Calculate'
            on_press: calculate
            style:
                padding: 15'''

    widget = load_widget_from_string(widget)
    accessor = BreadcrumbAccessor(widget)
    return widget


def main():
    return toga.App("Temperature Converter", "org.beeware.toga.tutorial", startup=build)


if __name__ == "__main__":
    main().main_loop()