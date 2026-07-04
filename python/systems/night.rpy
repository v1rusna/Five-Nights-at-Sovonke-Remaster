init python in v1FNaSR:
    class Night(FNaSRBase):
        def __init__(self, night, level=None, end_of_shift=6, player_start=None, start_callback=None, end_callback=None, start_label=None, end_label=None, always_available=False):
            end_of_shift = int(end_of_shift)

            self.night = str(night)
            self.always_available = bool(always_available)

            if level is None:
                self.level = int(night)
            else:
                self.level = int(level)
            
            if (end_of_shift > 0 and end_of_shift < 13) or end_of_shift == -1:
                self.end_of_shift = end_of_shift
            else:
                self.end_of_shift = 6

            self.player_start = player_start
            self.start_callback = start_callback
            if callable(end_callback):
                self.end_callback = end_callback
            else:
                self.end_callback = lambda: None

            if start_label is None or not renpy.has_label(start_label):
                self.start_label = "v1_game_FNaSR"
            else:
                self.start_label = start_label

            if renpy.has_label(start_label):
                self.end_label = end_label
            else:
                self.end_label = None

        def load(self):
            if self.player_start is not None:
                self._night_system.player_start = self.player_start

            for e in game.enemy_system:
                if e.nights_start > self.level:
                    e.activity = False

            if callable(self.start_callback):
                self.start_callback()

            self._callback_difficulty()

            if self.start_label != "v1_game_FNaSR":
                Selector.start()
            renpy.jump(self.start_label)

        def _callback_difficulty(self):
            if Settings.game_difficulty.callback is not None:
                Settings.game_difficulty.callback()

    class CustomNight(Night):
        def __init__(self, night="custom", level=-1, end_of_shift=6, player_start=None, start_label=None, end_label=None):
            super(CustomNight, self).__init__(night, level, end_of_shift, player_start, self._enemy_activate, start_label, end_label, always_available=True)
            self._init = False
            self._enemy_list = list()
            self.enemy_select = None

        def init_custom(self):
            if not self._init:
                self.pre_start_night()
                self._init = True

        def pre_start_night(self):
            for e in game.enemy_system:
                if self.enemy_select is None:
                    self.enemy_select = e
                e.activity = False
                e.ai_level = 0
                self._enemy_list.append(e)

        def start(self):
            self._night_system.loaded = self
            super(CustomNight, self).load()

        def _enemy_activate(self):
            for enemy in self._enemy_list:
                if enemy.ai_level:
                    enemy.activity = True

        def set_ai_level(self, enemy=None, level=0):
            if enemy is None:
                enemy = self.enemy_select
            if enemy is not None:
                enemy.ai_level = min(max(int(level), 0), Constants.MAX_AI_LEVEL)

        def select_enemy(self, direction):
            if not self._enemy_list:
                return

            if self.enemy_select is None:
                self.enemy_select = self._enemy_list[0]
                return

            self._select(direction)
            if self.enemy_select.tag == "ge":
                self._select(direction)

        def _select(self, direction):
            index = self._enemy_list.index(self.enemy_select)
            if direction > 0:
                index += 1
                if index >= len(self._enemy_list):
                    index = 0
            else:
                index -= 1
                if index < 0:
                    index = len(self._enemy_list) - 1

            self.enemy_select = self._enemy_list[index]

        def _callback_difficulty(self):
            pass

        def reset_custom(self):
            for e in self._enemy_list:
                e.reset()

            self._init = False
            self._enemy_list.clear()
            self.enemy_select = None

    class NightSystem(FNaSRBase):
        def __init__(self):
            self.__night_None = Night(0)

            self.loaded = self.__night_None 
            self.player_start = 4

            self._nights = {}
            self._nights_list = []

            self.custom_night = CustomNight()
            self.custom_night._night_system = self

        def __iter__(self):
            return iter(self._nights_list)

        def __getitem__(self, night):
            return self._nights.get(night)

        @property
        def is_night_loaded(self):
            return self.loaded is not self.__night_None

        def next_load(self):
            self.night_load(self.get_next_night())

        def get_next_night(self):
            _n = None
            for n in self._nights_list:
                if not Settings.nights_gone.get(n.night, False):
                    _n = n.night
                    break

            if _n is None:
                _n = self._nights_list[-1].night

            return _n

        def night_load(self, night):
            if isinstance(night, Night):
                night._night_system = self
                self.loaded = night
                night.load()
                return

            _n = self._nights.get(night)
            if _n is None:
                raise Exception("Night %s not found." % night)

            #renpy.music.play("ambience_int_cabin_night", "v1_game_ambience_1_FNaSR", loop=True, fadein=2)

            self.loaded = _n
            _n.load()

        def add_night(self, night):
            if not isinstance(night, Night):
                raise Exception("The 'night' parameter must be 'Night' or inherit from it.")

            if night.night in self._nights.keys() + [self.custom_night.night]:
                raise Exception("Night '{}' already exists.".format(night.night))

            night._night_system = self
            self._nights[night.night] = night
            self._nights_list.append(night)

        def remove_night(self, night):
            if isinstance(night, Night):
                index = night.night
            else:
                index = int(night)

            _n = self._nights.pop(index, None)
            if _n is not None:
                self._nights_list.remove(_n)

        def reset(self):
            self.loaded = self.__night_None

    class _NightCallback(FNaSRBase):
        @staticmethod
        def _1():
            game.mainL.is_bulb = False
            game.game_time.set_hour_time(game.game_time._hour_time / 2)
            for e in game.enemy_system:
                e.difficulty -= 6

            us_enemy = game.enemy_system.get_enemy("us")
            if us_enemy is not None:
                us_enemy.difficulty += 4

        @staticmethod
        def _2():
            game.mainL.is_bulb = False
            game.game_time.set_hour_time(game.game_time._hour_time / 1.5)
            for e in game.enemy_system:
                e.difficulty -= 4

            un_enemy = game.enemy_system.get_enemy("un")
            if un_enemy is not None:
                un_enemy.difficulty += 4

        @staticmethod
        def _3():
            pass

        @staticmethod
        def _4():
            for e in game.enemy_system:
                e.difficulty += 2

        @staticmethod
        def _5():
            for e in game.enemy_system:
                e.difficulty += 4

        @staticmethod
        def _6():
            game.mainL.is_bulb = False
            game.mainL.is_tablet = False
            game.mainL.is_door = False

        @staticmethod
        def _test():
            for e in game.enemy_system:
                e.activity = False
            #game.enemy_system.get_enemy("ge").activity = True


            #game.mainL.is_bulb = False
            #game.mainL.is_tablet = False
            #game.mainL.is_door = False








