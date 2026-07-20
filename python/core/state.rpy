init 5 python in v1FNaSR:
    class State(FNaSRBase):
        """
        Механизм именованных снимков состояния произвольных объектов
        (по сути -- ручной save/restore точки, независимый от rollback
        RenPy, который в этом моде не используется).

        Для класса объекта можно зарегистрировать свой обработчик через
        add_state_handler(); если обработчик не зарегистрирован, можно
        явно попросить использовать дефолтный (глубокая копия __dict__)
        через use_default_handler=True в save_state().
        """

        _state_handler = {}

        @staticmethod
        def _default_state_handler(obj):
            return copy.deepcopy(obj.__dict__)

        @classmethod
        def _get_handler(cls, obj, use_default):
            """Ищет обработчик по MRO класса объекта, чтобы работало и с наследниками."""
            for base in obj.__class__.__mro__:
                if base in cls._state_handler:
                    return cls._state_handler[base]

            if use_default:
                return cls._default_state_handler

            return None

        @classmethod
        def save_state(cls, obj, name_state, use_default_handler=False):
            """Сохраняет снимок состояния obj под именем name_state. Возвращает bool успеха."""
            if obj is None or isinstance(obj, type):
                return False

            handler = cls._get_handler(obj, use_default_handler)
            if handler is None:
                return False

            if not hasattr(obj, "_states"):
                obj._states = {}

            obj._states[name_state] = handler(obj)
            return True

        @classmethod
        def load_state(cls, obj, name_state, clear=True):
            """
            Восстанавливает ранее сохранённый снимок в obj.

            clear=True полностью заменяет __dict__ объекта содержимым
            снимка (объект "становится" тем, чем был на момент сохранения).
            clear=False домешивает снимок поверх текущего состояния.
            """
            if not hasattr(obj, "_states"):
                return False

            if name_state not in obj._states:
                return False

            state = obj._states[name_state]

            if clear:
                obj.__dict__.clear()

            obj.__dict__.update(copy.deepcopy(state))
            return True

        @classmethod
        def add_state_handler(cls, processed_class, handler):
            """Регистрирует обработчик сохранения состояния для конкретного класса."""
            if isinstance(processed_class, type) and callable(handler):
                cls._state_handler[processed_class] = handler
