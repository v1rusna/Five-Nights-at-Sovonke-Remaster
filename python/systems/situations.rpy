init 2 python in v1FNaSR:
    class SituationMemory:
        _memory = set()

        @classmethod
        def add(cls, key):
            with lock:
                cls._memory.add(str(key))

        @classmethod
        def remove(cls, key):
            with lock:
                cls._memory.discard(str(key))

        @classmethod
        def get(cls):
            with lock:
                return list(cls._memory)

        @classmethod
        def save(cls):
            with lock:
                for s in cls._memory:
                    if s not in Settings.situations_memory:
                        Settings.situations_memory.append(s)
                cls.clear()

        @classmethod
        def reset(cls):
            for s in list(cls._memory):
                situation.reset(s)

        @classmethod
        def clear(cls):
            with lock:
                cls._memory.clear()

        @classmethod
        def load_setting(cls, list_s):
            try:
                for s in list_s:
                    situation._skip_situation(s)
                    self.add(s)
            except Exception:
                pass

    # ──────────────────────────────────────────────
    # Один «слот» ситуации: хранит N вариантов,
    # при execute() выбирает случайный (с весами или без)
    # ──────────────────────────────────────────────

    class Situation(object):
        def __init__(self, *variants, **kwargs):
            self.variants = list(variants)
            self.weights  = kwargs.get("weights", None)
            self.mode     = kwargs.get("mode", "random")
            self._index   = 0
            self._pool    = []  # перемешанная очередь для режима shuffle

        def _refill_pool(self):
            self._pool = list(range(len(self.variants)))
            random.shuffle(self._pool)

        def execute(self):
            if not self.variants:
                return

            if self.mode == "cycle":
                self.variants[self._index]()
                self._index = (self._index + 1) % len(self.variants)

            elif self.mode == "shuffle":
                # Пул пуст — перемешиваем заново
                if not self._pool:
                    self._refill_pool()
                    # Если в пуле один вариант — повтора не избежать,
                    # но если вариантов > 1, следим чтобы первый в новой
                    # партии не совпал с последним в предыдущей
                    if len(self._pool) > 1 and hasattr(self, "_last_index"):
                        if self._pool[0] == self._last_index:
                            # меняем первый и второй местами
                            self._pool[0], self._pool[1] = self._pool[1], self._pool[0]

                idx = self._pool.pop(0)
                self._last_index = idx
                self.variants[idx]()

            elif self.mode == "random":
                if self.weights:
                    total = sum(self.weights)
                    r = random.uniform(0, total)
                    cumulative = 0.0
                    for fn, w in zip(self.variants, self.weights):
                        cumulative += w
                        if r <= cumulative:
                            fn()
                            return
                    self.variants[-1]()
                else:
                    random.choice(self.variants)()

    def variants(*fns, **kwargs):
        return Situation(*fns, **kwargs)

    # ──────────────────────────────────────────────
    # Менеджер: последовательность слотов для каждого ключа
    # ──────────────────────────────────────────────
    class SituationManager(object):
        def __init__(self):
            self._situations    = {}   # key -> {slots, repeat}
            self._indices       = {}   # key -> текущий индекс
            self._repeat_counts = {}   # key -> сколько раз уже зациклились

        def create(self, key, *slots, **kwargs):
            """
            key    — строковый идентификатор
            slots  — callable или Situation/variants(...)
            repeat — False: без повторений (умолч.)
                    True : бесконечно
                    N    : ровно N раз перезапустить после конца
            """
            key = str(key)
            self._situations[key] = {
                "slots":  list(slots),
                "repeat": kwargs.get("repeat", False),
            }
            self._indices[key]       = 0
            self._repeat_counts[key] = 0

        def next_situation(self, key):
            """
            Запускает следующий слот.
            Возвращает True если что-то выполнилось, False если цепочка кончилась.
            """
            key = str(key)
            if key not in self._situations:
                return False

            data   = self._situations[key]
            slots  = data["slots"]
            repeat = data["repeat"]
            idx    = self._indices[key]

            # Конец последовательности — проверяем повторение
            if idx >= len(slots):
                if repeat is True:
                    self._indices[key] = 0
                    idx = 0
                elif isinstance(repeat, int) and repeat > 0:
                    if self._repeat_counts[key] < repeat:
                        self._repeat_counts[key] += 1
                        self._indices[key] = 0
                        idx = 0
                        if not self._repeat_counts[key] < repeat:
                            SituationMemory.add(key)
                    else:
                        SituationMemory.add(key)
                        return False
                else:
                    SituationMemory.add(key)
                    return False

            slot = slots[idx]
            if isinstance(slot, Situation):
                slot.execute()
            elif callable(slot):
                slot()

            self._indices[key] += 1

            if idx >= len(slots):
                if isinstance(repeat, int) and repeat > 0:
                    if not self._repeat_counts[key] < repeat:
                        SituationMemory.add(key)
                else:
                    SituationMemory.add(key)

            return True

        def reset(self, key):
            """Сбросить цепочку на начало вручную."""
            key = str(key)
            if key in self._situations:
                self._indices[key]       = 0
                self._repeat_counts[key] = 0
                SituationMemory.remove(key)

        def is_done(self, key):
            """True — цепочка полностью отыграна."""
            key = str(key)
            if key not in self._situations:
                return True
            data = self._situations[key]
            return (self._indices[key] >= len(data["slots"])
                    and not data["repeat"])

        def _skip_situation(self, key):
            key = str(key)
            if key not in self._situations:
                return

            repeat = self._situations[key]["repeat"]
            self._indices[key] = len(self._situations[key]["slots"])
            if isinstance(repeat, int) and repeat > 0:
                self._repeat_counts[key] = repeat+1


    # ──────────────────────────────────────────────
    # Пример использования
    # ──────────────────────────────────────────────
    def _make_voice_action(sound_key, say_method, delay=1):
        def action():
            def _play():
                renpy.music.play(
                    resources.sounds.voice.gg.addition[sound_key],
                    "v1_character_voice_FNaSR"
                )
                say_method()
            game.game_time.timer(_play, delay)
        return action

    def _situation_yulia_action():
        def _play_8():
            renpy.music.play(
                resources.sounds.voice.gg.addition["8"],
                "v1_character_voice_FNaSR"
            )
            renpy.store.v1FNaSRSay.yulia_action_text_8.start()
        def _play_9():
            if not situation.is_done("yulia.action.tablet"):
                renpy.music.play(
                    resources.sounds.voice.gg.addition["9"],
                    "v1_character_voice_FNaSR"
                )
                renpy.store.v1FNaSRSay.yulia_action_text_9.start()

        game.game_time.timer(_play_8, 0.5)
        game.game_time.timer(_play_9, 5.5)

    situation = SituationManager()




        

    situation.create("ulyana.try_attack", _make_voice_action("5", renpy.store.v1FNaSRSay.ulyana_try_attack_text_5.start), lambda: None)
    situation.create("ulyana.lose_attack",
        variants(
            _make_voice_action("6", renpy.store.v1FNaSRSay.ulyana_try_attack_text_6.start),
            _make_voice_action("7", renpy.store.v1FNaSRSay.ulyana_try_attack_text_7.start),
            mode="shuffle"
        ), repeat=2
    )

    situation.create("yulia.action", _situation_yulia_action)
    situation.create("yulia.action.tablet",
        _make_voice_action("10", renpy.store.v1FNaSRSay.yulia_action_text_10.start, 0),
        _make_voice_action("11", renpy.store.v1FNaSRSay.yulia_action_text_11.start, 0)
    )

    situation.create("lena.look",
        _make_voice_action("14", renpy.store.v1FNaSRSay.lena_look_text_14.start, 0.5),
        _make_voice_action("15", renpy.store.v1FNaSRSay.lena_look_text_15.start, 0.5)
    )
    situation.create("lena.look.long", _make_voice_action("17", renpy.store.v1FNaSRSay.lena_look_text_17.start, 0))

    situation.create("alisa.look", _make_voice_action("18", renpy.store.v1FNaSRSay.alisa_text_18.start, 0.5))
    situation.create("alisa.look.long", _make_voice_action("19", renpy.store.v1FNaSRSay.alisa_text_19.start, 0.5))
    situation.create("alisa.look.button", _make_voice_action("20", renpy.store.v1FNaSRSay.alisa_text_20.start, 0))

    situation.create("shurik.action", _make_voice_action("21", renpy.store.v1FNaSRSay.shurik_text_21.start, 0.5))
    situation.create("shurik.action.bulb", _make_voice_action("23", renpy.store.v1FNaSRSay.shurik_text_23.start, 0))
    situation.create("shurik.action.left", _make_voice_action("24", renpy.store.v1FNaSRSay.shurik_text_24.start, 0))

    situation.create("electronic.action", _make_voice_action("25", renpy.store.v1FNaSRSay.electronic_text_25.start))
    situation.create("electronic.action.bulb", _make_voice_action("26", renpy.store.v1FNaSRSay.electronic_text_26.start, 0.5))
    situation.create("electronic.action.fear", _make_voice_action("27", renpy.store.v1FNaSRSay.electronic_text_27.start, 0))

    situation.create("slavia.action",
        _make_voice_action("28", renpy.store.v1FNaSRSay.slavia_text_28.start),
        _make_voice_action("29", renpy.store.v1FNaSRSay.slavia_text_29.start)
    )
    situation.create("slavia.action.left", _make_voice_action("30", renpy.store.v1FNaSRSay.slavia_text_30.start))

    situation.create("zhenya.action", _make_voice_action("31", renpy.store.v1FNaSRSay.zhenya_text_31.start))
    situation.create("zhenya.action.noise.5", _make_voice_action("32", renpy.store.v1FNaSRSay.zhenya_text_32.start))
    situation.create("zhenya.action.noise.button", _make_voice_action("33", renpy.store.v1FNaSRSay.zhenya_text_33.start, 0))
    situation.create("zhenya.action.noise.button.show", _make_voice_action("34", renpy.store.v1FNaSRSay.zhenya_text_34.start, 0.5))
    situation.create("zhenya.action.noise.button.hide", _make_voice_action("35", renpy.store.v1FNaSRSay.zhenya_text_35.start, 0.5))
    situation.create("zhenya.action.noise.70", _make_voice_action("36", renpy.store.v1FNaSRSay.zhenya_text_36.start, 0))
    situation.create("zhenya.action.noise.80", _make_voice_action("37", renpy.store.v1FNaSRSay.zhenya_text_37.start, 0))
    situation.create("zhenya.action.noise.salvation", _make_voice_action("38", renpy.store.v1FNaSRSay.zhenya_text_38.start, 0))

    situation.create("miku.action", _make_voice_action("39", renpy.store.v1FNaSRSay.miku_text_39.start, 0))
    situation.create("miku.action.click", _make_voice_action("40", renpy.store.v1FNaSRSay.miku_text_40.start, 0))

    situation.create("viola.action.1", _make_voice_action("41", renpy.store.v1FNaSRSay.viola_text_41.start, 0))
    situation.create("viola.action.2", _make_voice_action("42", renpy.store.v1FNaSRSay.viola_text_42.start, 0))
    situation.create("viola.action.observation", _make_voice_action("43", renpy.store.v1FNaSRSay.viola_text_43.start, 0))
    situation.create("viola.action.6seconds", _make_voice_action("44", renpy.store.v1FNaSRSay.viola_text_44.start, 0))
    situation.create("viola.action.door", _make_voice_action("45", renpy.store.v1FNaSRSay.viola_text_45.start, 0))
    situation.create("viola.action.relief", _make_voice_action("46", renpy.store.v1FNaSRSay.viola_text_46.start, 0))

    """Как же я заебался с этими пионерами..."""

    situation.create("situation.random.1", _make_voice_action("47", renpy.store.v1FNaSRSay.random_situation_text_47.start, 0))
    situation.create("situation.random.2", _make_voice_action("48", renpy.store.v1FNaSRSay.random_situation_text_48.start, 0))
    situation.create("situation.random.3", _make_voice_action("49", renpy.store.v1FNaSRSay.random_situation_text_49.start, 0))
    situation.create("situation.random.4", _make_voice_action("50", renpy.store.v1FNaSRSay.random_situation_text_50.start, 0))
    situation.create("situation.random.5", _make_voice_action("51", renpy.store.v1FNaSRSay.random_situation_text_51.start, 0))






















