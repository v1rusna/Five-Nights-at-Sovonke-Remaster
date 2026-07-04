init -5 python in v1FNaSR:
    class SoundRandomGenerator(FNaSRBase):
        """Генератор случайных звуков."""
        __is_init = False
        randomness_modifier = 0

        
        # Константы вероятностей
        RANDOM_SOUND_PROBABILITY = 0.005
        CAMERA_SOUND_PROBABILITY = 0.05
        FNASR_SOUND_PROBABILITY = 0.5
        
        # Предопределенные списки звуков (создаются один раз)
        _FNASR_SOUNDS = [
            "dog5",
            "distantlaugh",
            "breath",
            "circus",
            "distantlaugh",
            "echo1",
            "echo3b",
            "echo4b",
            "fredlaugh1",
            "fredlaugh2",
            "fredlaugh3",
            "fredlaugh4",
            "fredlaugh5",
            "laugh",
            "Laugh_Giggle_Girl_1"
        ]
        
        _CAMERA_SOUNDS = [
            "cOMPUTER_DIGITAL_L2076505",
            "popstatic",
            "v1_original_es_sound_flag"
        ]
        
        @classmethod
        def init(cls):
            """Инициализация генератора звуков."""
            if not cls.__is_init:
                cls._door_status = False
                
                # Регистрация обработчиков событий
                global_event.on("camera_system.select_camera", cls.on_camera_selected)
                global_event.on("camera_system.tablet", cls._on_tablet_change)
                global_event.on("door_system.door_use", cls._on_door_use)

                cls.__is_init = True
        
        @classmethod
        def _on_tablet_change(cls, status):
            """Обработчик изменения состояния планшета."""
            if not status:
                execute_in_main_thread(
                    renpy.music.stop,
                    channel="v1_camera_random_sfx_FNaSR"
                )
        
        @classmethod
        def _on_door_use(cls, status):
            """Обработчик использования двери."""
            cls._door_status = bool(status)
        
        @classmethod
        def _get_base_sounds(cls):
            """Получить базовый список звуков es."""
            return [
                renpy.store.music_list["dinner_horn_processed"],
                renpy.store.sfx_brass_drop,
                renpy.store.sfx_ghost_children_laugh,
                renpy.store.sfx_owl_far
            ]
        
        @classmethod
        def _get_door_sounds(cls):
            """Получить список звуков двери."""
            return [
                renpy.store.sfx_knock_door2,
                renpy.store.sfx_knock_door3_dull,
                renpy.store.sfx_knock_door7_polite
            ]
        
        @classmethod
        def _play_fnasr_sound(cls):
            """Воспроизвести случайный звук FNaSR."""
            sound = random.choice(cls._FNASR_SOUNDS)
            execute_in_main_thread(
                renpy.music.play,
                resources.sounds.random[sound],
                channel="v1_game_random_sfx_FNaSR",
                loop=False
            )
        
        @classmethod
        def _play_environment_sound(cls):
            """Воспроизвести случайный звук es."""
            sounds = cls._get_base_sounds()
            
            # Добавить звуки двери если дверь используется
            if cls._door_status:
                sounds.extend(cls._get_door_sounds())
            
            execute_in_main_thread(
                renpy.music.play,
                random.choice(sounds),
                channel="v1_game_random_sfx_FNaSR",
                loop=False
            )
        
        @classmethod
        def update(cls):
            """
            Обновление генератора звуков.
            """
            if random.random() >= cls.RANDOM_SOUND_PROBABILITY + cls.randomness_modifier:
                return
            
            # Выбор типа звука: FNaSR или стандартный
            if random.random() < cls.FNASR_SOUND_PROBABILITY:
                cls._play_fnasr_sound()
            else:
                cls._play_environment_sound()
        
        @staticmethod
        def on_camera_selected(camera_id=None):
            """Обработчик выбора камеры."""
            if random.random() >= SoundRandomGenerator.CAMERA_SOUND_PROBABILITY:
                return
            
            # Базовые звуки камеры
            sounds = list(SoundRandomGenerator._CAMERA_SOUNDS)
            
            # Добавить песню для камеры 11
            if camera_id == 11:
                sounds.append("pirate_song2")
            
            sound = random.choice(sounds)
            
            # Воспроизвести звук FNaSR
            if sound != "v1_original_es_sound_flag":
                execute_in_main_thread(
                    renpy.music.play,
                    resources.sounds.random[sound],
                    channel="v1_camera_random_sfx_FNaSR",
                    loop=False
                )
                return
            
            # Воспроизвести стандартный звук
            sounds = []
            if camera_id == 12:
                sounds.append(renpy.store.sfx_bus_honk)
            
            # Воспроизвести только если есть доступные звуки
            if sounds:
                execute_in_main_thread(
                    renpy.music.play,
                    random.choice(sounds),
                    channel="v1_game_random_sfx_FNaSR",
                    loop=False
                )
