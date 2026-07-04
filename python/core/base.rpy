init -5 python in v1FNaSR:
    import threading
    import random
    import math
    import time
    import copy
    import traceback
    import os
    import codecs
    import json
    from collections import deque

    # Фолбек для Py2
    try:
        monotime = time.monotonic
    except:
        from time import time as monotime

    try:
        lock = threading.RLock()
    except:
        class DummyLock(object):
            def acquire(self): pass
            def release(self): pass
            def __enter__(self): return self
            def __exit__(self, *a): pass
        lock = DummyLock()

    global_event = renpy.store.v1FNaSREvent
    display = renpy.store.v1FNaSRDisplay
    v1FNaSRThread = renpy.store.v1FNaSRThread

    execute_in_main_thread = renpy.store.v1rus.execute_in_main_thread # Функция для исполнения кода в главном потоке (например взаимодействия с UI)

    #class _FNaSRMeta(type):
    #    def __init__(cls, name, bases, attrs):
    #        super(_FNaSRMeta, cls).__init__(name, bases, attrs)
    #        if name != "FNaSRBase":
    #            if cls not in FNaSRBase.subclasses["all"]:
    #                FNaSRBase.subclasses["all"].append(cls)
    #            if name != "all":
    #                FNaSRBase.subclasses[name] = cls

    class FNaSRBase(renpy.python.RevertableObject):
        #__metaclass__ = _FNaSRMeta
        #subclasses = {"all": []}

        def update(self): pass
        def reset(self): pass

    #class InfoObject(FNaSRBase):
    #    __slots__ = ("_data",)
    #    __allowed_attrs__ = None  # None = любые, set = whitelist
    #    def __init__(self, **kwargs):
    #        object.__setattr__(self, "_data", {})
    #        for name, value in kwargs.items():
    #            self._validate_attr(name)
    #            self._data[name] = value
    #    def _validate_attr(self, name):
    #        if name.startswith("_"):
    #            raise AttributeError("Private attributes are forbidden")
    #        allowed = self.__allowed_attrs__
    #        if allowed is not None and name not in allowed:
    #            raise AttributeError("Attribute '{}' is not allowed".format(name))
    #    def __getattr__(self, item):
    #        try:
    #            return self._data[item]
    #        except KeyError:
    #            raise AttributeError(item)
    #    def __setattr__(self, key, value):
    #        self._validate_attr(key)
    #        self._data[key] = value



    class _ReadOnly(FNaSRBase):
        def _readonly(self, *args, **kwargs):
            raise TypeError("This object is read-only")

    class ConstList(_ReadOnly):
        def __init__(self, data):
            self._data = tuple(data)

        def __getitem__(self, index):
            return self._data[index]

        def __len__(self):
            return len(self._data)

        def __iter__(self):
            return iter(self._data)

        # запрещаем модификации
        append = extend = insert = remove = pop = clear = sort = reverse = _ReadOnly._readonly

        def __repr__(self):
            return repr(self._data)

    class ConstDict(_ReadOnly):
        def __init__(self, data):
            self._data = dict(data)

        def __getitem__(self, key):
            return self._data[key]

        def get(self, key, default=None):
            return self._data.get(key, default)

        def keys(self):
            return self._data.keys()

        def values(self):
            return self._data.values()

        def items(self):
            return self._data.items()

        # запрещаем модификации
        clear = pop = popitem = setdefault = update = _ReadOnly._readonly

        def __repr__(self):
            return repr(self._data)

    class ConstSet(_ReadOnly):
        def __init__(self, data):
            self._data = frozenset(data)

        def __contains__(self, item):
            return item in self._data

        def __iter__(self):
            return iter(self._data)

        def __len__(self):
            return len(self._data)

        add = remove = discard = pop = clear = update = difference_update = intersection_update = symmetric_difference_update = _ReadOnly._readonly

        def __repr__(self):
            return repr(self._data)

    class ConstByteArray(_ReadOnly):
        def __init__(self, data):
            self._data = bytes(data)

        def __getitem__(self, i):
            return self._data[i]

        def __len__(self):
            return len(self._data)

        def __repr__(self):
            return repr(self._data)

    def freeze(value):
        if isinstance(value, dict):
            return ConstDict({k: freeze(v) for k, v in value.items()})
        if isinstance(value, (list, tuple)):
            return ConstList([freeze(v) for v in value])
        if isinstance(value, set):
            return ConstSet([freeze(v) for v in value])
        if isinstance(value, bytearray):
            return ConstByteArray(value)
        return value


    class _ConstMeta(type):
        def __new__(mcls, name, bases, namespace):
            frozen = {}
            for k, v in namespace.items():
                frozen[k] = freeze(v)
            return type.__new__(mcls, name, bases, frozen)

        def __setattr__(cls, name, value):
            raise AttributeError("Constants are read-only")

    class ConstantBase(FNaSRBase):
        __metaclass__ = _ConstMeta

    class Constants(ConstantBase):
        DEFAULT_HOUR_TIME = 89
        DEFAULT_MAX_PANIC = 15
        DEFAULT_ROLLBACK_THRESHOLD = 10
        DEFAULT_UPDATE_STEP = 12
        KEYS = tuple((
            #"up", "down", "left", "right", "enter", "escape",
            "q", "w", "e", "r", "t", "y", "u", "i", "o", "p",
            "a", "s", "d", "f", "g", "h", "j", "k", "l",
            "z", "x", "c", "v", "b", "n", "m",
        ))
        MOD_FILES_PATH = "v1rus_team/FNaSR/"
        ENEMY_MOVE_CHANCE_FACTOR_RANGE = tuple((1, 200))
        MAX_AI_LEVEL = 20
        MAX_CHANGE_FACTOR_PENALTY = 50

    class ResultNight(ConstantBase):
        LOSS=0
        WIN=1







    class DebugInfo(object):
        def __init__(self, name=None, color=None, obj=None, additional_info=None):
            self.color = str(color)
            self.name = str(name)
            self.obj = obj
            self.additional_info = additional_info
            if self.additional_info is not None:
                self.additional_info = list(self.additional_info)

            if obj is not None:
                if name is None:
                    self.name = repr(obj)

                self.type_name = type(obj).__name__
                self.type_class = type(obj)

        @staticmethod
        def _get_enemy_general_info(enemy):
            return [
                "camera: {}({}/{})\n".format(enemy.enemy_path.get_camera_id_by_loc(), enemy.enemy_path.location, len(enemy.enemy_path)),
                "path: {}\n".format(repr(enemy.enemy_path.paths).replace("[", "[[")),
                "difficulty: {}\n".format(enemy.difficulty),
                "ai_level: {}\n".format(enemy.ai_level),
            ]

        @classmethod
        def get_enemy_debug_text(cls, enemy):
            lines = []
            if enemy.debug_info.name is not None:
                lines.append("{}({})\n".format(enemy.tag, enemy.debug_info.name))
            else:
                lines.append("{}\n".format(enemy.tag))

            lines += cls._get_enemy_general_info(enemy)
            if enemy.debug_info.additional_info is not None:
                for text, variable in enemy.debug_info.additional_info:
                    if callable(variable):
                        lines.append("{}: {}\n".format(text, variable()))
                    else:
                        lines.append("{}: {}\n".format(text, variable))

            if enemy.debug_info.color is not None:
                lines.insert(0, "{color=%s}" % enemy.debug_info.color)
                lines.append("{/color}")

            lines.append("---------------")

            result = ""
            for line in lines:
                result += line
            
            return result.strip()

        @classmethod
        def generate_enemy_debug_text(cls, enemy):
            lines = ["{}\n".format(enemy.tag)]
            lines += cls._get_enemy_general_info(enemy)
            lines.append("---------------")

            result = ""
            for line in lines:
                result += line
            
            return result.strip()

        @staticmethod
        def get_images():
            result = []

            sl = renpy.display.core.scene_lists()

            for i in sl.get_all_displayables():
                result.append(repr(i))

            return result


    def log(message):
        if not message.strip():
            return
        try:
            renpy.log("FNaSR | %s" % message)
        except Exception:
            pass
