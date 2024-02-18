![](https://github.com/tomplast/togax_wil/actions/workflows/python-tests.yml/badge.svg?branch=dev) 

Load Toga widgets from YAML like format

Usage example:
```
from togax_wil import load_widget_from_string
load_widget_from_string("""
Box:
    id: "box1"
    Button:
        id: "button1"
""")

```

There is also an breadcrumb accessor for easier access of the widget tree:
```
from togax_wil import load_widget_from_string, BreadcrumbAccessor
widget = load_widget_from_string("""
Box:
    id: "box1"
    Button:
        id: "button1"
""")

accessor = BreadcrumbAccessor(widget)
button = accessor['button1']
```

It's also possible to specify event handlers directly:

```
def button_handler(widget):
    print('hello world')

from togax_wil import load_widget_from_string
widget = load_widget_from_string("""
Box:
    id: "box1"
    Button:
        id: "button1"
        on_press: button_handler
""")
```

