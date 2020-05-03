# deditor

Python property exposing and editing utility

## Why

Traditionally, configuration files had to be saved somewhere on the hard drive
and if you wanted to change a value, you'd have to manually open the text file,
and make sure your program re-read the configuration file every time.

With *deditor*, you simply expose the variables you want as `configuration` variables
and a graphical user interface is generated to let you intuitively tweak values and
use them in your program without having to leave Python.

## How it works
1. You write your Python code as you normally would.
2. Add `DPROPERTY()` above the variables you want exposed.
   - Optionally you can add specifiers, like its range: `DPROPERTY(range=[0, 10])`
3. Run `make_html.py` to generate an HTML file for editing the values.

### Example
Here is an example of DPROPERTYs in action:
```python
from DEditor import DPROPERTY

# This will get exposed to the editor.
DPROPERTY()
attr1 = 0

# This will not be exposed.
attr2 = 0
```

## Interface options

There are two available interface options: Tkinter or HTML.
- **Tkinter** - included in Python's standard library and can be used to dynamically get the
edited values back into your Python script using the included `get_values()` function.
- **HTML** - works outside of Python only requiring a web browser to display. The values must be
saved in a middle-ground before your Python script can use them again.

## Features
These are the features currently supported or coming soon.
- [x] Class variables
- [x] Nested class variables
- [x] Default value expressions
- [x] Renaming variables
- [x] UI clamping and validation (Tkinter)
- [ ] UI clamping and validation (HTML)
- [ ] Tooltips
