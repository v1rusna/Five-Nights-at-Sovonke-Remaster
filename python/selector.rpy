init -5 python in v1FNaSR:
    class Selector(FNaSRBase):
        is_show = False
        __is_start = False

        @classmethod
        def start(cls):
            if not cls.__is_start:
                renpy.show_screen("V1BaseUIScreenFNaSR")
                cls.__is_start = True

        @classmethod
        def stop(cls):
            if cls.__is_start:
                renpy.hide_screen("V1BaseUIScreenFNaSR")
                cls.__is_start = False

        @classmethod
        def show(cls):
            if not cls.is_show:
                cls.is_show = True
                renpy.show_screen("V1GameMenuSelectorFNaSR")

        @classmethod
        def hide(cls):
            if cls.is_show:
                cls.is_show = False
                renpy.hide_screen("V1GameMenuSelectorFNaSR")



