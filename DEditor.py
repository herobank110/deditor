"""
DEngine definition for GUI editor of values.
"""

from tile_based_node_game2_ttk import *
import tkinter.constants
from tkinter.ttk import Label
import ast, linecache, sys

def DPROPERTY(*args, **kw):
    """
    Mark a variable to be used by DEditor. Must be placed above the variable.

    Available specifiers (not case-sensitive):
    edit_anywhere, visible_anywhere, category=VALUE, display_name=VALUE

    Example
    > DPROPERTY()
    > my_var = 10
    """
    return args, kw
def DFUNCTION(*args, **kw):
    return args, kw
def DCLASS(*args, **kw):
    return args, kw
def DSTRUCT(*args, **kw):
    return args, kw
def DENUM(*args, **kw):
    return args, kw
def DINTERFACE(*args, **kw):
    return args, kw


class _dattribute(object):
    """
    Base class for internal d* attribute classes, used for
    reading and writing to file and validation.
    """
    ## Set of all available non keyword specifiers
    noname_spec = None
    ## Set of all available keyword specifiers
    named_spec = None

class _dproperty(_dattribute):
    noname_spec = set(("edit_anywhere", "visible_anywhere"))
    named_spec  = set(("category", "display_name"))

    def __init__(self, *args, **kw):
        """
        Available kw are code_line, prop_line, ast_dict.
        """

        # Extract options from source strings.

        self.code_line = kw.get("code_line")
        if self.code_line:
            self.code_line = self.code_line.rstrip("\n")
        else:
            return

        self.prop_line = kw.get("prop_line")
        if self.prop_line:
            self.prop_line = self.prop_line.rstrip("\n")
        else:
            return

        self.ast_dict = kw.get("ast_dict")
        if self.ast_dict:
            # name │ lineno │ value │ namespace

            # Collection will check if namespace exists,
            # and create new collection if necessary.
            pass
        else:
            pass

        # Set instance attribute values.
        self.prop_args, self.prop_kw = eval(self.prop_line, globals())
        # Ensure keywords are case matched.
        self.prop_kw = {CasePicker.to_snake(k):v for k, v in self.prop_kw.items()}

        self.field_name = self.ast_dict["name"]
        self.default_val = self.ast_dict["value"]

        # Set options from DPROPERTY specifiers.
        self.data_type = self.prop_kw.get("type", type(self.default_val))
        ##self.default_val = self.data_type(self.default_val)
        self.category = self.prop_kw.get("category", "")
        #self.category = self.category.split("|") # Category|Subcategory
        self.display_name = self.prop_kw.get("display_name", CasePicker.to_pascal(self.field_name))

        # Set input ranges.
        self.from_ = self.prop_kw.get("from",
                     self.prop_kw.get("min", None))
        self.to    = self.prop_kw.get("to",
                     self.prop_kw.get("max", None))
        try:
            self.from_, self.to = self.prop_kw.get("range")
        except:
            pass

    def __str__(self):
        return "Showing details for DPROPERTY '{repr}':\n"\
            "\tCode line is '{code_line}'\n"\
            "\tField name is '{field_name}'\n"\
            "\tData type is '{data_type}'\n"\
            "\tDefault value is '{default_val}'\n"\
            "\tProperty line is '{prop_line}'\n"\
            "\tProperty arguments are '{prop_args}'\n"\
            "\tProperty keywords are '{prop_kw}'\n"\
            .format(repr=repr(self),
            code_line=self.code_line,
            field_name=self.field_name,
            data_type=self.data_type.__name__,
            default_val=self.default_val,
            prop_line=self.prop_line,
            prop_args=", ".join(self.prop_args),
            prop_kw=self.prop_kw)

class DAttrCollection:
    """
    Class containing all d* attributes belonging to a single collection.
    """
    def __init__(self, collection_name=None):
        ## Name of the collection.
        self.collection_name = collection_name if collection_name else ""

        ## Set of all _dproperty objects in this collection.
##        self.dproperties = set()

        ## List of all _dproperty objects in this collection.
        self.dproperties    = []

        ## List of all DAttrCollection objects in this collection.
        self.subcollections = []

        ## Active widget used to manipulate values, if GUI is used.
        self.widget         = None

    def add_prop(self, prop_to_add, namespace):
        """Add _dproperty object PROP_TO_ADD to the properties list under
        namespace NAMESPACE. Will create namespace if necessary.

        Namespace may be provided as a list of nested hierarchy, or a string
        with dot (.) separated nested hierarchy."""

        # Format namespace into a list if it was provided
        # in . separated string form, ie,
        # "myname.myname2.name3" -> ["myname", "myname2", "name3"]
        if isinstance(namespace, str):
            namespace = namespace.split(".")

        if len(namespace) == 0:
            # Invalid input.
            return

        elif len(namespace) == 1:
            # Add to itself.
            self.dproperties.append(prop_to_add)

        else:
            # Create new/use existing subcollection.

            # Get name of second element.
            # This is the namespace that will be directly
            # contained within this one.
            name = namespace[1]

            # Check if we have that subcollection already.
            for sub in self.subcollections:
                if sub.collection_name == name:
                    sub.add_prop(prop_to_add, namespace[1:])
                    return

            # Otherwise make a new collection.
            new_col = DAttrCollection(collection_name=name)
            self.subcollections.append(new_col)
            new_col.add_prop(prop_to_add, namespace[1:])

# File d* attribute extraction

class MyNodeViewer:
    def __init__(self):
        pass

    def visit(self, file_object):
        """Visit all nodes in a file and add to self.found dictionary."""

        module = ast.parse(file_object.read())
        # TODO remove prefixes such as C:\Users\...
        module_name = file_object.name.rstrip(".py").replace("/", ".")

        exec("import %s"%module_name)
        self._module = eval(module_name)

        self.found = {"vars":[], "classes":[], "funcs":[]}
        self.found_classes = set()

        self._explorer(self, [module_name]).visit(module)

    def visit_with_print(self, file_object):
        """Visit all nodes in a file and add to self.found dictionary,
        and print the findings."""

        module = ast.parse(file_object.read())
        # TODO remove prefixes such as C:\Users\...
        # For now, just assume they are relative paths.
##        module_name = ".".join(file_object.name.split("\\"))
##        module_name.rstrip(".py")
        module_name = file_object.name.rstrip(".py")
        module_name = module_name.replace("/", ".")

        try: sys.path.insert(0, sys._MEIPASS)
        except: sys.path.insert(0, sys.argv[0])

        exec("import %s"%module_name)
        self._module = eval(module_name)

        # Define table column headings.
        self.found = {"vars":[("name", "lineno", "value", "namespace")],
            "classes":[("name", "lineno", "namespace")],
            "funcs":[("name", "lineno", "namespace")]}
        self.found_classes = set()

        self._explorer(self, [module_name]).visit(module)

        # Print findings in tables.
        FancyPrinter.multi_dict_table_from_dict(self.found)

        # Remove table column headings for easy access.
        for table in self.found:
            self.found[table].pop(0)

    class _explorer(ast.NodeVisitor):
        """
        Internal class for viewing a node and adding found variables,
        functions and classes to the manager MyNodeViewer found dictionary.
        """

        def __init__(self, manager, parent=None):
            """Create an explorer with MANAGER in namespace PARENT."""
            if parent is None:
                self.parent = []
            else:
                self.parent = parent
            self.manager = manager

            super().__init__()

        def visit_ClassDef(self, node):
            """Called when visiting a class definition."""
            if node in self.manager.found_classes:
                return

            self.manager.found_classes.add(node)
            self.manager.found["classes"].append({"name":node.name,
                "lineno":node.lineno,
                "namespace":".".join(self.parent)})

            # Keep checking all nodes in this class.
            for my_node in node.body:
                self.manager._explorer(self.manager, self.parent + [node.name]).visit(my_node)

        def visit_Name(self, node):
            """Called when visiting a variable definition."""
            if isinstance(node.ctx, ast.Store):
                self.manager.found["vars"].append({"name":node.id,
                    "lineno":node.lineno,
                    "value":eval("self.manager._module." + ".".join(self.parent[1:] + [node.id])),
                    "namespace":".".join(self.parent)})

        def visit_FunctionDef(self, node):
            """Called when visiting a function definition."""
            self.manager.found["funcs"].append({"name":node.name,
                "lineno":node.lineno,
                "namespace":".".join(self.parent)})

def dcompile_ast(file_object):
    """
    Read the specified file and extract any d* attributes, using advanced
    syntax reading techniques.
    """
    # Use ast module to read nodes (classes, funcs and vars)

    my_node_viewer = MyNodeViewer()


        # If you want to print the variables, function and classes,
        # uncomment this line:
    my_node_viewer.visit_with_print(file_object)
##    my_node_viewer.visit(file_object)



    # Check each of the locations that ast found.

##    collections = {}
    collection = DAttrCollection()
    waiting_for_prop_code = False

    # Check variables.
    for var_row in my_node_viewer.found["vars"]:
        # name │ lineno │ value │ namespace


        # Set collection name. This only needs
        # to happen once, so putting it in the
        # loop is unnecessary, but we need to ensure
        # that the loop is executed at least once.
        collection.collection_name = var_row["namespace"].split(".")[0]

        for i in itertools.count(1):
            # Work backwards to see if there is a DPROPERTY line above.
            line = linecache.getline(file_object.name, var_row["lineno"] - i
                ).strip().rstrip("\n")

            if line.startswith("DPROPERTY("):
                # This is a DPROPERTY!
                prop_line = line
                code_line = linecache.getline(file_object.name, var_row["lineno"]
                    ).strip().rstrip("\n")
                new_prop = _dproperty(code_line=code_line, prop_line=prop_line,
                    ast_dict=var_row)

##                try:
##                    collections[var_row["namespace"]].append(new_prop)
##                except KeyError:
##                    collections[var_row["namespace"]] = [new_prop]

                collection.add_prop(new_prop, var_row["namespace"])
                break

            elif len(line) > 0 and line[0].isalnum():
                # This line is not a comment and is some other unrelated code.
                break

    # Go back to the beginning of the file.
##    file_object.seek(0)
##    for i, line in enumerate(file_object):
##        if waiting_for_prop_code and len(line) > 1 and line.count("=") >= 1:
##            waiting_for_prop_code = False
##            code_line = line
##            new_prop = _dproperty(code_line=code_line, prop_line=prop_line)
##            collection.add_prop(new_prop)
##
##        if line.strip().startswith("DPROPERTY("):
##            prop_line = line
##            waiting_for_prop_code = True

    return collection
##    return collections

##def dcompile(file_object):
##    """
##    Read the specified file and extract any d* attributes.
##    """
##
##    collection = DAttrCollection()
##    waiting_for_prop_code = False
##
##    for i, line in enumerate(file_object):
##        if waiting_for_prop_code and len(line) > 1 and line.count("=") >= 1:
##            waiting_for_prop_code = False
##            code_line = line
##            new_prop = _dproperty(code_line=code_line, prop_line=prop_line)
##            collection.add_prop(new_prop)
##
##        if line.strip().startswith("DPROPERTY("):
##            prop_line = line
##            waiting_for_prop_code = True
##
##    return collection


# GUI Menus

# Property editors

class PropEditMenuBase(MyMenu):
    """
    Base class for property editor menus.
    """
    def _pre_config(self, cnf):
        ## Reference to _dproperty object used for this menu.
        self.prop = cnf.pop("prop", None)

    def get_value(self):
        """Override to return current value."""
        return None

class PropEditNum(PropEditMenuBase):
    """
    Property editor for numerical values.
    """
    def make_widgets(self):
        # Ensure _dproperty object is valid.
        if not self.prop:
            return

        self.val_var = StringVar()
        self.val_var.set(self.prop.default_val)
        NumEdit(self.master,
            text=self.prop.display_name,
            variable=self.val_var,
            valtype=self.prop.data_type,
            from_=self.prop.from_,
            to=self.prop.to,
            precision=4,
            mode="external"
            )#.pack(fill=X, expand=TRUE)

    def get_value(self):
        return self.prop.data_type(self.val_var.get())

class PropEditLoc(PropEditMenuBase):
    """
    Property editor for Loc values.
    """
    def make_widgets(self):
        # Ensure _dproperty object is valid.
        if not self.prop:
            return

        self.val_var = LocVar()
        self.val_var.set(self.prop.default_val)
        LocEdit(self.master,
            text=self.prop.display_name,
            variable=self.val_var,
            from_=None,
            to=None,
            mode="external"
            )#.pack(side=LEFT, fill=X, expand=TRUE)

    def get_value(self):
        return self.val_var.get()

class PropEditBool(PropEditMenuBase):
    """
    Property editor for boolean values.
    """
    def make_widgets(self):
        # Ensure _dproperty object is valid.
        if not self.prop:
            return

        my_column, my_row = self.master.grid_size()
        my_row += 1 # Offset to allow for resize frames on row 0

        self.val_var = IntVar()
        self.val_var.set(self.prop.default_val)

        Label(self.master,
            text=self.prop.display_name
            ).grid(row=my_row, column=0, pady=5, sticky=W)
        Checkbutton(self.master,
            variable=self.val_var
            ).grid(row=my_row, column=2, padx=3, sticky=EW)

    def get_value(self):
        return self.prop.data_type(self.val_var.get())

class PropEditText(PropEditMenuBase):
    """
    Property editor for generic text values.
    """
    def make_widgets(self):
        # Ensure _dproperty object is valid.
        if not self.prop:
            return

        self.val_var = StringVar()
        self.val_var.set(self.prop.default_val)

        my_column, my_row = self.master.grid_size()
        my_row += 1 # Offset to allow for resize frames on row 0.
        Label(self.master,
            text=self.prop.display_name
            ).grid(row=my_row, column=0, pady=5, sticky=W)
        Entry(self.master,
            textvariable=self.val_var
            ).grid(row=my_row, column=2, padx=3, sticky=EW)

    def get_value(self):
        return self.val_var.get()

# General editor menus

class EditorMainMenu(MyMenu):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.collection_menu = None

    def set_collection(self, collection_attr):
        """
        Destroy old collection editor menu and make new one using data from
        collection_attr.
        """
        if self.collection_menu:
            self.collection_menu.destroy()

        self.collection_menu = _CollectionEditorMenu(collection=collection_attr)
        self.collection_menu.pack(fill=BOTH, expand=TRUE, padx=10, pady=10)

class EditorGuiUtilities(object):
    @staticmethod
    def get_best_edit_widget(prop):
        """
        Decide which editor to use based on data type of dproperty PROP.

        :return PropEditMenuBase: Appropriate class of editing widget to use.
        """

        # Use Text edit by default.
        widget_to_make = PropEditText

        # Use LocEdit for Loc objects.
        if prop.data_type == Loc:
            widget_to_make = PropEditLoc

        # Use NumEdit for numerical objects.
        elif prop.data_type in (int, float):
            widget_to_make = PropEditNum

        # Use Checkbutton for boolean objects.
        elif prop.data_type == bool:
            widget_to_make = PropEditBool

        else:
            try:
                # Check if the property can be accessed with indexes.
                prop.default_val[0]
                # Use LocEdit for non-Loc iterable objects.
                # TODO: this should be changed to support dynamic
                # sized list/dict/tuple/set of a given type, or
                # self-determined type widgets, where the user can
                # select which editor they wish to use.
                if prop.data_type != str:
                    widget_to_make = PropEditLoc
            except IndexError:
                # Use LocEdit for non-Loc iterable objects.
                # The data is an iterable, but its has no
                # data in index 0.
                if prop.data_type != str:
                    widget_to_make = PropEditLoc
            except TypeError:
                # Unrecognised type reached.
                # Use Text edit by default.
                pass

        return widget_to_make

class _CollectionEditorMenu(MyMenu):
    """
    Menu for editing a collection of attributes with GUI controls.
    """

    def _pre_config(self, cnf):
        self.attr_collection    = cnf.pop("collection", None)
        self.last_right_bias    = 0.0
        self.longest_label      = 0
        self.longest_entry      = 0
        self.created            = {}

        if self.attr_collection is not None:
            self.attr_collection.widget = self

    def make_widgets(self):
        if not self.attr_collection:
            return

##        # Create title.
##        Label(self,
##            text=self.attr_collection.collection_name
##            ).pack(padx=5, pady=10)

        lself = ToggledFrame(self, text=self.attr_collection.collection_name)
        lself.pack(fill=BOTH, expand=TRUE, padx=0, pady=3)

        # Create nested collections, if necessary.
        # Create widgets before its own properties to show
        # these are not contained directly in this collection.
        for sub in self.attr_collection.subcollections:
            # Subcollections list is not empty, meaning
            # there is at least one subcollection to make.
            _CollectionEditorMenu(lself.sub_frame, collection=sub
                ).pack(fill=BOTH, expand=TRUE)

        self.prop_frame = ToggledFrame(lself.sub_frame, text="Properties",
            onshow=self.on_show_prop, relief="flat")
        self.prop_frame.pack(fill=BOTH, expand=TRUE)

        # Create each property edit widgets.
        for prop in self.attr_collection.dproperties:
            # Choose appropriate widget class.
            widget_to_make = EditorGuiUtilities.get_best_edit_widget(prop)
            # Make the chosen edit widget.
            new_widget = widget_to_make(self.prop_frame.sub_frame, prop=prop)

            # Add to created widgets dictionary.
            self.created[prop.field_name] = new_widget


        # Add widgets for label-entry column resize.

        self.spacer_l = Labelframe(self.prop_frame.sub_frame, text="l")
        self.spacer_l.grid(row=0, column=0, sticky=NSEW)
        self.spacer_r = Labelframe(self.prop_frame.sub_frame, text="l")
        self.spacer_r.grid(row=0, column=2, sticky=NSEW)

        Style().configure("mid.TFrame", background="light grey")

        self.resize_frame = Frame(self.prop_frame.sub_frame, style="mid.TFrame", width=10, height=3)
        self.resize_frame.grid(row=0, column=1, rowspan=1000, padx=2, sticky=NSEW)
        self.resize_frame.bind("<ButtonPress-1>", self.on_user_resize_start)
        self.resize_frame.bind("<Button1-Motion>", self.on_user_resize)

        self.prop_frame.sub_frame.bind("<Configure>", self.on_parent_resize)

        ##self.resize()
        ##self.after(1, lambda :self.prop_frame.sub_frame.grid_propagate(0))
        ##self.after(1, self.init_longest_columns)

    def get_values(self, values=None, siblings=None):
        """Returns current values in collection's widgets."""

        if values is None:
            # First time being called. Create
            # a new dictionary.
            values = {}

        # Add values from this collection's properties.

        for name, widget in self.created.items():
            namespace = widget.prop.ast_dict["namespace"]
            if values.get(namespace) is None:
                values[namespace] = {}
            values[namespace][name] = widget.get_value()

        # Keep adding properties from nested collections,
        # or return the current values if possible.

        # First check subcollections.
        subs = self.attr_collection.subcollections.copy()
        if subs:
            # There are 1 or more subcollection to go through.
            if siblings:
                subs += siblings
            return subs.pop(0).widget.get_values(values, subs)

        # Next check siblings.
        if siblings:
            # Siblings is not None, (hence list) and is not empty.
            return siblings.pop(0).widget.get_values(values, siblings)

        # Otherwise we have already reached the end of the chain.
        # Return all the values we have gathered.
        return values

    def on_show_prop(self):
        self.resize()
        self.after(1, lambda :self.prop_frame.sub_frame.grid_propagate(0))
        self.after(1, self.init_longest_columns)

    def init_longest_columns(self):
        longest_label = 0
        longest_entry = 0
        for widget in self.prop_frame.sub_frame.grid_slaves():
            if type(widget) == Label:
                width = widget.winfo_width()
                if width > longest_label:
                    longest_label = width

            elif type(widget) == Entry:
                width = widget.winfo_width()
                if width > longest_entry:
                    longest_entry = width

        self.longest_label = longest_label
        self.longest_entry = longest_entry

    def on_user_resize_start(self, event):
        """Called when user presses LMB on resize frame"""
        # Save offset for use while dragging.
        self._mouse_drag_offset = self.resize_frame.winfo_rootx() - event.x_root

    def on_user_resize(self, event):
        """Called when user mouse mouse while holding LMB on resize frame"""
        self.resize_scaled(drag_rootx=event.x_root + self._mouse_drag_offset)

    def on_parent_resize(self, event):
        """Called when property frame resized by external forces."""
        #self.resize()
        #self.resize_scaled(drag_rootx=self.resize_frame.winfo_rootx())
        self.resize_scaled(current=MathStat.lerp(0,
            self.prop_frame.winfo_width(), self.last_right_bias))

    def resize_scaled(self, current=None, drag_rootx=None):
        """Resize field names and entry columns.

        If CURRENT is supplied, that will be used as the pixel offset column
        separator.
        If DRAG_ROOTX is supplied, that will be the root (screen) pixels x of
        column separator.
        If neither are supplied, function will not work.
        """

        if current is None:
            if drag_rootx is None:
                return
            # Convert root position to prop_frame relative position.
            current = drag_rootx - self.prop_frame.winfo_rootx()
        full = self.prop_frame.winfo_width()

        # this is the left hand "fieldname" side
        diff = current - self.longest_label
        if diff < 1:
            current -= diff

        # this is the right hand "input" side
        diff = current + self.longest_entry - full + 26
        if diff > 1:
            current -= diff

        self.resize(current/full, full)

    def resize(self, right_bias=None, total=None):
        if total is None:
            total = self.prop_frame.winfo_width()
            #total = 300

        if right_bias is None:
            right_bias = self.last_right_bias
        else:
            self.last_right_bias = right_bias

        l_width = MathStat.lerp(0, total, right_bias)
        r_width = total - l_width - 20

        self.spacer_l.config(width=l_width)
        self.spacer_r.config(width=r_width)

def main():

    with open("test2_class.py", buffering=8096) as file:
##        my_collection = dcompile(file)
        my_collection = dcompile_ast(file)

    #my_collection.collection_name = "My New Collection"

    #w = WgtManager()
    #w.make_window("DEditor", first_menu=EditorMainMenu, start_mainloop=False)
    #w._cur_menu.set_collection(my_collection)
    #return w.start_mainloop()

if __name__ == '__main__':
    main()


