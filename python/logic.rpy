init 11 python in v1FNaSR:
    """
    Пространство имён мода FNaSR - Five Nights at Sovenk Remaster
    """

    """
    На 6 ночь:
    - Так как она будет в катакомбах гг нужно будет вовремя принимать успокоительные, при этом рационально так как они ограничены
    """

    class GameTools(FNaSRBase):
        SCREENS = Tools.list_matching_screens()

        __state_obj = {}
        
        @staticmethod
        def time_scale():
            try:
                return 1.0 / max(game.game_time.sleep_time, 0.01)
            except:
                return 1.0

        @classmethod
        def add_display_obj(cls, category=None,  **k):
            with lock:
                category = cls.__validate_category_display_obj(category)

                game.object_display.add_obj(**k)
                cls.__state_obj[category].append(k["key"])

        @classmethod
        def remove_display_obj(cls, category=None, **k):
            with lock:
                category = cls.__validate_category_display_obj(category)

                game.object_display.pop_obj(**k)
                cls.__state_obj[category].remove(k["key"])

        @classmethod
        def remove_all_display_obj(cls, category=None):
            with lock:
                category = cls.__validate_category_display_obj(category)

                _au = game.object_display.auto_update
                game.object_display.auto_update = False

                for k in cls.__state_obj[category]:
                    game.object_display.pop_obj(k)
                cls.__state_obj[category] = []
                
                game.object_display.update_display()
                game.object_display.auto_update = _au

        @classmethod
        def __validate_category_display_obj(cls, category):
            if category is None:
                category = "master"
            if category not in cls.__state_obj:
                cls.__state_obj[category] = []

            return category

        @classmethod
        def hide_screens(cls, exception_list=None):
            if exception_list is None:
                exception_list = []
            for c in cls.SCREENS:
                if not c in exception_list:
                    renpy.hide_screen(c)

        @staticmethod
        def stop_all_channels(fadeout_time=0):
            for channel in renpy.audio.audio.channels.keys():
                renpy.audio.music.stop(channel=channel, fadeout=fadeout_time)



    class FNaSR(FNaSRBase):
        __is_init_mod = False
        debug = False

        """Код хуйня но осознал я это слишком поздно :("""

        def __init__(self):
            self.game_time = GameTime()
            self.camera_system = CameraSystem()
            self.enemy_system = EnemySystem()
            self.night_system = NightSystem()
            self.door_system = DoorSystem()
            self.mainL = MainLocation()
            self.trigger_system = TriggerManager(continue_condition=lambda: not self.game_time.is_freeze)
            self.trigger_system.set_time_scale_function(GameTools.time_scale)
            self.object_display = ObjectDisplaySystem()
            self.object_display.add_obj(
                key="main_location",
                obj=self.mainL.img_main_loc,
                priority=-1000,
                at_list=[renpy.store.truecenter]
            )

            self.__state_obj = {}
            self.god_mode = False
            self.deaths = {"all": 0}
            self.__last_result_night = None

            self.__thread = None

            self.__init_functions = list()
            self.__reset_functions = list()

        def start_mod(self):
            Settings.load()

            self.old_gl_performance_mode = renpy.store._preferences.gl_powersave

            renpy.store._preferences.gl_framerate = 144
            renpy.store.config.image_cache_size_mb = 400
            renpy.store._preferences.gl_powersave = False
            renpy.store.config.allow_skipping = False

            renpy.store.config.window_title = "Пять Ночей в Совёнке Remaster"
            renpy.store.config.name = "FNaSR"
            renpy.store.config.version = "04.12.2025"

            renpy.store.save_name = ("FNaSR - и как ты сохранился?")

            renpy.store.night_time()
            renpy.store.persistent.sprite_time = "night"

            self._init_state()

            Settings.process_settings()

            if Settings.game_difficulty is None:
                Settings.game_difficulty = GameDifficulty.NORMAL
                Settings.save()

            Settings.normalize_settings()

            SituationMemory.load_setting(Settings.situations_memory)

            for fn in self.__init_functions:
                fn()
      
        def quit_mod(self):
            Settings.save()

            renpy.store._preferences.gl_powersave = getattr(self, "old_gl_performance_mode", False)
            renpy.store.config.image_cache_size_mb = 300

            renpy.store.config.window_title = "Бесконечное лето"
            renpy.store.config.name = "Everlasting_Summer"
            renpy.store.config.version = "1.6"
            renpy.store.config.allow_skipping = True

            renpy.store.save_name = ("пусто")

        def reset(self):
            SoundRandomGenerator.randomness_modifier = 0
            self.game_time.reset()
            self.camera_system.reset()
            self.enemy_system.reset()
            self.night_system.reset()
            self.door_system.reset()
            self.trigger_system.clear_triggers()
            self.mainL.reset()
            self.object_display.reset()

            self.__state_obj = {}
            self.object_display.add_obj(
                key="main_location",
                obj=self.mainL.img_main_loc,
                priority=-1000,
                at_list=[renpy.store.truecenter]
            )

            for fn in self.__reset_functions:
                fn()


        def _init_state(self):
            if not self.__is_init_mod:
                self.__init_camera_state()
                self.__init_enemy_state()
                self.__init_night_state()
                SoundRandomGenerator.init()

                self.__is_init_mod = True

        def __init_camera_state(self):
            for c in [
                Camera(1, "anim v1_ext_square_night_party_anim_FNaSR", (710, 329, 54, 40), [9, 14, 4, 2, 7, 13]),
                Camera(2, resources.images.bg["v1_ext_aidpost_night_FNaSR"], (757, 215, 63, 59), [1, 4, 3]),
                Camera(3, resources.images.bg["v1_ext_library_night_FNaSR"], (863, 129, 63, 47), [8, 4, 2]),
                Camera(4, resources.images.bg["v1_ext_house_of_mt_night_FNaSR"], (694, 128, 70, 45), [8, 3, 2, 1, 14]),
                Camera(5, resources.images.bg["v1_ext_playground_night_FNaSR"], (1099, 377, 83, 49), [6]),
                Camera(6, resources.images.bg["v1_ext_beach_night_FNaSR"], (992, 409, 60, 41), [5, 15]),
                Camera(7, resources.images.bg["v1_ext_dining_hall_away_night_FNaSR"], (760, 357, 60, 52), [1, 13, 9, 15, ]),
                Camera(8, resources.images.bg["v1_ext_stage_normal_night_FNaSR"], (835, 83, 59, 46), [3, 4]),
                Camera(9, resources.images.bg["v1_ext_clubs_night_FNaSR"], (461, 356, 71, 53), [12, 10, 14, 1, 7, 13]),
                Camera(10, resources.images.bg["v1_ext_musclub_night_FNaSR"], (491, 235, 69, 58), [11, 9, 14]),
                Camera(11, resources.images.bg["v1_ext_polyana_night_FNaSR"], (423, 135, 74, 48), [10]),
                Camera(12, resources.images.bg["v1_ext_camp_entrance_night_FNaSR"], (311, 378, 66, 50), [9]),
                Camera(13, resources.images.bg["v1_ext_boathouse_night_FNaSR"], (710, 516, 73, 53), [1, 7, 9]),
                Camera(14, resources.images.bg["v1_ext_admin_night_FNaSR"], (611, 294, 72, 46), [9, 1, 4, 2]),
                Camera(15, resources.images.bg["v1_ext_storage_night_FNaSR"], (883, 355, 63, 44), [6, 7], "electrical_panel")
            ]:
                self.camera_system.add_camera(c)

        def __init_enemy_state(self):
            for e in [
                UlyanaEnemy(
                    tag="us",
                    sprite="us angry pioneer",
                    nights_start=1,
                    paths=[7,1,4],
                    ai_level=3,
                    transform_data=TransformScreamer(renpy.store.v1_uliana_screamer_t_FNaSR)
                ),
                LenaEnemy(
                    tag="un",
                    sprite="un evil_smile pioneer",
                    nights_start=2,
                    paths=AutoGeneratePath,
                    ai_level=6,
                    max_movement_opportunities=7,
                    transform_data=TransformScreamer(renpy.store.v1_phantom_screamer_t_FNaSR),
                    time_murder_variation=(4,6)
                ),
                AlisaEnemy(
                    tag="dv",
                    sprite="dv angry pioneer2",
                    nights_start=3,
                    paths=[AutoGeneratePath, 15],
                    ai_level=3,
                    max_movement_opportunities=10,
                ),
                MikuEnemy(
                    tag="mi",
                    sprite="mi angry pioneer",
                    nights_start=5,
                    paths=EnemyPath.find_path(10, self.night_system.player_start, self.camera_system.cameras),
                    ai_level=5
                ),
                SlaviaEnemy(
                    tag="sl",
                    sprite="sl angry pioneer",
                    nights_start=4,
                    paths=EnemyPath.find_path(12, self.night_system.player_start, self.camera_system.cameras),
                    ai_level=2,
                    max_movement_opportunities=8,
                    transform_data=TransformScreamer(renpy.store.v1_slavya_screamer_t_FNaSR),
                ),
                ShurikEnemy(
                    tag="sh",
                    sprite="sh rage",
                    nights_start=3,
                    paths=EnemyPath.find_path(9, self.night_system.player_start, self.camera_system.cameras),
                    ai_level=3,
                    max_movement_opportunities=6,
                    time_murder_variation=(4,6)
                ),
                ElectronicEnemy(
                    tag="el",
                    sprite="el angry pioneer",
                    nights_start=3,
                    paths=EnemyPath.find_path(9, self.night_system.player_start, self.camera_system.cameras),
                    ai_level=8,
                    max_movement_opportunities=1,
                ),
                OlgaEnemy(
                    tag="mt",
                    sprite="mt angry pioneer",
                    nights_start=5,
                    paths=[],
                    ai_level=1,
                    max_movement_opportunities=15,
                    transform_data=TransformScreamer(renpy.store.v1_olga_screamer_t_FNaSR),
                    call_time=12,
                    image_button=resources.images.other["call_button"],
                    alpha_button=0.2,
                    size_button=(290/3, 60/3)
                ),
                YuliaEnemy(
                    tag="uv",
                    sprite="uv rage",
                    nights_start=2,
                    paths=EnemyPath.find_path(11, self.night_system.player_start, self.camera_system.cameras),
                    ai_level=1,
                    transform_data=TransformScreamer(renpy.store.v1_uliya_screamer_t_FNaSR)
                ),
                ZhenyaEnemy(
                    tag="mz",
                    sprite="mz angry glasses pioneer",
                    nights_start=4,
                    paths=[],
                    ai_level=5,
                    max_movement_opportunities=8,
                    mz_camera_id=3,
                    image_button="Mute_Button"
                ),
                ViolaEnemy(
                    tag="cs",
                    sprite="cs normal",
                    nights_start=5,
                    paths=[],
                    ai_level=5,
                    max_movement_opportunities=20,
                    spawn_camera_id=2
                ),
                PioneerEnemy(
                    tag="pi",
                    sprite="pi normal",
                    nights_start=5,
                    paths=AutoGeneratePath,
                    ai_level=6,
                    max_movement_opportunities=5
                ),

                GendaSolo(
                    tag="ge",
                    sprite=resources.images.other["genda_ebat"],
                    nights_start=1,
                    paths=[],
                    ai_level=20,
                    max_movement_opportunities=1,
                    screamer_sound=resources.sounds.sfx["genda_aaaaa"]
                )
            ]:
                self.enemy_system.add_enemy(e)

        def __init_night_state(self):
            for n in [
                Night(1, start_callback=_NightCallback._1, start_label="v1_night_1_history_win_label_FNaSR", end_label="v1_day_1_history_win_label_FNaSR"),
                Night(2, start_callback=_NightCallback._2, start_label="v1_night_2_history_win_label_FNaSR", end_label="v1_day_2_history_win_label_FNaSR"),
                Night(3, start_callback=_NightCallback._3, start_label="v1_night_3_history_win_label_FNaSR"),
                Night(4, start_callback=_NightCallback._4, start_label="v1_night_4_history_win_label_FNaSR"),
                Night(5, start_callback=_NightCallback._5, start_label="v1_night_5_history_win_label_FNaSR"),
                Night(6, start_callback=_NightCallback._6, start_label="v1_night_6_history_win_label_FNaSR"),
                Night(666, start_callback=_NightCallback._test),
            ]:
                self.night_system.add_night(n)


        def start_game_loop(self):
            if self.is_game_loop_alive():
                return

            if Tools.thread_exists("V1FNaSRGameLoopThread"):
                raise RuntimeError("The GameLoopThread already exists")

            self.object_display.auto_update = True

            self.__thread = renpy.store.v1FNaSRThread.ThreadGame(target=self._game_loop, name="V1FNaSRGameLoopThread")
            self.__thread.setDaemon(True)
            self.__thread.start()

            self.trigger_system.start()

        def stop_game_loop(self):
            self.object_display.auto_update = False
            self.trigger_system.stop()
            if self.__thread is not None:
                self.__thread.stop()
                while self.__thread.is_alive():
                    time.sleep(0.1)
                self.__thread = None

        def is_game_loop_alive(self):
            if self.__thread is None:
                return False
            return self.__thread.is_alive()

        def _game_loop(self, is_alive):
            _is_stop_game = False
            global_event.emit("game.loop.start")

            while is_alive():
                if _is_stop_game:
                    self.game_time.sleep(0.1)
                    continue

                if not self.game_time.update():
                    continue

                self.camera_system.update()
                self.door_system.update()
                self.enemy_system.update()
                self.night_system.loaded.update()
                SoundRandomGenerator.update()

                if not is_alive():
                    global_event.emit("game.loop.stop")
                    return

                #if self.check_killer():
                #    global_event.emit("game.loop.stop")
                #    self.loss()
                #    return

                if self.game_time.clock.hour % 24 == self.night_system.loaded.end_of_shift:
                    execute_in_main_thread(self.win)
                    _is_stop_game = True
                    continue

                global_event.emit("game.loop")

            global_event.emit("game.loop.stop")


        def check_killer(self):
            if not self.enemy_system.enemy_killer:
                return False

            if self.god_mode:
                enemy = self.enemy_system.enemy_killer
                if hasattr(enemy, "loss_kill"):
                    enemy.loss_kill()
                elif not State.load_state(enemy, "pre-kill"):
                    enemy.reset()

                self.deaths["all"] += 1
                self.deaths.setdefault(enemy.tag, 0)
                self.deaths[enemy.tag] += 1

                self.enemy_system.enemy_killer = None
                return False
            else:
                self.loss()

            return True

        def win(self):
            if not self.god_mode:
                Settings.nights_gone[self.night_system.loaded.night] = True

            self.stop_game_loop()
            GameTools.hide_screens()
            GameTools.stop_all_channels()

            self.__last_result_night = ResultNight.WIN

            renpy.jump("v1_win_label_FNaSR")

        def loss(self):
            self.stop_game_loop()
            GameTools.hide_screens()
            GameTools.stop_all_channels(2)
            self.__last_result_night = ResultNight.LOSS
            renpy.jump("v1_loss_label_FNaSR")
            #execute_in_main_thread(renpy.jump, "v1_loss_label_FNaSR")

        def restart_night(self):
            if self.night_system.is_night_loaded:
                _nl = self.night_system.loaded.night
                self.stop_game_loop()
                GameTools.stop_all_channels()
                GameTools.hide_screens(["V1GameMenuSelectorFNaSR"])
                self.reset()
                self.night_system.night_load(_nl)


        def get_last_pass_result(self):
            return self.__last_result_night

        def add_init_function(self, fn):
            if callable(fn):
                self.__init_functions.append(fn)

        def remove_init_function(self, fn):
            if fn in self.__init_functions:
                self.__init_functions.remove(fn)

        def add_reset_function(self, fn):
            if callable(fn):
                self.__reset_functions.append(fn)

        def remove_reset_function(self, fn):
            if fn in self.__reset_functions:
                self.__reset_functions.remove(fn)

    game = FNaSR()






    class DebugPanel(FNaSRBase):
        @staticmethod
        def break_all_cameras():
            for camera in game.camera_system.list_cameras:
                camera.break_c(random.randint(10, 99))

        @staticmethod
        def repair_all_cameras():
            for camera in game.camera_system.list_cameras:
                camera.repair()

        @staticmethod
        def break_random_cameras():
            for camera in game.camera_system.list_cameras:
                if random.random() > 0.5:
                    camera.break_c(random.randint(10, 99))

        


