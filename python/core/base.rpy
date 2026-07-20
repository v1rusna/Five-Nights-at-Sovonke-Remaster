
init python in v1FNaSR:
    import threading
    import random
    import math
    import time
    import copy
    import traceback
    import os
    import codecs
    import json
    import sys
    from collections import deque

    if sys.version_info[0] == 2:
        import __builtin__
        native_str = __builtin__.str  # настоящий bytes-str, а не unicode из песочницы RenPy
    else:
        native_str = str

    # --- Совместимость Py2/Py3 -------------------------------------------
    # time.monotonic появился в Python 3.3, в Py2 его нет вовсе.
    # Ловим именно AttributeError, а не всё подряд -- если что-то другое
    # сломается внутри time, мы должны это увидеть, а не проглотить.
    try:
        monotime = time.monotonic
    except AttributeError:
        from time import time as monotime

    # threading.RLock есть практически везде, но на некоторых урезанных
    # платформах (например, кастомные Android-сборки) модуль threading
    # может быть недоступен. DummyLock -- осознанный фолбек на этот случай,
    # а не попытка скрыть реальную ошибку.
    try:
        lock = threading.RLock()
    except AttributeError:
        class DummyLock(object):
            def acquire(self):
                pass

            def release(self):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

        lock = DummyLock()

    global_event = renpy.store.v1FNaSREvent
    display = renpy.store.v1FNaSRDisplay
    v1FNaSRThread = renpy.store.v1FNaSRThread

    # Функция для исполнения кода в главном потоке (например, взаимодействия с UI)
    execute_in_main_thread = renpy.store.v1rus.execute_in_main_thread


    class FNaSRBase(renpy.object.Object):
        """Базовый класс для всех объектов мода."""

        def update(self):
            pass

        def reset(self):
            pass


    # === Иммутабельные контейнеры ==========================================
    # Нужны там, где важно гарантировать, что константы мода нельзя случайно
    # изменить во время игры (например, из консоли отладки или чужого кода).

    def with_metaclass(meta, *bases):
        """
        Создаёт базовый класс с заданным метаклассом.
        Работает одинаково в Python 2 и Python 3, без внешних зависимостей.
        """
        class metaclass(meta):
            def __new__(cls, name, this_bases, namespace):
                if this_bases is None:
                    return type.__new__(cls, native_str(name), (), namespace)
                return meta(native_str(name), bases, namespace)

            @classmethod
            def __prepare__(cls, name, this_bases):
                return meta.__prepare__(native_str(name), bases)

        return type.__new__(metaclass, native_str('temporary_class'), (), {})

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

        add = remove = discard = pop = clear = update = difference_update = \
            intersection_update = symmetric_difference_update = _ReadOnly._readonly

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
        """Рекурсивно превращает изменяемые коллекции в их read-only аналоги."""
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
        """
        Метакласс, замораживающий все атрибуты класса при его создании.
        """

        def __new__(mcls, name, bases, namespace):
            frozen = dict((k, freeze(v)) for k, v in namespace.items())
            return type.__new__(mcls, name, bases, frozen)

        def __setattr__(cls, name, value):
            raise AttributeError("Constants are read-only")

    class ConstantBase(with_metaclass(_ConstMeta, FNaSRBase)):
        pass

    class Constants(ConstantBase):
        DEFAULT_HOUR_TIME = 89
        DEFAULT_MAX_PANIC = 15
        DEFAULT_ROLLBACK_THRESHOLD = 10
        DEFAULT_UPDATE_STEP = 12
        KEYS = tuple((
            # "up", "down", "left", "right", "enter", "escape",
            "q", "w", "e", "r", "t", "y", "u", "i", "o", "p",
            "a", "s", "d", "f", "g", "h", "j", "k", "l",
            "z", "x", "c", "v", "b", "n", "m",
        ))
        MOD_FILES_PATH = "v1rus_team/FNaSR/"
        ENEMY_MOVE_CHANCE_FACTOR_RANGE = tuple((1, 200))
        MAX_AI_LEVEL = 20
        MAX_CHANGE_FACTOR_PENALTY = 50

    class ResultNight(ConstantBase):
        LOSS = 0
        WIN = 1


    # === Отладочная информация ============================================

    class DebugInfo(object):
        """Контейнер отладочных данных, привязываемых к объекту (например, к врагу)."""

        def __init__(self, name=None, color=None, obj=None, additional_info=None):
            self.name = str(name)
            self.color = str(color)
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
                "camera: {}({}/{})\n".format(
                    enemy.enemy_path.get_camera_id_by_loc(),
                    enemy.enemy_path.location,
                    len(enemy.enemy_path),
                ),
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
            return "".join(lines).strip()

        @classmethod
        def generate_enemy_debug_text(cls, enemy):
            lines = ["{}\n".format(enemy.tag)]
            lines += cls._get_enemy_general_info(enemy)
            lines.append("---------------")
            return "".join(lines).strip()

        @staticmethod
        def get_images():
            sl = renpy.display.core.scene_lists()
            return [repr(i) for i in sl.get_all_displayables()]

        @staticmethod
        def _activities_all_pioneer(activity):
            for enemy in game.enemy_system:
                enemy.activity = activity


    def log(message):
        """
        Логирует сообщение мода через renpy.log с префиксом "FNaSR | ".

        message должен быть строкой. Пустые/пробельные сообщения
        игнорируются осознанно (незачем засорять лог).
        """
        if not message.strip():
            return
        renpy.log("FNaSR | %s" % message)
