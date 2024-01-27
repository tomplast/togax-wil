Load Toga widgets from YAML like format

Usage example:
```
from togawil import load_widget_from_string
load_widget_from_string("""
Box:
    id: "box1"
    Button:
        id: "button1"
""")

```

There is also an breadcrumb accessor for easier access of the widget tree:
```
from togawil import load_widget_from_string, BreadcrumbAccessor
widget = load_widget_from_string("""
Box:
    id: "box1"
    Button:
        id: "button1"
""")

accessor = BreadcrumbAccessor(widget)
button = accessor['button1']
```

