from DEditor import DPROPERTY

class MyClass:
    DPROPERTY()
    attr1 = 0

    DPROPERTY()
    attr2 = 0.3

    attr3 = [1,2,3]

    class Dog:
        DPROPERTY()
        attr1_1 = 1.1
        class Cat:
            strange_hierarchy = True

    def dog(self):
        return self.attr1

    class SecondClass:
        attr3 = 38383


DPROPERTY()
global_attr1 = 1

DPROPERTY(type="Loc")
icon_position = (100, -200)

DPROPERTY()
icon_scale = 0.25

DPROPERTY()
my_really_cool_attribute = "haha"

def my_global_func(arg1, arg2):
    """
    My documentation
    """
    pass
