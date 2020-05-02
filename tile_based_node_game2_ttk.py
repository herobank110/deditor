from tkinter import Tk, StringVar, IntVar, Canvas, Variable, Toplevel
from tkinter.constants import *
from tkinter.ttk import *
from tkinter import Frame
import string, itertools, ast
from math import sqrt

##try:
##    from Tkinter import *
##except ImportError:
##    from tkinter import *

class Loc(list):
    """Structure for representing coordinates, with basic arithmetic.

    Usage example:
    ```
    a = Loc([0]*3) # Make 3D Loc like (X=0, Y=0, Z=0).
    b = Loc(-20, 0, 20)
    c = a + b   # Add components of a and b.
    c += 20     # Add 20 to components of c.
    print(c)
    # Output: (X=0, Y=20, Z=40)
    ```
    """
    _repr_items = "XYZ"

    def get_named(self, i):
        return self[i]
    def set_named(self, i, value):
        self[i] = value

    # allow index 0 - 2 to be accessed through letters:
    # x,y,z or r,g,b. IndexError if list too small!
    x = r = property(lambda self: self.get_named(0),
                     lambda self, v: self.set_named(0,v))
    y = g = property(lambda self: self.get_named(1),
                     lambda self, v: self.set_named(1,v))
    z = b = property(lambda self: self.get_named(2),
                     lambda self, v: self.set_named(2,v))

    def set(self, *args):
        self.__init__(*list(args))

    def __init__(self, *args):
        """Create a new Loc object of any size, although the size will
        be set from how many values are given. These can be given
        separately or as an iterable.

        Eg,
        `Loc(10, 10)` or
        `Loc([10, 10])`
        """
        try:
            super().__init__(list(*args))
        except TypeError:
            super().__init__(list(args))

    @classmethod
    def from_str(self, other):
        """Return Loc with types (int or float) from repr string OTHER.
        Example input is `(10.0, 5.0)`, not `(X=2, Y=30)`"""
        ret = Loc()
        items = other.strip().replace(" ", "").strip("()").split(",")
        for it in items:
            try:
                ret.append(eval(it))
            except:
                pass
        return ret

    def __repr__(self):
        return "(%s)"%", ".join((str(it) for it in self))
    def __str__(self):
        return "(%s)"%", ".join(("%s=%s"%(self._repr_items[i], str(it))
                                 if i < len(self._repr_items) else str(it)
                                 for i, it in enumerate(self)))
    def __add__(self, other):
        ret = Loc()
        for i in range(len(self)):
            try:
                ret.append(self[i] + other[i])
            except TypeError:
                ret.append(self[i] + other)
        return ret
    def __mul__(self, other):
        ret = Loc()
        for i in range(len(self)):
            try:
                ret.append(self[i] * other[i])
            except TypeError:
                ret.append(self[i] * other)
        return ret
    def __mod__(self, other):
        ret = Loc()
        for i in range(len(self)):
            try:
                ret.append(self[i] % other[i])
            except TypeError:
                ret.append(self[i] % other)
        return ret
    def __sub__(self, other):
        ret = Loc()
        for i in range(len(self)):
            try:
                ret.append(self[i] - other[i])
            except TypeError:
                ret.append(self[i] - other)
        return ret
    def __truediv__(self, other):
        ret = Loc()
        for i in range(len(self)):
            try:
                ret.append(self[i] / other[i])
            except TypeError:
                ret.append(self[i] / other)
        return ret
    def __floordiv__(self, other):
        ret = Loc()
        for i in range(len(self)):
            try:
                ret.append(self[i] // other[i])
            except TypeError:
                ret.append(self[i] // other)
        return ret
    def __pow__(self, other):
        ret = Loc()
        for i in range(len(self)):
            try:
                ret.append(pow(self[i], other[i]))
            except TypeError:
                ret.append(pow(self[i], other))
        return ret
    def __pos__(self):
        ret = Loc()
        for i in range(len(self)):
            ret.append(abs(self[i]))
        return ret
    def __neg__(self):
        ret = Loc()
        for i in range(len(self)):
            ret.append(-self[i])
        return ret
    def __abs__(self):
        return sqrt(sum(it**2 for it in self))
    def __round__(self, *args):
        ret = Loc()
        for i in range(len(self)):
            ret.append(round(self[i], *args))
        return ret
    def __iadd__(self, other):
        self = self + other
        return self
    def __isub__(self, other):
        self = self - other
        return self
    def __imul__(self, other):
        self = self * other
        return self
    def __imod__(self, other):
        self = self % other
        return self
    def __itruediv__(self, other):
        self = self / other
        return self
    def __ifloordiv__(self, other):
        self = self / other
        return self
    def copy(self):
        return Loc(*self)

class LocVar(Variable):
    """Value holder for Loc variables."""
    _default = Loc(0.0, 0.0)
    def __init__(self, master=None, value=None, name=None):
        """Construct an Loc variable.

        MASTER can be given as master widget.
        VALUE is an optional value (defaults to 0)
        NAME is an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable and VALUE is omitted
        then the existing value is retained.
        """
        Variable.__init__(self, master, value, name)

    def set(self, value):
        """Set the variable to value, converting iterable to Loc."""
        if not isinstance(value, Loc):
            try:
                value = Loc(*value)
            except TypeError:
                pass
        return Variable.set(self, repr(value))

    def get(self):
        """Return the value of the variable as an Loc."""
        return Loc.from_str(self._tk.globalgetvar(self._name))

class MathStat(object):

    @staticmethod
    def clamp(val, min=0, max=1):
        return min if val < min else max if val > max else val

    @staticmethod
    def getpercent(val, min, max):
        """returns what percent (0 to 1) val is between min and max.
        eg: val of 15 from 10 to 20 will return 0.5"""
        return MathStat.clamp((val-min) / (max-min))

    @staticmethod
    def map_range(val, in_a, in_b, out_a=0, out_b=1):
        """returns val mapped from range(in_a to in_b) to range(out_a to out_b)
        eg: 15 mapped from 10,20 to 1,100 returns 50"""
        return MathStat.lerp(out_a, out_b, MathStat.getpercent(val, in_a, in_b))

    @staticmethod
    def map_range_clamped(val, in_a, in_b, out_a=0, out_b=1):
        """returns val mapped from range(in_a to in_b) to range(out_a to out_b)
        eg: 15 mapped from 10,20 to 1,100 returns 50"""
        return MathStat.lerp(out_a, out_b, MathStat.getpercent(val, in_a, in_b))

    @staticmethod
    def lerp(a, b, bias, clamp=True):
        """returns interpolation between a and b. bias 0 = a, bias 1 = b.
        also works with iterables by lerping each element of a and b
        can also extrapolate if clamp is set to False"""
        def lerp1(a, b, bias):
            return a + (b-a) * bias
        def cross_iter(a, b):
            for i in range(len(a)):
                yield a[i], b[i]
        def cross_iter_str(a, b):
            # format: '#rrggbb...' hex codes
            # yields integers rr, gg, bb, etc for a and b
            for i in range(1, len(a)):
                if i % 2 == 1:
                    yield int("0x%s"%a[i:i+2], 0), int("0x%s"%b[i:i+2], 0)
        if clamp:
            bias = bias if bias > 0 else 1 if bias > 1 else 0
        try:
##                cross_lerp = [lerp1(ax, bx, bias)
##                              for ax, bx in cross_iter_str(a, b)]
##                return cross_lerp

            # lerp each element in iterable container
            cross_lerp = [lerp1(ax, bx, bias) for ax, bx in cross_iter(a, b)]
            try:
                return type(a)(*cross_lerp)
            except:
                return type(a)(cross_lerp)
        except:
            # string hex code color lerp
            if isinstance(a, str):
                ret_str = "#"
                for ax, bx in cross_iter_str(a, b):
                    ret_str += "%02x"%int(lerp1(ax, bx, bias))
                return ret_str
            # simple lerp
            return lerp1(a, b, bias)

    @staticmethod
    def getdistsquared(loc1, loc2):
        """returns squared distance between coords"""
        return sum((loc2-loc1)**2)

##    @staticmethod
##    def getdist(x1, y1, x2, y2):
##        """returns distance between coords"""
##        return sqrt((x2-x1)**2 + (y2-y1)**2)

    @staticmethod
    def getdist(loc1, loc2):
        """returns distance between coords"""
        return sqrt(sum((loc2-loc1)**2))

    # @staticmethod
    # def getedgelengths(verts):
    #     return [getdist(coords[0], coords[1],
    #                     *verts[i+1 if i+1<len(verts) else 0])
    #             for i, coords in enumerate(verts)]

    # @staticmethod
    # def getlengthpos(verts, bias):
    #     """returns location at an edge between set of verts at the given bias (0-1)"""
    #     bias = 1 if bias > 1 else 0 if bias < 0 else bias
    #     edge_lengths = getedgelengths(verts)
    #     perimeter = sum(edge_lengths)
    #     desired_point = perimeter * bias

    #     cursum = 0
    #     for i, leng in enumerate(edge_lengths):
    #         cursum += leng
    #         if cursum >= desired_point:
    #             vert_hi = verts[i]
    #             vert_lo = verts[i-1 if i>0 else len(verts)-1]
    #             break

    #     return lerp(vert_lo, vert_hi, getpercent(desired_point, cursum-leng,
    #                 cursum))

    @staticmethod
    def get_random_location_in_bounding_box(origin, bounds):
        return origin + [MathStat.lerp(0, i, random()) for i in bounds]

class MotionInput(object):
    def __init__(self, *args, **kw):
        """initialise attributes. optionally call bind_to_widget with
        specified args if args are not empty

        AVAILABLE KEYWORDS
            normalise (bool) Whether to use acceleration smoothing on motion.
            True by default
        """
        self._isheld = False

        self._delta = (0, 0)
        self._normalised_delta_max = 5
        self._use_normalisation = kw.get("normalise", True)

        self._bound_events = {}
        ##self._held_buttons = {}

        # bind to widget if extra args given
        if args:
            self.bind_to_widget(*args)


    @property
    def delta(self):
        return Loc(self._delta)

    def bind_to_widget(self, in_widget, button="1"):
        """binds relevant inputs to in_widget, optionally using the
        specified button (1=LMB, 2=MMB, 3=RMB)"""
        in_widget.bind("<ButtonPress-%s>"%button, self.inp_press)
        in_widget.bind("<ButtonRelease-%s>"%button, self.inp_release)
        in_widget.bind("<Button%s-Motion>"%button, self.inp_motion)
        # add to held buttons dict (defualt False not held)
        ##self._held_buttons[button] = False

    def bind(self, event_code=None, func=None, add=None):
        """Binds func to be called on event_code.
        Event codes is written in the format <MODIFIER-MODIFIER-IDENTIFIER>.
        Available MODIFIERS:
##            Button1
##            Button2
##            Button3
            Motion
        Available IDENTIFIERS:
            X
            Y
            XY"""
        event_code = event_code.replace("<", "").replace(">", "")
        keys = event_code.split("-")
        identifier = keys.pop()
        modifiers = keys
        # check if the event_code is valid
        if identifier not in ["X", "Y", "XY"]:
            return False # fail
        for m in modifiers:
            if m not in ["Motion", "Button1", "Button2", "Button3"]:
                return False # epic fail!

        # bind the function
        # create new list for event if not already bound
        if event_code not in self._bound_events:
            self._bound_events[event_code] = [func]
        else:
            # append to list if necessary
            if add:
                self._bound_events[event_code].append(func)
            # otherwise initialise new list
            else:
                self._bound_events[event_code] = [func]
        return True # success

    def _get_bound_events(self, identifier=None, *modifiers):
        """Returns list of bound functions to call for the specified event"""
        ret_funcs = []
        modifiers = set(modifiers) # ensure modifiers are unique

        # check every bound event code
        for event_code, func_list in self._bound_events.items():
            event_keys = event_code.split("-")
            event_id = event_keys.pop()
            event_mods = event_keys
            all_mods_work = True

            # check identifier
            id_works = (identifier is None
                        or identifier is not None and identifier == event_id)
            # only check modifiers if identifier is correct
            if id_works:
                for m in modifiers:
                    if m not in event_mods:
                        all_mods_work = False
                        break
            # add bound functions if id and modifiers are correct
            if id_works and all_mods_work:
                    ret_funcs = ret_funcs + func_list

        # finally return found functions
        return ret_funcs if ret_funcs else None

    def _normalise_delta(self, in_delta, set_in_place=True):
        """Normalises in_delta to range (-1, 1).
        Optionally don't set in place"""

        # set attributes of passed in list object if necessary
        if set_in_place:
            in_delta.x = MathStat.map_range(in_delta.x,
                                          -self._normalised_delta_max,
                                          self._normalised_delta_max, -1, 1)
            in_delta.y = MathStat.map_range(in_delta.y,
                                          -self._normalised_delta_max,
                                          self._normalised_delta_max, -1, 1)
            return in_delta

        # otherwise initialise a new Loc object
        else:
            return Loc(MathStat.map_range(in_delta.x,
                                          -self._normalised_delta_max,
                                          self._normalised_delta_max, -1, 1),
                       MathStat.map_range(in_delta.y,
                                          -self._normalised_delta_max,
                                          self._normalised_delta_max, -1, 1))

    def _is_held(self, button):
        """returns whether the button is held"""
        return button in self._held_buttons and self._held_buttons[button]

    def inp_press(self, event, func=None):
        """Bind this to a widget on a ButtonPress-X event"""
        self._isheld = True
        ##self._held_buttons[event.num] = True
        self._last_loc = Loc(event.x, event.y)
        self._orig_press_loc = self._last_loc.copy()
        # call function if specified with event
        if func:
            func(event)

    def inp_release(self, event=None, func=None):
        """Bind this to a widget on a ButtonRelease-X event"""
        self._isheld = False
        ##self._held_buttons[event.num] = False
        # call function if specified with event
        if func:
            func(event)

    def inp_motion(self, event, func=None):
        """Bind this to a widget on a ButtonX-Motion event"""
        def near_to_zero(val, offset=0.05):
            return val < offset and val > -offset

        if self._isheld:
            # get and set delta
            new_loc = Loc(event.x, event.y)
            self._delta = d = new_loc - self._last_loc
            if self._use_normalisation:
                self._normalise_delta(d)
            else:
                d *= 0.2
            # set delta in event object to return in callbacks
            event.delta = d
            # ensure the last location is updated for next motion
            self._last_loc = new_loc

            # call function if specified with event and delta (in event)
            if func:
                func(event)

        # fire bound events for button invariant bindings

        if not near_to_zero(d.x):
            be = self._get_bound_events("X", "Motion")
            if be:
                for func in be:
                    func(event)

        if not near_to_zero(d.y):
            be = self._get_bound_events("Y", "Motion")
            if be:
                for func in be:
                    func(event)

        if not near_to_zero(d.x) or not near_to_zero(d.y):
            be = self._get_bound_events("XY", "Motion")
            if be:
                for func in be:
                    func(event)

class LocalPlayer(object):
    def __init__(self, canvas):
        self.input_tracker = {}
        self._setup_input(canvas)

    def _setup_input(self, input_component):
        """Setup input bindings to input_component using widget bindings"""
        pass

class WgtManager(object):
    _window = None
    _cur_menu = None
    _top_levels = {}

    def make_window(self, title="tk", start_mainloop=True, first_menu=None):
        # make Tk object
        self._window = Tk()
        self._window.title(title)

        # make first menu
        if first_menu:
            self.make_menu(first_menu)

        # start mainloop
        if start_mainloop:
            return self.start_mainloop()
        else:
            return self._window

    def start_mainloop(self):
        if self._window:
            return self._window.mainloop()

    def make_menu(self, menu_class, **kw):
        # destroy old menu if possible
        if self._cur_menu:
            self._cur_menu.destroy()

        # create new menu from class
        self._cur_menu = menu_class(self._window, **kw)
        self._cur_menu.pack(fill=BOTH, expand=TRUE)

        # return newly made menu
        return self._cur_menu

    def make_menu_top_level(self, menu_class, master=None):
        # destroy old menu if possible
        if menu_class in self._top_levels:
            self._top_levels[menu_class].destroy()

        if not master:
            master = self._window

        # create top level to house the new menu
        top_level = Toplevel(master)

        # create new menu from class
        new_menu = menu_class(top_level)
        new_menu.pack(fill=BOTH, expand=TRUE)

        # add to top levels dict
        self._top_levels[menu_class] = top_level

        # return newly made menu
        return new_menu

##class Styles(object):
##    default =   {
##                "bg":"orange"
##                }
##
##    label = default.copy()
##    label.update({
##                "fg":"#000000"
##                })
##
##    entry =     {
##                "fg":"#000000",
##                "bg":"white"
##                }
##
##    button =    {
##                "fg":"#000000",
##                "bg":"SystemButtonFace",
##                "activeforeground":"#000000",
##                "activebackground":"SystemButtonFace"
##                }
##
##    title =     label.copy()
##    title.update({
##                "font":"Arial 9 bold"
##                })

class MyMenu(Frame):
##    style = Styles.default
    def _pre_config(self, cnf):
        pass

    def __init__(self, master=None, cnf={}, **kw):
        # configure using kw args before initialising frame
        # must remove specific options or frame will not initialise properly
        self._pre_config(kw)

        # initialise the frame
##        Frame.__init__(self, master, cnf, **kw)
        Frame.__init__(self, master, **kw)
##        cnf_opts = self.style
        cnf_opts = {}
        cnf_opts.update(cnf)
        cnf_opts.update(kw)
##        if self.style:
##            self.config(cnf_opts)
        # make widgets
        self.make_widgets()

    def make_widgets(self):
        pass

    def Spacer(self, parent=None, cnf={}, **kw):
        heigh = kw.get("height", 0)
        widt = kw.get("width", 0)
##        styl = kw.get("style", self.style)
##        cnf.update(styl)
        if not parent:
            parent = self
        # make an empty frame and pack it
        Frame(parent, cnf, width=widt, height=heigh).pack()

class Spacer(MyMenu):
    def make_widgets(self):
        # pack the frame straight away
        # specify height/width when initialising
        self.pack()

class NumEdit(MyMenu):
    def _pre_config(self, cnf):
        self.val_var = cnf.pop("variable", None)
        self._callback = cnf.pop("command", None)
        self._width = cnf.pop("width", 4)
        self._text = cnf.pop("text", " ")
        self._val_type = cnf.pop("valtype", int)
        self._mode = cnf.pop("mode", "contained")
        # precision used to determine rounding accuracy
        self._precision = cnf.pop("precision", 1)
        self._delta_mult = cnf.pop("speed", None)

        # set from and to range
        self._from = cnf.pop("from",
                     cnf.pop("from_", None))
        self._to = cnf.pop("to", None)

        # create new stringvar object if variable not defined
        if self.val_var is None:
            self.val_var = StringVar()
            # set initial value to any defined val
            if self._from is not None:
                self.val_var.set(self._from)
            elif self._to is not None:
                self.val_var.set(self._to)
            else:
                self.val_var.set(0)

        if self._to is not None and self._from is not None:
            # get normalised speed from given range
            if self._delta_mult is None:
                self._delta_mult = MathStat.map_range(0.06, 0, 1,
                                                      self._from, self._to)

        self.last_valid_val = self._val_type(self.val_var.get())
        self.last_displayed_val = self.last_valid_val
        self._is_entering_formula = False

    def _set(self, val=None, force_no_callback=False):
        """Internal function for setting the value in the widget.
        param   val                 new value to store
        param   force_no_callback   override to disable calling bound callback
                                    function if one exists

        If called with val=None, the new value will attempt to be calculated
        based on what is entered in the widget currently.
        """

        # update value from what is already entered
        if val is None and not self._is_entering_formula:
            try:
                val = self._val_type(self.entry_var.get())
            except ValueError:
                try:
                    val = self._val_type(eval(self.entry_var.get(),
                                                  None, None))
                except:
                    val = self.last_valid_val

        # clamp to range if necessary
        try:
            new_val = round(val, self._precision)
            if self._from != None and new_val < self._from:
                new_val = self._from
            if self._to != None and new_val > self._to:
                new_val = self._to

            # set last valid val
            self.last_valid_val = new_val

        # otherwise get last valid val
        except:
            new_val = self.last_valid_val

        new_val = self._val_type(new_val)

        # set value in tkinter var (not for display)
        self.val_var.trace_vdelete("w", self.val_var.trace_id)
        self.val_var.set(new_val)
        self.val_var.trace_id = self.val_var.trace("w", self._on_trace_val_var)

        # set values for display
        is_same = new_val == self.last_displayed_val
        self.last_displayed_val = new_val
        self.entry_var.set(new_val)

        # callback if possible
        if is_same:
            return
        if self._callback:
            self._callback(new_val)

    def on_motion_x(self, event):
        # get delta x component of motion event
        delta = event.delta.x
        if self._delta_mult is not None:
            delta *= self._delta_mult

        # adjust delta to give fractional part
        delta = delta/(7/3)
##        if self._val_type != int:
##            delta = self._val_type(delta/(7/3))
##        else:
##            delta = self._val_type(delta)

        if self._to is None and self._from is None:
            delta *= 1.06

        # calculate new value using last valid val
        new_val = self.last_valid_val + delta

        # round to specified precision if necessary
        if self._val_type != int:
            new_val = round(new_val, self._precision)

        # set value with validation
        self._set(new_val)

    def _prepare_entry(self):
        self.entry.selection_clear()
        self.entry.focus_set()

    def on_return(self, event):
        # attempt to set val with validation
        self._is_entering_formula = False
        self._set()

    def on_label_click(self, event):
        self.on_return(event)
        self._prepare_entry()
        self.last_valid_val = self.last_displayed_val

    def on_key(self, event):
        self._is_entering_formula = True
##        try:
##            if not self._is_entering_formula and event.keysym.isnumeric():
####                self.after(0, self._set)
##                pass
##            else:
##                self._is_entering_formula = True
##        except AttributeError:
##            pass

    def _on_trace_val_var(self, *args):
        """
        This is only called by externally calling set() on val_var.
        """
        self.entry_var.set(self.val_var.get())
        self._set()

    def config(self, cnf={}, **kw):
##        if "bg" in kw:
##            self.label.config(bg=kw["bg"])
        return super().config(cnf, **kw)

    def make_widgets(self):

        if self.val_var:
            self.val_var.trace_id = self.val_var.trace("w", self._on_trace_val_var)

        # create widgets for operation

        if self._mode == "contained":
            parent = self
        elif self._mode == "external":
            parent = self.master

        # create label for title
        self.label = Label(parent,
                           text=self._text,
                           cursor="sb_h_double_arrow"
##                           bg=self.cget("bg")
                           )

        # create entry for displaying/entered value
        self.entry_var = StringVar()
        self.entry = Entry(parent,
                           textvariable=self.entry_var,
                           width=self._width,
                           cursor="arrow"
                           )
        self._set(None, True)

        if self._mode == "contained":
            self.label.pack(side=LEFT, anchor=N, padx=2)
            self.entry.pack(side=LEFT, fill=X, expand=TRUE, padx=3, anchor=CENTER)
        elif self._mode == "external":
            my_column, my_row = self.master.grid_size()
            my_row += 1 # Offset to allow for resize frames on row 0.
            self.label.grid(row=my_row, column=0, pady=5, sticky=W)
            self.entry.grid(row=my_row, column=2, padx=3, sticky=EW)


        # set up input for dragging text to change value

        # bind functions for delta in motion to be calculated
        self.motion_inp_comp = mic = MotionInput(self.label, normalise=False)

        # bind function to update value with x axis motion
        mic.bind("<Motion-X>", self.on_motion_x)

        # set up input to change value from entry
        self.entry.bind("<Return>", self.on_return)
        self.entry.bind("<FocusOut>", self.on_return)
        self.entry.bind("<Key>", self.on_key)
        self.label.bind("<ButtonPress-1>", self.on_label_click, True)

    def __init__(self, *args, **kw):
        """
        Initialise new NumEdit widget.

        Optional available keywords are:
            variable    Tkinter variable for holding value.
            command     Function to call when value changes. New value is
                        supplied as param.
            mode        How editor will be used. Can be "contained" or "external"
                        Default is contained.
            width       Width of editing entry space, in characters. Default
                        is 4.
            text        Text to show next to editing entry space.
            valtype     Type of value to edit. Must be numerical type. Default
                        is int.
            precision   Number of decimal places to round to when adjusting
                        value. Default is 1
            speed       Multiplier value for rate of change when dragging mouse.
            from/from_  Minimum limit when editing value. If unspecified, there
                        will be no minimum limit.
            to          Maximum limit when editing value. If unspecified, there
                        will be no maximum limit.
        """
        super().__init__(*args, **kw)

class LocEdit(MyMenu):
    def _pre_config(self, cnf):
        self._loc_to_update = cnf.pop("locationvar",
                              cnf.pop("variable", LocVar()))
        self._titles = cnf.pop("titles", "XYZ")
        self._text = cnf.pop("text", None)
        self._callback = cnf.pop("command", None)
        self._pack_dir = cnf.pop("packdir", LEFT)
        self._width = cnf.pop("width", 4)
        self._mode = cnf.pop("mode", "contained")

        self._from = cnf.pop("from",
                     cnf.pop("from_", None))

        self._to = cnf.pop("to", None)

    def _set_locvar(self, i, val):
        if self._loc_to_update:
            # update locationvar
            tmp = self._loc_to_update.get()
            tmp[i] = val
            if tmp == self._loc_to_update:
                return
            self._loc_to_update.set(tmp)
            # callback if necessary
            if self._callback:
                self._callback(tmp)

    def _on_loc_trace(self, *args):
        for i, it in enumerate(self._loc_to_update.get()):
            self.val_vars[i].set(it)

    def make_widgets(self):
        if not self._loc_to_update:
            return

        self.val_vars = []

        if self._mode == "contained":
            parent = self
        elif self._mode == "external":
            parent = self.master

        # Create title label.
        if self._text:
            self.label = Label(parent,
                text=self._text
                )#.pack(side=self._pack_dir, fill=X, expand=TRUE, padx=3)

        # make widgets for each item in locvar
        self.nums_frame = Frame(parent)

        for i, item in enumerate(self._loc_to_update.get()):

            # calculate clamping values for this NumEdit

            # clamp from
            try:
                tmp_from = self._from[i] # get value for this index
            except IndexError:
                tmp_from = None # dont set if value for this index not specified
            except TypeError:
                tmp_from = self._from # use a single value for all or none
            # clamp to
            try:
                tmp_to = self._to[i] # get value for this index
            except IndexError:
                tmp_to = None # dont set if value for this index not specified
            except TypeError:
                tmp_to = self._to # use a single value for all or none

            # create widget for this item
            new_val_var = StringVar()
            new_val_var.set(self._loc_to_update.get()[i])

            NumEdit(self.nums_frame,
                variable=new_val_var,
                text=self._titles[i] if i < len(self._titles) else " ",
                command=lambda v, idx=i: self._set_locvar(idx, v),
                valtype=type(self._loc_to_update.get()[i]),
                from_=tmp_from,
                to=tmp_to,
                precision=4,
                width=self._width
                ).pack(side=self._pack_dir, fill=X, expand=TRUE)#, padx=3)

            # add to int vars list (used by get function)
            self.val_vars.append(new_val_var)

            # set variable tracing for external changes
            self._loc_to_update.trace("w", self._on_loc_trace)

        if self._mode == "contained":
            self.label.pack(side=self._pack_dir, fill=X, expand=TRUE, padx=3)
            self.nums_frame.pack(side=self._pack_dir, fill=X, expand=TRUE, padx=3, anchor=CENTER)
        elif self._mode == "external":
            my_column, my_row = self.master.grid_size()
            my_row += 1 # Offset to allow for resize frames on row 0.
            self.label.grid(row=my_row, column=0, pady=5, sticky=W)
            self.nums_frame.grid(row=my_row, column=2, sticky=EW)

    def get(self):
        return Loc([a.get for a in self.val_vars])

class Gradient(object):
    def __init__(self):
        #self.color_keys = {} # stores color keys in format LOCATION:COLOR
        self.color_keys = [] # stores sorted list of dicts

    def add_key(self, color, location):
        """Inserts a new key to the gradient at the given location, ensuring the
        list is in location order.
        Returns index new key was added at if successful
        Color should be a 6 digit hex code prefixed with #, eg "#f10c34"
        Location should be normalised between 0 and 1"""

        location = MathStat.clamp(location) # ensure location between 0 and 1
        # validate color
        if color[0] != "#":
            return
        try: # check each pair of values is a valid hexadecimal digit
            for i in range(1, len(color)):
                if i % 2 == 1:
                    int("0x%s"%color[i:i+2], 0)
        except ValueError:
            return

        # adjust location if value already exists at that location
        while self._key_exists_at_loc(location):
            location += 0.001
            if location > 1:
                return

        # determine the correct location to add the key
        new_idx = self._get_index_for_loc(location)

        # create dictionary to store key in
        new_key = {"location":location, "color":color}

        # insert the new key at the specified location
        self.color_keys.insert(new_idx, new_key)
        return new_idx # return index successfully added at

    def remove_key(self, index=None, location=None):
        """Remove the key at the given index or location.
        Returns whether it was successful True/False"""
        # get index from location if specified
        if location is not None:
            location = MathStat.clamp(location)
            index = self.get_key(location)
        # validate index using range check
        if index not in range(len(self.color_keys)):
            return False
        # perform removal of the key
        self.color_keys.remove(index)
        return True # success

    def get_color(self, location, default=None):
        """returns color at any location on the gradient by interpolating
        between surrounding keys, optionally returns default if key not found"""
        location = MathStat.clamp(location) # clamp to 0-1
        # check there are any keys
        if not self.color_keys:
            return default # return default color
        # get keys surrouding the location
        key_min, key_max = self._get_keys_around_loc(location)
        if key_min == key_max is not None: # out of key bounds
            bias = 0
        else:
            bias = MathStat.map_range(location, key_min["location"],
                                      key_max["location"])

        return MathStat.lerp(key_min["color"], key_max["color"], bias)

    def set_color(self, color, index=None, location=None):
        """Set color of the key at the given index or location.
        Returns whether it was successful True/False"""
        # get index from location if specified
        if location is not None:
            location = MathStat.clamp(location)
            index = self.get_key(location)
        # validate index using range check
        if index not in range(len(self.color_keys)):
            return False
        # set color
        self.color_keys[index]["color"] = color
        return True # success

    def get_key(self, location, radius=0.01):
        """Returns the index of key at the given location in a radius or -1
        if one isn't found."""
        for i, key in enumerate(self.color_keys):
            loc = key["location"]
            if loc > location-radius and loc < location+radius:
                return i
        return -1

    def _key_exists_at_loc(self, location):
        """returns whether a key exists at an exact location"""
        for key in self.color_keys:
            if key["location"] == location:
                return True
        return False

    def _get_index_for_loc(self, location):
        """returns index for the location to be inserted at in the sorted
        color_keys list"""
        for key in reversed(self.color_keys):
            if key["location"] < location:
                return self.color_keys.index(key) + 1
        return 0

    def _get_closest_key(self, location):
        """Returns closest color key to the given location or None if
        no keys exist"""
        # check if any keys exist
        if not self.color_keys:
            return
        # search through the keys to find the closest
        best_gap = None
        best_col = None
        for loc, col in self.color_keys.items():
            gap = abs(location - loc)
            if gap < best_gap or best_gap is None:
                best_gap = gap
                best_col = col
        return best_col

    def _get_keys_around_loc(self, location):
        """Returns closest color above the location and closest color below the
        location"""
        # return None if no keys
        if not self.color_keys:
            return None, None
        # return single key if only 1 key
        if len(self.color_keys) == 1:
            return self.color_keys[0], self.color_keys[0]
        # otherwise return surrounding keys
        location = MathStat.clamp(location, 0.001, 0.999)
        i = self._get_index_for_loc(location)
        # return surrounding keys
        if i <= len(self.color_keys)-1:
            return self.color_keys[i-1], self.color_keys[i]
        # return last key twice - we went beyond the last key
        else:
            return self.color_keys[i-1], self.color_keys[i-1]

class GradEdit(MyMenu):
    held_node = None
    edit_key = None

    def _pre_config(self, cnf):
        self._gradient = cnf.pop("gradient", Gradient())

    def on_strip_press(self, event):
        pass

    def on_strip_release(self, event):
        if (event.x < 0 or event.x > self.frame_strip.winfo_width()
            or event.y < 0 or event.y > self.frame_strip.winfo_height()):
            return

        location = event.x / self.frame_strip.winfo_width()
        color = self._gradient.get_color(location, "#000000")
        new_key = self._gradient.add_key(color, location)
        if new_key is not None:
            self._key_color_var.set("")
            self.edit_key = new_key
            self.frame_strip.create_line(event.x, 0,
                                         event.x,
                                         self.frame_strip.winfo_height(),
                                         fill="red",
                                         width=2
                                         )

    def on_strip_motion(self, event):
        pass

    def on_motion(self, event):
        new_bg = self._gradient.get_color(event.x / self.frame_strip.winfo_width())
##        if new_bg is not None:
##            self.frame_sample.config(bg=new_bg)
        print("new bg:", new_bg)

    def _on_key_col_confirm(self):
        print(self.edit_key)
        # confirm a key is active for editing
        if self.edit_key is None:
            return
        # validate input by making sure it starts with '#'
        inp = self._key_color_var.get()
        if len(inp) == 0 or inp[0] != "#":
            inp = "#" + inp
            self._key_color_var.set(inp)
        # validate input by making sure it is a valid hex code
        for i in range(1, len(inp)):
            if i % 2 == 1:
                try:
                    int("0x%s"%inp[i:i+2], 0)
                except ValueError:
                    return

        # finally set key color with confirmed value
        print(self._gradient.color_keys[self.edit_key])
        self._gradient.set_color(inp, self.edit_key)
        print(self._gradient.color_keys[self.edit_key])

    def make_widgets(self):
        Label(self, ##Styles.default,
              text="Gradient Editor"
              ).pack(fill=X, expand=TRUE)

        self.frame_strip = Canvas(self,
                                      height=20,
                                      width=60)
        self.frame_strip.pack(fill=X, expand=TRUE, padx=10, pady=10)
        self.frame_strip.bind("<ButtonPress-1>", self.on_strip_press)
        self.frame_strip.bind("<ButtonRelease-1>", self.on_strip_release)
        self.frame_strip.bind("<Button1-Motion>", self.on_strip_motion)
        self.frame_strip.bind("<Motion>", self.on_motion)


        frame_left = Frame(self)##, Styles.default)
        frame_left.pack(side=LEFT, padx=10, pady=10)

        self._key_color_var = StringVar()
        Label(frame_left,## Styles.label,
              text="Key Color"
              ).pack()
        Entry(frame_left,## Styles.entry,
              textvariable=self._key_color_var,
              width=10
              ).pack()
        Button(frame_left,## Styles.button,
               text="Confirm",
               command=self._on_key_col_confirm,
               width=7
               ).pack(pady=3)


        frame_right = Frame(self)##, Styles.default)
        frame_right.pack(side=LEFT, padx=10, pady=10)

        Label(frame_right, ##Styles.label,
              text="Sample"
              ).pack()

        self.frame_sample = Frame(frame_right,
                                  width=50,
                                  height=50
                                  )
        self.frame_sample.pack()

class TestMenu(MyMenu):
    def on_color_bias(self, val):
        new_bg = MathStat.lerp("#4e59bf", "#92db53", val)
        #new_bg = self.g.get_color(val)
        self.config(bg=new_bg)
        self.my_num_edit.config(bg=new_bg)
##        print(val)
        pass

    def make_widgets(self):

##        self.g = Gradient()
##        self.g.add_key("#000000", 0)
##        self.g.add_key("#ffffff", 0.7)
##        self.g.add_key("#000000", 0.9)
##        self.g.add_key("#ffffff", 1)

        test_var = StringVar()
        test_var.set(0.5)
        self.my_num_edit = NumEdit(self,
            variable=test_var,
            text="Color Bias",
            command=self.on_color_bias,
            valtype=float,
            from_=0,
            to=1,
            precision=4,
            width=6)
        self.my_num_edit.pack(padx=60, pady=30)

        if 0:
            test_loc_var = LocVar()
            test_loc_var.set(Loc(0, 0.0))
            self.my_loc_edit = LocEdit(self,
                variable=test_loc_var,
    ##            command=self.on_loc_changed,
                from_=(1, 3),
                to=20
                )
            self.my_loc_edit.pack(fill=X, pady=30)
            test_loc_var.set(Loc(10, 10.0))

        self.on_color_bias(0.5)

##        GradEdit(self).pack(fill=X, expand=TRUE)

    def on_loc_changed(self, new_loc):
        print(new_loc)

# Case picking

class CasePicker():
    """
    Class with static methods for determining and converting the cases of
    strings from common naming conventions snake_case, PascalCase and camelCase.
    """

    @staticmethod
    def general_split(s, first_index=0):
        """
        Yield each word in a string that starts with a capital letter or that
        has any whitespace immediately before it.
        """
        s = s.strip() + "A"

        for i, letter in enumerate(s):
            if i > first_index:

                # Split at capital letter
                if letter.isupper():
                    yield s[first_index:i]
                    first_index = i

                # Split at underscore
                elif letter == "_":
                    yield s[first_index:i]
                    first_index = i + 1

                # Split at whitespace
                elif letter in string.whitespace \
                    and (i+1 < len(s) and not s[i + 1] in string.whitespace):
                    yield s[first_index:i]
                    first_index = i + 1

    @staticmethod
    def camel_split(s):
        """
        Split a string into words list using camelCase rules.
        """
        return [word for word in CasePicker.general_split(s)]

    @staticmethod
    def pascal_split(s):
        """
        Split a string into words list using PascalCase rules.
        """
        return [word for word in CasePicker.general_split(s, -1)]

    @staticmethod
    def snake_split(s):
        """
        Split a string into words list using snake_case rules.
        """
        s = s.strip().replace(" ", "")
        return s.split("_")

    @staticmethod
    def to_words(s):
        """
        Return a list of words for a given string.
        """
        return CasePicker.general_split(s)

    @staticmethod
    def to_camel(s):
        """
        Convert a string or list of words to camelCase.
        """
        if isinstance(s, str):
            return CasePicker.to_camel(CasePicker.to_words(s))

        ret = ""
        for word in s:
            if word:
                if not ret:
                    ret += word.lower()
                else:
                    ret += word[0].upper()
                    ret += word[1:].lower()
        return ret

    @staticmethod
    def to_pascal(s):
        """
        Convert a string or list of words to PascalCase.
        """
        if isinstance(s, str):
            return CasePicker.to_pascal(CasePicker.to_words(s))

        ret = ""
        for word in s:
            if word:
                ret += word[0].upper()
                ret += word[1:].lower()
        return ret

    @staticmethod
    def to_snake(s):
        """
        Convert a string or list of words to snake_case.
        """
        if isinstance(s, str):
            return CasePicker.to_snake(CasePicker.to_words(s))

        return "_".join(word.lower().replace("_", "") for word in s if word)

    @staticmethod
    def get_case(s):
        """
        Return the best estimate for what case a string is using.
        """

        # Calculate words lists for all cases.
        cases = ({"name":"snake",   "words":CasePicker.snake_split(s)},
                 {"name":"camel",   "words":CasePicker.camel_split(s)},
                 {"name":"pascal",  "words":CasePicker.pascal_split(s)})

        # Get lengths of calculated lists.
        case_lens = [len(case["words"]) for case in cases]

        # Pick the case that identified the most individual words.
        return cases[case_lens.index(max(case_lens))]["name"]

    @staticmethod
    def to_custom(s, **kw):
        """
        Convert a string to custom case method.

        Available keywords:
        sepword, sepchar, rule["pascal", "camel", "snake"]
        """

        sepword = kw.get("sepword", "")
        sepchar = kw.get("sepchar", "")
        rule = kw.get("rule")
        rule_functs = {"pascal":CasePicker.to_pascal,
            "camel":CasePicker.to_camel, "snake":CasePicker.to_snake}
        try:
            # Convert words using rule,
            words = rule_functs[rule](s)
            # then back to words list for further manipulation.
            words = CasePicker.to_words("".join(words))
        except KeyError:
            words = CasePicker.to_words(s)

        for word in words:
            # DO SOMETHING!
            pass

class FancyPrinter(object):
    """
    Class with static methods for printing complex types like `dict` or `list`
    in fancy ways.

    All fancy string formatting functions have a param `output`. If set to None,
    the formatted contents will be returned, but not printed. If left at True,
    the contents will be printed.
    """

    @staticmethod
    def multi_pairs_table_from_dict(in_dict, col_sz=None, just=None, output=True):
        """
        Returns IN_DICT into pairs tables, where each key is the table name
        and each value is the table list. See table_from_pairs.
        """
        if output:
            return print(FancyPrinter.multi_pairs_table_from_dict(in_dict, col_sz=col_sz, just=just, output=False))

        return "\n\n".join(
            "{name} table:\n"\
            "{table}"\
            .format(name=name,
            table=FancyPrinter.table_from_pairs(table, col_sz=col_sz, just=just, output=False))
            for name, table in in_dict.items())

    @staticmethod
    def multi_rows_table_from_dict(in_dict, col_sz=None, just=None, output=True):
        """
        Returns IN_DICT into rows tables, where each key is the table name
        and each value is the table list (rows are dicts). See table_from_rows.
        """
        if output:
            return print(FancyPrinter.multi_rows_table_from_dict(in_dict, col_sz=col_sz, just=just, output=False))

        return "\n\n".join(
            "{name} table:\n"\
            "{table}"\
            .format(name=name,
            table=FancyPrinter.table_from_rows(table, col_sz=col_sz, just=just, output=False))
            for name, table in in_dict.items())

    @staticmethod
    def multi_dict_table_from_dict(in_dict, col_sz=None, just=None, output=True):
        """
        Returns IN_DICT into dict tables, where each key is the table name
        and each value is the table list (rows are dicts). See table_from_dict.
        """
        if output:
            return print(FancyPrinter.multi_dict_table_from_dict(in_dict, col_sz, just, output=False))

        return "\n\n".join(
            "{name} table:\n"\
            "{table}"\
            .format(name=name,
            table=FancyPrinter.table_from_dict(table, col_sz=col_sz, just=just, output=False))
            for name, table in in_dict.items())

    @staticmethod
    def table_from_pairs(in_list, col_sz=None, just=None, output=True, max_col=40):
        """
        Returns IN_LIST turned into tables using header-value pair tuples, with
        each column having COL_SZ width.

        Each item in IN_LIST is a row.
        Each row has an ordered series of paired tuples, where
        index 0 is the header name and index 1 is the value.

        Should be in this format:

        ```[
        [(header1, row1val1), (header2, row1val2) ...],
        [(header1, row2val1), (header2, row2val2) ...],
        ...
        ]```

        COL_SZ is static column lengths. Default will decide best size.
        JUST is one of str.center, str.ljust or str.rjust. Default is center.
        """
        if output:
            return print(FancyPrinter.table_from_pairs(in_list, col_sz=col_sz, just=just, output=False))

        if just is None:
            # Use central justify by default.
            just = str.center

        if col_sz is None:
            # Optional first pass - determine column sizes
            col_sz = [0 for column in in_list[0]]
            for i, row in enumerate(in_list):
                for j, col in enumerate(row):
                    # Add 2 space padding.
                    col_sz[j] = max(col_sz[j], *(len(str(val)) + 2 for val in col))
                    if col_sz[j] > max_col: col_sz[j] = max_col
            return FancyPrinter.table_from_pairs(in_list, col_sz=col_sz, just=just, output=output)
        else:
            try:
                col_sz[0]
            except TypeError:
                # A single value was given. Use constant values for each column.
                col_sz = [col_sz for column in in_list[0]]

        return "┌{div_top}┐\n"\
               "│{headers}│\n"\
               "├{divider}┤\n"\
               "│{content}│\n"\
               "└{div_bot}┘"\
            .format(
            headers="│".join([just(str(x[0])[:col_sz[i]], col_sz[i]) for i, x in enumerate(in_list[0])]),
            div_top="┬".join("─"*col_sz[i] for i in range(len(in_list[0]))),
            divider="┼".join("─"*col_sz[i] for i in range(len(in_list[0]))),
            div_bot="┴".join("─"*col_sz[i] for i in range(len(in_list[0]))),
            content="│\n│".join(
                "│".join([just(str(x[1])[:col_sz[i]], col_sz[i]) for i, x in enumerate(row)]
                ) for row in in_list))

    @staticmethod
    def table_from_rows(in_list, col_sz=None, just=None, output=True, max_col=40):
        """
        Returns IN_LIST turned into tables using each item as a row, with
        each column having COL_SZ width.

        IN_LIST is a 2d list where the indexes of each item is its place in the
        table. The first row is treated as a header row.

        Should be in this format:

        ```[
        [header1, header2, ... ],
        [row1val1, row1val2, ... ],
        [row2val1, row2val2, ... ]
        ...
        ]```

        COL_SZ is static column lengths. Default will decide best size.
        JUST is one of str.center, str.ljust or str.rjust. Default is center.
        """
        if output:
            return print(FancyPrinter.table_from_rows(in_list, col_sz=col_sz, just=just, output=False))

        if just is None:
            # Use central justify by default.
            just = str.center

        if col_sz is None:
            # Optional first pass - determine column sizes
            col_sz = [0 for column in in_list[0]]
            for i, row in enumerate(in_list):
                for j, col in enumerate(row):
                    if i == 0:
                        # Add 2 space padding.
                        col_sz[j] = max(col_sz[j], len(str(col)) + 2)
                        if col_sz[j] > max_col: col_sz[j] = max_col
                    else:
                        col_sz[j] = max(col_sz[j], len(str(col)) + 2)
                        if col_sz[j] > max_col: col_sz[j] = max_col
            return FancyPrinter.table_from_rows(in_list, col_sz=col_sz, just=just, output=output)
        else:
            try:
                col_sz[0]
            except TypeError:
                # A single value was given. Use constant values for each column.
                col_sz = [col_sz for column in in_list[0]]

        return "┌{div_top}┐\n"\
               "│{headers}│\n"\
               "├{divider}┤\n"\
               "│{content}│\n"\
               "└{div_bot}┘"\
            .format(
            headers="│".join([just(str(x)[:col_sz[i]], col_sz[i]) for i, x in enumerate(in_list[0])]),
            div_top="┬".join("─"*col_sz[i] for i in range(len(in_list[0]))),
            divider="┼".join("─"*col_sz[i] for i in range(len(in_list[0]))),
            div_bot="┴".join("─"*col_sz[i] for i in range(len(in_list[0]))),
            content="│\n│".join(
                "│".join([just(str(x)[:col_sz[i]], col_sz[i]) for i, x in enumerate(row)]
                ) for i, row in enumerate(in_list) if i > 0))

    @staticmethod
    def table_from_dict(in_list, col_sz=None, just=None, output=True, max_col=40):
        """
        Returns IN_LIST formatted into a table with each column having COL_SZ
        width.

        Each item in IN_LIST is a row.
        The first row has the heading names, in displayed order. It should be
        an ordered iterable, such as a list or tuple.
        All subsequent rows are dictionaries, where the keys are headings and
        values are values.

        Should be in this format:

        ```[
        [heading1, heading2, ... ],
        {heading1:row1val1, heading2:row1val2, ... },
        {heading1:row2val1, heading2:row2val2, ... },
        ...
        ]```

        COL_SZ is static column lengths. Default will decide best size.
        JUST is one of str.center, str.ljust or str.rjust. Default is center.
        """
        if output:
            return print(FancyPrinter.table_from_dict(in_list, col_sz=col_sz, just=just, output=False))

        if just not in (str.ljust, str.center, str.rjust):
            # Use central justify by default.
            just = str.center

        if col_sz is None:
            # Optional first pass - determine column sizes
            col_sz = [0 for column in in_list[0]]
            for i, row in enumerate(in_list):
                for j, col in enumerate(row):
                    if i == 0:
                        # Add 2 space padding.
                        col_sz[j] = max(col_sz[j], len(str(col)) + 2)
                        if col_sz[j] > max_col: col_sz[j] = max_col
                    else:
                        col_sz[j] = max(col_sz[j], len(str(row[col])) + 2)
                        if col_sz[j] > max_col: col_sz[j] = max_col
            return FancyPrinter.table_from_dict(in_list, col_sz=col_sz, just=just, output=output)
        else:
            try:
                col_sz[0]
            except TypeError:
                # A single value was given. Use constant values for each column.
                col_sz = [col_sz for column in in_list[0]]

        # Second pass - determine string to print
        return "┌{div_top}┐\n"\
               "│{headers}│\n"\
               "├{divider}┤\n"\
               "│{content}│\n"\
               "└{div_bot}┘"\
            .format(
            headers="│".join([just(str(x)[:col_sz[i]], col_sz[i]) for i, x in enumerate(in_list[0])]),
            div_top="┬".join("─"*col_sz[i] for i in range(len(in_list[0]))),
            divider="┼".join("─"*col_sz[i] for i in range(len(in_list[0]))),
            div_bot="┴".join("─"*col_sz[i] for i in range(len(in_list[0]))),
            content="│\n│".join(
                "│".join([just(str(row[x])[:col_sz[i]], col_sz[i]) for i, x in enumerate(in_list[0])]
                ) for i, row in enumerate(in_list) if i > 0))

class ToggledFrame(Frame):

    def __init__(self, parent, text="", *args, **options):
        ## Callback when widget is going to be shown.
        self._on_show = options.pop("onshow", None)
        self._on_hide = options.pop("onhide", None)

        Frame.__init__(self, parent, *args,
            relief=options.pop("relief", "sunken"),
            borderwidth=options.pop("borderwidth", 1),
            **options)

        self.show = IntVar()
        self._show = False
        self.show.set(self._show)

        self.title_frame = Frame(self)
        self.title_frame.pack(fill="x", expand=1)

        # Text to use as icons for toggle button
        # (arrindicator Label widget). The "up"
        # is used when not hovered, and "up1" is
        # used when hovered over over the indicator.
        # The same is for "down" and "down1".

        # alt 30    ▲△▵   Triangle up
        self.up      = u"▲"
        self.up1     = u"△"

        # alt 31    ▼▽▿   Triangle down
        self.down    = u"▽"
        self.down1   = u"▼"

        title = Label(self.title_frame, text=text)
        title.pack(side="left", fill="x", expand=1)
        title.bind("<Double-1>", self.toggle)

        arrindicator = Label(self.title_frame, text=self.down)
        arrindicator.bind("<ButtonPress-1>", self.toggle)
        arrindicator.bind("<Enter>", lambda e, s=self,
            state=lambda s: s.up1 if s._show else s.down1:
            arrindicator.config(text=state(s)))
        arrindicator.bind("<Leave>", lambda e, s=self,
            state=lambda s:s.up if s._show else s.down:
            arrindicator.config(text=state(s)))

        arrindicator.pack(side="left", padx=2)
        self.arrindicator = arrindicator

        self._subframe = Frame(self, relief="sunken", borderwidth=1)
        self.sub_frame = Frame(self._subframe)
        self.sub_frame.pack(fill="x", expand=1, padx=2, pady=2)

    def toggle(self, event=None):
        # Toggle internal boolean state, but
        # never keep button highlighted.
        self._show = not self._show
        self.show.set(False)

        if self._show:
            self._subframe.pack(fill="x", expand=1)
            self.arrindicator.config(text=self.up)
            if self._on_show is not None:
                self._on_show()
        else:
            self._subframe.forget()
            self.arrindicator.config(text=self.down)
            if self._on_hide is not None:
                self._on_hide()

class SimpleDialog(Toplevel):

    def __init__(self, parent, title = None):

        Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    #
    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):

        return 1 # override

    def apply(self):

        pass # override


class OptionDialog(SimpleDialog):

    def __init__(self, parent, title=None, default=None, *values):
        """Create dialog with options and store result."""

        # Store for making widgets in body
        self.default = default
        self.values = values

        # Call parent generic dialog constructor.
        super().__init__(parent, title)

    def buttonbox(self):
        # add OK button box.

        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)

        box.pack()

    def body(self, master):

        Label(master, text="Choose an option:").grid(row=0)

        self.val_var = StringVar()
        self.val_var.set(self.default)

        self.opts = OptionMenu(master, self.val_var, self.default, *self.values)
        self.opts.grid(row=0, column=1)

        return self.opts # initial focus

    def apply(self):
        self.result = self.val_var.get()

    def cancel(self):
        self.apply()
        super().cancel()


##def main():
##    FancyPrinter.multi_pairs_table_from_dict({
##    "dog":
##        [
##        [("id", 0), ("name", "benjamin"), ("breed", "labrador")],
##        [("id", 1), ("name", "edward"), ("breed", "poodle")]
##        ],
##    "cat":
##        [
##        [("id", 0), ("name", "katie"), ("favourite shape", "triange")],
##        [("id", 1), ("name", "bethany"), ("favourite shape", "square")]
##        ]
##    })

##    FancyPrinter.multi_rows_table_from_dict({
##    "dog":
##        [
##        ["id", "name", "breed"],
##        [0, "benjamin", "labrador"],
##        [1, "edward", "poodle"]
##        ],
##    "cat":
##        [
##        ["id", "name", "favourite shape"],
##        [0, "katie", "triange"],
##        [1, "bethany", "square"]
##        ]
##    })

##    FancyPrinter.multi_dict_table_from_dict({
##    "dog":
##        [
##        ["id", "name", "breed"],
##        {"id":0, "name":"benjamin", "breed":"labrador"},
##        {"id":1, "name":"edward", "breed":"poodle"}
##        ],
##    "cat":
##        [
##        ["id", "name", "favourite shape"],
##        {"id":0, "name":"katie", "favourite shape":"triange"},
##        {"id":1, "name":"bethany", "favourite shape":"square"}
##        ]
##    })

##
##    w = WgtManager()
##    w.make_window("test", True, TestMenu)
##
##if __name__ == '__main__':
##    main()

##if __name__ == "__main__":
##    root = Tk()
##
##    t = ToggledFrame(root, text='Rotate')
##    t.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")
##
##    Label(t.sub_frame, text='Rotation [deg]:').pack(side="left", fill="x", expand=1)
##    Entry(t.sub_frame).pack(side="left")
##
##    t2 = ToggledFrame(root, text='Resize')
##    t2.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")
##
##    for i in range(10):
##        Label(t2.sub_frame, text='Test' + str(i)).pack()
##
##    t3 = ToggledFrame(root, text='Fooo')
##    t3.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")
##
##    for i in range(10):
##        Label(t3.sub_frame, text='Bar' + str(i)).pack()
##
##    t4 = ToggledFrame(root, text="HAHAHA")
##    t4.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")
##    Label(t4.sub_frame, text="hahahahahahaha").pack()
##
##    root.mainloop()

if __name__ == "__main__":
    w = WgtManager()
    w.make_window("test", True, TestMenu)
    a = Loc(-10, 10)
    print(Loc.__pos__(a))
