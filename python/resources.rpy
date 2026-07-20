init 10 python in v1FNaSR:

    import posixpath

    class Folder(object):
        def __init__(self, name="", parent=None):
            self._name = name
            self._parent = parent
            self._files = {}          # local files only
            self._folders = {}        # name -> folder
            self._cache_files_flat = {}    # recursive file cache
            self._cache_folders_flat = {}  # recursive folder cache

        def add_file(self, name, full_path):
            self._files[name] = full_path

        def __getitem__(self, key):
            return self._files[key]

        def get_or_create_folder(self, name):
            if name not in self._folders:
                self._folders[name] = Folder(name, self)
            return self._folders[name]

        def __getattr__(self, key):
            if key in self._folders:
                return self._folders[key]
            raise AttributeError(key)

        def list_files(self):
            return list(self._files.keys())

        def list_folders(self):
            return list(self._folders.keys())

        def build_cache(self):
            """Рекурсивно строит кеш файлов и папок."""
            self._cache_files_flat = dict(self._files)
            self._cache_folders_flat = {}

            for folder_name, folder in self._folders.items():
                folder.build_cache()

                # cache subfolders
                self._cache_folders_flat[folder_name] = folder
                self._cache_folders_flat.update(folder._cache_folders_flat)

                # cache files
                self._cache_files_flat.update(folder._cache_files_flat)

        # быстрый поиск файла по имени
        def find_file(self, name, default=None):
            return self._cache_files_flat.get(name, default)


        def tree(self, indent=""):
            """Печатает древовидную структуру папок/файлов."""
            renpy.log("----------| FNaSR |----------")
            renpy.log(indent + self._name)

            # files
            for f in sorted(self._files):
                renpy.log(indent + "    ├── " + f)

            # folders
            for i, name in enumerate(sorted(self._folders)):
                folder = self._folders[name]
                last = (i == len(self._folders) - 1)
                branch = "    └── " if last else "    ├── "

                renpy.log(indent + branch + name)
                folder.tree(indent + ("    " if last else "    |"))
            renpy.log("------------------------------")


    class Resources(object):
        """Менеджер ресурсов: изображения, звуки, шрифты."""
        
        def __init__(self, mod_path, images="images", sounds="sounds", fonts="fonts"):
            self.mod_path = mod_path
            self.paths_directors = {
                "images": images,
                "sounds": sounds,
                "fonts": fonts
            }

            self.whitelist_extensions = {
                "images": ["png", "jpg", "jpeg", "webp", "avif", "svg", "bmp", "gif", "tga", "tif", "tiff"],
                "sounds": ["ogg", "opus", "mp3", "wav", "flac", "m4a", "mp2", "aif", "aiff", "mod", "xm", "it", "s3m"],
                "fonts": ["ttf", "otf"]
            }
            
            # корневые папки
            self.images = Folder("images")
            self.sounds = Folder("sounds")
            self.fonts  = Folder("fonts")

            # внутренние индексы
            self._image_index = {}
            self._sound_index = {}
            self._font_index  = {}

            self._initialized = False

        # -------------------------------------------------------

        def init(self):
            if self._initialized:
                return

            files = renpy.list_files()
            self._index_category(self.images, "images", files)
            self._index_category(self.sounds, "sounds", files)
            self._index_category(self.fonts,  "fonts",  files)

            # build caches
            self.images.build_cache()
            self.sounds.build_cache()
            self.fonts.build_cache()

            self._initialized = True

        # -------------------------------------------------------

        def _index_category(self, root_folder, category, files):
            """Строит дерево для конкретной категории."""
            base_dir = posixpath.join(self.mod_path, self.paths_directors[category])
            prefix = base_dir + "/"

            allowed_ext = self.whitelist_extensions[category]

            for path in files:
                if not path.startswith(prefix):
                    continue

                filename = path.split("/")[-1]
                if "." not in filename:
                    continue

                ext = filename.rsplit(".", 1)[-1].lower()
                if ext not in allowed_ext:
                    continue

                name_no_ext = filename.rsplit(".", 1)[0]

                # относительный путь после категории
                rel = path[len(prefix):]      # dir1/dir2/a.png

                parts = rel.split("/")        # ["dir1", "dir2", "a.png"]
                folders = parts[:-1]          # ["dir1", "dir2"]
                file_name = name_no_ext

                # Проверка конфликтов с методами менеджера
                for f in folders:
                    if hasattr(self, f):
                        raise Exception(
                            "Folder '%s' conflicts with V1ResourcesFNaSR attribute." % f
                        )

                # создаём вложенную цепочку
                folder = root_folder
                for f in folders:
                    folder = folder.get_or_create_folder(f)

                folder.add_file(file_name, path)

                # индекс для быстрого доступа (только для файлов верхнего уровня)
                if category == "images":
                    self._image_index[file_name] = path
                elif category == "sounds":
                    self._sound_index[file_name] = path
                else:
                    self._font_index[file_name] = path

        # -------------------------------------------------------

        def find_image(self, name, default=None):
            return self.images.find_file(name, default)

        def find_sound(self, name, default=None):
            return self.sounds.find_file(name, default)

        def find_font(self, name, default=None):
            return self.fonts.find_file(name, default)

        def get_image(self, name, default=None):
            return self._image_index.get(name, default)

        def get_sound(self, name, default=None):
            return self._sound_index.get(name, default)

        def get_font(self, name, default=None):
            return self._font_index.get(name, default)

        def reload(self):
            self.images = Folder("images")
            self.sounds = Folder("sounds")
            self.fonts  = Folder("fonts")

            self._image_index.clear()
            self._sound_index.clear()
            self._font_index.clear()

            self._initialized = False
            self.init()

        def __repr__(self):
            return "V1ResourcesFNaSR(%s)" % self.mod_path


    # Инициализация
    resources = Resources(Adapter.get_mod_folder())#resources = Resources("FNaS_R")
    resources.init()
    renpy.store.v1resFNaSR = resources

    for im_name in resources.images.bg.list_files():
        resources.images.bg.add_file(im_name, Adapter.scale_image(resources.images.bg[im_name], 1920, 1080))





    renpy.music.register_channel("v1_camera_sfx_FNaSR", mixer="sound", loop=False)
    renpy.music.register_channel("v1_camera_random_sfx_FNaSR", mixer="sound", loop=False)
    renpy.music.register_channel("v1_screamer_sfx_FNaSR", mixer="sound", loop=False)
    renpy.music.register_channel("v1_camera_ambience_FNaSR", mixer="ambience", loop=True)
    renpy.music.register_channel("v1_show_camera_ambience_FNaSR", mixer="ambience", loop=True)

    renpy.music.register_channel("v1_game_ambience_1_FNaSR", mixer="ambience", loop=True)
    renpy.music.register_channel("v1_game_ambience_2_FNaSR", mixer="ambience", loop=True)
    renpy.music.register_channel("v1_game_random_sfx_FNaSR", mixer="sound", loop=False)

    renpy.music.register_channel("v1heartbeatFNaSR", mixer="sound", loop=False)
    renpy.music.register_channel("v1breathingFNaSR", mixer="sound", loop=False)

    renpy.music.register_channel("v1_noise_FNaSR", mixer="sound", loop=True)

    renpy.music.register_channel("sound2", mixer="sound", loop=False)

init 11:

    image v1_ui_monitor_button_FNaSR = v1FNaSR.Adapter.scale_image(v1resFNaSR.images.other["FNaG_Monitor_Button"], 537, 47)

    image v1_ui_door_open_FNaSR = v1FNaSR.Adapter.scale_image(v1resFNaSR.images.other["button_unclick"], 231, 47)
    image v1_ui_door_close_FNaSR = v1FNaSR.Adapter.scale_image(v1resFNaSR.images.other["button_click"], 231, 47)

    image v1_ui_bulb_on_FNaSR = v1FNaSR.Adapter.scale_image(v1resFNaSR.images.other["bulb_on"], 231, 47)
    image v1_ui_bulb_off_FNaSR = v1FNaSR.Adapter.scale_image(v1resFNaSR.images.other["bulb_off"], 231, 47)

    image bg v1_view_train_window_FNaSR = v1resFNaSR.images.bg["v1_view_train_window"]
    image bg v1_checkpoint_FNaSR = v1FNaSR.Adapter.scale_image(v1resFNaSR.images.bg["v1_checkpoint"], 1920, 1080)
    image bg v1_ext_houses_night_FNaSR = v1resFNaSR.images.bg["ext_houses_night"]
    image bg v1_int_house_of_mt_sunset_parallax_FNaSR = v1FNaSRDisplay.Parallax(
        displayable=v1resFNaSR.images.es["int_house_of_mt_sunset"], # "images/bg/int_house_of_mt_sunset.jpg",
        zoom=1.15,
        anchor=(renpy.config.screen_width>>1, renpy.config.screen_height>>1),
        power=0.07,
        sharpness_factor=0.1
    )

    default persistent.v1_recommendation_say_FNaSR = False

    image v1_recommendation_FNaSR = v1FNaSR.Adapter.scale_image(v1resFNaSR.images.other["recommendation"], 1024, 1024)

    #image v1_mod_button_text_FNaSR = At(Text("{unstable=(5, 2.5, v1_text_24_mod_button_FNaSR)}Пять Ночей в Совёнке Remaster{/unstable}", style="v1_text_24_mod_button_static_FNaSR"), v1_vhs_crt_shader_t_FNaSR(0.0175))
    #image v1_mod_button_text_FNaSR = Text("{unstable=(5, 2.5, v1_text_24_mod_button_FNaSR)}Пять Ночей в Совёнке Remaster{/unstable}", style="v1_text_24_mod_button_static_FNaSR")
    image v1_mod_button_text_FNaSR = At(Text("Пять Ночей в Совёнке Remaster", style="v1_text_24_mod_button_static_FNaSR"), v1_vhs_crt_shader_t_FNaSR(0.0575))

    # 5 - разброс букв, 2.5 - время на обновление
    #image v1_mod_button_text_FNaSR = At(Text("{unstable=(5, 0.1, v1_text_24_mod_button_FNaSR)}Пять Ночей в Совёнке Remaster{/unstable}", style="v1_text_24_mod_button_static_FNaSR"), v1_vhs_crt_shader_t_FNaSR(0.0175))

    image v1_door_hold_vignette_FNaSR = v1resFNaSR.images.other["door_hold_vignette"]

    image v1testimage = v1FNaSRDisplay.Parallax(
        displayable=v1resFNaSR.images.bg["R_int_mt_house_night_light"],
        zoom=1.15,
        anchor=(renpy.config.screen_width>>1, renpy.config.screen_height>>1),
        power=0.07,
        sharpness_factor=0.1
    )

    image anim v1_tablet_open_entire_FNaSR:
        v1resFNaSR.images.anim["Tablet_Opening_1"]
        pause 0.03
        v1resFNaSR.images.anim["Tablet_Opening_2"]
        pause 0.03
        v1resFNaSR.images.anim["Tablet_Opening_3"]
        pause 0.03
        v1resFNaSR.images.anim["Tablet_Opening_4"]
        pause 0.03
        v1resFNaSR.images.anim["Tablet_Opening_5"]
        pause 0.03
        v1resFNaSR.images.anim["Tablet_Opening_6"]
        pause 0.03
        v1resFNaSR.images.anim["Tablet_Opening_7"]
    

    image anim v1_tablet_close_entire_VNaSR:
        v1resFNaSR.images.anim["Tablet_Opening_7"]
        pause 0.03
        v1resFNaSR.images.anim["Tablet_Opening_6"]
        pause 0.03
        v1resFNaSR.images.anim["Tablet_Opening_5"]
        pause 0.03
        v1resFNaSR.images.anim["Tablet_Opening_4"]
        pause 0.03
        v1resFNaSR.images.anim["Tablet_Opening_3"]
        pause 0.03
        v1resFNaSR.images.anim["Tablet_Opening_2"]
        pause 0.03
        v1resFNaSR.images.anim["Tablet_Opening_1"]

    image anim v1_ext_square_night_party_anim_FNaSR:
        v1resFNaSR.images.bg["v1_ext_square_night_party_FNaSR"] with dissolve2
        pause(2.5)
        v1resFNaSR.images.bg["v1_ext_square_night_party2_FNaSR"] with dissolve2
        pause(2.5)
        repeat

    image anim v1_ext_square_night_party_genda_none_anim_FNaSR:
        v1resFNaSR.images.bg["genda_none"] with dissolve2
        pause(2.5)
        v1resFNaSR.images.bg["genda_none1"] with dissolve2
        pause(2.5)
        repeat

    image v1_C_static_entire_FNaSR:
        v1resFNaSR.images.static["C_static_1"]
        pause 0.04
        v1resFNaSR.images.static["C_static_2"]
        pause 0.04
        v1resFNaSR.images.static["C_static_3"]
        pause 0.04
        v1resFNaSR.images.static["C_static_4"]
        pause 0.04
        repeat

    image v1_button_static_entire_FNaSR:
        v1resFNaSR.images.ButtonStatic["B_static_1"]
        pause 0.04
        v1resFNaSR.images.ButtonStatic["B_static_2"]
        pause 0.04
        v1resFNaSR.images.ButtonStatic["B_static_3"]
        pause 0.04
        v1resFNaSR.images.ButtonStatic["B_static_4"]
        pause 0.04
        repeat

















