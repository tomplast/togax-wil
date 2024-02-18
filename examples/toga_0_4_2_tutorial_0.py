import toga
from togax_wil import load_widget_from_string

def button_handler(widget):
    print('hello')

def build(app):
    widget_string = '''Box:
    Button:
        text: 'Hello World'
        on_press: button_handler
    style:
        padding: 50
        flex: 1'''
    widget = load_widget_from_string(widget_string)
    return widget

def main():
    return toga.App('First App', 'org.beeware.toga.tutorial', startup=build)

if __name__ == '__main__':
    main().main_loop()