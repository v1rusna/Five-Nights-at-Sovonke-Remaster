
init python in v1FNaSR:
    class _DifficultyCallback:
        _easy_d = (
            "Легкая сложность",
            "Для тех кто хочет расслабленно пройти игру",
            "Уменьшенная активность пионеров",
            "Некоторые пионеры всегда неактивны, а именно:",
            "Виола",
            "Женя",
            "Юля",
            "Ольга",
            "Алиса",
            "Пионер",
            "{color=#e60000}Данная сложность негативно сказывается на игровом опыте!{/color}"
        )

        _normal_d = (
            "Нормальная сложность",
            "Самый стандартный режим игры",
            "Именно такой предполагался разработчиками",
        )

        _hard_d = (
            "Сложная сложность",
            "Повышенная сложность пионеров",
            "Пионеры становятся гораздо сильнее и опаснее",
        )

        _nightmare_d = (
            "Сложность {color=#e60000}Кошмар{/color}",
            "Максимальная сложность пионеров",
            "Пионеры становятся невероятно сильными и активными",
            "Чем выше уровень ночи, тем сильнее пионеры становятся",
            "Все пионеры всегда активны",
        )

        @staticmethod
        def _easy():
            not_activity = ("cs", "mz", "uv", "mt", "dv", "pi")

            for e in game.enemy_system:
                if e.tag in not_activity:
                    e.activity = False
                e.difficulty -= 6

            SoundRandomGenerator.randomness_modifier -= 0.01

        @staticmethod
        def _hard():
            for e in game.enemy_system:
                e.difficulty += 8

            SoundRandomGenerator.randomness_modifier += 0.005

        @staticmethod
        def _nightmare():
            night = game.night_system
            for e in game.enemy_system:
                e.difficulty += 10 + game.night_system.loaded.level
                e.activity = True

            SoundRandomGenerator.randomness_modifier += 0.015



    class Difficulty(str):
        def __new__(cls, name="<none>", level=0, callback=None, description=None):
            obj = str.__new__(cls, name)
            obj.level = level
            obj.callback = callback
            if description is None:
                obj.description = name.capitalize()
            else:
                obj.description = tuple(description)
            return obj

        def __add__(self, other):
            raise ValueError("Difficulty objects cannot be concatenated")

    class GameDifficulty(ConstantBase):
        EASY = Difficulty(name="easy", level=1,
                        callback=_DifficultyCallback._easy,
                        description=_DifficultyCallback._easy_d)

        NORMAL = Difficulty(name="normal", level=2,
                            description=_DifficultyCallback._normal_d)

        HARD = Difficulty(name="hard", level=3,
                        callback=_DifficultyCallback._hard,
                        description=_DifficultyCallback._hard_d)

        NIGHTMARE = Difficulty(name="nightmare", level=4,
                            callback=_DifficultyCallback._nightmare,
                            description=_DifficultyCallback._nightmare_d)

        @classmethod
        def get_difficulty_by_level(cls, level):
            for d in cls.list_difficulties():
                if d.level == level:
                    return d
            return None

        @classmethod
        def list_difficulties(cls):
            return (cls.EASY, cls.NORMAL, cls.HARD, cls.NIGHTMARE)

        def __new__(cls, value):
            for d in cls.list_difficulties():
                if d == value:
                    return d
            return None













