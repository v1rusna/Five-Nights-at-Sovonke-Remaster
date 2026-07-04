init -5 python in v1FNaSR:
    class Tools(FNaSRBase):
        @staticmethod
        def start_thread(*a, **k):
            with lock:
                thread = renpy.store.v1FNaSRThread.ThreadWithCatch(*a, **k)
                thread.setDaemon(True)
                thread.start()
                return thread

        @staticmethod
        def list_matching_screens(startS="V1", endS="FNaSR"):
            with lock:
                screen_list = []
                for screen_name in renpy.display.screen.screens_by_name.keys():
                    if screen_name.startswith(startS) and screen_name.endswith(endS):
                        screen_list.append(screen_name)
                return sorted(screen_list)

        @staticmethod
        def get_current_background(layer="master", startS="bg"):
            with lock:
                showing = renpy.get_showing_tags(layer=layer)

                for tag in showing:
                    if tag.startswith(startS):
                        return tag
                return None

        @staticmethod
        def thread_exists(name):
            return any(t.name == name for t in threading.enumerate())

        @staticmethod
        def _register_channel(
            name,
            mixer=None,
            loop=None,
            stop_on_mute=True,
            tight=False,
            file_prefix="",
            file_suffix="",
            buffer_queue=True,
            movie=False,
            framedrop=True,
            synchro_start=None
        ):
            """
            !!!Предупреждение для других разработчиков!!!
            Этот метод запрещено использовать, как минимум вне мода FNaSR
            Мод FNaSR не использует сохранения и загрузку сохранений, а так же систему rollback, так что этот метод не рассчитан на эти сценарии
            Какие риски создает использования этого метода вне мода FNaSR:
                -Нарушает стабильность игры так как состояние аудиосистемы зависит от того, какие части кода выполнились во время игры
                -Игра, загруженная из сейва, может иметь другой набор каналов, чем была при сохранении, что приведет к ошибкам
                -Rollback система - RenPy имеет сложную систему отката (rollback). Каналы, созданные динамически, создают неоднозначности при откате игры назад
                -Усложняет отладку проблем
            """
            with lock:
                import renpy.audio.audio as audio
                
                # Валидация имени
                name = name.strip()
                if not name:
                    raise ValueError("The name of the audio channel cannot be empty.")
                
                if " " in name:
                    raise ValueError("Channel name '{}' cannot contain spaces.".format(name))
                
                if name == "movie":
                    movie = True
                
                if name in audio.channels:
                    try:
                        audio.channels[name].stop()
                    except Exception:
                        pass 
                    audio.all_channels.remove(audio.channels[name])
                    del audio.channels[name]
                
                try:
                    if "7.4" in renpy.version() or "7.5" in renpy.version() or "7.6" in renpy.version():
                        if renpy.android and renpy.config.hw_video and name == "movie":
                            if hasattr(audio, 'AndroidVideoChannel'):
                                c = audio.AndroidVideoChannel(
                                    name, 
                                    default_loop=loop, 
                                    file_prefix=file_prefix, 
                                    file_suffix=file_suffix
                                )
                            else:
                                c = audio.Channel(
                                    name, loop, stop_on_mute, tight, 
                                    file_prefix, file_suffix, buffer_queue, 
                                    movie=movie, framedrop=framedrop
                                )
                        elif renpy.ios and renpy.config.hw_video and name == "movie":
                            if hasattr(audio, 'IOSVideoChannel'):
                                c = audio.IOSVideoChannel(
                                    name, 
                                    default_loop=loop, 
                                    file_prefix=file_prefix, 
                                    file_suffix=file_suffix
                                )
                            else:
                                c = audio.Channel(
                                    name, loop, stop_on_mute, tight, 
                                    file_prefix, file_suffix, buffer_queue, 
                                    movie=movie, framedrop=framedrop
                                )
                        else:
                            c = audio.Channel(
                                name, loop, stop_on_mute, tight, 
                                file_prefix, file_suffix, buffer_queue, 
                                movie=movie, framedrop=framedrop
                            )
                    else:
                        if synchro_start is None:
                            synchro_start = False if movie else loop
                        
                        c = audio.Channel(
                            name,
                            loop,
                            stop_on_mute,
                            tight,
                            file_prefix,
                            file_suffix,
                            buffer_queue,
                            movie=movie,
                            framedrop=framedrop,
                            synchro_start=synchro_start,
                        )
                    
                    c.mixer = mixer
                    audio.all_channels.append(c)
                    audio.channels[name] = c
                    
                except Exception as e:
                    renpy.log("FNaSR | Failed to register channel '{}': {}".format(name, e))
                    raise

        @staticmethod
        def get_random_align():
            x = random.random()
            y = random.random()

            return x, y

    class Settings(object):
        _settings_handler = [lambda k, v: v if k != "game_difficulty" else GameDifficulty(v)]

        @staticmethod
        def _init_settings():
            try:
                os.makedirs(Constants.MOD_FILES_PATH)
            except:
                pass

            if not os.path.isfile(Constants.MOD_FILES_PATH + "settings.json"):
                default_settings = {
                    "nights_gone": dict(),
                    "game_difficulty": GameDifficulty.NORMAL,
                    "view_story": True,
                    "situations_memory": []
                }

                with codecs.open(Constants.MOD_FILES_PATH + "settings.json", "w", "utf-8") as f:
                    f.write(json.dumps(default_settings, indent=4, ensure_ascii=False))

        @classmethod
        def load(cls):
            with lock:
                cls._init_settings()

                with codecs.open(Constants.MOD_FILES_PATH + "settings.json", "r", "utf-8") as f:
                    data = json.load(f)

                for k, v in data.items():
                    renpy.log("FNaSR | Settings load: {} = {}".format(k, v))
                    setattr(cls, k, v)

        @classmethod
        def save(cls):
            with lock:
                data = dict()
                old_data = dict()

                with codecs.open(Constants.MOD_FILES_PATH + "settings.json", "r", "utf-8") as f:
                    old_data = json.load(f)

                for k in dir(cls):
                    if not k.startswith("_") and not callable(getattr(cls, k)):
                        data[k] = getattr(cls, k)

                try:
                    with codecs.open(Constants.MOD_FILES_PATH + "settings.json", "w", "utf-8") as f:
                        renpy.log("FNaSR | Settings save: {}".format(data))
                        f.write(json.dumps(data, indent=4, ensure_ascii=False))
                except Exception as e:
                    renpy.log("FNaSR | Settings save error: {}".format(e))
                    with codecs.open(Constants.MOD_FILES_PATH + "settings.json", "w", "utf-8") as f:
                        f.write(json.dumps(old_data, indent=4, ensure_ascii=False))
                    raise

        #@classmethod
        #def start_auto_save(cls, interval=60):
        #    def auto_save_fn():
        #        while True:
        #            time.sleep(interval)
        #            cls.save()
        #    cls.autosave_thread = Tools.start_thread(target=auto_save_fn, name="v1FNaSRAutoSaveThread")
        #    cls.autosave_thread.setDaemon(True)

        @classmethod
        def process_settings(cls):
            for k in dir(cls):
                if not k.startswith("_") and not callable(getattr(cls, k)):
                    v = getattr(cls, k)
                    for handler in cls._settings_handler:
                        v = handler(k, v)
                    setattr(cls, k, v)

        @classmethod
        def add_setting_handler(cls, handler):
            if callable(handler) and handler not in cls._settings_handler:
                cls._settings_handler.append(handler)

        @classmethod
        def normalize_settings(cls):
            with lock:
                if not hasattr(cls, "game_difficulty"):
                    cls.game_difficulty = GameDifficulty.NORMAL

                if not hasattr(cls, "nights_gone"):
                    cls.nights_gone = dict()

                if not hasattr(cls, "view_story"):
                    cls.view_story = True

                if not hasattr(cls, "situations_memory"):
                    cls.situations_memory = []


                if not isinstance(cls.game_difficulty, Difficulty):
                    cls.game_difficulty = GameDifficulty.NORMAL

                if not isinstance(cls.view_story, bool):
                    cls.view_story = True

        def __init__(self):
            raise RuntimeError("Settings is a static class and cannot be instantiated.")

    from renpy.store import At, Text, v1_vhs_crt_shader_t_FNaSR

    class MainMenu(FNaSRBase):
        __text_cache = {}
        __bg = None
        __screens = ("V1MainMenuFNaSR", "V1MainMenuFNaSR",)
        __show_enemy = None
        __old_bg = 0

        _dd = None
            
        @classmethod
        def text(cls, text, text_style="v1_text_24_mod_button_static_FNaSR", size=26, g_power=0.0875):
            text = str(text)
            if text in cls.__text_cache:
                _item = cls.__text_cache[text]
                if _item["style"] == text_style and _item["size"] == size and _item["g_power"] == g_power:
                    return cls.__text_cache[text]["text"]

            _t = At(Text(text, style=text_style, size=size), v1_vhs_crt_shader_t_FNaSR(g_power))
            cls.__text_cache[text] = {"text": _t, "style": text_style, "size": size, "g_power": g_power}
            return _t

        @classmethod
        def screen_switching(cls, oldS=None, newS=None, **param_screen):
            if oldS is None:
                oldS = cls.__screens[0]
            if newS is None:
                newS = cls.__screens[1]

            cls.__screens = (oldS, newS,)
            cls.set_bg("random")
            renpy.hide_screen(oldS)
            renpy.music.play(resources.sounds.sfx["blip3"], "v1_camera_sfx_FNaSR")
            renpy.show_screen(newS, **param_screen)

        @classmethod
        def restart_screen(cls):
            renpy.hide_screen(cls.__screens[1])
            renpy.music.play(resources.sounds.sfx["blip3"], "v1_camera_sfx_FNaSR")
            renpy.show_screen(cls.__screens[1])

        @classmethod
        def set_bg(cls, name="random"):
            cls.__old_bg = name
            if name == "random":
                cls.__bg = random.choice(game.camera_system.list_cameras).image
            else:
                cls.__bg = name

        @classmethod
        def get_bg(cls):
            if cls.__bg is None:
                cls.set_bg("random")
            if cls.__old_bg == cls.__bg:
                cls.__show_enemy = None
            return cls.__bg

        @classmethod
        def get_enemy(cls):
            if cls.__show_enemy is None:
                enemy_list = [enemy for enemy in game.enemy_system.get_enemy_list() if enemy.tag != "ge"]
                cls.__show_enemy = (random.choice(enemy_list).sprite, (random.randint(0, 999), 0))
            return cls.__show_enemy

        @staticmethod
        def normalize_action(action, add_action):
            if isinstance(add_action, list):
                action = tuple(add_action)

            if action is None:
                return add_action if isinstance(add_action, tuple) else (add_action,)

            if isinstance(action, list):
                action = tuple(action)

            if not isinstance(action, tuple):
                action = (action,)

            if not isinstance(add_action, tuple):
                add_action = (add_action,)

            return action + add_action

    class _Screen(FNaSRBase):
        __is_replace = False
        @classmethod
        def _replace(cls):
            if cls.__is_replace:
                #renpy.display.screen.screens[("game_menu_selector", None)] = renpy.display.screen.screens[("v1FNaSR_old_game_menu_selector", None)]
                renpy.display.screen.screens[("save", None)] = renpy.display.screen.screens[("v1FNaSR_old_save", None)]
                renpy.display.screen.screens[("load", None)] = renpy.display.screen.screens[("v1FNaSR_old_load", None)]
                renpy.display.screen.screens[("say", None)] = renpy.display.screen.screens[("v1FNaSR_old_say", None)]
                cls.__is_replace = False
            else:
                #renpy.display.screen.screens[("v1FNaSR_old_game_menu_selector", None)] = renpy.display.screen.screens[("game_menu_selector", None)]
                #renpy.display.screen.screens[("game_menu_selector", None)] = renpy.display.screen.screens[("V1GameMenuSelectorFNaSR", None)]

                renpy.display.screen.screens[("v1FNaSR_old_save", None)] = renpy.display.screen.screens[("save", None)]
                renpy.display.screen.screens[("save", None)] = renpy.display.screen.screens[("V1SaveLoadScreenFNaSR", None)]

                renpy.display.screen.screens[("v1FNaSR_old_load", None)] = renpy.display.screen.screens[("load", None)]
                renpy.display.screen.screens[("load", None)] = renpy.display.screen.screens[("V1SaveLoadScreenFNaSR", None)]

                renpy.display.screen.screens[("v1FNaSR_old_say", None)] = renpy.display.screen.screens[("say", None)]
                renpy.display.screen.screens[("say", None)] = renpy.display.screen.screens[("V1SayScreenFNaSR", None)]

                cls.__is_replace = True

        @staticmethod
        def _activities_all_pioneer(activity):
            for enemy in game.enemy_system:
                enemy.activity = activity




